import base64
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from uuid import uuid4

from app.schemas.generate import GenerateRequest


ONLINE_IMAGE_BASE_URL = "https://image.pollinations.ai/prompt"
ONLINE_IMAGE_MODEL = "flux"
ONLINE_IMAGE_TIMEOUT_SECONDS = 90
ONLINE_IMAGE_WIDTH = 512
ONLINE_IMAGE_HEIGHT = 768
BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"
GENERATED_DIR = STATIC_DIR / "generated"
PLACEHOLDER_PATH = STATIC_DIR / "placeholder.png"


CONTENT_TYPE_KEYWORDS = {
    "science_popularization": [
        "健身",
        "睡眠",
        "护肤",
        "饮食",
        "健康",
        "健康管理",
        "情绪管理",
        "养生",
        "恢复",
        "恢复训练",
        "拉伸",
        "久坐改善",
        "跑步",
        "科普",
        "知识",
        "睡前",
        "呼吸练习",
    ],
    "lifestyle": [
        "家居",
        "日常分享",
        "穿搭",
        "种草",
        "习惯",
        "晨间习惯",
        "收纳",
        "整理习惯",
        "生活方式",
        "日常",
        "居家",
        "分享",
        "读书",
        "独处时光",
        "亲子阅读",
        "家庭陪伴",
    ],
    "study_work": [
        "学习方法",
        "专注力",
        "时间管理",
        "备考",
        "英语学习",
        "考研",
        "职场效率",
        "高效办公",
        "复盘",
        "办公",
        "学习",
        "工作",
        "效率",
        "书桌",
        "职场成长",
    ],
    "tutorial_guide": [
        "步骤",
        "教程",
        "方法",
        "技巧",
        "指南",
        "怎么做",
        "操作",
        "入门",
        "流程",
        "讲解",
    ],
    "emotional_healing": [
        "焦虑",
        "焦虑缓解",
        "睡前放松",
        "情绪陪伴",
        "疗愈",
        "自我关怀",
        "治愈",
        "放松",
        "安静",
        "舒缓",
        "睡眠",
        "睡前仪式",
        "放松习惯",
        "呼吸练习",
    ],
    "marketing_promo": [
        "课程推广",
        "课程推荐",
        "宣传",
        "活动",
        "产品介绍",
        "卖点展示",
        "营销海报",
        "推广",
        "海报",
        "课程",
        "招生",
        "宣传图文",
        "宣传海报",
    ],
    "product_usage": [
        "app推荐",
        "工具推荐",
        "软件使用",
        "智能设备",
        "智能手表",
        "健康监测",
        "功能展示",
        "产品推荐",
        "产品推荐图文",
        "工具",
        "软件",
        "app",
        "设备",
        "产品使用",
        "手机查看",
    ],
    "food_nutrition": [
        "减脂餐",
        "早餐",
        "健康饮食",
        "营养搭配",
        "食谱",
        "高蛋白",
        "低脂",
        "餐食",
        "营养",
        "轻食",
        "午餐搭配",
        "咖啡",
        "饮食分享",
    ],
}


STYLE_MAPPING = {
    "科普风": "清晰、简洁、明亮、专业、易读，适合知识分享主视觉配图",
    "治愈风": "温暖、柔和、安静、舒缓、低刺激、具有陪伴感",
    "年轻化": "明亮、轻盈、清爽、自然、富有活力、符合年轻审美",
    "极简风": "构图简洁、背景干净、主体突出、留白感强",
    "插画风": "平面插画、柔和色彩、统一笔触、简洁造型",
    "写实风": "真实生活场景、自然光线、生活方式摄影感",
    "简洁专业风": "现代、理性、清晰、整洁、结构明确",
    "现代简洁风": "现代、清爽、结构清晰、主体明确、视觉统一",
    "温暖生活方式风": "温馨、自然、舒适、居家感、审美生活方式",
    "清新生活方式风": "清爽、自然、轻盈、生活方式感强、适合作为无文字主视觉配图",
    "现代营销风": "主体鲜明、现代、吸睛、整洁、有明确主视觉重点",
    "文艺风": "细腻、安静、清新、柔和、有审美感和生活气息",
}


