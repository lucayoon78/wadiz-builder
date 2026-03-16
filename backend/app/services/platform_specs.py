"""
E-commerce platform specifications for page builder
"""

PLATFORM_SPECS = {
    "wadiz": {
        "name": "와디즈 크라우드펀딩",
        "page_type": "long_form",
        "max_width": 1080,
        "image_specs": {
            "detail_page": {"width": 1080, "format": ["JPG", "PNG", "GIF"]},
            "thumbnail": {"width": 640, "height": 640, "format": ["JPG", "PNG"]},
            "main_image": {"width": 1920, "height": 1080, "format": ["JPG"]},
        },
        "content_style": {
            "length": "very_long",  # 5,000-15,000px
            "tone": "storytelling",
            "hooking": True,
            "sections": ["intro", "problem", "solution", "features", "specs", "team", "faq", "rewards"],
        },
        "gif_allowed": True,
        "video_embed": True,
        "html_allowed": False,  # 이미지만
        "max_file_size_mb": 10,
    },
    
    "smartstore": {
        "name": "네이버 스마트스토어",
        "page_type": "standard",
        "max_width": 860,
        "image_specs": {
            "detail_page": {"width": 860, "format": ["JPG", "PNG", "GIF"]},
            "thumbnail": {"width": 500, "height": 500, "format": ["JPG"]},
            "additional_images": {"count": 20, "width": 700, "height": 700},
        },
        "content_style": {
            "length": "medium",  # 2,000-5,000px
            "tone": "direct",
            "hooking": False,
            "sections": ["main_image", "features", "specs", "usage", "notice"],
        },
        "gif_allowed": True,
        "video_embed": True,
        "html_allowed": True,  # 스마트에디터
        "max_file_size_mb": 10,
        "seo_important": True,
        "keywords_limit": 50,
    },
    
    "coupang": {
        "name": "쿠팡",
        "page_type": "standard",
        "max_width": 860,
        "image_specs": {
            "detail_page": {"width": 860, "format": ["JPG", "PNG"]},
            "thumbnail": {"width": 500, "height": 500, "format": ["JPG"]},
            "main_image": {"width": 1000, "height": 1000, "format": ["JPG"]},
            "additional_images": {"count": 9, "width": 1000, "height": 1000},
        },
        "content_style": {
            "length": "short",  # 1,000-3,000px
            "tone": "concise",
            "hooking": False,
            "sections": ["main_image", "key_features", "specs", "certification"],
        },
        "gif_allowed": False,  # 쿠팡은 GIF 제한적
        "video_embed": False,
        "html_allowed": False,
        "max_file_size_mb": 5,
        "strict_guidelines": True,  # 쿠팡은 가이드라인 엄격
    },
    
    "gmarket": {
        "name": "G마켓/옥션",
        "page_type": "standard",
        "max_width": 860,
        "image_specs": {
            "detail_page": {"width": 860, "format": ["JPG", "PNG", "GIF"]},
            "thumbnail": {"width": 500, "height": 500, "format": ["JPG"]},
            "main_image": {"width": 800, "height": 800, "format": ["JPG"]},
        },
        "content_style": {
            "length": "medium",  # 2,000-4,000px
            "tone": "promotional",
            "hooking": True,
            "sections": ["main_image", "promotion", "features", "specs", "delivery"],
        },
        "gif_allowed": True,
        "video_embed": False,
        "html_allowed": True,
        "max_file_size_mb": 10,
    },
    
    "11st": {
        "name": "11번가",
        "page_type": "standard",
        "max_width": 860,
        "image_specs": {
            "detail_page": {"width": 860, "format": ["JPG", "PNG", "GIF"]},
            "thumbnail": {"width": 500, "height": 500, "format": ["JPG"]},
        },
        "content_style": {
            "length": "medium",
            "tone": "direct",
            "sections": ["main_image", "features", "specs", "notice"],
        },
        "gif_allowed": True,
        "video_embed": False,
        "html_allowed": True,
        "max_file_size_mb": 10,
    },
}

# 플랫폼별 차이점 요약
PLATFORM_DIFFERENCES = {
    "page_length": {
        "wadiz": "매우 김 (스토리텔링)",
        "smartstore": "중간 (정보 전달)",
        "coupang": "짧음 (간결)",
        "gmarket": "중간 (프로모션)",
        "11st": "중간",
    },
    "image_width": {
        "wadiz": 1080,
        "smartstore": 860,
        "coupang": 860,
        "gmarket": 860,
        "11st": 860,
    },
    "tone": {
        "wadiz": "스토리텔링, 감성적",
        "smartstore": "직관적, 정보 중심",
        "coupang": "간결, 핵심만",
        "gmarket": "프로모션, 할인 강조",
        "11st": "직관적",
    },
    "gif_support": {
        "wadiz": "✅ 적극 활용",
        "smartstore": "✅ 가능",
        "coupang": "❌ 제한적",
        "gmarket": "✅ 가능",
        "11st": "✅ 가능",
    },
}

# 썸네일 규격
THUMBNAIL_SPECS = {
    "wadiz": {
        "size": (640, 640),
        "ratio": "1:1",
        "format": "JPG",
        "style": "감성적, 제품+배경",
    },
    "smartstore": {
        "size": (500, 500),
        "ratio": "1:1",
        "format": "JPG",
        "style": "깔끔한 배경, 제품 강조",
    },
    "coupang": {
        "size": (500, 500),
        "ratio": "1:1",
        "format": "JPG",
        "style": "순백 배경, 제품만",
        "requirements": "배경 100% 흰색 필수",
    },
    "gmarket": {
        "size": (500, 500),
        "ratio": "1:1",
        "format": "JPG",
        "style": "제품 + 간단한 텍스트",
    },
}

# GIF 규격
GIF_SPECS = {
    "wadiz": {
        "recommended": True,
        "max_width": 1080,
        "max_size_mb": 10,
        "frame_count": "10-30 프레임",
        "duration": "2-5초",
        "use_cases": ["제품 회전", "기능 시연", "비포애프터"],
    },
    "smartstore": {
        "recommended": True,
        "max_width": 860,
        "max_size_mb": 5,
        "frame_count": "10-20 프레임",
        "duration": "2-3초",
        "use_cases": ["제품 360도", "사용법"],
    },
    "coupang": {
        "recommended": False,
        "note": "GIF 사용 지양, 정적 이미지 권장",
    },
    "gmarket": {
        "recommended": True,
        "max_width": 860,
        "max_size_mb": 5,
        "frame_count": "10-20 프레임",
        "duration": "2-3초",
        "use_cases": ["프로모션", "제품 특징"],
    },
}
