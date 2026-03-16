"""
Enhanced Template endpoints for internal production tool
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.core.database import get_db
from app.services.template_application_service import TemplateApplicationService
from app.services.auth_service import get_current_user
from app.models.models import User

router = APIRouter()


# Schemas
class TemplateApplyRequest(BaseModel):
    project_id: int
    template_id: int
    product_name: str
    usp: str
    target_audience: str
    brand_tone: str = "친근함"  # 친근함, 전문적, 감성적
    color_override: Optional[dict] = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    thumbnail_url: Optional[str]
    funding_amount: int
    success_rate: int
    usage_count: int
    difficulty: str
    is_featured: bool


class TemplateApplicationResponse(BaseModel):
    html_content: str
    page_structure: dict
    ai_copy: str
    alternatives: List[str]
    template_info: dict
    color_scheme: dict


@router.get("/categories", response_model=List[dict])
async def get_template_categories(
    db: AsyncSession = Depends(get_db),
):
    """템플릿 카테고리 목록"""
    from app.models.templates_enhanced import TemplateCategory
    from sqlalchemy import select
    
    result = await db.execute(
        select(TemplateCategory)
        .where(TemplateCategory.is_active == True)
        .order_by(TemplateCategory.sort_order)
    )
    categories = result.scalars().all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon": cat.icon,
        }
        for cat in categories
    ]


@router.get("/", response_model=List[dict])
async def list_templates(
    category_slug: Optional[str] = None,
    difficulty: Optional[str] = None,
    featured_only: bool = False,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """
    템플릿 목록 조회
    
    - **category_slug**: 카테고리 필터 (tech-electronics, fashion-beauty, etc.)
    - **difficulty**: 난이도 필터 (easy, medium, hard)
    - **featured_only**: 추천 템플릿만 보기
    - **limit**: 최대 개수
    """
    template_service = TemplateApplicationService(db)
    templates = await template_service.get_recommended_templates(category_slug, limit)
    
    # Apply filters
    if difficulty:
        templates = [t for t in templates if t.difficulty == difficulty]
    
    if featured_only:
        templates = [t for t in templates if t.is_featured]
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category.name if t.category else None,
            "thumbnail_url": t.thumbnail_url,
            "funding_amount": t.funding_amount,
            "success_rate": t.success_rate,
            "usage_count": t.usage_count,
            "difficulty": t.difficulty,
            "is_featured": t.is_featured,
            "color_scheme": t.color_scheme,
        }
        for t in templates
    ]


@router.get("/{template_id}", response_model=dict)
async def get_template_detail(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """템플릿 상세 정보"""
    from app.models.templates_enhanced import Template
    from sqlalchemy import select
    
    result = await db.execute(
        select(Template).where(Template.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    return {
        "id": template.id,
        "name": template.name,
        "description": template.description,
        "category": template.category.name if template.category else None,
        "html_structure": template.html_structure,
        "css_style": template.css_style,
        "color_scheme": template.color_scheme,
        "based_on_project_url": template.based_on_project_url,
        "funding_amount": template.funding_amount,
        "success_rate": template.success_rate,
        "usage_count": template.usage_count,
        "difficulty": template.difficulty,
        "is_featured": template.is_featured,
    }


@router.post("/apply", response_model=dict)
async def apply_template(
    request: TemplateApplyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    템플릿을 프로젝트에 적용 ⭐ 핵심 기능
    
    1. 템플릿 선택
    2. 제품 정보 입력 (제품명, USP, 타겟)
    3. AI가 템플릿에 맞춰 자동 생성
    4. 프리뷰 즉시 확인
    
    **예상 소요 시간: 3-5초**
    """
    template_service = TemplateApplicationService(db)
    
    try:
        result = await template_service.apply_template_to_project(
            project_id=request.project_id,
            template_id=request.template_id,
            customization_params={
                "product_name": request.product_name,
                "usp": request.usp,
                "target_audience": request.target_audience,
                "brand_tone": request.brand_tone,
                "color_override": request.color_override,
            },
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Template application failed: {str(e)}",
        )


@router.post("/quick-generate", response_model=dict)
async def quick_generate_from_template(
    category_slug: str,
    product_name: str,
    usp: str,
    target_audience: str,
    brand_tone: str = "친근함",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    빠른 생성: 카테고리만 선택하면 자동으로 가장 적합한 템플릿 선택 ⭐
    
    **사용 시나리오**:
    1. 고객 의뢰 들어옴
    2. 카테고리 선택 (테크/패션/식품/생활)
    3. 제품 정보 3가지만 입력
    4. 자동으로 최적 템플릿 선택 + 페이지 생성
    5. 5분 안에 초안 완성!
    """
    from app.services.project_service import ProjectService
    
    # Auto-create project
    project_service = ProjectService(db)
    project = await project_service.create_project(
        {
            "title": f"{product_name} 펀딩 페이지",
            "category": category_slug,
            "product_name": product_name,
            "usp": usp,
            "target_audience": target_audience,
        },
        current_user.id,
    )
    
    # Get best template for category
    template_service = TemplateApplicationService(db)
    templates = await template_service.get_recommended_templates(category_slug, limit=1)
    
    if not templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No templates found for category: {category_slug}",
        )
    
    # Apply template
    result = await template_service.apply_template_to_project(
        project_id=project.id,
        template_id=templates[0].id,
        customization_params={
            "product_name": product_name,
            "usp": usp,
            "target_audience": target_audience,
            "brand_tone": brand_tone,
        },
    )
    
    result["project_id"] = project.id
    result["project_slug"] = project.slug
    
    return result


@router.get("/stats/popular", response_model=List[dict])
async def get_popular_templates(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """가장 많이 사용된 템플릿 통계"""
    from app.models.templates_enhanced import Template
    from sqlalchemy import select
    
    result = await db.execute(
        select(Template)
        .where(Template.is_active == True)
        .order_by(Template.usage_count.desc())
        .limit(limit)
    )
    templates = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category.name if t.category else None,
            "usage_count": t.usage_count,
            "success_count": t.success_count,
            "success_rate_percent": (t.success_count / t.usage_count * 100) if t.usage_count > 0 else 0,
        }
        for t in templates
    ]
