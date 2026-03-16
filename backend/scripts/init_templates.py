"""
Database initialization script - Seed templates
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from app.models.templates_enhanced import TemplateCategory, Template, Base
from app.services.template_seeds import TEMPLATE_CATEGORIES, TEMPLATES


async def init_db():
    """Initialize database with template data"""
    
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        # Insert categories
        category_map = {}
        for cat_data in TEMPLATE_CATEGORIES:
            category = TemplateCategory(**cat_data)
            session.add(category)
            await session.flush()
            category_map[cat_data["slug"]] = category.id
        
        await session.commit()
        print(f"✅ Created {len(TEMPLATE_CATEGORIES)} template categories")
        
        # Insert templates
        for tmpl_data in TEMPLATES:
            category_slug = tmpl_data.pop("category_slug")
            tmpl_data["category_id"] = category_map[category_slug]
            
            template = Template(**tmpl_data)
            session.add(template)
        
        await session.commit()
        print(f"✅ Created {len(TEMPLATES)} templates")
    
    print("🎉 Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
