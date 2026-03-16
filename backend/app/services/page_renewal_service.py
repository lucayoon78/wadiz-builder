"""
Page Renewal AI Service
기존 와디즈/쿠팡 페이지 분석 → AI 개선 제안 → 리뉴얼 버전 생성
"""
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import httpx


class PageRenewalService:
    """
    기존 페이지 리뉴얼 서비스
    - URL 또는 HTML 파일에서 콘텐츠 추출
    - AI로 현재 페이지 분석
    - 개선 포인트 도출
    - 리뉴얼 버전 생성
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
    
    async def fetch_page_from_url(self, url: str) -> Dict[str, Any]:
        """URL에서 페이지 콘텐츠 가져오기"""
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                html_content = response.text
                return await self._extract_content_from_html(html_content, url)
                
        except Exception as e:
            raise Exception(f"URL 페이지 가져오기 실패: {str(e)}")
    
    async def analyze_html_content(self, html_content: str) -> Dict[str, Any]:
        """HTML 콘텐츠에서 정보 추출"""
        return await self._extract_content_from_html(html_content)
    
    async def _extract_content_from_html(self, html_content: str, url: Optional[str] = None) -> Dict[str, Any]:
        """HTML에서 핵심 콘텐츠 추출"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 제목 추출
            title = ""
            if soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)
            elif soup.find('title'):
                title = soup.find('title').get_text(strip=True)
            
            # 본문 텍스트 추출 (script, style 제외)
            for script in soup(["script", "style"]):
                script.decompose()
            
            text_content = soup.get_text(separator='\n', strip=True)
            
            # 이미지 URL 추출
            images = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if src:
                    images.append({"src": src, "alt": alt})
            
            # 메타 정보 추출
            meta_description = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_description = meta_tag.get('content', '')
            
            return {
                "title": title,
                "text_content": text_content[:10000],  # 처음 10,000자만
                "images_count": len(images),
                "images": images[:10],  # 처음 10개만
                "meta_description": meta_description,
                "html_length": len(html_content),
                "source_url": url
            }
            
        except Exception as e:
            raise Exception(f"HTML 파싱 실패: {str(e)}")
    
    async def analyze_page_with_ai(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        AI로 기존 페이지 분석
        1단계: Gemini로 빠른 분석
        2단계: GPT-4로 상세 개선안
        """
        
        # 1단계: Gemini로 현재 페이지 분석
        analysis = await self._analyze_with_gemini(page_data)
        
        # 2단계: GPT-4로 개선 방향 제시
        improvements = await self._suggest_improvements_with_gpt4(page_data, analysis)
        
        return {
            "current_analysis": analysis,
            "improvement_suggestions": improvements,
            "ai_model": "hybrid_gemini_gpt4"
        }
    
    async def _analyze_with_gemini(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gemini로 현재 페이지 분석"""
        
        if not self.gemini_model:
            return self._get_basic_analysis(page_data)
        
        prompt = f"""
당신은 크라우드펀딩 페이지 전문 분석가입니다.
아래 기존 페이지를 분석하고 평가해주세요.

**제목:** {page_data.get('title', '없음')}

**본문 내용 (일부):**
{page_data.get('text_content', '')[:2000]}

**이미지 수:** {page_data.get('images_count', 0)}개

**분석 항목:**
1. 현재 강점 (3가지)
2. 현재 약점 (3가지)
3. 구조적 문제점
4. 카피라이팅 평가
5. 시각적 요소 평가
6. 와디즈 황금구조 준수 여부
7. 개선 우선순위 (1-5)

**출력 형식 (JSON):**
{{
  "strengths": ["강점1", "강점2", "강점3"],
  "weaknesses": ["약점1", "약점2", "약점3"],
  "structure_issues": "구조적 문제 설명",
  "copy_rating": "1-10점 + 이유",
  "visual_rating": "1-10점 + 이유",
  "golden_structure_score": "1-10점",
  "priority_improvements": ["우선순위1", "우선순위2", "우선순위3"]
}}

JSON만 출력하세요.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            # JSON 파싱
            import json
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
            
            analysis = json.loads(result_text.strip())
            return analysis
            
        except Exception as e:
            print(f"Gemini 분석 실패: {e}")
            return self._get_basic_analysis(page_data)
    
    async def _suggest_improvements_with_gpt4(
        self,
        page_data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """GPT-4로 구체적 개선 방향 제시"""
        
        if not self.openai_client:
            return self._get_basic_improvements()
        
        prompt = f"""
당신은 와디즈 펀딩 페이지 리뉴얼 전문가입니다.

**기존 페이지 분석 결과:**
- 강점: {', '.join(analysis.get('strengths', []))}
- 약점: {', '.join(analysis.get('weaknesses', []))}
- 구조 문제: {analysis.get('structure_issues', '')}

**제목:** {page_data.get('title', '')}

**개선 방향 제시:**
1. 새로운 헤드라인 (더 강렬하고 후킹력 있게)
2. 구조 개선안 (와디즈 5단계 기준)
3. 카피 개선 포인트 (3가지)
4. 시각적 개선 포인트 (3가지)
5. 예상 펀딩 증가율 (%)

**출력 형식 (JSON):**
{{
  "new_headline": "개선된 헤드라인",
  "new_subheadline": "개선된 부제목",
  "structure_plan": ["1단계: ...", "2단계: ...", ...],
  "copy_improvements": ["개선점1", "개선점2", "개선점3"],
  "visual_improvements": ["개선점1", "개선점2", "개선점3"],
  "estimated_improvement": "30-50% 증가 예상 + 이유"
}}

JSON만 출력하세요.
"""
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "당신은 와디즈 펀딩 페이지 리뉴얼 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            improvements = json.loads(response.choices[0].message.content)
            return improvements
            
        except Exception as e:
            print(f"GPT-4 개선안 생성 실패: {e}")
            return self._get_basic_improvements()
    
    async def generate_renewed_page(
        self,
        page_data: Dict[str, Any],
        analysis: Dict[str, Any],
        improvements: Dict[str, Any],
        product_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        리뉴얼된 페이지 생성
        기존 콘텐츠 + AI 개선안 → 새 페이지
        """
        
        # 기존 강점 유지 + 약점 개선
        prompt = f"""
와디즈 펀딩 페이지 리뉴얼을 위한 새로운 카피를 작성하세요.

**기존 페이지:**
- 제목: {page_data.get('title', '')}
- 강점: {', '.join(analysis.get('strengths', []))}

**개선 방향:**
- 새 헤드라인: {improvements.get('new_headline', '')}
- 새 부제목: {improvements.get('new_subheadline', '')}

**요구사항:**
1. 기존 강점은 유지
2. 약점은 개선
3. 와디즈 5단계 황금구조 적용
4. 감성적 스토리텔링 강화
5. 후킹 포인트 명확화

메인 카피, 대안 3개, CTA를 생성하세요.
"""
        
        try:
            if self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "당신은 와디즈 전문 카피라이터입니다."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                
                renewed_copy = response.choices[0].message.content
                
                return {
                    "renewed_headline": improvements.get('new_headline', page_data.get('title', '')),
                    "renewed_subheadline": improvements.get('new_subheadline', ''),
                    "renewed_main_copy": renewed_copy,
                    "structure_plan": improvements.get('structure_plan', []),
                    "before_after_comparison": {
                        "before": {
                            "title": page_data.get('title', ''),
                            "strengths": analysis.get('strengths', []),
                            "weaknesses": analysis.get('weaknesses', [])
                        },
                        "after": {
                            "title": improvements.get('new_headline', ''),
                            "improvements": improvements.get('copy_improvements', []),
                            "estimated_increase": improvements.get('estimated_improvement', '')
                        }
                    }
                }
        except Exception as e:
            print(f"리뉴얼 페이지 생성 실패: {e}")
        
        # 폴백: 기본 리뉴얼
        return {
            "renewed_headline": improvements.get('new_headline', page_data.get('title', '')),
            "renewed_subheadline": improvements.get('new_subheadline', ''),
            "renewed_main_copy": "리뉴얼된 카피가 여기에 생성됩니다.",
            "structure_plan": improvements.get('structure_plan', []),
            "before_after_comparison": {}
        }
    
    def _get_basic_analysis(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 분석 (AI 없을 때 폴백)"""
        return {
            "strengths": ["콘텐츠 존재", "구조화된 정보"],
            "weaknesses": ["AI 분석 필요", "상세 평가 불가"],
            "structure_issues": "AI 분석이 필요합니다",
            "copy_rating": "AI 평가 필요",
            "visual_rating": f"이미지 {page_data.get('images_count', 0)}개 감지",
            "golden_structure_score": "평가 불가",
            "priority_improvements": ["AI 분석 실행", "상세 리포트 생성"]
        }
    
    def _get_basic_improvements(self) -> Dict[str, Any]:
        """기본 개선안 (AI 없을 때 폴백)"""
        return {
            "new_headline": "개선된 헤드라인 (AI 생성 필요)",
            "new_subheadline": "개선된 부제목 (AI 생성 필요)",
            "structure_plan": ["AI 분석이 필요합니다"],
            "copy_improvements": ["AI 개선안 생성 필요"],
            "visual_improvements": ["AI 개선안 생성 필요"],
            "estimated_improvement": "AI 예측 필요"
        }


# 싱글톤 인스턴스
page_renewal_service = PageRenewalService()
