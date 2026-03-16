from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import json
import os

class Settings(BaseSettings):
    # 프로젝트 정보
    PROJECT_NAME: str = "Wadiz Page Builder"
    VERSION: str = "4.2.0"
    API_V1_STR: str = "/api/v1"
    
    # 데이터베이스
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/wadiz_builder",
        description="PostgreSQL 연결 문자열"
    )
    
    # 보안
    SECRET_KEY: str = Field(
        default="wadiz-builder-default-secret-key-minimum-32-characters-long",
        min_length=32,
        description="JWT 토큰 시크릿 키 (SECRET_KEY와 JWT_SECRET_KEY 동일하게 사용)"
    )
    
    # JWT 설정 (SECRET_KEY와 동일한 값 사용)
    @property
    def JWT_SECRET_KEY(self) -> str:
        return self.SECRET_KEY
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일
    
    # AI 설정
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API 키")
    GEMINI_API_KEY: str = Field(default="", description="Gemini API 키")
    AI_MODE: str = Field(default="hybrid", description="AI 모드: gemini, openai, hybrid")
    
    # AWS S3 설정 (선택사항 - 이미지 업로드용)
    AWS_ACCESS_KEY_ID: str = Field(default="", description="AWS Access Key (선택)")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="AWS Secret Key (선택)")
    AWS_S3_BUCKET_NAME: str = Field(default="", description="S3 버킷명 (선택)")
    AWS_REGION: str = Field(default="ap-northeast-2", description="AWS 리전")
    
    # CORS
    CORS_ORIGINS_STR: str = Field(default='["*"]', description="CORS origins JSON 문자열")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """CORS_ORIGINS_STR을 파싱하여 리스트로 반환"""
        try:
            return json.loads(self.CORS_ORIGINS_STR)
        except:
            return ["*"]
    
    # 환경 설정
    DEBUG: bool = Field(default=False, description="디버그 모드")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # 추가 필드 허용

# 전역 설정 인스턴스
settings = Settings()
