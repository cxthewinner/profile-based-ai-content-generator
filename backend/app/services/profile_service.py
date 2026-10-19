from app.schemas.generate import GenerateRequest


def build_profile_summary(payload: GenerateRequest) -> str:
    """Create a simple rule-based profile summary in Chinese."""
    interests_text = "、".join(payload.interests)
    parts = [
        f"该用户关注{interests_text}。",
        f"偏好{payload.style}内容风格。",
        f"适用于{payload.scenario}场景。",
        f"目标用户是{payload.target_user}。",
    ]

    if payload.input_text and payload.input_text.strip():
        parts.append(f"补充说明：{payload.input_text.strip()}")

    return "".join(parts)
