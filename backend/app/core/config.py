from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import json


class Settings(BaseSettings):
    # 앱 기본 정보
    APP_NAME: str = "Wadiz Page Builder"
    PROJECT_NAME: str = "Wadiz Page Builder"
    VERSION: str = "4.2.0"
    
    # API 설정
    API_V1_STR: str = "/api/v1"
    API_V1_PREFIX: str = "/api/v1"
    
    # 데이터베이스
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/wadiz_builder"
    )
    
    # 보안
    SECRET_KEY: str = Field(
        default="wadiz-builder-default-secret-key-minimum-32-characters-long",
        min_length=32
    )
    JWT_SECRET_KEY: str = Field(
        default="wadiz-builder-jwt-secret-key-minimum-32-characters-required",
        min_length=32
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # AI 설정
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_MODE: str = "hybrid"
    
    # CORS
    CORS_ORIGINS_STR: str = Field(default='["*"]')
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        try:
            return json.loads(self.CORS_ORIGINS_STR)
        except Exception:
            return ["*"]
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str = ""
    
    # 기타
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"


settings = Settings()
