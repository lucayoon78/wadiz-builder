"""
Template management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import TemplateResponse
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    category: str = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """템플릿 목록 (성공 사례 기반)"""
    template_service = TemplateService(db)
    templates = await template_service.get_templates(category, skip, limit)
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
):
    """템플릿 상세"""
    template_service = TemplateService(db)
    template = await template_service.get_template(template_id)
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    
    return template
