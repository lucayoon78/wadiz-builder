"""
E-commerce Bestseller Crawler - Analyze top-performing product pages
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import json
import re


class BestsellerCrawler:
    """베스트셀러 상품 페이지 크롤링 및 분석"""
    
    def __init__(self):
        self.results = []
    
    async def crawl_smartstore_bestsellers(
        self,
        category: str = "전체",
        min_reviews: int = 1000,
        min_purchases: int = 100,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        네이버 스마트스토어 베스트셀러 크롤링
        
        Args:
            category: 카테고리 (전체, 패션의류, 식품, 가전디지털 등)
            min_reviews: 최소 리뷰 수
            min_purchases: 최소 구매 건수
            limit: 크롤링 개수
        
        Returns:
            List of product analysis data
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 네이버 쇼핑 베스트 페이지
            url = f"https://shopping.naver.com/home/p/best/category"
            await page.goto(url, wait_until="networkidle")
            
            products = []
            
            try:
                # 상품 리스트 추출
                items = await page.query_selector_all(".product_item")
                
                for item in items[:limit]:
                    try:
                        # 상품명
                        title_elem = await item.query_selector(".product_title")
                        title = await title_elem.inner_text() if title_elem else ""
                        
                        # 상품 링크
                        link_elem = await item.query_selector("a")
                        link = await link_elem.get_attribute("href") if link_elem else ""
                        
                        # 리뷰 수
                        review_elem = await item.query_selector(".review_count")
                        review_text = await review_elem.inner_text() if review_elem else "0"
                        review_count = self._extract_number(review_text)
                        
                        # 구매 건수
                        purchase_elem = await item.query_selector(".purchase_count")
                        purchase_text = await purchase_elem.inner_text() if purchase_elem else "0"
                        purchase_count = self._extract_number(purchase_text)
                        
                        if review_count >= min_reviews and purchase_count >= min_purchases:
                            # 상세 페이지 분석
                            detail = await self._analyze_product_page(page, link)
                            
                            products.append({
                                "platform": "smartstore",
                                "title": title,
                                "url": link,
                                "reviews": review_count,
                                "purchases": purchase_count,
                                "detail_analysis": detail,
                                "crawled_at": datetime.utcnow().isoformat(),
                            })
                    
                    except Exception as e:
                        print(f"Error crawling item: {e}")
                        continue
            
            finally:
                await browser.close()
            
            return products
    
    async def _analyze_product_page(self, page, url: str) -> Dict[str, Any]:
        """상세페이지 분석"""
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)  # 이미지 로딩 대기
            
            # HTML 가져오기
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            
            # 상세페이지 이미지 영역 찾기
            detail_area = soup.find('div', {'class': re.compile('detail|product_detail|상세')})
            
            if not detail_area:
                # 대체 셀렉터들 시도
                detail_area = soup.find('div', {'id': re.compile('detail|product')})
            
            analysis = {
                "total_height": 0,
                "image_count": 0,
                "gif_count": 0,
                "text_sections": 0,
                "structure": [],
                "color_scheme": [],
                "font_sizes": [],
            }
            
            if detail_area:
                # 이미지 분석
                images = detail_area.find_all('img')
                analysis["image_count"] = len(images)
                
                # GIF 개수
                analysis["gif_count"] = len([img for img in images if '.gif' in str(img.get('src', ''))])
                
                # 이미지 크기로 높이 추정
                for img in images:
                    # 이미지 높이 속성 확인
                    height = img.get('height', 0)
                    if height:
                        try:
                            analysis["total_height"] += int(height)
                        except:
                            pass
                
                # 예상 높이 (이미지당 평균 800px)
                if analysis["total_height"] == 0:
                    analysis["total_height"] = analysis["image_count"] * 800
                
                # 텍스트 섹션 분석
                text_elements = detail_area.find_all(['p', 'h1', 'h2', 'h3', 'div'])
                analysis["text_sections"] = len([elem for elem in text_elements if elem.get_text(strip=True)])
                
                # 구조 분석 (간단히)
                structure = []
                for elem in detail_area.find_all(['img', 'h2', 'h3'])[:20]:
                    if elem.name == 'img':
                        structure.append({"type": "image", "src": elem.get('src', '')})
                    else:
                        structure.append({"type": "heading", "text": elem.get_text(strip=True)[:50]})
                
                analysis["structure"] = structure
            
            return analysis
        
        except Exception as e:
            print(f"Error analyzing page: {e}")
            return {
                "error": str(e),
                "total_height": 0,
                "image_count": 0,
                "gif_count": 0,
            }
    
    async def crawl_coupang_bestsellers(
        self,
        category: str = "전체",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        쿠팡 베스트셀러 크롤링
        
        Note: 쿠팡은 로그인 필요 + API 제한이 있어 주의 필요
        """
        # TODO: 쿠팡 API 또는 Selenium 활용
        # 현재는 플레이스홀더
        
        return []
    
    async def crawl_gmarket_bestsellers(
        self,
        category: str = "전체",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """G마켓 베스트셀러 크롤링"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            products = []
            
            try:
                # G마켓 베스트 페이지
                url = "http://corners.gmarket.co.kr/Bestsellers"
                await page.goto(url, wait_until="networkidle")
                
                # 상품 추출 로직
                # TODO: G마켓 구조에 맞게 구현
                
            finally:
                await browser.close()
            
            return products
    
    def _extract_number(self, text: str) -> int:
        """텍스트에서 숫자 추출 (예: "1,234건" -> 1234)"""
        numbers = re.findall(r'\d+', text.replace(',', ''))
        return int(numbers[0]) if numbers else 0
    
    async def analyze_patterns(self, products: List[Dict]) -> Dict[str, Any]:
        """
        크롤링한 제품들의 패턴 분석
        
        Returns:
            플랫폼별 황금 패턴
        """
        
        if not products:
            return {}
        
        platform = products[0]["platform"]
        
        # 통계 계산
        stats = {
            "platform": platform,
            "sample_size": len(products),
            "avg_page_height": 0,
            "avg_image_count": 0,
            "gif_usage_rate": 0,
            "common_structure": [],
            "recommendations": [],
        }
        
        total_height = 0
        total_images = 0
        total_gifs = 0
        
        for product in products:
            detail = product.get("detail_analysis", {})
            total_height += detail.get("total_height", 0)
            total_images += detail.get("image_count", 0)
            total_gifs += detail.get("gif_count", 0)
        
        count = len(products)
        stats["avg_page_height"] = int(total_height / count) if count > 0 else 0
        stats["avg_image_count"] = int(total_images / count) if count > 0 else 0
        stats["gif_usage_rate"] = (total_gifs / total_images * 100) if total_images > 0 else 0
        
        # 추천 사항
        stats["recommendations"] = [
            f"평균 페이지 높이: {stats['avg_page_height']}px",
            f"평균 이미지 수: {stats['avg_image_count']}개",
            f"GIF 사용 비율: {stats['gif_usage_rate']:.1f}%",
        ]
        
        return stats


# 간단한 사용 예시
async def main():
    crawler = BestsellerCrawler()
    
    # 스마트스토어 크롤링
    print("🕷️ 네이버 스마트스토어 베스트셀러 크롤링 중...")
    smartstore_products = await crawler.crawl_smartstore_bestsellers(
        min_reviews=1000,
        min_purchases=100,
        limit=20,
    )
    
    print(f"✅ {len(smartstore_products)}개 제품 분석 완료")
    
    # 패턴 분석
    if smartstore_products:
        pattern = await crawler.analyze_patterns(smartstore_products)
        print("\n📊 분석 결과:")
        print(json.dumps(pattern, indent=2, ensure_ascii=False))
        
        # JSON 저장
        with open('/tmp/smartstore_bestsellers.json', 'w', encoding='utf-8') as f:
            json.dump(smartstore_products, f, indent=2, ensure_ascii=False)
        
        print("\n💾 데이터 저장: /tmp/smartstore_bestsellers.json")


if __name__ == "__main__":
    asyncio.run(main())
