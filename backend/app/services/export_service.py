"""
Export service - Generate HTML from project
"""
import os
import uuid
import zipfile
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.models import Project
from app.schemas.schemas import HTMLExportResponse
from app.services.project_service import ProjectService


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_service = ProjectService(db)
        
        # Setup Jinja2
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    async def export_to_html(
        self, project_id: int, template_id: Optional[int] = None
    ) -> HTMLExportResponse:
        """Export project to HTML ZIP"""
        
        # Get project with images
        project = await self.project_service.get_project(project_id)
        if not project:
            raise ValueError("Project not found")
        
        # Generate HTML
        html_content = await self._generate_html(project, template_id)
        
        # Create ZIP file
        file_key = str(uuid.uuid4())
        zip_path = f"/tmp/wadiz-export-{file_key}.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add HTML file
            zipf.writestr("index.html", html_content)
            
            # Add CSS
            css_content = self._get_default_css()
            zipf.writestr("style.css", css_content)
            
            # Note: Images are referenced by URL, not embedded
            # If you want to embed images, download them here
        
        # Generate download URL
        download_url = f"/api/v1/export/download/{file_key}"
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        return HTMLExportResponse(
            html_url=download_url,
            expires_at=expires_at,
        )
    
    async def _generate_html(self, project: Project, template_id: Optional[int]) -> str:
        """Generate HTML from project data"""
        
        # Use default Wadiz template
        template = self.jinja_env.get_template("wadiz_default.html")
        
        # Prepare data
        context = {
            "project": project,
            "product_name": project.product_name,
            "main_copy": project.ai_copy,
            "page_structure": project.page_structure or {},
            "images": project.images,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        html_content = template.render(**context)
        return html_content
    
    def _get_default_css(self) -> str:
        """Get default Wadiz-style CSS"""
        return """
/* 와디즈 스타일 CSS */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #333;
    background: #fff;
}

.container {
    max-width: 1080px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Intro Section */
.intro {
    padding: 60px 0;
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.intro h1 {
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 20px;
}

.intro .hooking {
    font-size: 1.5rem;
    margin-bottom: 30px;
}

/* Body Section */
.body {
    padding: 80px 0;
}

.section {
    margin-bottom: 80px;
}

.section h2 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 20px;
    text-align: center;
}

.section h3 {
    font-size: 1.8rem;
    color: #666;
    margin-bottom: 30px;
    text-align: center;
}

.section p {
    font-size: 1.2rem;
    line-height: 1.8;
    margin-bottom: 20px;
}

.section img {
    width: 100%;
    height: auto;
    margin: 20px 0;
    border-radius: 8px;
}

/* Outro Section */
.outro {
    padding: 60px 0;
    background: #f8f9fa;
}

.faq {
    margin: 40px 0;
}

.faq-item {
    background: white;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.faq-item h4 {
    font-size: 1.3rem;
    margin-bottom: 10px;
    color: #667eea;
}

.cta {
    text-align: center;
    padding: 40px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    margin-top: 40px;
}

.cta h2 {
    font-size: 2rem;
    margin-bottom: 20px;
}

.cta-button {
    display: inline-block;
    padding: 15px 50px;
    background: white;
    color: #667eea;
    font-size: 1.3rem;
    font-weight: bold;
    border-radius: 50px;
    text-decoration: none;
    transition: transform 0.3s;
}

.cta-button:hover {
    transform: scale(1.05);
}

/* Mobile Responsive */
@media (max-width: 768px) {
    .intro h1 {
        font-size: 2rem;
    }
    
    .section h2 {
        font-size: 1.8rem;
    }
    
    .section p {
        font-size: 1rem;
    }
}
"""
    
    async def get_export_file(self, file_key: str) -> str:
        """Get export file path"""
        file_path = f"/tmp/wadiz-export-{file_key}.zip"
        
        if not os.path.exists(file_path):
            raise FileNotFoundError("Export file not found or expired")
        
        return file_path