DEFAULT_NEGATIVE_PROMPT = (
    "no text, no words, no letters, no typography, no fake text, no unreadable text, "
    "no captions, no title, no paragraph, no logo, no watermark, no poster, no banner, "
    "no magazine cover, no advertisement, no infographic, no UI, no button, no label, "
    "no text box, no layout grid, "
    "不要乱码，不要假文字，不要伪排版，不要标题区，不要按钮样式，"
    "不要海报模板感，不要广告感，不要杂志封面感，不要宣传页，不要信息图，"
    "不要复杂大场景，不要杂乱背景，不要构图混乱，不要低清晰度，不要过暗，不要水印，"
    "不要人物畸形，不要错误手部，不要奇怪手指，不要手部特写，不要多余肢体，不要脸部崩坏"
)


def _log(message: str) -> None:
    """Print concise backend-side logs for image generation."""
    print(f"[image_service] {message}")


def _ensure_static_files() -> None:
    """Ensure static and generated directories exist."""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_placeholder_image() -> str:
    """Create a local placeholder image and return its static path."""
    _ensure_static_files()
    if not PLACEHOLDER_PATH.exists():
        try:
            from PIL import Image, ImageDraw

            image = Image.new("RGB", (600, 400), color=(244, 237, 227))
            draw = ImageDraw.Draw(image)
            draw.rectangle((30, 30, 570, 370), outline=(217, 119, 6), width=4)
            draw.text((170, 185), "Local Placeholder", fill=(120, 53, 15))
            image.save(PLACEHOLDER_PATH)
        except Exception:
            placeholder_bytes = base64.b64decode(
                "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9WnR8i0AAAAASUVORK5CYII="
            )
            PLACEHOLDER_PATH.write_bytes(placeholder_bytes)
    return "/static/placeholder.png"


def ensure_static_assets() -> None:
    """Prepare static folders and the fallback placeholder image."""
    _ensure_placeholder_image()


def _collect_routing_text(
    *,
    payload: GenerateRequest,
    profile_summary: str,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Collect all available input text for simple routing."""
    parts = [
        " ".join(payload.interests),
        payload.style,
        payload.scenario,
        payload.target_user,
        payload.input_text or "",
        profile_summary,
        title or "",
        content or "",
    ]
    return " ".join(part for part in parts if part).lower()


def _infer_content_type(
    *,
    payload: GenerateRequest,
    profile_summary: str,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Route the request into a readable content type."""
    routing_text = _collect_routing_text(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )

    if any(keyword in routing_text for keyword in ["宣传", "海报", "推广", "课程推荐", "课程推广", "宣传图文"]):
        return "marketing_promo"
    if any(keyword in routing_text for keyword in ["教程", "指南", "怎么做", "步骤", "动作讲解", "技巧"]):
        return "tutorial_guide"
    if any(keyword in routing_text for keyword in ["app推荐", "产品推荐", "智能手表", "健康监测", "软件使用", "工具推荐"]):
        return "product_usage"
    if any(keyword in routing_text for keyword in ["减脂餐", "早餐", "高蛋白", "午餐搭配", "轻食", "咖啡"]):
        return "food_nutrition"
    if any(keyword in routing_text for keyword in ["焦虑", "焦虑缓解", "睡前", "情绪管理", "呼吸练习", "放松习惯", "睡眠质量", "睡前仪式"]):
        return "emotional_healing"

    best_type = "lifestyle"
    best_score = 0
    for content_type, keywords in CONTENT_TYPE_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in routing_text)
        if score > best_score:
            best_type = content_type
            best_score = score
    return best_type


