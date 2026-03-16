"""
Template seed data - 와디즈 성공 사례 기반 10개 템플릿
"""

TEMPLATE_CATEGORIES = [
    {
        "name": "테크/가전",
        "slug": "tech-electronics",
        "description": "스마트 기기, IoT, 가전제품",
        "icon": "💻",
        "sort_order": 1,
    },
    {
        "name": "패션/뷰티",
        "slug": "fashion-beauty",
        "description": "의류, 액세서리, 화장품",
        "icon": "👗",
        "sort_order": 2,
    },
    {
        "name": "식품",
        "slug": "food",
        "description": "건강식품, 간편식, 음료",
        "icon": "🍱",
        "sort_order": 3,
    },
    {
        "name": "생활용품",
        "slug": "lifestyle",
        "description": "주방용품, 인테리어, 생활잡화",
        "icon": "🏠",
        "sort_order": 4,
    },
    {
        "name": "출판/콘텐츠",
        "slug": "content",
        "description": "책, 클래스, 디지털 콘텐츠",
        "icon": "📚",
        "sort_order": 5,
    },
]

TEMPLATES = [
    # 테크/가전 (3개)
    {
        "category_slug": "tech-electronics",
        "name": "스마트 디바이스 - 미니멀",
        "description": "깔끔한 디자인으로 기술 특장점 강조. IoT, 스마트홈 제품에 최적화.",
        "html_structure": {
            "intro": {
                "layout": "centered",
                "background_type": "gradient",
                "blocks": [
                    {"type": "heading", "style": "large", "placeholder": "{product_name}"},
                    {"type": "tagline", "style": "bold", "placeholder": "{usp}"},
                    {"type": "hero_image", "style": "product_showcase"},
                ]
            },
            "body": [
                {
                    "section_type": "feature",
                    "layout": "image_left_text_right",
                    "blocks": [
                        {"type": "title", "placeholder": "핵심 기능 1"},
                        {"type": "description", "placeholder": "기술 설명"},
                        {"type": "specs", "placeholder": "스펙 표"},
                        {"type": "image", "style": "device_mockup"},
                    ]
                },
                {
                    "section_type": "comparison",
                    "layout": "two_column",
                    "blocks": [
                        {"type": "before_after", "placeholder": "기존 vs 우리 제품"},
                    ]
                },
                {
                    "section_type": "app_screenshot",
                    "layout": "carousel",
                    "blocks": [
                        {"type": "app_images", "count": 3},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "faq", "count": 5},
                    {"type": "early_bird", "style": "pricing_table"},
                    {"type": "cta", "text": "얼리버드 특가 지금 펀딩하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#2563eb",
            "secondary": "#3b82f6",
            "accent": "#60a5fa",
            "text": "#1e293b",
        },
        "ai_prompt_template": """제품명: {product_name}
핵심 기능: {usp}

아래 구조로 테크 제품 상세페이지를 작성하세요:
1. 인트로: 3초 후킹 문구 (기술혁신 강조)
2. 본론: 핵심 기능 3개 (각각 제목+설명+스펙)
3. 비교: 기존 제품 대비 우월성
4. 앱: 앱 사용법 간단 설명
5. FAQ: 기술 관련 질문 5개

톤: 전문적이지만 쉽게, 수치로 증명""",
        "based_on_project_url": "https://www.wadiz.kr/web/campaign/detail/123456",
        "funding_amount": 50000000,
        "success_rate": 1523,
        "difficulty": "easy",
        "is_featured": True,
    },
    {
        "category_slug": "tech-electronics",
        "name": "가전제품 - 감성 스토리텔링",
        "description": "제품보다 라이프스타일 강조. 청소기, 공기청정기 등에 적합.",
        "html_structure": {
            "intro": {
                "layout": "full_screen_video",
                "blocks": [
                    {"type": "video", "placeholder": "제품 사용 영상"},
                    {"type": "overlay_text", "placeholder": "{product_name}과 함께하는 일상"},
                ]
            },
            "body": [
                {
                    "section_type": "story",
                    "layout": "narrative",
                    "blocks": [
                        {"type": "user_story", "placeholder": "사용자 이야기"},
                        {"type": "problem", "placeholder": "이런 불편 겪으셨나요?"},
                        {"type": "solution", "placeholder": "우리 제품의 해결책"},
                    ]
                },
                {
                    "section_type": "features",
                    "layout": "icon_grid",
                    "blocks": [
                        {"type": "feature_icons", "count": 6},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "testimonials", "count": 3},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "더 나은 일상 시작하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#10b981",
            "secondary": "#34d399",
            "accent": "#6ee7b7",
            "text": "#064e3b",
        },
        "funding_amount": 80000000,
        "success_rate": 2341,
        "difficulty": "medium",
    },
    {
        "category_slug": "tech-electronics",
        "name": "크라우드펀딩 킹 - 올인원",
        "description": "모든 요소 포함. 대형 프로젝트용. 동영상, GIF, 인터랙티브 요소.",
        "html_structure": {
            "intro": {
                "layout": "split_screen",
                "blocks": [
                    {"type": "video_left"},
                    {"type": "text_right", "with_countdown": True},
                ]
            },
            "body": [
                {"section_type": "awards", "blocks": [{"type": "award_badges"}]},
                {"section_type": "media", "blocks": [{"type": "press_logos"}]},
                {"section_type": "features", "layout": "tabs"},
                {"section_type": "team", "blocks": [{"type": "team_photos"}]},
                {"section_type": "timeline", "blocks": [{"type": "roadmap"}]},
            ],
            "outro": {
                "blocks": [
                    {"type": "pricing_comparison", "count": 3},
                    {"type": "risk_free", "text": "100% 환불 보장"},
                    {"type": "cta_large"},
                ]
            }
        },
        "funding_amount": 300000000,
        "success_rate": 5000,
        "difficulty": "hard",
        "is_featured": True,
    },
    
    # 패션/뷰티 (2개)
    {
        "category_slug": "fashion-beauty",
        "name": "패션 - 룩북 스타일",
        "description": "대형 이미지 중심. 모델컷, 착용샷 강조.",
        "html_structure": {
            "intro": {
                "layout": "fullscreen_image",
                "blocks": [
                    {"type": "hero_image", "style": "model_shot"},
                    {"type": "brand_logo"},
                ]
            },
            "body": [
                {
                    "section_type": "lookbook",
                    "layout": "masonry_grid",
                    "blocks": [
                        {"type": "model_images", "count": 6},
                    ]
                },
                {
                    "section_type": "details",
                    "layout": "accordion",
                    "blocks": [
                        {"type": "fabric", "placeholder": "소재 상세"},
                        {"type": "size_chart"},
                        {"type": "care_guide"},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "size_recommendation"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "지금 바로 구매하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#000000",
            "secondary": "#404040",
            "accent": "#d4af37",
            "text": "#1a1a1a",
        },
        "funding_amount": 30000000,
        "success_rate": 1200,
        "difficulty": "easy",
    },
    {
        "category_slug": "fashion-beauty",
        "name": "뷰티 - 비포애프터",
        "description": "효과 중심. 사용 전후 비교, 성분 강조.",
        "html_structure": {
            "intro": {
                "layout": "before_after_slider",
                "blocks": [
                    {"type": "comparison_image"},
                    {"type": "result_text", "placeholder": "7일만에 이 변화"},
                ]
            },
            "body": [
                {
                    "section_type": "ingredients",
                    "layout": "card_grid",
                    "blocks": [
                        {"type": "ingredient_cards", "count": 4},
                    ]
                },
                {
                    "section_type": "clinical_test",
                    "blocks": [
                        {"type": "test_results", "with_charts": True},
                    ]
                },
                {
                    "section_type": "reviews",
                    "layout": "testimonial_carousel",
                    "blocks": [
                        {"type": "user_reviews", "count": 5},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "dermatologist_approved"},
                    {"type": "faq", "count": 5},
                    {"type": "limited_offer"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#ec4899",
            "secondary": "#f472b6",
            "accent": "#fbcfe8",
            "text": "#831843",
        },
        "funding_amount": 45000000,
        "success_rate": 1800,
        "difficulty": "medium",
    },
    
    # 식품 (2개)
    {
        "category_slug": "food",
        "name": "식품 - 건강 강조",
        "description": "성분, 효능 중심. 건강식품, 다이어트 제품.",
        "html_structure": {
            "intro": {
                "layout": "centered_with_badge",
                "blocks": [
                    {"type": "certification_badges"},
                    {"type": "product_name"},
                    {"type": "natural_image", "style": "fresh_ingredients"},
                ]
            },
            "body": [
                {
                    "section_type": "nutrition",
                    "blocks": [
                        {"type": "nutrition_table"},
                        {"type": "calorie_info"},
                    ]
                },
                {
                    "section_type": "benefits",
                    "layout": "icon_list",
                    "blocks": [
                        {"type": "health_benefits", "count": 5},
                    ]
                },
                {
                    "section_type": "how_to_use",
                    "blocks": [
                        {"type": "recipe_suggestions", "count": 3},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "subscription_options"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "건강한 습관 시작하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#059669",
            "secondary": "#10b981",
            "accent": "#6ee7b7",
            "text": "#064e3b",
        },
        "funding_amount": 60000000,
        "success_rate": 2000,
        "difficulty": "easy",
        "is_featured": True,
    },
    {
        "category_slug": "food",
        "name": "식품 - 맛있어 보이게",
        "description": "푸드 포토 중심. 간편식, 디저트, 음료.",
        "html_structure": {
            "intro": {
                "layout": "hero_food_photo",
                "blocks": [
                    {"type": "delicious_image", "style": "close_up"},
                    {"type": "tagline", "placeholder": "집에서 즐기는 레스토랑 맛"},
                ]
            },
            "body": [
                {
                    "section_type": "photos",
                    "layout": "grid_gallery",
                    "blocks": [
                        {"type": "food_photos", "count": 8},
                    ]
                },
                {
                    "section_type": "story",
                    "blocks": [
                        {"type": "chef_story"},
                        {"type": "recipe_origin"},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "bundle_options"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "지금 주문하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#f59e0b",
            "secondary": "#fbbf24",
            "accent": "#fde68a",
            "text": "#78350f",
        },
        "funding_amount": 35000000,
        "success_rate": 1500,
        "difficulty": "easy",
    },
    
    # 생활용품 (2개)
    {
        "category_slug": "lifestyle",
        "name": "생활용품 - 심플 라이프",
        "description": "미니멀 디자인. 주방, 욕실, 정리용품.",
        "html_structure": {
            "intro": {
                "layout": "clean_minimal",
                "blocks": [
                    {"type": "product_white_bg"},
                    {"type": "one_line_benefit"},
                ]
            },
            "body": [
                {
                    "section_type": "use_cases",
                    "blocks": [
                        {"type": "lifestyle_photos", "count": 4},
                    ]
                },
                {
                    "section_type": "specs",
                    "blocks": [
                        {"type": "dimensions"},
                        {"type": "materials"},
                        {"type": "colors", "with_swatches": True},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "bundle_discount"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "깔끔한 일상 만들기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#64748b",
            "secondary": "#94a3b8",
            "accent": "#cbd5e1",
            "text": "#1e293b",
        },
        "funding_amount": 25000000,
        "success_rate": 1100,
        "difficulty": "easy",
    },
    {
        "category_slug": "lifestyle",
        "name": "인테리어 - 공간 변신",
        "description": "공간 연출 강조. 가구, 조명, 데코.",
        "html_structure": {
            "intro": {
                "layout": "room_showcase",
                "blocks": [
                    {"type": "room_photo", "style": "wide_angle"},
                    {"type": "transformation_text"},
                ]
            },
            "body": [
                {
                    "section_type": "before_after",
                    "blocks": [
                        {"type": "space_transformation", "slider": True},
                    ]
                },
                {
                    "section_type": "styling_tips",
                    "blocks": [
                        {"type": "coordination_guide"},
                        {"type": "room_type_suggestions"},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "installation_guide"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "내 공간 업그레이드하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#8b5cf6",
            "secondary": "#a78bfa",
            "accent": "#c4b5fd",
            "text": "#5b21b6",
        },
        "funding_amount": 40000000,
        "success_rate": 1600,
        "difficulty": "medium",
    },
    
    # 출판/콘텐츠 (1개)
    {
        "category_slug": "content",
        "name": "책/클래스 - 전문가 신뢰",
        "description": "저자 소개, 목차, 샘플 중심.",
        "html_structure": {
            "intro": {
                "layout": "author_hero",
                "blocks": [
                    {"type": "author_photo"},
                    {"type": "credentials"},
                    {"type": "book_cover"},
                ]
            },
            "body": [
                {
                    "section_type": "contents",
                    "blocks": [
                        {"type": "table_of_contents"},
                        {"type": "sample_chapter"},
                    ]
                },
                {
                    "section_type": "reviews",
                    "blocks": [
                        {"type": "expert_reviews", "count": 3},
                    ]
                },
            ],
            "outro": {
                "blocks": [
                    {"type": "bonus_materials"},
                    {"type": "faq", "count": 5},
                    {"type": "cta", "text": "지금 시작하기"},
                ]
            }
        },
        "color_scheme": {
            "primary": "#7c3aed",
            "secondary": "#8b5cf6",
            "accent": "#a78bfa",
            "text": "#4c1d95",
        },
        "funding_amount": 20000000,
        "success_rate": 900,
        "difficulty": "medium",
    },
]
