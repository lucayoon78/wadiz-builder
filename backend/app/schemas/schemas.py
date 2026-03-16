"""
Pydantic schemas for API requests and responses
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl


# ===== User Schemas =====
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Auth Schemas =====
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None


# ===== Image Schemas =====
class ImageBase(BaseModel):
    filename: str
    file_url: str
    position: int = 0
    section: str = "body"


class ImageCreate(ImageBase):
    original_filename: str
    file_size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None


class ImageResponse(ImageBase):
    id: int
    project_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Project Schemas =====
class ProjectBase(BaseModel):
    title: str
    category: Optional[str] = None
    product_name: Optional[str] = None
    usp: Optional[str] = None
    target_audience: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    product_name: Optional[str] = None
    usp: Optional[str] = None
    target_audience: Optional[str] = None
    ai_copy: Optional[str] = None
    ai_alternatives: Optional[List[str]] = None
    page_structure: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    slug: str
    ai_copy: Optional[str] = None
    ai_alternatives: Optional[List[str]] = None
    page_structure: Optional[Dict[str, Any]] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    
    class Config:
        from_attributes = True


# ===== AI Generation Schemas =====
class AIGenerateRequest(BaseModel):
    project_id: int
    product_name: str
    usp: str
    target_audience: str
    category: Optional[str] = None
    additional_context: Optional[str] = None


class AIGenerateResponse(BaseModel):
    main_copy: str
    alternatives: List[str]
    page_structure: Dict[str, Any]


# ===== Template Schemas =====
class TemplateBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class TemplateCreate(TemplateBase):
    structure: Dict[str, Any]


class TemplateResponse(TemplateBase):
    id: int
    structure: Dict[str, Any]
    usage_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== HTML Export Schemas =====
class HTMLExportRequest(BaseModel):
    project_id: int
    template_id: Optional[int] = None


class HTMLExportResponse(BaseModel):
    html_url: str  # URL to download HTML ZIP
    expires_at: datetime
