"""
Thumbnail generation service - Auto-generate product thumbnails
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from typing import Optional, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor


class ThumbnailGeneratorService:
    """상품 썸네일 자동 생성"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def create_thumbnail(
        self,
        product_image_url: str,
        output_path: str,
        platform: str = "smartstore",
        style: str = "clean",
        add_badge: Optional[str] = None,
    ) -> str:
        """
        플랫폼별 썸네일 생성
        
        Args:
            product_image_url: 제품 이미지 URL
            output_path: 출력 경로
            platform: wadiz, smartstore, coupang, gmarket
            style: clean, promotional, premium
            add_badge: "NEW", "BEST", "50% OFF" 등
        
        Returns:
            생성된 썸네일 경로
        """
        from app.services.platform_specs import THUMBNAIL_SPECS
        
        specs = THUMBNAIL_SPECS.get(platform, THUMBNAIL_SPECS["smartstore"])
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_thumbnail_sync,
            product_image_url, output_path, specs, style, add_badge
        )
    
    def _create_thumbnail_sync(
        self, product_image_url, output_path, specs, style, add_badge
    ):
        """동기 썸네일 생성"""
        
        # Load product image
        if product_image_url.startswith('http'):
            import requests
            response = requests.get(product_image_url)
            product_img = Image.open(BytesIO(response.content))
        else:
            product_img = Image.open(product_image_url)
        
        # Get target size
        target_size = specs["size"]
        
        # Create thumbnail based on style
        if style == "clean":
            thumbnail = self._create_clean_thumbnail(product_img, target_size)
        elif style == "promotional":
            thumbnail = self._create_promotional_thumbnail(product_img, target_size)
        elif style == "premium":
            thumbnail = self._create_premium_thumbnail(product_img, target_size)
        else:
            thumbnail = self._create_clean_thumbnail(product_img, target_size)
        
        # Add badge if specified
        if add_badge:
            thumbnail = self._add_badge(thumbnail, add_badge)
        
        # Save
        thumbnail.save(output_path, format='JPEG', quality=95)
        
        return output_path
    
    def _create_clean_thumbnail(
        self, product_img: Image.Image, size: Tuple[int, int]
    ) -> Image.Image:
        """깔끔한 스타일 (스마트스토어, 쿠팡용)"""
        
        # Create white background
        thumbnail = Image.new('RGB', size, (255, 255, 255))
        
        # Convert product image
        product_img = product_img.convert('RGBA')
        
        # Calculate size to fit with padding
        padding = int(size[0] * 0.05)  # 5% padding
        max_size = (size[0] - 2 * padding, size[1] - 2 * padding)
        
        # Resize product image
        product_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Center position
        x = (size[0] - product_img.width) // 2
        y = (size[1] - product_img.height) // 2
        
        # Paste product image
        if product_img.mode == 'RGBA':
            thumbnail.paste(product_img, (x, y), product_img)
        else:
            thumbnail.paste(product_img, (x, y))
        
        return thumbnail
    
    def _create_promotional_thumbnail(
        self, product_img: Image.Image, size: Tuple[int, int]
    ) -> Image.Image:
        """프로모션 스타일 (G마켓용)"""
        
        # Create gradient background
        thumbnail = Image.new('RGB', size, (255, 255, 255))
        draw = ImageDraw.Draw(thumbnail)
        
        # Gradient (yellow to white)
        for i in range(size[1]):
            ratio = i / size[1]
            r = int(255)
            g = int(255 - 50 * (1 - ratio))
            b = int(255 - 100 * (1 - ratio))
            draw.line([(0, i), (size[0], i)], fill=(r, g, b))
        
        # Add product image
        product_img = product_img.convert('RGBA')
        padding = int(size[0] * 0.08)
        max_size = (size[0] - 2 * padding, int(size[1] * 0.7))
        product_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        x = (size[0] - product_img.width) // 2
        y = padding
        
        if product_img.mode == 'RGBA':
            thumbnail.paste(product_img, (x, y), product_img)
        else:
            thumbnail.paste(product_img, (x, y))
        
        return thumbnail
    
    def _create_premium_thumbnail(
        self, product_img: Image.Image, size: Tuple[int, int]
    ) -> Image.Image:
        """프리미엄 스타일 (와디즈용)"""
        
        # Create soft gradient background
        thumbnail = Image.new('RGB', size, (245, 245, 250))
        
        # Add product image with shadow
        product_img = product_img.convert('RGBA')
        padding = int(size[0] * 0.1)
        max_size = (size[0] - 2 * padding, size[1] - 2 * padding)
        product_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Create shadow
        shadow = Image.new('RGBA', product_img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.ellipse(
            [(0, 0), product_img.size],
            fill=(0, 0, 0, 50)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        
        x = (size[0] - product_img.width) // 2
        y = (size[1] - product_img.height) // 2
        
        # Paste shadow first
        thumbnail.paste(shadow, (x + 10, y + 10), shadow)
        
        # Then paste product
        if product_img.mode == 'RGBA':
            thumbnail.paste(product_img, (x, y), product_img)
        else:
            thumbnail.paste(product_img, (x, y))
        
        return thumbnail
    
    def _add_badge(self, thumbnail: Image.Image, badge_text: str) -> Image.Image:
        """배지 추가 (NEW, BEST, 할인율 등)"""
        
        draw = ImageDraw.Draw(thumbnail)
        
        # Badge settings
        badge_size = 80
        badge_color = (255, 59, 48)  # Red
        text_color = (255, 255, 255)
        
        # Position (top-left corner)
        position = (20, 20)
        
        # Draw circle badge
        draw.ellipse(
            [position, (position[0] + badge_size, position[1] + badge_size)],
            fill=badge_color
        )
        
        # Draw text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Center text in badge
        bbox = draw.textbbox((0, 0), badge_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        text_x = position[0] + (badge_size - text_width) // 2
        text_y = position[1] + (badge_size - text_height) // 2
        
        draw.text((text_x, text_y), badge_text, fill=text_color, font=font)
        
        return thumbnail
    
    async def create_thumbnail_grid(
        self,
        product_image_urls: list,
        output_path: str,
        grid_size: Tuple[int, int] = (2, 2),
        thumbnail_size: int = 300,
    ) -> str:
        """
        여러 제품 이미지를 그리드로 배치한 썸네일 생성
        (세트 상품, 컬렉션 등)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._create_thumbnail_grid_sync,
            product_image_urls, output_path, grid_size, thumbnail_size
        )
    
    def _create_thumbnail_grid_sync(
        self, product_image_urls, output_path, grid_size, thumbnail_size
    ):
        """동기 그리드 썸네일 생성"""
        
        cols, rows = grid_size
        padding = 10
        
        # Calculate total size
        total_width = cols * thumbnail_size + (cols + 1) * padding
        total_height = rows * thumbnail_size + (rows + 1) * padding
        
        # Create canvas
        canvas = Image.new('RGB', (total_width, total_height), (255, 255, 255))
        
        # Load and place images
        for i, url in enumerate(product_image_urls[:cols * rows]):
            # Load image
            if url.startswith('http'):
                import requests
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
            else:
                img = Image.open(url)
            
            # Resize
            img = img.convert('RGB')
            img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
            
            # Calculate position
            col = i % cols
            row = i // cols
            
            x = padding + col * (thumbnail_size + padding)
            y = padding + row * (thumbnail_size + padding)
            
            # Paste
            canvas.paste(img, (x, y))
        
        # Save
        canvas.save(output_path, format='JPEG', quality=95)
        
        return output_path
    
    async def remove_background(
        self,
        product_image_url: str,
        output_path: str,
    ) -> str:
        """
        배경 제거 (쿠팡 필수)
        
        Note: 실제 배경 제거는 rembg 라이브러리 또는 AI API 필요
        여기서는 간단한 처리만
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._remove_background_sync,
            product_image_url, output_path
        )
    
    def _remove_background_sync(self, product_image_url, output_path):
        """
        동기 배경 제거
        
        TODO: rembg 또는 remove.bg API 연동
        """
        # Placeholder: Just load and save
        if product_image_url.startswith('http'):
            import requests
            response = requests.get(product_image_url)
            img = Image.open(BytesIO(response.content))
        else:
            img = Image.open(product_image_url)
        
        # Convert to RGBA
        img = img.convert('RGBA')
        
        # Save (actual background removal would happen here)
        img.save(output_path, format='PNG')
        
        return output_path
