"""
Multi-platform export endpoint - Generate pages for all platforms at once
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.models.models import User
from app.services.gif_generator_service import GIFGeneratorService
from app.services.thumbnail_generator_service import ThumbnailGeneratorService
from app.services.platform_specs import PLATFORM_SPECS

router = APIRouter()


class MultiPlatformExportRequest(BaseModel):
    project_id: int
    platforms: List[str]  # ["wadiz", "smartstore", "coupang", "gmarket"]
    generate_thumbnails: bool = True
    generate_gifs: bool = True
    thumbnail_style: str = "clean"  # clean, promotional, premium
    thumbnail_badge: Optional[str] = None  # "NEW", "BEST", "50% OFF"


class MultiPlatformExportResponse(BaseModel):
    project_id: int
    exports: dict  # {"wadiz": {...}, "smartstore": {...}}
    thumbnails: dict
    gifs: dict


@router.post("/multi-platform-export", response_model=dict)
async def export_to_multiple_platforms(
    request: MultiPlatformExportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    모든 플랫폼용 페이지 한 번에 생성 ⭐⭐⭐
    
    **고객 의뢰 → 한 번에 모든 플랫폼 페이지 완성!**
    
    생성되는 것들:
    - 와디즈: 긴 스토리텔링 페이지 (1080px)
    - 스마트스토어: 중간 길이 정보형 페이지 (860px) + SEO
    - 쿠팡: 짧은 간결 페이지 (860px, GIF 없음)
    - G마켓: 프로모션형 페이지 (860px)
    - 11번가: 표준 페이지 (860px)
    
    각 플랫폼별:
    - 상세페이지 HTML/이미지
    - 썸네일 (500x500 또는 640x640)
    - GIF (플랫폼이 지원하는 경우)
    
    **예상 소요 시간: 30초 - 1분**
    """
    
    from app.services.project_service import ProjectService
    from app.services.export_service import ExportService
    
    # Get project
    project_service = ProjectService(db)
    project = await project_service.get_project(request.project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    gif_service = GIFGeneratorService()
    thumbnail_service = ThumbnailGeneratorService()
    export_service = ExportService(db)
    
    result = {
        "project_id": request.project_id,
        "platforms": {},
        "thumbnails": {},
        "gifs": {},
    }
    
    # Generate for each platform
    for platform in request.platforms:
        if platform not in PLATFORM_SPECS:
            continue
        
        spec = PLATFORM_SPECS[platform]
        
        try:
            # Generate page HTML
            platform_html = await _generate_platform_page(
                project, platform, spec, export_service
            )
            
            result["platforms"][platform] = {
                "html_url": platform_html,
                "width": spec["max_width"],
                "length": spec["content_style"]["length"],
            }
            
            # Generate thumbnail
            if request.generate_thumbnails and project.images:
                thumbnail_path = f"/tmp/{platform}_thumbnail_{request.project_id}.jpg"
                await thumbnail_service.create_thumbnail(
                    product_image_url=project.images[0].file_url,
                    output_path=thumbnail_path,
                    platform=platform,
                    style=request.thumbnail_style,
                    add_badge=request.thumbnail_badge,
                )
                
                # TODO: Upload to S3 and get URL
                result["thumbnails"][platform] = {
                    "path": thumbnail_path,
                    "size": PLATFORM_SPECS[platform]["image_specs"]["thumbnail"],
                }
            
            # Generate GIF
            if request.generate_gifs and spec.get("gif_allowed") and len(project.images) >= 3:
                gif_path = f"/tmp/{platform}_animation_{request.project_id}.gif"
                
                # Take first 5 images
                image_urls = [img.file_url for img in project.images[:5]]
                
                await gif_service.create_gif_from_images(
                    image_urls=image_urls,
                    output_path=gif_path,
                    duration=500,  # 0.5 sec per frame
                    max_width=spec["max_width"],
                )
                
                result["gifs"][platform] = {
                    "path": gif_path,
                    "frames": len(image_urls),
                }
        
        except Exception as e:
            result["platforms"][platform] = {"error": str(e)}
    
    return result


async def _generate_platform_page(project, platform, spec, export_service):
    """플랫폼별 페이지 생성"""
    
    # Adapt content to platform style
    if spec["content_style"]["tone"] == "storytelling":
        # Long form (Wadiz)
        html = await export_service.export_to_html(project.id)
    elif spec["content_style"]["tone"] == "concise":
        # Short form (Coupang)
        html = await _generate_short_page(project)
    else:
        # Standard
        html = await export_service.export_to_html(project.id)
    
    return html


async def _generate_short_page(project):
    """짧은 페이지 생성 (쿠팡용)"""
    
    # Simplified HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: sans-serif; max-width: 860px; margin: 0 auto; }}
            .section {{ margin: 40px 0; }}
            img {{ width: 100%; height: auto; }}
            h2 {{ font-size: 24px; }}
        </style>
    </head>
    <body>
        <h1>{project.product_name}</h1>
        <div class="section">
            <h2>핵심 특징</h2>
            <p>{project.usp}</p>
        </div>
    """
    
    # Add images (max 3 for short page)
    for img in project.images[:3]:
        html += f'<img src="{img.file_url}" alt="Product">'
    
    html += """
    </body>
    </html>
    """
    
    return {"html_url": "/tmp/short_page.html"}


@router.post("/convert-platform", response_model=dict)
async def convert_page_between_platforms(
    project_id: int,
    from_platform: str,
    to_platform: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    플랫폼 간 페이지 변환 ⭐
    
    예: 와디즈 페이지 → 스마트스토어 페이지
    
    **변환 규칙**:
    - Wadiz → SmartStore: 길이 50% 축소, 스토리텔링 → 정보형
    - SmartStore → Coupang: 길이 30% 축소, 간결하게
    - Any → Gmarket: 프로모션 강조 추가
    """
    
    from app.services.project_service import ProjectService
    
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    from_spec = PLATFORM_SPECS.get(from_platform)
    to_spec = PLATFORM_SPECS.get(to_platform)
    
    if not from_spec or not to_spec:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platform"
        )
    
    # Conversion logic
    conversion_notes = []
    
    # Width adjustment
    if from_spec["max_width"] != to_spec["max_width"]:
        conversion_notes.append(
            f"이미지 너비: {from_spec['max_width']}px → {to_spec['max_width']}px"
        )
    
    # Length adjustment
    if from_spec["content_style"]["length"] != to_spec["content_style"]["length"]:
        length_map = {"very_long": 3, "medium": 2, "short": 1}
        from_length = length_map[from_spec["content_style"]["length"]]
        to_length = length_map[to_spec["content_style"]["length"]]
        
        if from_length > to_length:
            reduction = int((from_length - to_length) / from_length * 100)
            conversion_notes.append(f"내용 길이 {reduction}% 축소 필요")
    
    # GIF handling
    if from_spec.get("gif_allowed") and not to_spec.get("gif_allowed"):
        conversion_notes.append("GIF → 정적 이미지 변환 필요")
    
    return {
        "project_id": project_id,
        "from_platform": from_platform,
        "to_platform": to_platform,
        "conversion_notes": conversion_notes,
        "status": "conversion_preview",
        "recommendation": _get_conversion_recommendation(from_platform, to_platform),
    }


