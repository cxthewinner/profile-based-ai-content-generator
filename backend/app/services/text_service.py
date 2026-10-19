from functools import lru_cache
import re
from typing import Any

from app.schemas.generate import GenerateRequest


TEXT_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
TEXT_MODEL_FALLBACK = "Qwen/Qwen2.5-1.5B-Instruct"
MAX_OUTPUT_TOKENS = 260


GENERIC_TAGS = {
    "用户画像",
    "图文生成",
    "本地模型",
    "内容生成",
    "社交平台",
    "经验分享",
}


def _log(message: str) -> None:
    """Print concise backend-side logs for text generation."""
    print(f"[text_service] {message}")


def _collect_routing_text(profile_summary: str, payload: GenerateRequest | None = None) -> str:
    """Collect readable text for tone and topic inference."""
    if payload is None:
        return profile_summary

    parts = [
        " ".join(payload.interests),
        payload.style,
        payload.scenario,
        payload.target_user,
        payload.input_text or "",
        profile_summary,
    ]
    return " ".join(part for part in parts if part)


def _infer_content_type(profile_summary: str, payload: GenerateRequest | None = None) -> str:
    """Infer a simple content type for tone and brief generation."""
    text = _collect_routing_text(profile_summary, payload)

    if any(keyword in text for keyword in ["宣传", "海报", "推广", "课程推荐", "课程推广", "宣传图文"]):
        return "marketing_promo"
    if any(keyword in text for keyword in ["教程", "指南", "步骤", "动作讲解", "怎么做"]):
        return "tutorial_guide"
    if any(keyword in text for keyword in ["减脂餐", "早餐", "轻食", "高蛋白", "午餐搭配", "咖啡"]):
        return "food_nutrition"
    if any(keyword in text for keyword in ["健身", "护肤", "跑步", "恢复训练", "拉伸", "久坐改善", "健康管理", "科普"]):
        return "science_popularization"
    if any(keyword in text for keyword in ["学习方法", "专注力", "备考", "高效办公", "时间管理", "职场成长", "英语学习"]):
        return "study_work"
    if any(keyword in text for keyword in ["app推荐", "工具推荐", "产品推荐", "智能手表", "健康监测", "设备"]):
        return "product_usage"
    if any(keyword in text for keyword in ["情绪管理", "焦虑", "焦虑缓解", "睡前", "呼吸练习", "放松习惯", "睡前仪式", "睡眠质量"]):
        return "emotional_healing"
    return "lifestyle"


def _infer_text_tone(
    profile_summary: str,
    payload: GenerateRequest | None = None,
) -> str:
    """Infer a practical writing tone for the post copy."""
    content_type = _infer_content_type(profile_summary, payload)
    tone_map = {
        "science_popularization": "轻科普、清晰易懂、自然不生硬、带一点生活化表达",
        "lifestyle": "自然温暖、轻松好读、像日常分享、带一点生活方式氛围",
        "study_work": "简洁实用、清楚有条理、像方法总结、但不要太硬",
        "tutorial_guide": "友好易懂、步骤感自然、像经验讲解而不是说明书",
        "emotional_healing": "温柔舒缓、陪伴感强、轻轻安抚、不夸张不说教",
        "marketing_promo": "简洁有力、清楚有吸引力、带一点行动感、但不要硬广",
        "product_usage": "清爽自然、实用友好、像真实推荐体验，不像功能清单",
        "food_nutrition": "轻盈自然、生活方式感强、像早餐或饮食经验分享",
    }
    return tone_map.get(content_type, "自然、好读、友好、适合直接发社交平台")


def _extract_topic_keywords(profile_summary: str, payload: GenerateRequest | None = None) -> list[str]:
    """Extract concise topic keywords for title and tags."""
    if payload is not None and payload.interests:
        return [item.strip() for item in payload.interests if item.strip()]

    matched = re.findall(r"[\u4e00-\u9fffA-Za-z0-9]{2,8}", profile_summary)
    filtered = [
        item
        for item in matched
        if item not in {"用户", "内容", "风格", "场景", "目标", "补充说明", "平台", "适用"}
    ]
    return filtered[:4]


