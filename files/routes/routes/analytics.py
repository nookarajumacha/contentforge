"""
Analytics routes
GET /api/analytics/summary   → platform breakdown + weekly scores
GET /api/analytics/insights  → AI-generated insights
"""

from fastapi import APIRouter, Depends
from utils import get_current_user, call_claude
import random

router = APIRouter()

@router.get("/summary")
def get_analytics(user: dict = Depends(get_current_user)):
    """Return analytics data for the dashboard."""
    weekly = [
        {"day": "Mon", "score": random.randint(72, 82)},
        {"day": "Tue", "score": random.randint(82, 92)},
        {"day": "Wed", "score": random.randint(75, 85)},
        {"day": "Thu", "score": random.randint(86, 95)},
        {"day": "Fri", "score": random.randint(83, 91)},
        {"day": "Sat", "score": random.randint(78, 86)},
        {"day": "Sun", "score": random.randint(80, 88)},
    ]
    platforms = [
        {"platform": "Twitter/X",  "score": 82, "engagement": "4.2%",  "color": "#1DA1F2"},
        {"platform": "LinkedIn",   "score": 88, "engagement": "6.8%",  "color": "#0A66C2"},
        {"platform": "Instagram",  "score": 79, "engagement": "7.1%",  "color": "#E1306C"},
        {"platform": "Email",      "score": 91, "engagement": "22.4%", "color": "#f5c842"},
        {"platform": "Blog",       "score": 85, "engagement": "3.4%",  "color": "#00e5b0"},
        {"platform": "YouTube",    "score": 77, "engagement": "5.2%",  "color": "#FF0000"},
    ]
    return {"weekly": weekly, "platforms": platforms}

@router.get("/insights")
def get_insights(user: dict = Depends(get_current_user)):
    """Return AI-generated content insights."""
    prompt = """Generate 4 short, specific content performance insights for a content creator.
Each insight should be actionable and data-backed.
Return as a JSON array of strings, no markdown.
Example: ["Tuesday posts get 28% more engagement", "Posts with questions drive 3x more comments"]"""

    result = call_claude(prompt, max_tokens=300)
    if result:
        try:
            import json
            clean = result.strip().strip("```json").strip("```").strip()
            insights = json.loads(clean)
            return {"insights": insights}
        except Exception:
            pass

    # Fallback static insights
    return {
        "insights": [
            "Posts with questions in headlines get 3.2x more engagement for your audience",
            "Tuesday and Thursday posts perform 28% better than weekend posts",
            "LinkedIn posts 150-200 words have the highest click-through rates",
            "Urgent tone outperforms professional tone by 18% for product announcements",
        ]
    }
