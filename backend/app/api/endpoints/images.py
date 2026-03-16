"""
Image upload and management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import ImageResponse
from app.services.image_service import ImageService
from app.services.auth_service import get_current_user
from app.models.models import User

router = APIRouter()


@router.post("/upload/{project_id}", response_model=List[ImageResponse])
async def upload_images(
    project_id: int,
    files: List[UploadFile] = File(...),
    section: str = Form("body"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    이미지 업로드 (최대 20장)
    
    - **project_id**: 프로젝트 ID
    - **files**: 이미지 파일들 (JPG, PNG, GIF, WebP)
    - **section**: 섹션 (intro, body, outro)
    """
    image_service = ImageService(db)
    
    # Verify project ownership
    from app.services.project_service import ProjectService
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Validate file count
    if len(files) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 20 images allowed",
        )
    
    # Upload images
    try:
        uploaded_images = await image_service.upload_images(
            project_id, files, section
        )
        return uploaded_images
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}",
        )


@router.get("/project/{project_id}", response_model=List[ImageResponse])
async def get_project_images(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """프로젝트의 모든 이미지"""
    image_service = ImageService(db)
    
    # Verify project ownership
    from app.services.project_service import ProjectService
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    images = await image_service.get_project_images(project_id)
    return images


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """이미지 삭제"""
    image_service = ImageService(db)
    
    # Get image and verify ownership
    image = await image_service.get_image(image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    # Verify project ownership
    from app.services.project_service import ProjectService
    project_service = ProjectService(db)
    project = await project_service.get_project(image.project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this image",
        )
    
    await image_service.delete_image(image_id)
    return None


@router.patch("/{image_id}/reorder", response_model=ImageResponse)
async def reorder_image(
    image_id: int,
    new_position: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """이미지 순서 변경"""
    image_service = ImageService(db)
    
    # Get image and verify ownership
    image = await image_service.get_image(image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found",
        )
    
    from app.services.project_service import ProjectService
    project_service = ProjectService(db)
    project = await project_service.get_project(image.project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    
    updated_image = await image_service.reorder_image(image_id, new_position)
    return updated_image
