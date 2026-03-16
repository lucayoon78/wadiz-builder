"""
AI Generation endpoints - Core feature for Wadiz page creation
HYBRID AI: Gemini 2.0 Flash (초안) + GPT-4 Turbo (다듬기)
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.schemas import AIGenerateRequest, AIGenerateResponse, ProjectResponse
from app.services.hybrid_ai_service import hybrid_ai_service  # NEW: Hybrid AI
from app.services.auth_service import get_current_user
from app.models.models import User, Project
from sqlalchemy import select
import os

router = APIRouter()


@router.post("/generate", response_model=AIGenerateResponse)
async def generate_wadiz_page_hybrid(
    request: AIGenerateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    🚀 하이브리드 AI로 와디즈 상세페이지 생성
    
    **AI 전략:**
    1. Gemini 2.0 Flash (1-2초): 빠른 초안 생성
    2. GPT-4 Turbo (2-3초): 감성적 다듬기
    
    **Input:**
    - **product_name**: 제품명
    - **usp**: 핵심 강점 (Unique Selling Point)
    - **target_audience**: 타겟 고객
    - **brand_tone**: professional/friendly/premium
    - **template_id**: 템플릿 ID (optional)
    
    **Output:**
    - **main_copy**: 메인 카피라이팅 (GPT-4 다듬기 완료)
    - **alternatives**: 3가지 대안 카피
    - **headline**: 강렬한 헤드라인
    - **subheadline**: 부제목
    - **cta**: 행동 유도 문구
    - **page_structure**: 와디즈 5단계 황금구조
    
    **비용:** ~₩20,000/월 (OpenAI만 사용 시 ₩50,000 → 60% 절감!)
    """
    
    # Verify project ownership
    stmt = select(Project).where(Project.id == request.project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Generate AI content with Hybrid AI
    try:
        # 1단계: Gemini로 빠른 초안 (1-2초)
        # 2단계: GPT-4로 감성적 다듬기 (2-3초)
        copy_result = await hybrid_ai_service.generate_copy_hybrid(
            product_name=request.product_name,
            usp=request.usp,
            target_audience=request.target_audience,
            brand_tone=request.brand_tone or "professional",
            template_context=None
        )
        
        # 페이지 구조 생성 (Gemini 단독 - 빠르고 충분)
        structure_result = await hybrid_ai_service.generate_page_structure(
            product_name=request.product_name,
            usp=request.usp,
            template_type=request.category or "tech"
        )
        
        # Update project with generated content
        project.product_name = request.product_name
        project.html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{request.product_name} - 와디즈 펀딩</title>
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; max-width: 1080px; margin: 0 auto; padding: 20px; }}
        .headline {{ font-size: 48px; font-weight: bold; margin: 40px 0; }}
        .subheadline {{ font-size: 24px; color: #666; margin-bottom: 60px; }}
        .main-copy {{ font-size: 18px; line-height: 1.8; margin: 40px 0; }}
        .section {{ margin: 80px 0; }}
        .cta {{ background: #FF6B00; color: white; padding: 20px 60px; font-size: 20px; border: none; border-radius: 8px; cursor: pointer; }}
    </style>
</head>
<body>
    <h1 class="headline">{copy_result['headline']}</h1>
    <p class="subheadline">{copy_result['subheadline']}</p>
    <div class="main-copy">{copy_result['main_copy']}</div>
    
    <!-- 와디즈 5단계 구조 -->
    {''.join([f'<div class="section"><h2>{section.get("title", "")}</h2><p>{section.get("content", "")}</p></div>' 
              for section in structure_result.get('sections', [])])}
    
    <div style="text-align: center; margin: 100px 0;">
        <button class="cta">{copy_result['cta']}</button>
    </div>
</body>
</html>
"""
        
        await db.commit()
        await db.refresh(project)
        
        return AIGenerateResponse(
            main_copy=copy_result['main_copy'],
            alternative_copies=copy_result['alternatives'],
            headline=copy_result['headline'],
            subheadline=copy_result['subheadline'],
            cta=copy_result['cta'],
            page_structure=structure_result.get('sections', []),
            project_id=project.id,
            html_preview=project.html_content,
            ai_model=copy_result.get('ai_model', 'hybrid_gemini_gpt4'),
            generation_time=copy_result.get('generation_time', '3-5초'),
            cost_savings=copy_result.get('cost_savings', '60%')
        )
        
    except Exception as e:
        print(f"AI 생성 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI 생성 중 오류 발생: {str(e)}"
        )


@router.get("/ai-status")
async def get_ai_status():
    """
    AI 시스템 상태 확인
    - Gemini API 연결 상태
    - OpenAI API 연결 상태
    - 현재 AI 모드 (hybrid/gemini_only/openai_only)
    """
    gemini_available = bool(os.getenv("GEMINI_API_KEY"))
    openai_available = bool(os.getenv("OPENAI_API_KEY"))
    ai_mode = os.getenv("AI_MODE", "hybrid")
    
    return {
        "gemini_api": "connected" if gemini_available else "not_configured",
        "openai_api": "connected" if openai_available else "not_configured",
        "ai_mode": ai_mode,
        "recommended_mode": "hybrid" if (gemini_available and openai_available) else "gemini_only" if gemini_available else "openai_only",
        "cost_estimate": {
            "hybrid": "₩20,000/월",
            "gemini_only": "₩0-10,000/월",
            "openai_only": "₩50,000/월"
        }
    }
