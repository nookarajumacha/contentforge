"""
Calendar routes
GET  /api/calendar          → get 30-day content plan
POST /api/calendar/generate → regenerate calendar with AI
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from utils import get_current_user, call_claude

router = APIRouter()

DEFAULT_PLAN = {
    1:  {"platform": "twitter",   "label": "Tweet Thread",        "color": "#1DA1F2"},
    2:  {"platform": "linkedin",  "label": "Industry Post",        "color": "#0A66C2"},
    4:  {"platform": "blog",      "label": "Blog Article",         "color": "#00e5b0"},
    5:  {"platform": "email",     "label": "Newsletter",           "color": "#f5c842"},
    7:  {"platform": "instagram", "label": "Story Post",           "color": "#E1306C"},
    9:  {"platform": "twitter",   "label": "Poll + Thread",        "color": "#1DA1F2"},
    11: {"platform": "linkedin",  "label": "Case Study",           "color": "#0A66C2"},
    14: {"platform": "youtube",   "label": "Video Script",         "color": "#FF0000"},
    16: {"platform": "blog",      "label": "How-To Guide",         "color": "#00e5b0"},
    18: {"platform": "email",     "label": "Campaign Email",       "color": "#f5c842"},
    21: {"platform": "twitter",   "label": "Thread Series",        "color": "#1DA1F2"},
    23: {"platform": "instagram", "label": "Carousel Post",        "color": "#E1306C"},
    25: {"platform": "linkedin",  "label": "Thought Leadership",   "color": "#0A66C2"},
    28: {"platform": "blog",      "label": "Monthly Roundup",      "color": "#00e5b0"},
    30: {"platform": "email",     "label": "Monthly Digest",       "color": "#f5c842"},
}

class CalendarRequest(BaseModel):
    topic: Optional[str] = "content marketing"
    industry: Optional[str] = "technology"

@router.get("")
def get_calendar(user: dict = Depends(get_current_user)):
    return {"plan": DEFAULT_PLAN}

@router.post("/generate")
def regenerate_calendar(body: CalendarRequest, user: dict = Depends(get_current_user)):
    """Use Claude to generate a custom 30-day content calendar."""
    prompt = f"""Create a 30-day content calendar for a {body.industry} brand focused on {body.topic}.

Select 15 key posting days and assign a platform and content type for each.
Respond ONLY with a JSON object like:
{{
  "1":  {{"platform": "twitter",   "label": "Thread on AI trends",  "color": "#1DA1F2"}},
  "3":  {{"platform": "linkedin",  "label": "Industry analysis",     "color": "#0A66C2"}},
  ...
}}

Use platforms: twitter (#1DA1F2), linkedin (#0A66C2), instagram (#E1306C), email (#f5c842), blog (#00e5b0), youtube (#FF0000)
Choose realistic, varied content types."""

    result = call_claude(prompt, max_tokens=800)
    if result:
        try:
            import json, re
            # strip markdown fences if present
            clean = re.sub(r'```json?', '', result).strip('`').strip()
            plan = json.loads(clean)
            # convert string keys to int
            plan = {int(k): v for k, v in plan.items()}
            return {"plan": plan, "regenerated": True}
        except Exception:
            pass

    return {"plan": DEFAULT_PLAN, "regenerated": False}
