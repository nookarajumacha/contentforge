"""
History routes
GET    /api/history           → list all content history
POST   /api/history           → add item to history
PUT    /api/history/{id}      → update (edit content, change status)
DELETE /api/history/{id}      → delete item
DELETE /api/history           → clear all history
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from utils import get_current_user

router = APIRouter()

_history: List[dict] = []

class HistoryItem(BaseModel):
    id: str
    platform: str
    platLabel: str
    platEmoji: str
    platColor: str
    topic: str
    tone: str
    content: str
    scores: Dict[str, Any]
    wordCount: int
    compliance: Optional[Dict[str, Any]] = {}
    xai: Optional[Dict[str, Any]] = {}
    status: Optional[str] = "pending"
    timestamp: Optional[str] = ""

class UpdateRequest(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None

@router.get("")
def list_history(platform: Optional[str] = None, user: dict = Depends(get_current_user)):
    items = _history
    if platform and platform != "all":
        items = [i for i in items if i.get("platform") == platform]
    return {"items": items, "total": len(_history)}

@router.post("")
def add_to_history(item: HistoryItem, user: dict = Depends(get_current_user)):
    _history.insert(0, item.dict())
    return {"success": True}

@router.post("/bulk")
def add_bulk_to_history(items: List[HistoryItem], user: dict = Depends(get_current_user)):
    for item in items:
        _history.insert(0, item.dict())
    return {"success": True, "count": len(items)}

@router.put("/{item_id}")
def update_history_item(item_id: str, body: UpdateRequest, user: dict = Depends(get_current_user)):
    for item in _history:
        if str(item["id"]) == str(item_id):
            if body.content is not None:
                item["content"] = body.content
                item["wordCount"] = len(body.content.split())
            if body.status is not None:
                item["status"] = body.status
            return {"success": True, "item": item}
    raise HTTPException(404, "Item not found.")

@router.delete("")
def clear_history(user: dict = Depends(get_current_user)):
    global _history
    _history = []
    return {"success": True}

@router.delete("/{item_id}")
def delete_history_item(item_id: str, user: dict = Depends(get_current_user)):
    global _history
    _history = [i for i in _history if str(i["id"]) != str(item_id)]
    return {"success": True}