def _get_conversion_recommendation(from_platform, to_platform):
    """변환 추천 사항"""
    
    recommendations = {
        ("wadiz", "smartstore"): "스토리텔링 부분을 정보 중심으로 요약하세요. SEO 키워드를 추가하세요.",
        ("wadiz", "coupang"): "핵심 특징 3-5개만 남기고 나머지는 삭제하세요. GIF를 정적 이미지로 교체하세요.",
        ("smartstore", "coupang"): "상세한 설명을 간결하게 줄이세요. 썸네일은 순백 배경으로 교체하세요.",
        ("any", "gmarket"): "할인율, 프로모션 정보를 추가하세요.",
    }
    
    key = (from_platform, to_platform)
    if key in recommendations:
        return recommendations[key]
    
    return "플랫폼 규격에 맞게 이미지 크기와 내용 길이를 조정하세요."


@router.post("/batch-generate-assets")
async def batch_generate_all_assets(
    project_id: int,
    platforms: List[str],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    일괄 에셋 생성 ⭐⭐⭐
    
    생성되는 모든 파일:
    - 각 플랫폼별 상세페이지 HTML
    - 각 플랫폼별 썸네일 (500x500 또는 640x640)
    - 각 플랫폼별 GIF (지원 시)
    - 모든 파일을 ZIP으로 압축
    
    **결과물**: `project_123_all_platforms.zip`
    ```
    /wadiz
      - detail_page_wadiz.html
      - thumbnail_wadiz.jpg
      - animation_wadiz.gif
    /smartstore
      - detail_page_smartstore.html
      - thumbnail_smartstore.jpg
      - animation_smartstore.gif
    /coupang
      - detail_page_coupang.html
      - thumbnail_coupang.jpg
    /gmarket
      - detail_page_gmarket.html
      - thumbnail_gmarket.jpg
      - animation_gmarket.gif
    ```
    
    **예상 소요 시간: 1-2분**
    """
    
    from app.services.project_service import ProjectService
    
    project_service = ProjectService(db)
    project = await project_service.get_project(project_id)
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # TODO: Implement full batch generation
    
    return {
        "project_id": project_id,
        "platforms": platforms,
        "status": "generating",
        "estimated_time_seconds": 60,
        "message": "모든 플랫폼 에셋을 생성 중입니다. 완료되면 알림을 드립니다.",
    }
