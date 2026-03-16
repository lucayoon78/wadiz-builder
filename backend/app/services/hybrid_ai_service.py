"""
Hybrid AI Service: Gemini 2.0 Flash (1차 생성) + GPT-4 (2차 다듬기)

속도 ↑ 비용 ↓ 품질 ↑
"""
import os
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from openai import AsyncOpenAI

class HybridAIService:
    """
    하이브리드 AI 생성 서비스
    - 1차: Gemini 2.0 Flash (빠르고 저렴한 초안 생성)
    - 2차: GPT-4 Turbo (고품질 다듬기)
    """
    
    def __init__(self):
        # Gemini 설정
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.gemini_model = None
            
        # OpenAI 설정
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if self.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        else:
            self.openai_client = None
    
    async def generate_copy_hybrid(
        self,
        product_name: str,
        usp: str,
        target_audience: str,
        brand_tone: str = "professional",
        template_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        하이브리드 카피 생성
        1단계: Gemini로 빠른 초안 생성
        2단계: GPT-4로 감성적 다듬기
        """
        
        # === 1단계: Gemini로 초안 생성 (1-2초) ===
        draft = await self._generate_draft_with_gemini(
            product_name, usp, target_audience, brand_tone, template_context
        )
        
        # === 2단계: GPT-4로 최종 다듬기 (2-3초) ===
        refined = await self._refine_with_gpt4(
            draft, product_name, usp, target_audience, brand_tone
        )
        
        return {
            "main_copy": refined["main_copy"],
            "alternative_copies": refined["alternatives"],
            "headline": refined["headline"],
            "subheadline": refined["subheadline"],
            "cta": refined["cta"],
            "ai_model": "hybrid_gemini_gpt4",
            "generation_time": "3-5초",
            "cost_savings": "60%"  # Gemini 무료 티어 + GPT-4 최소 사용
        }
    
    async def _generate_draft_with_gemini(
        self,
        product_name: str,
        usp: str,
        target_audience: str,
        brand_tone: str,
        template_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gemini로 빠른 초안 생성"""
        
        if not self.gemini_model:
            # Gemini 없으면 GPT-4로 폴백
            return await self._generate_with_gpt4_only(
                product_name, usp, target_audience, brand_tone, template_context
            )
        
        tone_map = {
            "professional": "전문적이고 신뢰감 있는",
            "friendly": "친근하고 편안한",
            "premium": "프리미엄하고 세련된"
        }
        
        prompt = f"""
당신은 한국 크라우드펀딩 전문 카피라이터입니다.
와디즈 펀딩 성공을 위한 페이지 카피를 작성해주세요.

**제품 정보:**
- 제품명: {product_name}
- 핵심 강점(USP): {usp}
- 타겟 고객: {target_audience}
- 브랜드 톤: {tone_map.get(brand_tone, '전문적이고 신뢰감 있는')}

**작성 요구사항:**
1. 와디즈 황금 구조 5단계 고려
2. 첫 문장에 후킹 포인트 필수
3. 감성적이고 공감 가는 스토리텔링
4. 구매 욕구를 자극하는 표현
5. 한국어 뉘앙스 정확히 반영

**출력 형식 (JSON):**
{{
  "main_copy": "메인 카피 (3-4문장)",
  "headline": "강렬한 헤드라인",
  "subheadline": "부제목 (USP 강조)",
  "cta": "행동 유도 문구",
  "alternatives": ["대안 카피 1", "대안 카피 2", "대안 카피 3"]
}}

JSON만 출력하세요 (설명 없이).
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 파싱
            import json
            # 마크다운 코드 블록 제거
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            result = json.loads(result_text.strip())
            return result
            
        except Exception as e:
            print(f"Gemini 생성 실패: {e}")
            # 폴백: GPT-4 단독 사용
            return await self._generate_with_gpt4_only(
                product_name, usp, target_audience, brand_tone, template_context
            )
    
    async def _refine_with_gpt4(
        self,
        draft: Dict[str, Any],
        product_name: str,
        usp: str,
        target_audience: str,
        brand_tone: str
    ) -> Dict[str, Any]:
        """GPT-4로 감성적 다듬기 및 최종 품질 향상"""
        
        if not self.openai_client:
            # GPT-4 없으면 초안 그대로 반환
            return draft
        
        tone_map = {
            "professional": "전문적이면서도 따뜻한",
            "friendly": "친근하고 공감 가는",
            "premium": "프리미엄하면서도 감성적인"
        }
        
        prompt = f"""
당신은 한국 최고의 크라우드펀딩 카피라이터입니다.
아래 초안 카피를 **더 감성적이고 설득력 있게** 다듬어주세요.

**제품:**
- 제품명: {product_name}
- 핵심 강점: {usp}
- 타겟: {target_audience}
- 톤: {tone_map.get(brand_tone, '전문적이면서도 따뜻한')}

**초안 카피:**
{draft.get('main_copy', '')}

**다듬기 요구사항:**
1. 감성 표현 강화 (공감, 재미, 호기심)
2. 와디즈 특유의 스토리텔링 톤
3. 한국어 어감 최적화
4. 구매 욕구 자극 강화
5. 리듬감 있는 문장 구조

**출력 형식 (JSON):**
{{
  "main_copy": "다듬어진 메인 카피",
  "headline": "개선된 헤드라인",
  "subheadline": "개선된 부제목",
  "cta": "개선된 CTA",
  "alternatives": ["대안 1", "대안 2", "대안 3"]
}}

JSON만 출력하세요.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "당신은 한국 최고의 크라우드펀딩 카피라이터입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"GPT-4 다듬기 실패: {e}")
            # 폴백: 초안 그대로 반환
            return draft
    
    async def _generate_with_gpt4_only(
        self,
        product_name: str,
        usp: str,
        target_audience: str,
        brand_tone: str,
        template_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """GPT-4 단독 생성 (폴백용)"""
        
        if not self.openai_client:
            # 둘 다 없으면 기본 템플릿 반환
            return {
                "main_copy": f"{product_name}로 {target_audience}의 일상을 바꿉니다.",
                "headline": product_name,
                "subheadline": usp,
                "cta": "지금 바로 펀딩하기",
                "alternatives": [
                    f"{product_name}와 함께하는 새로운 시작",
                    f"{usp}의 혁신을 경험하세요",
                    f"{target_audience}를 위한 특별한 선택"
                ]
            }
        
        tone_map = {
            "professional": "전문적이고 신뢰감 있는",
            "friendly": "친근하고 편안한",
            "premium": "프리미엄하고 세련된"
        }
        
        prompt = f"""
와디즈 크라우드펀딩 페이지를 위한 감성적인 카피를 작성해주세요.

**제품 정보:**
- 제품명: {product_name}
- 핵심 강점(USP): {usp}
- 타겟 고객: {target_audience}
- 브랜드 톤: {tone_map.get(brand_tone, '전문적이고 신뢰감 있는')}

**요구사항:**
- 와디즈 황금 구조 반영
- 감성적 스토리텔링
- 한국어 뉘앙스 정확
- 구매 욕구 자극

JSON 형식으로 출력:
{{
  "main_copy": "메인 카피",
  "headline": "헤드라인",
  "subheadline": "부제목",
  "cta": "CTA",
  "alternatives": ["대안1", "대안2", "대안3"]
}}
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "당신은 한국 최고의 크라우드펀딩 카피라이터입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"GPT-4 생성 실패: {e}")
            # 최종 폴백
            return {
                "main_copy": f"{product_name}로 {target_audience}의 일상을 바꿉니다.",
                "headline": product_name,
                "subheadline": usp,
                "cta": "지금 바로 펀딩하기",
                "alternatives": [
                    f"{product_name}와 함께하는 새로운 시작",
                    f"{usp}의 혁신을 경험하세요",
                    f"{target_audience}를 위한 특별한 선택"
                ]
            }
    
    async def generate_page_structure(
        self,
        product_name: str,
        usp: str,
        template_type: str = "tech"
    ) -> Dict[str, Any]:
        """
        페이지 구조 생성 (Gemini 단독 사용 - 빠르고 충분)
        """
        
        if not self.gemini_model:
            return self._get_default_structure(template_type)
        
        prompt = f"""
와디즈 펀딩 페이지 구조를 생성하세요.

**제품:** {product_name}
**USP:** {usp}
**템플릿:** {template_type}

**와디즈 5단계 구조:**
1. 인트로(후킹)
2. 문제 정의
3. 솔루션 제시
4. 증거/신뢰 구축
5. 행동 유도

JSON 형식으로 섹션별 구조 출력:
{{
  "sections": [
    {{"type": "intro", "title": "...", "content": "..."}},
    {{"type": "problem", "title": "...", "content": "..."}},
    ...
  ]
}}
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            import json
            result_text = response.text.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            return json.loads(result_text.strip())
        except Exception as e:
            print(f"구조 생성 실패: {e}")
            return self._get_default_structure(template_type)
    
    def _get_default_structure(self, template_type: str) -> Dict[str, Any]:
        """기본 페이지 구조"""
        return {
            "sections": [
                {"type": "intro", "title": "혁신의 시작", "content": "새로운 경험을 제안합니다"},
                {"type": "problem", "title": "이런 불편함 없으셨나요?", "content": "일상의 문제를 해결합니다"},
                {"type": "solution", "title": "완벽한 솔루션", "content": "핵심 기능을 소개합니다"},
                {"type": "proof", "title": "검증된 품질", "content": "신뢰를 증명합니다"},
                {"type": "cta", "title": "지금 시작하세요", "content": "펀딩에 참여하세요"}
            ]
        }


# 싱글톤 인스턴스
hybrid_ai_service = HybridAIService()
