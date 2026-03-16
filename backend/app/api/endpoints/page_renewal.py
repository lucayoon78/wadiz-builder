"""
Page Renewal API Endpoints
기존 페이지 업로드 → 분석 → 리뉴얼
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.page_renewal_service import page_renewal_service
from app.services.auth_service import get_current_user
from app.models.models import User
from pydantic import BaseModel, HttpUrl
from typing import Optional
import tempfile
import os

router = APIRouter()


class PageRenewalURLRequest(BaseModel):
    url: HttpUrl
    project_name: Optional[str] = None


class PageRenewalResponse(BaseModel):
    analysis: dict
    improvements: dict
    renewed_content: dict
    estimated_time: str = "10-15초"
    cost: str = "약 ₩200"


@router.post("/analyze-url", response_model=dict)
async def analyze_page_from_url(
    request: PageRenewalURLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    🔍 URL로 기존 페이지 분석
    
    **Input:**
    - url: 분석할 페이지 URL (와디즈, 쿠팡, 스마트스토어 등)
    
    **Output:**
    - current_analysis: 현재 페이지 분석 결과
      - strengths: 강점 3가지
      - weaknesses: 약점 3가지
      - structure_issues: 구조적 문제
      - ratings: 카피/시각 평가 (1-10점)
    
    **AI 처리:**
    1. URL에서 HTML 가져오기
    2. Gemini로 빠른 분석
    3. 분석 결과 반환
    
    **예상 시간:** 5-10초
    """
    try:
        # URL에서 페이지 가져오기
        page_data = await page_renewal_service.fetch_page_from_url(str(request.url))
        
        # AI 분석
        analysis_result = await page_renewal_service.analyze_page_with_ai(page_data)
        
        return {
            "success": True,
            "page_info": {
                "title": page_data.get("title", ""),
                "images_count": page_data.get("images_count", 0),
                "content_length": len(page_data.get("text_content", "")),
                "source_url": str(request.url)
            },
            "analysis": analysis_result["current_analysis"],
            "message": "페이지 분석 완료. 리뉴얼 생성을 진행하세요."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"페이지 분석 실패: {str(e)}"
        )


@router.post("/analyze-html", response_model=dict)
async def analyze_page_from_html(
    html_file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    📄 HTML 파일 업로드로 기존 페이지 분석
    
    **Input:**
    - html_file: HTML 파일 (드래그앤드롭)
    - project_name: 프로젝트 이름 (선택)
    
    **Output:**
    - 분석 결과 (analyze-url과 동일)
    
    **예상 시간:** 5-10초
    """
    try:
        # HTML 파일 읽기
        html_content = await html_file.read()
        html_text = html_content.decode('utf-8')
        
        # HTML 분석
        page_data = await page_renewal_service.analyze_html_content(html_text)
        
        # AI 분석
        analysis_result = await page_renewal_service.analyze_page_with_ai(page_data)
        
        return {
            "success": True,
            "page_info": {
                "title": page_data.get("title", ""),
                "images_count": page_data.get("images_count", 0),
                "content_length": len(page_data.get("text_content", "")),
                "source_file": html_file.filename
            },
            "analysis": analysis_result["current_analysis"],
            "message": "HTML 파일 분석 완료. 리뉴얼 생성을 진행하세요."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"HTML 파일 분석 실패: {str(e)}"
        )


@router.post("/renew-from-url", response_model=PageRenewalResponse)
async def renew_page_from_url(
    request: PageRenewalURLRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    🚀 URL 기반 페이지 리뉴얼 (분석 + 개선 + 생성 한번에)
    
    **전체 프로세스:**
    1. URL에서 페이지 가져오기 (2초)
    2. Gemini로 현재 분석 (3초)
    3. GPT-4로 개선안 도출 (3초)
    4. GPT-4로 리뉴얼 카피 생성 (5초)
    
    **총 시간:** 10-15초
    **비용:** 약 ₩200 (Gemini 무료 + GPT-4 사용)
    
    **Output:**
    - analysis: 현재 페이지 분석
    - improvements: AI 개선 제안
    - renewed_content: 리뉴얼된 콘텐츠
      - renewed_headline: 새 헤드라인
      - renewed_main_copy: 새 메인 카피
      - before_after_comparison: 비교 리포트
    """
    try:
        # 1. URL에서 페이지 가져오기
        page_data = await page_renewal_service.fetch_page_from_url(str(request.url))
        
        # 2. AI 분석
        analysis_result = await page_renewal_service.analyze_page_with_ai(page_data)
        
        # 3. 리뉴얼 페이지 생성
        renewed_content = await page_renewal_service.generate_renewed_page(
            page_data=page_data,
            analysis=analysis_result["current_analysis"],
            improvements=analysis_result["improvement_suggestions"]
        )
        
        return PageRenewalResponse(
            analysis=analysis_result["current_analysis"],
            improvements=analysis_result["improvement_suggestions"],
            renewed_content=renewed_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"페이지 리뉴얼 실패: {str(e)}"
        )


@router.post("/renew-from-html", response_model=PageRenewalResponse)
async def renew_page_from_html(
    html_file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    📄 HTML 파일 기반 페이지 리뉴얼
    
    **전체 프로세스:**
    1. HTML 파일 읽기
    2. Gemini로 현재 분석
    3. GPT-4로 개선안 도출
    4. GPT-4로 리뉴얼 카피 생성
    
    **총 시간:** 10-15초
    **비용:** 약 ₩200
    """
    try:
        # HTML 파일 읽기
        html_content = await html_file.read()
        html_text = html_content.decode('utf-8')
        
        # HTML 분석
        page_data = await page_renewal_service.analyze_html_content(html_text)
        
        # AI 분석
        analysis_result = await page_renewal_service.analyze_page_with_ai(page_data)
        
        # 리뉴얼 페이지 생성
        renewed_content = await page_renewal_service.generate_renewed_page(
            page_data=page_data,
            analysis=analysis_result["current_analysis"],
            improvements=analysis_result["improvement_suggestions"]
        )
        
        return PageRenewalResponse(
            analysis=analysis_result["current_analysis"],
            improvements=analysis_result["improvement_suggestions"],
            renewed_content=renewed_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"HTML 파일 리뉴얼 실패: {str(e)}"
        )


@router.get("/renewal-stats")
async def get_renewal_stats(
    current_user: User = Depends(get_current_user),
):
    """
    📊 리뉴얼 서비스 통계
    
    **Output:**
    - 평균 개선율
    - 처리 시간
    - 비용 정보
    - 사용 팁
    """
    return {
        "average_improvement": "30-50% 펀딩 증가 예상",
        "processing_time": {
            "url_analysis": "5-10초",
            "full_renewal": "10-15초"
        },
        "cost": {
            "analysis_only": "₩50 (Gemini 무료)",
            "full_renewal": "₩200 (Gemini + GPT-4)"
        },
        "tips": [
            "URL 입력이 가장 빠름 (2초)",
            "HTML 파일은 정확도 높음",
            "분석 후 수동 조정 가능",
            "리뉴얼 전 백업 권장"
        ],
        "supported_platforms": [
            "와디즈",
            "쿠팡",
            "네이버 스마트스토어",
            "G마켓",
            "11번가",
            "기타 HTML 페이지"
        ]
    }
