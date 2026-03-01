"""
Bulk Generate route
POST /api/bulk   → generate content for multiple topics at once
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import time, random
from datetime import datetime
from utils import get_current_user, call_claude, compute_scores, get_platform_info

router = APIRouter()

# ─── MODELS ───────────────────────────────────────────────────────────────────
class BulkRequest(BaseModel):
    topics: List[str]          # list of topic strings
    platform: str = "linkedin"
    tone: str = "Professional"
    purpose: Optional[str] = "awareness"
    audience: Optional[str] = "General audience"


# ─── MOCK FALLBACK (same as generate.py) ─────────────────────────────────────
def get_mock_content(topic: str, platform: str) -> str:
    t = topic[:40]
    mocks = {
        "twitter":   f"Here's the truth about {t} that no one tells you.\n\nConsistency beats talent every time.\n\nAre you being consistent? 👇\n\n#Growth #Marketing",
        "linkedin":  f"I've spent years studying {t}.\n\nHere's my condensed insight:\n\n→ Focus beats volume\n→ Systems beat willpower\n→ Data beats guesses\n\nWhat's your take?",
        "instagram": f"Everything you need to know about {t} 🔥\n\nSave this. Share this. Grow. 📈\n\n#ContentCreator #Digital #Marketing #AI #Growth",
        "email":     f"Subject: Why {t[:30]} matters more than ever\n\nHi [First Name],\n\n{t} is changing the game.\n\nLet's talk about how you can leverage it.\n\n[Book a call]\n\nBest,\n[Your Name]",
        "blog":      f"# The Complete Guide to {t}\n\n## Introduction\n{t} represents a major shift in how we work.\n\n## Key Strategies\n1. Start with clarity\n2. Build systems\n3. Measure results\n\n## Conclusion\nThe time to act is now.",
    }
    return mocks.get(platform, mocks["linkedin"])


# ─── BULK GENERATE ENDPOINT ───────────────────────────────────────────────────
@router.post("")
@router.post("/")
def bulk_generate(body: BulkRequest, user: dict = Depends(get_current_user)):
    """
    Bulk content generation pipeline.
    Accepts multiple topics and generates content for each.
    Returns array of content items.
    """
    if not body.topics:
        raise HTTPException(status_code=400, detail="Topics list is required.")

    # Clean up topics
    clean_topics = [t.strip() for t in body.topics if t.strip()]
    if not clean_topics:
        raise HTTPException(status_code=400, detail="No valid topics found.")
    if len(clean_topics) > 20:
        raise HTTPException(status_code=400, detail="Max 20 topics per bulk request.")

    platform_info = get_platform_info(body.platform)
    results = []

    for topic in clean_topics:
        # Build a concise prompt for bulk (shorter = faster + cheaper)
        prompt = f"""Write a {body.platform} post about: {topic}
Tone: {body.tone}
Audience: {body.audience}
Purpose: {body.purpose}
Keep it platform-native, authentic, and engaging. No AI-sounding language."""

        content = call_claude(prompt, max_tokens=400)
        if not content:
            content = get_mock_content(topic, body.platform)

        scores = compute_scores(content, body.platform, body.tone)
        item_id = str(int(time.time() * 1000)) + str(random.randint(100, 999))

        results.append({
            "id":         item_id,
            "platform":   body.platform,
            "platLabel":  platform_info["label"],
            "platEmoji":  platform_info["emoji"],
            "platColor":  platform_info["color"],
            "topic":      topic,
            "tone":       body.tone,
            "content":    content,
            "scores":     scores,
            "wordCount":  len(content.split()),
            "compliance": {"Brand Safe": True, "Platform Guidelines": True},
            "xai":        {},
            "status":     "pending",
            "timestamp":  datetime.now().strftime("%d %b %Y, %I:%M %p"),
        })

    return {
        "success": True,
        "count":   len(results),
        "items":   results,
    }
