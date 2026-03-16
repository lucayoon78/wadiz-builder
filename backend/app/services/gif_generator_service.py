"""
GIF generation service - Create animated GIFs from images
"""
import os
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from io import BytesIO
import asyncio
from concurrent.futures import ThreadPoolExecutor


class GIFGeneratorService:
    """이미지 시퀀스로 GIF 생성"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def create_gif_from_images(
        self,
        image_urls: List[str],
        output_path: str,
        duration: int = 500,  # ms per frame
        loop: int = 0,  # 0 = infinite loop
        optimize: bool = True,
        max_width: int = 860,
    ) -> str:
        """
        이미지 리스트로 GIF 생성
        
        Args:
            image_urls: 이미지 URL 리스트
            output_path: 출력 파일 경로
            duration: 프레임당 지속 시간 (ms)
            loop: 반복 횟수 (0 = 무한)
            optimize: 최적화 여부
            max_width: 최대 너비
        
        Returns:
            생성된 GIF 파일 경로
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_gif_sync,
            image_urls, output_path, duration, loop, optimize, max_width
        )
    
    def _create_gif_sync(
        self, image_urls, output_path, duration, loop_count, optimize, max_width
    ):
        """동기 GIF 생성 (CPU-bound 작업)"""
        
        frames = []
        
        # Load and resize images
        for url in image_urls:
            # Download or load image
            if url.startswith('http'):
                import requests
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(url)
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            frames.append(img)
        
        if not frames:
            raise ValueError("No images to create GIF")
        
        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop_count,
            optimize=optimize,
        )
        
        return output_path
    
    async def create_product_rotation_gif(
        self,
        image_url: str,
        output_path: str,
        angles: int = 12,  # 360도를 12등분
        duration: int = 100,
    ) -> str:
        """
        제품 이미지로 360도 회전 GIF 생성 (가상)
        실제로는 동일 이미지를 회전시킴
        
        TODO: 실제 3D 모델이나 다각도 이미지가 있으면 사용
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_rotation_gif_sync,
            image_url, output_path, angles, duration
        )
    
    def _create_rotation_gif_sync(self, image_url, output_path, angles, duration):
        """동기 회전 GIF 생성"""
        
        # Load image
        if image_url.startswith('http'):
            import requests
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(image_url)
        
        # Convert to RGBA for rotation
        img = img.convert('RGBA')
        
        frames = []
        angle_step = 360 // angles
        
        for i in range(angles):
            angle = i * angle_step
            rotated = img.rotate(angle, expand=False, fillcolor=(255, 255, 255, 0))
            
            # Convert back to RGB
            rgb_frame = Image.new('RGB', rotated.size, (255, 255, 255))
            rgb_frame.paste(rotated, mask=rotated.split()[3])  # Use alpha as mask
            
            frames.append(rgb_frame)
        
        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True,
        )
        
        return output_path
    
    async def create_text_animation_gif(
        self,
        base_image_url: str,
        texts: List[str],
        output_path: str,
        duration: int = 800,
        font_size: int = 60,
    ) -> str:
        """
        이미지에 텍스트 애니메이션 추가 (프로모션용)
        예: "50% 할인!" → "지금 바로!" → "무료배송!"
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_text_animation_sync,
            base_image_url, texts, output_path, duration, font_size
        )
    
    def _create_text_animation_sync(
        self, base_image_url, texts, output_path, duration, font_size
    ):
        """동기 텍스트 애니메이션 GIF"""
        
        # Load base image
        if base_image_url.startswith('http'):
            import requests
            response = requests.get(base_image_url)
            base_img = Image.open(BytesIO(response.content))
        else:
            base_img = Image.open(base_image_url)
        
        base_img = base_img.convert('RGB')
        
        frames = []
        
        # Try to load font (fallback to default)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        for text in texts:
            # Create frame
            frame = base_img.copy()
            draw = ImageDraw.Draw(frame)
            
            # Calculate text position (center bottom)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (frame.width - text_width) // 2
            y = frame.height - text_height - 50
            
            # Draw text with outline
            outline_color = (0, 0, 0)
            text_color = (255, 255, 0)
            
            # Outline
            for adj in range(-2, 3):
                for adj2 in range(-2, 3):
                    draw.text((x+adj, y+adj2), text, font=font, fill=outline_color)
            
            # Main text
            draw.text((x, y), text, font=font, fill=text_color)
            
            frames.append(frame)
        
        # Save
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True,
        )
        
        return output_path
    
    async def optimize_gif(
        self,
        input_path: str,
        output_path: str,
        max_size_mb: int = 5,
        max_width: int = 860,
    ) -> str:
        """
        GIF 최적화 (파일 크기 줄이기)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._optimize_gif_sync,
            input_path, output_path, max_size_mb, max_width
        )
    
    def _optimize_gif_sync(self, input_path, output_path, max_size_mb, max_width):
        """동기 GIF 최적화"""
        
        with Image.open(input_path) as img:
            frames = []
            
            # Extract frames
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGB')
                
                # Resize if too large
                if frame.width > max_width:
                    ratio = max_width / frame.width
                    new_height = int(frame.height * ratio)
                    frame = frame.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                frames.append(frame)
            
            # Save optimized
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=img.info.get('duration', 500),
                loop=img.info.get('loop', 0),
                optimize=True,
                quality=85,  # Slightly reduce quality
            )
        
        # Check file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            # Further optimization: reduce frames
            with Image.open(output_path) as img:
                frames = []
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    if i % 2 == 0:  # Skip every other frame
                        frames.append(frame.convert('RGB'))
                
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=img.info.get('duration', 500) * 2,
                    loop=0,
                    optimize=True,
                    quality=75,
                )
        
        return output_path
