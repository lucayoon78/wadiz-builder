"""
Template service
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Template


class TemplateService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_templates(
        self, category: Optional[str] = None, skip: int = 0, limit: int = 20
    ) -> List[Template]:
        """Get all templates"""
        query = select(Template).where(Template.is_active == True)
        
        if category:
            query = query.where(Template.category == category)
        
        query = query.order_by(Template.usage_count.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()
