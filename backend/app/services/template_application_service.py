"""
Template application service - Apply template to project with AI customization
"""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.templates_enhanced import Template, TemplateCategory
from app.models.models import Project, Image


class TemplateApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def apply_template_to_project(
        self,
        project_id: int,
        template_id: int,
        customization_params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        템플릿을 프로젝트에 적용하고 AI로 자동 커스터마이징
        
        Args:
            project_id: 프로젝트 ID
            template_id: 템플릿 ID
            customization_params: {
                "product_name": "스마트 텀블러",
                "usp": "24시간 온도 유지",
                "target_audience": "바쁜 직장인",
                "brand_tone": "친근함" | "전문적" | "감성적",
                "color_override": {"primary": "#ff0000"},  # optional
            }
        
        Returns:
            {
                "html_content": "...",
                "page_structure": {...},
                "ai_copy": "...",
                "template_info": {...}
            }
        """
        
        # Get template
        template = await self._get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get project with images
        project = await self._get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Generate AI content using template's prompt
        ai_content = await self._generate_content_with_template(
            template, customization_params
        )
        
        # Apply customizations
        customized_structure = self._customize_template_structure(
            template.html_structure,
            customization_params,
            ai_content,
        )
        
        # Update project
        project.template_id = template_id
        project.page_structure = customized_structure
        project.ai_copy = ai_content["main_copy"]
        project.ai_alternatives = ai_content.get("alternatives", [])
        
        # Apply color scheme
        color_scheme = customization_params.get("color_override") or template.color_scheme
        
        await self.db.commit()
        await self.db.refresh(project)
        
        # Increment usage count
        template.usage_count += 1
        await self.db.commit()
        
        return {
            "html_content": self._generate_html_preview(
                customized_structure, project.images, color_scheme
            ),
            "page_structure": customized_structure,
            "ai_copy": ai_content["main_copy"],
            "alternatives": ai_content.get("alternatives", []),
            "template_info": {
                "id": template.id,
                "name": template.name,
                "category": template.category.name if template.category else None,
            },
            "color_scheme": color_scheme,
        }
    
    async def _get_template(self, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        result = await self.db.execute(
            select(Template).where(Template.id == template_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_project(self, project_id: int) -> Optional[Project]:
        """Get project with images"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def _generate_content_with_template(
        self, template: Template, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI content using template's prompt"""
        
        # Fill template prompt
        prompt = template.ai_prompt_template.format(
            product_name=params.get("product_name", ""),
            usp=params.get("usp", ""),
            target_audience=params.get("target_audience", ""),
        )
        
        # Add brand tone
        brand_tone = params.get("brand_tone", "친근함")
        tone_guide = {
            "친근함": "친근하고 편안한 톤으로, 반말 사용 가능",
            "전문적": "전문적이고 신뢰감 있는 톤으로, 데이터와 수치 강조",
            "감성적": "감성적이고 스토리텔링 중심으로, 공감 유발",
        }
        
        system_prompt = f"""당신은 와디즈 크라우드펀딩 전문 카피라이터입니다.
템플릿: {template.name}
브랜드 톤: {tone_guide.get(brand_tone, tone_guide["친근함"])}

아래 프롬프트에 맞춰 작성하되, JSON 형식으로 응답하세요."""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=2500,
                response_format={"type": "json_object"},
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "main_copy": result.get("main_copy", ""),
                "alternatives": result.get("alternatives", []),
                "section_content": result.get("sections", {}),
            }
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return {
                "main_copy": f"# {params.get('product_name')}\n\n{params.get('usp')}",
                "alternatives": [],
                "section_content": {},
            }
    
    def _customize_template_structure(
        self,
        template_structure: Dict[str, Any],
        params: Dict[str, Any],
        ai_content: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Customize template structure with actual content"""
        
        import copy
        customized = copy.deepcopy(template_structure)
        
        # Replace placeholders in intro
        if "intro" in customized:
            for block in customized["intro"].get("blocks", []):
                if block.get("placeholder"):
                    block["placeholder"] = block["placeholder"].format(**params)
        
        # Replace placeholders in body
        if "body" in customized:
            section_content = ai_content.get("section_content", {})
            for idx, section in enumerate(customized["body"]):
                for block in section.get("blocks", []):
                    if block.get("placeholder"):
                        # Try to get AI-generated content
                        section_key = f"section_{idx}"
                        if section_key in section_content:
                            block["content"] = section_content[section_key]
                        else:
                            block["placeholder"] = block["placeholder"].format(**params)
        
        return customized
    
    def _generate_html_preview(
        self,
        structure: Dict[str, Any],
        images: list,
        color_scheme: Dict[str, str],
    ) -> str:
        """Generate HTML preview from structure"""
        
        html_parts = ["<!DOCTYPE html><html><head><meta charset='utf-8'>"]
        
        # Add inline CSS
        css = f"""
        <style>
            :root {{
                --primary: {color_scheme.get('primary', '#667eea')};
                --secondary: {color_scheme.get('secondary', '#764ba2')};
                --accent: {color_scheme.get('accent', '#5b21b6')};
                --text: {color_scheme.get('text', '#1e293b')};
            }}
            body {{ 
                font-family: 'Pretendard', sans-serif; 
                color: var(--text);
                margin: 0;
                padding: 0;
            }}
            .intro {{ 
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
                padding: 80px 20px;
                text-align: center;
            }}
            .intro h1 {{ font-size: 3rem; margin-bottom: 20px; }}
            .intro p {{ font-size: 1.5rem; }}
            .body {{ max-width: 1080px; margin: 0 auto; padding: 40px 20px; }}
            .section {{ margin: 60px 0; }}
            .section h2 {{ font-size: 2.5rem; margin-bottom: 20px; }}
            .section img {{ width: 100%; height: auto; border-radius: 8px; }}
            .outro {{ background: #f8f9fa; padding: 60px 20px; }}
            .cta {{ 
                background: var(--primary);
                color: white;
                padding: 20px 40px;
                border-radius: 50px;
                font-size: 1.3rem;
                display: inline-block;
                margin-top: 20px;
            }}
        </style>
        """
        html_parts.append(css)
        html_parts.append("</head><body>")
        
        # Intro
        if "intro" in structure:
            html_parts.append("<section class='intro'>")
            for block in structure["intro"].get("blocks", []):
                if block["type"] == "heading":
                    html_parts.append(f"<h1>{block.get('placeholder', 'Product Name')}</h1>")
                elif block["type"] in ["tagline", "text"]:
                    html_parts.append(f"<p>{block.get('placeholder', 'Description')}</p>")
            html_parts.append("</section>")
        
        # Body
        if "body" in structure:
            html_parts.append("<main class='body'>")
            for section in structure["body"]:
                html_parts.append("<div class='section'>")
                for block in section.get("blocks", []):
                    if block["type"] == "title":
                        html_parts.append(f"<h2>{block.get('placeholder', 'Section')}</h2>")
                    elif block["type"] == "description":
                        html_parts.append(f"<p>{block.get('content', block.get('placeholder', ''))}</p>")
                    elif block["type"] == "image":
                        if images:
                            html_parts.append(f"<img src='{images[0].file_url}' alt='Product'>")
                html_parts.append("</div>")
            html_parts.append("</main>")
        
        # Outro
        if "outro" in structure:
            html_parts.append("<section class='outro'><div style='max-width:1080px;margin:0 auto;text-align:center;'>")
            for block in structure["outro"].get("blocks", []):
                if block["type"] == "cta":
                    html_parts.append(f"<a href='#' class='cta'>{block.get('text', '펀딩하기')}</a>")
            html_parts.append("</div></section>")
        
        html_parts.append("</body></html>")
        
        return "".join(html_parts)
    
    async def get_recommended_templates(
        self, category_slug: Optional[str] = None, limit: int = 10
    ):
        """Get recommended templates for a category"""
        
        query = select(Template).where(Template.is_active == True)
        
        if category_slug:
            category = await self.db.execute(
                select(TemplateCategory).where(TemplateCategory.slug == category_slug)
            )
            cat = category.scalar_one_or_none()
            if cat:
                query = query.where(Template.category_id == cat.id)
        
        # Order by: featured first, then by success rate
        query = query.order_by(
            Template.is_featured.desc(),
            Template.success_rate.desc(),
        ).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
