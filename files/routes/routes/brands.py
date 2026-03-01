"""
Brands routes
GET/POST/DELETE /api/brands
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils import get_current_user
from datetime import date

router = APIRouter()

# In-memory store (per-process — fine for hackathon)
_brands: List[dict] = []

class BrandRequest(BaseModel):
    name: str
    tagline: Optional[str] = ""
    audience: Optional[str] = ""
    language: Optional[str] = "en"
    tones: Optional[List[str]] = []
    guidelines: Optional[str] = ""

@router.get("")
def list_brands(user: dict = Depends(get_current_user)):
    return {"brands": _brands}

@router.post("")
def create_brand(body: BrandRequest, user: dict = Depends(get_current_user)):
    if not body.name.strip():
        raise HTTPException(400, "Brand name is required.")
    brand = {
        "id": len(_brands) + 1,
        "name": body.name,
        "tagline": body.tagline,
        "audience": body.audience,
        "language": body.language,
        "tones": body.tones,
        "guidelines": body.guidelines,
        "createdAt": str(date.today()),
        "status": "active",
    }
    _brands.append(brand)
    return {"success": True, "brand": brand}

@router.delete("/{brand_id}")
def delete_brand(brand_id: int, user: dict = Depends(get_current_user)):
    global _brands
    _brands = [b for b in _brands if b["id"] != brand_id]
    return {"success": True}
