import json
from collections import defaultdict
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from app.database import connect
from app.schemas import HomeInput, PartyInput, JewelryInput, PlanResponse
from app.security import get_current_user
from app.services.catalog import recommendations
from app.services.gemini import generate_advice

router = APIRouter(tags=["planners"])


def make_plan(planner: str, payload: dict, user: dict, image: bytes | None = None, image_mime: str | None = None) -> dict:
    budget = float(payload["budget"])
    products = recommendations(planner, budget, int(payload.get("guests", 1)))
    total = round(sum(item["estimated_price"] * item["quantity"] for item in products), 2)
    allocations = defaultdict(float)
    for item in products:
        allocations[item["category"]] += item["estimated_price"] * item["quantity"]
    allocation = [{"category": name, "amount": round(amount, 2), "percent": round(amount / budget * 100, 1)}
                  for name, amount in allocations.items()]
    advice = generate_advice(planner, payload, image, image_mime)
    ai_enabled = bool(advice)
    if not advice:
        advice = (f"A starter {planner} plan with {len(products)} options is estimated at "
                  f"{payload['currency']} {total:,.0f}, leaving {payload['currency']} {max(0, budget-total):,.0f} "
                  "for delivery, taxes, or personal adjustments. Marketplace prices and availability can change; "
                  "confirm details with the seller before purchasing.")
    result = {"planner": planner, "currency": payload["currency"].upper(), "budget": budget,
              "estimated_total": total, "remaining": round(max(0, budget-total), 2), "summary": advice,
              "ai_enabled": ai_enabled, "allocation": allocation,
              "recommendations": products, "created_at": datetime.now(timezone.utc).isoformat()}
    with connect() as db:
        db.execute("INSERT INTO recommendations(user_id, planner, request_json, result_json) VALUES (?, ?, ?, ?)",
                   (user["id"], planner, json.dumps(payload), json.dumps(result)))
    return result


@router.post("/generate-home", response_model=PlanResponse)
def generate_home(payload: HomeInput, user: dict = Depends(get_current_user)):
    return make_plan("home", payload.model_dump(), user)


@router.post("/generate-party", response_model=PlanResponse)
def generate_party(payload: PartyInput, user: dict = Depends(get_current_user)):
    return make_plan("party", payload.model_dump(), user)


@router.post("/generate-jewelry", response_model=PlanResponse)
async def generate_jewelry(
    budget: float = Form(gt=0, le=10_000_000), currency: str = Form(default="INR"),
    occasion: str = Form(min_length=2, max_length=100), style: str = Form(default="Classic"),
    outfit_colors: str = Form(default=""), notes: str = Form(default=""),
    image: UploadFile | None = File(default=None), user: dict = Depends(get_current_user),
):
    payload = JewelryInput(budget=budget, currency=currency, occasion=occasion, style=style,
                           outfit_colors=outfit_colors, notes=notes).model_dump()
    image_bytes = None
    mime = None
    if image and image.filename:
        mime = image.content_type or ""
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            raise HTTPException(status_code=400, detail="Upload a JPG, PNG, or WEBP outfit image")
        image_bytes = await image.read(settings.max_image_mb * 1024 * 1024 + 1)
        if len(image_bytes) > settings.max_image_mb * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"Image must be {settings.max_image_mb} MB or smaller")
    return make_plan("jewelry", payload, user, image_bytes, mime)
