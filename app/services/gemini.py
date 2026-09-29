import json
from google import genai
from google.genai import types
from app.config import settings


def generate_advice(planner: str, details: dict, image_bytes: bytes | None = None, image_mime: str | None = None) -> str | None:
    if not settings.gemini_api_key:
        return None
    prompt = (
        "You are PocketSmart, a careful budget planning assistant. Give a concise, practical 2-3 sentence note "
        "for this plan. Respect the stated budget, never claim live inventory or verified prices, and describe all "
        "catalog prices as estimates. If an image is included, discuss only visible colors/style, not identity. "
        f"Planner: {planner}. Input: {json.dumps(details, ensure_ascii=False)}"
    )
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        content: list = [prompt]
        if image_bytes:
            content.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime or "image/jpeg"))
        response = client.models.generate_content(model=settings.gemini_model, contents=content)
        return (response.text or "").strip() or None
    except Exception:
        # A remote AI outage must not prevent deterministic budget guidance from working.
        return None
