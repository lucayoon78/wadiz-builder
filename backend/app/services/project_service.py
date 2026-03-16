"""
Project service
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slugify import slugify
from app.models.models import Project
from app.schemas.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreate, user_id: int) -> Project:
        """Create new project"""
        # Generate slug
        slug = slugify(project_data.title)
        
        # Ensure unique slug
        counter = 1
        original_slug = slug
        while await self._slug_exists(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        project = Project(
            user_id=user_id,
            title=project_data.title,
            slug=slug,
            category=project_data.category,
            product_name=project_data.product_name,
            usp=project_data.usp,
            target_audience=project_data.target_audience,
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def _slug_exists(self, slug: str) -> bool:
        """Check if slug already exists"""
        result = await self.db.execute(
            select(Project).where(Project.slug == slug)
        )
        return result.scalar_one_or_none() is not None
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_projects(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Project]:
        """Get all projects for a user"""
        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate) -> Project:
        """Update project"""
        project = await self.get_project(project_id)
        if not project:
            return None
        
        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        await self.db.commit()
        await self.db.refresh(project)
        return project
    
    async def delete_project(self, project_id: int):
        """Delete project"""
        project = await self.get_project(project_id)
        if project:
            await self.db.delete(project)
            await self.db.commit()