def _build_content_brief(profile_summary: str, payload: GenerateRequest | None = None) -> str:
    """Convert profile information into a soft content brief."""
    topic_keywords = _extract_topic_keywords(profile_summary, payload)
    topic_text = "、".join(topic_keywords[:3]) if topic_keywords else "相关主题"
    content_type = _infer_content_type(profile_summary, payload)
    tone = _infer_text_tone(profile_summary, payload)

    if payload is None:
        return (
            f"主题方向：{topic_text}。"
            f"内容类型：{content_type}。"
            f"文案语气：{tone}。"
            "请写成真实可发布的社交平台图文文案，而不是系统说明。"
        )

    parts = [
        f"主题方向：{topic_text}。",
        f"内容类型：{content_type}。",
        f"文案语气：{tone}。",
        f"希望呈现的风格：{payload.style}。",
        f"主要使用场景：{payload.scenario}。",
        f"面向人群：{payload.target_user}。",
    ]
    if payload.input_text and payload.input_text.strip():
        parts.append(f"额外写作提示：{payload.input_text.strip()}。")
    parts.append("请把它写成真实可发的图文文案，不要写成分析说明。")
    return "".join(parts)


def _normalize_tags(tags: list[str], topic_keywords: list[str]) -> list[str]:
    """Make tags more specific and remove generic system tags."""
    normalized: list[str] = []
    for tag in tags:
        cleaned = tag.strip().strip("#").replace(" ", "")
        if not cleaned or cleaned in GENERIC_TAGS:
            continue
        if len(cleaned) < 2:
            continue
        if cleaned not in normalized:
            normalized.append(cleaned)

    for keyword in topic_keywords:
        cleaned = keyword.strip()
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)

    return normalized[:6] if normalized else topic_keywords[:4]


def _build_template_text(
    profile_summary: str,
    payload: GenerateRequest | None = None,
) -> dict[str, Any]:
    """Return safe template text when local model loading or inference fails."""
    content_type = _infer_content_type(profile_summary, payload)
    topic_keywords = _extract_topic_keywords(profile_summary, payload)
    topic_text = "、".join(topic_keywords[:2]) if topic_keywords else "日常分享"

    fallback_map = {
        "science_popularization": {
            "title": f"{topic_text}这件事，真的别只靠硬扛",
            "content": (
                f"很多时候，{topic_text}的问题不是突然出现的，而是日常习惯一点点累积出来的。"
                "比起追求一次性改变，更重要的是先把节奏放慢，找到真正适合自己的调整方式。\n\n"
                "如果你最近也有类似感受，不妨先从最小的一步开始：观察自己的状态、保留一点恢复空间、"
                "把看似普通的小习惯慢慢做稳。很多改变，都是在看起来不夸张的日常里发生的。\n\n"
                "不用一下子做得很满，先把身体和情绪照顾好，后面的节奏才会慢慢顺起来。"
            ),
            "tags": topic_keywords[:4] or ["健身恢复", "睡眠质量", "轻科普"],
        },
        "food_nutrition": {
            "title": f"{topic_text}这样吃，轻松很多",
            "content": (
                f"这类{topic_text}最怕的不是吃不饱，而是吃完很快又饿，或者吃得太重让状态变钝。"
                "想要更轻松一点，关键还是搭配自然、食材简单、吃完身体舒服。\n\n"
                "我更喜欢把选择放在高蛋白、清爽和容易坚持上，不追求花哨，重点是吃起来顺口、"
                "准备起来不费劲，也更适合忙碌日常里反复复刻。\n\n"
                "好吃、轻盈、能坚持，往往比一顿“完美饮食”更重要。"
            ),
            "tags": topic_keywords[:4] or ["高蛋白早餐", "减脂饮食", "健康生活"],
        },
        "study_work": {
            "title": f"{topic_text}，其实更讲方法感",
            "content": (
                f"很多人一提到{topic_text}，第一反应都是“再努力一点”，但真正拉开差距的，"
                "往往不是强撑，而是方法有没有更顺手。\n\n"
                "把注意力放在更清楚的节奏、更稳定的步骤和更容易坚持的安排上，"
                "比一味堆时间更有效。方法对了，状态会轻松很多，执行感也会明显提升。\n\n"
                "先把能重复做到的小动作做好，效率和反馈通常都会慢慢跟上。"
            ),
            "tags": topic_keywords[:4] or ["学习方法", "专注力", "效率提升"],
        },
        "emotional_healing": {
            "title": f"最近的{topic_text}，想慢慢放轻一点",
            "content": (
                f"如果最近总觉得被{topic_text}拖着走，先别急着逼自己马上恢复。"
                "很多时候，我们真正需要的不是再多一点道理，而是一点点能让身体和情绪安静下来的空间。\n\n"
                "把节奏放慢一点，先照顾呼吸、睡前状态和那些最容易被忽略的小感受，"
                "反而更容易慢慢找回稳定感。\n\n"
                "不用一下子变得很好，先允许自己慢一点，也是一种很重要的修复。"
            ),
            "tags": topic_keywords[:4] or ["情绪管理", "睡眠放松", "自我关怀"],
        },
        "marketing_promo": {
            "title": f"{topic_text}，这次想讲得更直接一点",
            "content": (
                f"如果你最近也在关注{topic_text}，也许比起空泛口号，更需要的是一套真正能看懂、"
                "能用上、也愿意继续了解下去的内容。\n\n"
                "这次想把重点讲清楚：方向是什么、为什么值得花时间了解、能带来什么变化。"
                "不夸张，不堆信息，只把真正有用的部分留给你。\n\n"
                "如果你也想更稳一点地往前走，这类内容也许刚好能给你一个不错的起点。"
            ),
            "tags": topic_keywords[:4] or ["课程推荐", "职场成长", "技能提升"],
        },
    }

    result = fallback_map.get(
        content_type,
        {
            "title": f"{topic_text}，慢慢来会更顺",
            "content": (
                f"关于{topic_text}，我越来越觉得，真正有用的不是一下子做很多，"
                "而是找到适合自己的节奏，把重要的小事慢慢做稳。\n\n"
                "当内容回到真实场景里，很多问题都会变得没那么复杂。比起追求完美，"
                "更值得做的是保留一点轻松感、自然感和能长期坚持的空间。\n\n"
                "先从最贴近日常的那一步开始，很多变化就会一点点发生。"
            ),
            "tags": topic_keywords[:4] or ["生活方式", "经验分享", "日常灵感"],
        },
    )
    return {
        "title": result["title"],
        "content": result["content"],
        "tags": _normalize_tags(result["tags"], topic_keywords),
    }


