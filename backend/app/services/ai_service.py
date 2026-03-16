"""
AI Service - Integration with OpenAI GPT-4 and Genspark for Wadiz page generation
"""
import json
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.models import Project
from app.schemas.schemas import AIGenerateResponse


class AIService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def get_project(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        result = await self.db.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()
    
    async def generate_wadiz_content(
        self,
        product_name: str,
        usp: str,
        target_audience: str,
        category: Optional[str] = None,
        additional_context: Optional[str] = None,
    ) -> AIGenerateResponse:
        """
        Generate Wadiz page content using OpenAI GPT-4
        
        와디즈 황금 구조:
        1. 인트로 (Intro): 3초 안에 후킹 (공감/재미/호기심)
        2. 본론 (Body): 대제목 + 소제목 + 시각자료 + 설명
        3. 아웃트로 (Outro): FAQ + CTA + 펀딩 정보
        """
        
        # System prompt for Wadiz expert
        system_prompt = """당신은 와디즈 크라우드펀딩 전문가입니다. 10년 이상의 경험으로 수백 개의 억대 펀딩 프로젝트를 성공시켰습니다.

**와디즈 상세페이지 작성 10계명:**
1. 머리말에 후킹포인트 필수 (공감/재미/호기심)
2. 핵심 강점 1개만 강조, 나머지는 부수적 나열
3. 글자는 최대한 크게, 최소한으로
4. 이미지 → 문구 → 이미지 → 문구 순서
5. 스토리텔링 + 재미 요소
6. 전문용어는 쉽게 풀어서
7. 메이커 스토리는 극적으로
8. 특허/인증서로 신뢰도 확보
9. 광고성 멘트 많이 사용 (일반 상세페이지와 다름)
10. 와디즈 특유의 긴 스토리형 구성

**황금 구조:**
- 인트로: 3초 후킹 문구 (20자 이내, 강렬하게)
- 본론: 대제목 (핵심 특징) + 소제목 (근거) + 설명 (3-5개 섹션)
- 아웃트로: FAQ 5개 + CTA + 얼리버드 혜택

JSON 형식으로 응답하세요."""

        user_prompt = f"""
제품명: {product_name}
핵심 강점 (USP): {usp}
타겟 고객: {target_audience}
카테고리: {category or "일반"}
추가 정보: {additional_context or "없음"}

위 정보를 바탕으로:
1. 메인 카피 1개 (와디즈 황금 구조 전체)
2. 대안 카피 3개 (다른 톤앤매너: 전문적/친근함/감성적)
3. 페이지 구조 (섹션별 가이드)

를 생성하세요.
"""

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.8,
                max_tokens=3000,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse response
            main_copy = result.get("main_copy", "")
            alternatives = result.get("alternatives", [])
            page_structure = result.get("page_structure", {})
            
            # Ensure we have 3 alternatives
            while len(alternatives) < 3:
                alternatives.append(f"대안 카피 {len(alternatives) + 1}: {main_copy[:200]}...")
            
            # Default page structure if not provided
            if not page_structure:
                page_structure = {
                    "intro": {
                        "hooking": "3초 안에 사로잡는 후킹 문구",
                        "image_guide": "제품 사용 장면 또는 감성 이미지",
                    },
                    "body": [
                        {
                            "title": "핵심 특징 1",
                            "subtitle": "이 특징을 가능하게 하는 기술/소재",
                            "description": "자세한 설명",
                            "image_guide": "특징을 보여주는 비교 이미지 또는 도해",
                        },
                    ],
                    "outro": {
                        "faq": ["자주 묻는 질문 1?", "자주 묻는 질문 2?"],
                        "cta": "지금 바로 펀딩하고 얼리버드 혜택 받으세요!",
                    },
                }
            
            return AIGenerateResponse(
                main_copy=main_copy,
                alternatives=alternatives[:3],
                page_structure=page_structure,
            )
            
        except Exception as e:
            # Fallback response
            print(f"OpenAI API Error: {e}")
            return self._generate_fallback_content(product_name, usp, target_audience)
    
    def _generate_fallback_content(
        self, product_name: str, usp: str, target_audience: str
    ) -> AIGenerateResponse:
        """Fallback content when AI fails"""
        main_copy = f"""
# {product_name}을(를) 소개합니다

## {usp}

{target_audience}을(를) 위한 완벽한 솔루션입니다.

[본문 내용은 AI 생성 후 자동으로 채워집니다]
"""
        return AIGenerateResponse(
            main_copy=main_copy,
            alternatives=[
                f"{product_name} - 대안 카피 1",
                f"{product_name} - 대안 카피 2",
                f"{product_name} - 대안 카피 3",
            ],
            page_structure={
                "intro": {"hooking": f"{usp}"},
                "body": [],
                "outro": {"faq": [], "cta": "지금 펀딩하세요!"},
            },
        )
    
    async def update_project_with_ai_content(
        self, project_id: int, ai_content: AIGenerateResponse
    ):
        """Update project with AI-generated content"""
        project = await self.get_project(project_id)
        if project:
            project.ai_copy = ai_content.main_copy
            project.ai_alternatives = ai_content.alternatives
            project.page_structure = ai_content.page_structure
            await self.db.commit()
    
    async def apply_alternative_copy(self, project_id: int, alternative_index: int) -> Project:
        """Apply alternative copy as main copy"""
        project = await self.get_project(project_id)
        if project and project.ai_alternatives:
            # Swap main and alternative
            old_main = project.ai_copy
            project.ai_copy = project.ai_alternatives[alternative_index]
            project.ai_alternatives[alternative_index] = old_main
            await self.db.commit()
            await self.db.refresh(project)
        return project
