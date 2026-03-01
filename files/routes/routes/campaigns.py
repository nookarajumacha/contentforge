"""
Campaigns routes
GET/POST/DELETE /api/campaigns
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils import get_current_user, get_platform_info
from datetime import date

router = APIRouter()

_campaigns: List[dict] = []

class CampaignRequest(BaseModel):
    name: str
    goal: Optional[str] = ""
    platform: Optional[str] = "all"
    start: Optional[str] = ""
    end: Optional[str] = ""

@router.get("")
def list_campaigns(user: dict = Depends(get_current_user)):
    return {"campaigns": _campaigns}

@router.post("")
def create_campaign(body: CampaignRequest, user: dict = Depends(get_current_user)):
    if not body.name.strip():
        raise HTTPException(400, "Campaign name is required.")
    pi = get_platform_info(body.platform) if body.platform != "all" else {"label": "All Platforms", "color": "#7c5cff", "emoji": "🌐"}
    c = {
        "id": len(_campaigns) + 1,
        "name": body.name,
        "goal": body.goal,
        "platform": body.platform,
        "platLabel": pi["label"],
        "platColor": pi["color"],
        "platEmoji": pi["emoji"],
        "start": body.start,
        "end": body.end,
        "createdAt": str(date.today()),
        "status": "active",
        "contentCount": 0,
    }
    _campaigns.append(c)
    return {"success": True, "campaign": c}

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, user: dict = Depends(get_current_user)):
    global _campaigns
    _campaigns = [c for c in _campaigns if c["id"] != campaign_id]
    return {"success": True}