def _build_text_prompt(profile_summary: str, payload: GenerateRequest | None = None) -> str:
    """Build a concise prompt for publishable social-media copy."""
    content_type = _infer_content_type(profile_summary, payload)
    tone = _infer_text_tone(profile_summary, payload)
    brief = _build_content_brief(profile_summary, payload)

    return (
        "你是一名中文社交平台文案写作者，请直接输出可发布的图文文案。\n"
        "不要分析系统，不要解释生成过程，不要出现“该用户关注”“目标用户是”“后续可以”等说明口吻。\n"
        f"内容类型参考：{content_type}。\n"
        f"语气要求：{tone}。\n"
        "要求：标题 12 到 24 个中文字符；正文 2 到 4 段，表达自然、有信息量；标签 3 到 6 个，具体且贴近主题。\n"
        "请严格按照以下格式输出，不要添加额外说明：\n"
        "Title: 标题\n"
        "Content: 正文\n"
        "Tags: 标签1, 标签2, 标签3\n\n"
        f"内容 brief：{brief}\n"
    )


def _get_content_value(lines: list[str], start_index: int, first_value: str) -> tuple[str, int]:
    """Collect multi-line content until the next known prefix."""
    values = [first_value] if first_value else []
    index = start_index + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            values.append("")
            index += 1
            continue
        if any(stripped.startswith(prefix) for prefix in ("Title:", "Content:", "Tags:")):
            break
        values.append(stripped)
        index += 1
    content = "\n".join(item for item in values if item != "").strip()
    return content, index - 1


def _extract_after_prefix(text: str, prefix: str) -> str:
    """Extract text after a known prefix such as Title: or Content:."""
    if not text.lower().startswith(prefix.lower()):
        return ""
    return text.split(":", 1)[1].strip() if ":" in text else ""


def _normalize_title(title: str, topic_keywords: list[str]) -> str:
    """Trim robotic wording and keep the title concise."""
    cleaned = title.strip("：: \n\t")
    cleaned = re.sub(r"(该用户|目标用户|适用于平台|用户画像|内容生成|图文内容建议)", "", cleaned)
    cleaned = re.sub(r"\s+", "", cleaned)
    if len(cleaned) > 24:
        cleaned = cleaned[:24]
    if len(cleaned) < 8 and topic_keywords:
        cleaned = f"{'、'.join(topic_keywords[:2])}这样做更轻松"[:24]
    return cleaned or f"{'、'.join(topic_keywords[:2])}这样做更顺手"[:24]


