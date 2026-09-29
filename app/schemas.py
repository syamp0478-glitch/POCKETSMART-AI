from typing import Literal
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterInput(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class HomeInput(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    rooms: list[str] = Field(min_length=1, max_length=8)
    style: str = Field(default="Modern", max_length=80)
    priorities: str = Field(default="", max_length=500)


class PartyInput(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    event_type: str = Field(min_length=2, max_length=80)
    guests: int = Field(gt=0, le=5000)
    venue: str = Field(default="Flexible", max_length=100)
    city: str = Field(default="", max_length=100)
    preferences: str = Field(default="", max_length=500)


class JewelryInput(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="Classic", max_length=100)
    outfit_colors: str = Field(default="", max_length=200)
    notes: str = Field(default="", max_length=500)


class Recommendation(BaseModel):
    title: str
    category: str
    estimated_price: float
    quantity: int = 1
    platform: str
    url: str
    reason: str


class PlanResponse(BaseModel):
    planner: Literal["home", "party", "jewelry"]
    currency: str
    budget: float
    estimated_total: float
    remaining: float
    summary: str
    ai_enabled: bool
    allocation: list[dict]
    recommendations: list[Recommendation]
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