def _extract_theme_keywords(
    *,
    payload: GenerateRequest,
    profile_summary: str,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Extract concise theme keywords for prompt templates."""
    keywords = [item.strip() for item in payload.interests if item.strip()]
    if keywords:
        return "、".join(keywords[:3])
    if title and title.strip():
        return title.strip()
    if content and content.strip():
        return content.strip()[:24]
    return profile_summary[:24]


def _map_visual_style(style: str, input_text: str | None) -> str:
    """Map user style words into stable visual descriptions."""
    style_text = f"{style} {(input_text or '')}".strip()
    mapped_styles: list[str] = []

    for keyword, description in STYLE_MAPPING.items():
        if keyword in style_text:
            mapped_styles.append(description)

    extra_keywords = {
        "明亮": "画面明亮通透",
        "年轻化": "更年轻化、更轻盈",
        "清新": "色调清新自然",
        "轻松": "氛围更轻松",
        "简洁": "构图更简洁",
        "温暖": "整体更温暖",
        "柔和": "视觉更柔和",
        "插画": "采用高质量插画化表达",
        "写实": "偏真实生活场景表达",
        "分享感": "有经验分享感和社交平台分享氛围",
        "封面": "适合作为社交平台无文字主视觉配图",
        "高级感": "具有精致感和高级感",
        "现代感": "具有现代感和统一审美",
        "平台感": "具有平台友好型主视觉质感",
        "传播感": "适合平台传播和展示",
    }
    for keyword, description in extra_keywords.items():
        if keyword in style_text and description not in mapped_styles:
            mapped_styles.append(description)

    if not mapped_styles:
        return "画面简洁、主体清晰、适合作为无文字主视觉配图"
    return "，".join(mapped_styles)


def _extract_emotional_tone(content_type: str, input_text: str | None) -> str:
    """Infer a gentle emotional tone for the scene."""
    base_map = {
        "science_popularization": "理性、清晰、专业、健康、可信",
        "lifestyle": "温暖、自然、轻松、舒适、有生活方式氛围",
        "study_work": "安静、专注、理性、整洁、清爽",
        "tutorial_guide": "明确、自然、易懂、清晰、稳定",
        "emotional_healing": "温柔、安静、低刺激、舒缓、治愈、有陪伴感",
        "marketing_promo": "现代、鲜明、积极、清晰、有传播感",
        "product_usage": "现代、自然、实用、清爽、有科技感",
        "food_nutrition": "新鲜、健康、轻盈、舒适、有晨间氛围",
    }
    tone = base_map.get(content_type, "自然、清晰、现代、舒适")

    extra_tones = []
    text = input_text or ""
    if "温暖" in text:
        extra_tones.append("温暖")
    if "柔和" in text:
        extra_tones.append("柔和")
    if "专业" in text:
        extra_tones.append("专业")
    if "治愈" in text:
        extra_tones.append("治愈")
    if "年轻" in text:
        extra_tones.append("年轻化")

    if extra_tones:
        return f"{tone}，{'、'.join(extra_tones)}"
    return tone


def _build_global_quality_boosters(content_type: str) -> str:
    """Build shared positive visual constraints."""
    base_parts = [
        "A clean text-free lifestyle illustration with no words, no typography, no logo, and no poster layout.",
        "主视觉配图要构图清晰、主体突出、背景简洁、光线自然，适合作为社交平台无文字主视觉。",
        "场景真实、元素自然、视觉统一，不做海报排版，不做抽象概念图。",
    ]

    type_specific = {
        "science_popularization": "强调清晰、专业、易理解、画面明亮、主体突出，用生活场景表达轻科普主题，不出现任何文字元素。",
        "lifestyle": "强调温暖自然、生活方式美感、日常场景真实舒适、明亮清爽、轻松自然和平台分享感。",
        "study_work": "强调简洁理性、整洁有秩序、专注氛围明显、现代清晰、结构明确和安静清爽。",
        "tutorial_guide": "强调易懂、清晰、示意明确、主体动作准确简洁，并具有辅助理解作用。",
        "emotional_healing": "强调温柔、安静、柔和、低刺激、疗愈氛围、陪伴感和安全感。",
        "marketing_promo": "强调视觉中心明确、简洁现代、主体鲜明、有吸引力，但仍然只是无文字主视觉氛围图。",
        "product_usage": "强调使用场景自然真实、产品与用户互动清楚、现代简洁，并兼具实用感与生活感。",
        "food_nutrition": "强调食物新鲜健康、饮食场景自然美观、晨间氛围舒适、轻盈精致清爽，是无文字早餐主视觉配图。",
    }
    base_parts.append(type_specific.get(content_type, "强调内容相关性、主体明确和平台展示友好度。"))
    return " ".join(base_parts)


def _infer_core_subject(content_type: str, theme_keywords: str, target_user: str) -> str:
    """Describe the core subject and scene by content type."""
    subject_map = {
        "science_popularization": f"{theme_keywords}相关的真实生活方式或健康行为场景",
        "lifestyle": f"{theme_keywords}相关的自然日常生活方式场景",
        "study_work": f"{theme_keywords}相关的专注学习或高效工作场景",
        "tutorial_guide": f"体现{theme_keywords}操作步骤、动作示意或方法过程的清晰场景",
        "emotional_healing": f"{theme_keywords}相关的休息、放松、呼吸或情绪疗愈场景",
        "marketing_promo": f"突出{theme_keywords}主题氛围和积极状态的生活方式主视觉场景",
        "product_usage": f"用户正在使用{theme_keywords}相关产品、设备或工具的真实生活场景",
        "food_nutrition": f"{theme_keywords}相关的高蛋白早餐、轻食餐桌或健康饮食生活方式场景",
    }
    subject = subject_map.get(content_type, f"{theme_keywords}相关的生活方式场景")
    return f"{subject}，目标用户为{target_user}"


def _build_prompt_by_type(
    *,
    content_type: str,
    theme_keywords: str,
    target_user: str,
    scenario: str,
    style_description: str,
    emotional_tone: str,
    core_subject: str,
    profile_summary: str,
    input_text: str | None = None,
) -> str:
    """Choose a richer Chinese prompt template by content type."""
    quality_boosters = _build_global_quality_boosters(content_type)
    extra_hint = f"补充需求：{input_text}。" if input_text and input_text.strip() else ""

    templates = {
        "science_popularization": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Focus on healthy lifestyle, recovery, sleep, body care, or other science-popularization-related daily scenes. "
            "Communicate the topic through scene and action only, with no text elements anywhere in the image. "
            "{quality_boosters}{extra_hint}"
        ),
        "lifestyle": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Highlight warm, natural, relaxed daily life scenes. "
            "Make it feel like a polished visual companion image for social media content, not a poster or layout template. "
            "{quality_boosters}{extra_hint}"
        ),
        "study_work": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Highlight a tidy desk, quiet focus, and a clear structured environment. "
            "Keep it suitable as a visual companion image for study or work content, with no text elements anywhere. "
            "{quality_boosters}{extra_hint}"
        ),
        "tutorial_guide": (
            "A clean text-free illustrative scene about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Show a clear action, method, or step-related scene with natural gestures and simple composition. "
            "This is a no-text companion image, not an infographic or tutorial card. "
            "{quality_boosters}{extra_hint}"
        ),
        "emotional_healing": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Create a gentle, calm, low-stimulation, healing atmosphere with soft warm light and relaxed indoor details when appropriate. "
            "The image should feel safe, quiet, comforting, and contain no text. "
            "{quality_boosters}{extra_hint}"
        ),
        "marketing_promo": (
            "A clean text-free modern lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Create a strong visual focus, attractive scene, and clear subject through people, objects, and atmosphere only. "
            "This should be a clean visual companion image with no typography, no banner, and no poster template. "
            "{quality_boosters}{extra_hint}"
        ),
        "product_usage": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Show a real usage scenario with clear interaction between user and product or device. "
            "The product should be visible but naturally integrated into the scene, with no UI labels or text elements anywhere. "
            "{quality_boosters}{extra_hint}"
        ),
        "food_nutrition": (
            "A clean text-free lifestyle illustration about {theme_keywords}. "
            "The image shows {core_subject}. "
            "The target audience is {target_user}. "
            "Style: {style_description}. Emotional tone: {emotional_tone}. "
            "Highlight healthy breakfast, high-protein food, light meal combinations, fresh ingredients, and a cozy morning atmosphere. "
            "This should be a text-free main visual image, not a poster, menu board, or magazine-style food cover. "
            "{quality_boosters}{extra_hint}"
        ),
    }
    template = templates.get(content_type, templates["lifestyle"])
    prompt = template.format(
        scenario=scenario,
        theme_keywords=theme_keywords,
        core_subject=core_subject,
        target_user=target_user,
        style_description=style_description,
        emotional_tone=emotional_tone,
        quality_boosters=quality_boosters,
        extra_hint=extra_hint,
    )
    return f"{prompt} 用户画像参考：{profile_summary}"


def _build_negative_prompt(content_type: str) -> str:
    """Build a reusable negative prompt string."""
    type_specific = {
        "food_nutrition": "no menu text, no food poster, no recipe card, 不要大块文字，不要广告摆拍感，不要杂乱餐桌，不要夸张装饰背景。",
        "marketing_promo": "no headline block, no promo banner, no poster frame, 不要模板海报框，不要标题条，不要按钮组件，不要杂志封面排版感。",
        "product_usage": "no UI overlay, no app card, no floating mockup, 不要产品悬浮样机，不要夸张科技海报，不要过度 UI 叠层。",
        "tutorial_guide": "no instruction labels, no step card, no diagram text, 不要复杂分镜，不要动作模糊，不要说明文字块。",
    }
    extra = type_specific.get(content_type, "")
    if extra:
        return f"{DEFAULT_NEGATIVE_PROMPT} {extra}"
    return DEFAULT_NEGATIVE_PROMPT


def _build_final_visual_prompt(
    *,
    payload: GenerateRequest,
    profile_summary: str,
    title: str | None = None,
    content: str | None = None,
) -> tuple[str, str]:
    """Build the final prompt package step by step."""
    content_type = _infer_content_type(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )
    theme_keywords = _extract_theme_keywords(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )
    style_description = _map_visual_style(payload.style, payload.input_text)
    emotional_tone = _extract_emotional_tone(content_type, payload.input_text)
    core_subject = _infer_core_subject(content_type, theme_keywords, payload.target_user)
    main_prompt = _build_prompt_by_type(
        content_type=content_type,
        theme_keywords=theme_keywords,
        target_user=payload.target_user,
        scenario=payload.scenario,
        style_description=style_description,
        emotional_tone=emotional_tone,
        core_subject=core_subject,
        profile_summary=profile_summary,
        input_text=payload.input_text,
    )
    negative_prompt = _build_negative_prompt(content_type)

    return main_prompt, negative_prompt


def _build_online_image_url(prompt: str, negative_prompt: str | None = None) -> str:
    """Build a public online image URL for demo use."""
    encoded_prompt = quote(prompt, safe="")
    url = (
        f"{ONLINE_IMAGE_BASE_URL}/{encoded_prompt}"
        f"?model={ONLINE_IMAGE_MODEL}"
        f"&width={ONLINE_IMAGE_WIDTH}"
        f"&height={ONLINE_IMAGE_HEIGHT}"
        f"&nologo=true"
        f"&safe=true"
        f"&enhance=false"
    )
    if negative_prompt:
        url += f"&negative={quote(negative_prompt, safe='')}"
    return url


def _download_online_image(prompt: str, negative_prompt: str | None = None) -> bytes:
    """Generate and download an image from the public online service."""
    image_url = _build_online_image_url(prompt, negative_prompt=negative_prompt)
    headers = {
        "User-Agent": "graduation-project-image-generator/1.0",
        "Accept": "image/png,image/jpeg,image/*;q=0.8,*/*;q=0.5",
    }

    request = Request(image_url, headers=headers, method="GET")
    with urlopen(request, timeout=ONLINE_IMAGE_TIMEOUT_SECONDS) as response:
        image_bytes = response.read()

    if not image_bytes:
        raise ValueError("Online image service returned empty image data")

    return image_bytes


def build_visual_prompt(
    *,
    payload: GenerateRequest,
    profile_summary: str,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Build the final main visual prompt for the image service."""
    main_prompt, _ = _build_final_visual_prompt(
        payload=payload,
        profile_summary=profile_summary,
        title=title,
        content=content,
    )
    return main_prompt


def build_negative_prompt(
    *,
    payload: GenerateRequest | None = None,
    profile_summary: str | None = None,
    title: str | None = None,
    content: str | None = None,
) -> str:
    """Build the final negative prompt for the image service."""
    if payload and profile_summary:
        content_type = _infer_content_type(
            payload=payload,
            profile_summary=profile_summary,
            title=title,
            content=content,
        )
        return _build_negative_prompt(content_type)
    return DEFAULT_NEGATIVE_PROMPT


def generate_image(prompt: str, negative_prompt: str | None = None) -> str:
    """Generate an image online, save it locally, or fallback to a placeholder."""
    _ensure_static_files()
    _log("Image generation started")

    try:
        image_bytes = _download_online_image(prompt, negative_prompt=negative_prompt)
        file_name = f"{uuid4().hex}.png"
        file_path = GENERATED_DIR / file_name
        file_path.write_bytes(image_bytes)
        _log("Image generation succeeded")
        return f"/static/generated/{file_name}"
    except Exception:
        _log("Image generation failed, using fallback placeholder")
        return _ensure_placeholder_image()


def generate_mock_image_url(payload: GenerateRequest) -> str:
    """Backward-compatible wrapper for current route imports."""
    profile_summary = (
        f"该用户关注{'、'.join(payload.interests)}。"
        f"内容风格偏向{payload.style}。"
        f"适用于{payload.scenario}。"
        f"目标用户是{payload.target_user}。"
    )
    prompt, negative_prompt = _build_final_visual_prompt(
        payload=payload,
        profile_summary=profile_summary,
    )
    return generate_image(prompt, negative_prompt=negative_prompt)