def _normalize_content(content: str) -> str:
    """Remove backend-like wording and smooth the content."""
    cleaned = content.strip()
    banned_phrases = [
        "该用户关注",
        "目标用户是",
        "适用于平台",
        "当前结果",
        "后续可以",
        "用户画像",
        "本地模型",
        "后端",
        "系统生成",
        "平台适用",
    ]
    for phrase in banned_phrases:
        cleaned = cleaned.replace(phrase, "")

    cleaned = cleaned.replace("适用于", "更适合")
    cleaned = re.sub(r"[ \t]+", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"([。！？])([^\n])", r"\1\n\2", cleaned)
    paragraphs = [paragraph.strip() for paragraph in cleaned.split("\n") if paragraph.strip()]
    if len(paragraphs) > 4:
        paragraphs = paragraphs[:4]
    return "\n\n".join(paragraphs)


def _postprocess_generated_text(
    result: dict[str, Any],
    topic_keywords: list[str],
) -> dict[str, Any]:
    """Lightweight post-processing for title/content/tags."""
    title = _normalize_title(str(result.get("title", "")), topic_keywords)
    content = _normalize_content(str(result.get("content", "")))
    tags = _normalize_tags(list(result.get("tags", [])), topic_keywords)

    return {
        "title": title,
        "content": content,
        "tags": tags[:6],
    }


@lru_cache(maxsize=1)
def _get_text_generator():
    """Load the local text generation pipeline once and reuse it."""
    try:
        import torch
        from transformers import pipeline

        device = 0 if torch.cuda.is_available() else -1
        return pipeline(
            task="text-generation",
            model=TEXT_MODEL_NAME,
            device=device,
        )
    except Exception:
        try:
            import torch
            from transformers import pipeline

            device = 0 if torch.cuda.is_available() else -1
            return pipeline(
                task="text-generation",
                model=TEXT_MODEL_FALLBACK,
                device=device,
            )
        except Exception:
            return None


def _parse_generated_result(
    raw_text: str,
    profile_summary: str,
    payload: GenerateRequest | None = None,
) -> dict[str, Any]:
    """Parse model output and fall back to the template when fields are missing."""
    topic_keywords = _extract_topic_keywords(profile_summary, payload)
    result = _build_template_text(profile_summary, payload)

    lines = raw_text.splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue

        title = _extract_after_prefix(stripped, "Title:")
        if title:
            result["title"] = title
            index += 1
            continue

        content = _extract_after_prefix(stripped, "Content:")
        if content or stripped.startswith("Content:"):
            parsed_content, end_index = _get_content_value(lines, index, content)
            if parsed_content:
                result["content"] = parsed_content
            index = end_index + 1
            continue

        tags_text = _extract_after_prefix(stripped, "Tags:")
        if tags_text:
            parsed_tags = [
                tag.strip()
                for tag in re.split(r"[，,、#\s]+", tags_text)
                if tag.strip()
            ]
            if parsed_tags:
                result["tags"] = parsed_tags[:6]
            index += 1
            continue

        index += 1

    return _postprocess_generated_text(result, topic_keywords)


def generate_text(
    profile_summary: str,
    payload: GenerateRequest | None = None,
) -> dict[str, Any]:
    """Generate title, content, and tags with a local Qwen model or fallback."""
    generator = _get_text_generator()
    if generator is None:
        _log("Text generation failed, using fallback template")
        return _build_template_text(profile_summary, payload)

    prompt = _build_text_prompt(profile_summary, payload)
    _log("Text generation started")

    try:
        outputs = generator(
            prompt,
            max_new_tokens=MAX_OUTPUT_TOKENS,
            do_sample=True,
            temperature=0.85,
            top_p=0.92,
            repetition_penalty=1.12,
        )
        generated_text = outputs[0]["generated_text"]
        new_text = (
            generated_text[len(prompt) :].strip()
            if generated_text.startswith(prompt)
            else generated_text.strip()
        )
        result = _parse_generated_result(new_text, profile_summary, payload)
        _log("Text generation succeeded")
        return result
    except Exception:
        _log("Text generation failed, using fallback template")
        return _build_template_text(profile_summary, payload)


def generate_mock_text(payload: GenerateRequest) -> tuple[str, str, list[str]]:
    """Backward-compatible wrapper for older imports."""
    profile_parts = [
        f"该用户关注{'、'.join(payload.interests)}。",
        f"偏好{payload.style}内容风格。",
        f"适用于{payload.scenario}场景。",
        f"目标用户是{payload.target_user}。",
    ]
    if payload.input_text and payload.input_text.strip():
        profile_parts.append(f"补充说明：{payload.input_text.strip()}")

    result = generate_text("".join(profile_parts), payload=payload)
    return result["title"], result["content"], result["tags"]
