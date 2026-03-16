"""
Image service - S3/R2 upload and management
"""
import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import boto3
from botocore.client import Config
from PIL import Image as PILImage
from io import BytesIO
from app.core.config import settings
from app.models.models import Image


class ImageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Initialize S3/R2 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL if settings.AWS_ENDPOINT_URL else None,
            config=Config(signature_version='s3v4'),
        )
        self.bucket_name = settings.AWS_S3_BUCKET_NAME
    
    async def upload_images(
        self, project_id: int, files: List[UploadFile], section: str
    ) -> List[Image]:
        """Upload multiple images to S3/R2"""
        uploaded_images = []
        
        for idx, file in enumerate(files):
            # Validate file type
            if not file.content_type.startswith('image/'):
                continue
            
            # Read file
            contents = await file.read()
            
            # Get image dimensions
            pil_image = PILImage.open(BytesIO(contents))
            width, height = pil_image.size
            
            # Generate unique filename
            ext = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            s3_key = f"projects/{project_id}/{unique_filename}"
            
            # Upload to S3/R2
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=contents,
                    ContentType=file.content_type,
                )
                
                # Generate public URL
                if settings.AWS_ENDPOINT_URL:
                    # Cloudflare R2 or custom endpoint
                    file_url = f"{settings.AWS_ENDPOINT_URL}/{self.bucket_name}/{s3_key}"
                else:
                    # Standard S3
                    file_url = f"https://{self.bucket_name}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{s3_key}"
                
                # Get current max position
                max_position = await self._get_max_position(project_id)
                
                # Create DB record
                image = Image(
                    project_id=project_id,
                    filename=unique_filename,
                    original_filename=file.filename,
                    file_url=file_url,
                    file_size=len(contents),
                    width=width,
                    height=height,
                    mime_type=file.content_type,
                    position=max_position + idx + 1,
                    section=section,
                )
                
                self.db.add(image)
                uploaded_images.append(image)
                
            except Exception as e:
                print(f"Failed to upload {file.filename}: {e}")
                continue
        
        await self.db.commit()
        
        # Refresh all images
        for image in uploaded_images:
            await self.db.refresh(image)
        
        return uploaded_images
    
    async def _get_max_position(self, project_id: int) -> int:
        """Get max position for images in project"""
        result = await self.db.execute(
            select(Image)
            .where(Image.project_id == project_id)
            .order_by(Image.position.desc())
            .limit(1)
        )
        image = result.scalar_one_or_none()
        return image.position if image else 0
    
    async def get_image(self, image_id: int) -> Optional[Image]:
        """Get image by ID"""
        result = await self.db.execute(
            select(Image).where(Image.id == image_id)
        )
        return result.scalar_one_or_none()
    
    async def get_project_images(self, project_id: int) -> List[Image]:
        """Get all images for a project"""
        result = await self.db.execute(
            select(Image)
            .where(Image.project_id == project_id)
            .order_by(Image.position)
        )
        return result.scalars().all()
    
    async def delete_image(self, image_id: int):
        """Delete image from S3 and DB"""
        image = await self.get_image(image_id)
        if not image:
            return
        
        # Delete from S3
        try:
            s3_key = f"projects/{image.project_id}/{image.filename}"
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key,
            )
        except Exception as e:
            print(f"Failed to delete from S3: {e}")
        
        # Delete from DB
        await self.db.delete(image)
        await self.db.commit()
    
    async def reorder_image(self, image_id: int, new_position: int) -> Image:
        """Change image position"""
        image = await self.get_image(image_id)
        if image:
            image.position = new_position
            await self.db.commit()
            await self.db.refresh(image)
        return image
