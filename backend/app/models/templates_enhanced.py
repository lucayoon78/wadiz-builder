"""
Enhanced Template models for internal production tool
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TemplateCategory(Base):
    """템플릿 카테고리 (테크/가전, 패션, 식품, 생활용품 등)"""
    __tablename__ = "template_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "테크/가전"
    slug = Column(String(100), unique=True, index=True)  # e.g., "tech-electronics"
    description = Column(Text)
    icon = Column(String(100))  # emoji or icon name
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    templates = relationship("Template", back_populates="category")


class Template(Base):
    """와디즈 템플릿 (성공 사례 기반)"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("template_categories.id"))
    
    # Basic Info
    name = Column(String(255), nullable=False)  # e.g., "테크 제품 - 미니멀 스타일"
    description = Column(Text)
    thumbnail_url = Column(String(1000))  # 템플릿 미리보기 이미지
    
    # Template Content
    html_structure = Column(JSON, nullable=False)  # JSON 블록 구조
    """
    {
        "intro": {
            "layout": "centered",
            "blocks": [
                {"type": "heading", "placeholder": "{product_name}"},
                {"type": "text", "placeholder": "{usp}"},
                {"type": "image", "position": "hero"}
            ]
        },
        "body": [...],
        "outro": [...]
    }
    """
    
    css_style = Column(Text)  # 커스텀 CSS
    color_scheme = Column(JSON)  # {"primary": "#667eea", "secondary": "#764ba2"}
    
    # AI Prompts for this template
    ai_prompt_template = Column(Text)  # 이 템플릿에 맞는 AI 프롬프트
    
    # Metadata
    based_on_project_url = Column(String(1000))  # 참고한 와디즈 프로젝트 URL
    funding_amount = Column(Integer)  # 참고 프로젝트 펀딩액 (만원)
    success_rate = Column(Integer)  # 참고 프로젝트 달성률 (%)
    
    # Stats
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)  # 이 템플릿으로 성공한 프로젝트 수
    avg_completion_time = Column(Integer)  # 평균 제작 시간 (분)
    
    # Flags
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # 추천 템플릿
    difficulty = Column(String(20), default="easy")  # easy, medium, hard
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("TemplateCategory", back_populates="templates")
    projects = relationship("Project", back_populates="template")


class ProjectTemplateUsage(Base):
    """프로젝트-템플릿 사용 이력 (통계용)"""
    __tablename__ = "project_template_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    template_id = Column(Integer, ForeignKey("templates.id"))
    
    # Customization
    customizations = Column(JSON)  # 어떤 부분을 수정했는지
    
    # Time tracking
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_time_minutes = Column(Integer)  # 제작 소요 시간
    
    # Success
    was_successful = Column(Boolean, nullable=True)  # 클라이언트 승인 여부


# Update existing Project model
class ProjectEnhanced(Base):
    """Enhanced Project model with template support"""
    __tablename__ = "projects"
    
    # ... (existing fields from original models.py)
    
    # NEW: Template relation
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    template = relationship("Template", back_populates="projects")
    
    # NEW: Client info (for internal use)
    client_company = Column(String(255))  # 고객사명
    client_contact = Column(String(255))  # 담당자명
    client_email = Column(String(255))
    client_phone = Column(String(50))
    
    # NEW: Status tracking
    status = Column(String(50), default="draft")  
    # draft, in_progress, client_review, approved, published, rejected
    
    deadline = Column(DateTime, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # 담당 직원
