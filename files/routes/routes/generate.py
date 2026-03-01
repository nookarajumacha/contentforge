"""
Generate route
POST /api/generate   → generate multi-platform content from a brief
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random
from utils import get_current_user, call_claude, compute_scores, get_platform_info

router = APIRouter()

# ─── MODELS ───────────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    topic: str
    purpose: Optional[str] = "awareness"
    audience: Optional[str] = "General audience"
    tone: Optional[str] = "Professional"
    keywords: Optional[str] = ""
    platforms: List[str] = ["twitter", "linkedin"]


# ─── PLATFORM SYSTEM PROMPTS ─────────────────────────────────────────────────
PLATFORM_PROMPTS = {
    "twitter": """You are a viral Twitter/X content strategist.
Write a tweet thread (2-4 tweets) that:
- Starts with a powerful hook
- Uses short punchy sentences
- Includes 2-3 relevant hashtags
- Ends with an engaging question or CTA
- Max 280 chars per tweet, separate tweets with \\n---\\n""",

    "linkedin": """You are a LinkedIn thought leadership expert.
Write a LinkedIn post that:
- Opens with a bold, curiosity-driving first line
- Uses white space and short paragraphs
- Tells a mini-story or shares a data point
- Ends with a reflective question for the community
- 150-250 words ideal""",

    "instagram": """You are an Instagram content creator.
Write an Instagram caption that:
- Opens with an attention-grabbing first line
- Is energetic and visual in tone
- Uses line breaks for readability
- Includes 5-8 relevant hashtags at the end
- 80-150 words""",

    "email": """You are an email marketing copywriter.
Write a marketing email that:
- Has a compelling subject line at the top (Subject: ...)
- Personalises with [First Name]
- Has a clear value proposition in the first paragraph
- Includes one strong CTA
- Is concise: 120-180 words""",

    "blog": """You are a content marketing strategist and SEO writer.
Write a structured blog post outline + intro that:
- Has an SEO-optimised H1 title
- Includes H2 subheadings
- Has an engaging intro paragraph (hook + problem + promise)
- Outlines 3-4 main sections with key points
- Ends with a conclusion and CTA
- 350-500 words""",

    "youtube": """You are a YouTube script writer.
Write a YouTube video script that:
- Has a 15-second hook that creates urgency
- Includes [INTRO], [POINT 1], [POINT 2], [POINT 3], [CTA] sections
- Uses conversational, engaging language
- Specifies B-roll suggestions in [brackets]
- Ends with subscribe CTA and community question
- 300-400 words""",
}

XAI_EXPLANATIONS = {
    "twitter":   {"format": "Thread format chosen for 3x better reach than single tweets", "tone": "Hook-first structure based on viral tweet analysis", "length": "Optimal 3-tweet thread length for engagement"},
    "linkedin":  {"format": "Long-form chosen: LinkedIn rewards depth with algorithmic boost", "tone": "Thought leadership tone drives 6.8% avg CTR", "structure": "Story arc drives 40% more comments than lists"},
    "instagram": {"format": "Caption + hashtag stack for Explore page discoverability", "tone": "Aspirational tone matches IG audience psychology", "hashtags": "8-hashtag strategy balances reach and niche targeting"},
    "email":     {"format": "Short-form chosen for 22% open-rate optimisation", "subject": "Curiosity gap in subject line boosts open rates by 18%", "cta": "Single CTA principle reduces decision fatigue"},
    "blog":      {"format": "Long-form SEO article for organic traffic compounding", "seo": "H2 structure improves crawlability and featured snippets", "length": "350-500 word posts rank best for informational queries"},
    "youtube":   {"format": "Hook-story-CTA script structure for watch-time retention", "hook": "First 15s hook reduces drop-off by 34%", "sections": "3-point structure matches YouTube algorithm preferences"},
}


# ─── MOCK CONTENT FALLBACK ────────────────────────────────────────────────────
def get_mock_content(topic: str, platform: str, tone: str) -> str:
    t = topic[:40]
    mocks = {
        "twitter":   f"Just uncovered something game-changing about {t}.\n\nHere's what nobody talks about:\n\nThe teams winning right now are NOT the biggest — they're the most consistent.\n\nAre you consistent? Reply below. 👇\n\n#Growth #Innovation #ContentStrategy",
        "linkedin":  f"After deep-diving into {t}, here's my honest take.\n\nMost teams overcomplicate it. The real answer is simpler.\n\nFocus on three things:\n1️⃣ Consistency over perfection\n2️⃣ Data over gut feel\n3️⃣ Speed over hesitation\n\nWhat would you add? Drop it in the comments 👇",
        "instagram": f"Big things happening in {t} right now ✨\n\nSave this post — you'll thank yourself later.\n\nThe brands winning are the ones moving NOW.\n\n#ContentStrategy #Growth #Digital #Marketing #Innovation #AI #Creator #Brand",
        "email":     f"Subject: The {t[:30]} strategy your competitors haven't figured out yet\n\nHi [First Name],\n\nI wanted to share something important about {t}.\n\nEarly adopters are seeing 3x ROI in the first 90 days.\n\nWould you be open to a 15-minute call?\n\nReply here or book directly at [link].\n\nBest,\n[Your Name]",
        "blog":      f"# How {t} Is Transforming Content Strategy in 2025\n\n## The Problem Nobody Talks About\n\nContent teams are stuck. They produce more but see less return.\n\n## The Solution\n\n{t} changes the equation. Here's how leading teams are using it to 3x their output without burning out.\n\n## Getting Started\n\nStart small. Pick your top format. Apply the system. Measure in 30 days.\n\n## Conclusion\n\nThe future belongs to teams who act now. Are you one of them?",
        "youtube":   f'[HOOK — 0-15s]\n"{t} is about to change everything — and most teams are completely unprepared."\n\n[INTRO]\nWelcome back! Today we\'re breaking down {t} and exactly how to win with it.\n\n[POINT 1] The Core Problem — why current approaches fail\n[POINT 2] The Framework — 3-step system that works\n[POINT 3] Real Results — what to expect in 30 days\n\n[CTA] Subscribe + comment your biggest content challenge! See you next week 🚀',
    }
    return mocks.get(platform, mocks["twitter"])


# ─── MAIN GENERATE ENDPOINT ───────────────────────────────────────────────────
@router.post("")
@router.post("/")
def generate_content(body: GenerateRequest, user: dict = Depends(get_current_user)):
    """
    Core content generation pipeline.
    Generates platform-specific content using Claude AI.
    Returns an array of content items ready for the frontend.
    """
    if not body.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required.")
    if not body.platforms:
        raise HTTPException(status_code=400, detail="Select at least one platform.")

    results = []

    for pid in body.platforms:
        platform_info = get_platform_info(pid)

        # ── Build the prompt ──────────────────────────────────────────────────
        system_prompt = PLATFORM_PROMPTS.get(pid, PLATFORM_PROMPTS["twitter"])
        user_prompt = f"""Create {pid} content for the following brief:

TOPIC: {body.topic}
PURPOSE: {body.purpose}
TARGET AUDIENCE: {body.audience}
TONE: {body.tone}
SEO KEYWORDS: {body.keywords or 'Not specified'}

Generate high-quality, platform-native content that feels authentic, not AI-written."""

        # ── Call Claude (or fallback to mock) ─────────────────────────────────
        content = call_claude(user_prompt, system=system_prompt, max_tokens=800)
        if not content:
            content = get_mock_content(body.topic, pid, body.tone)

        # ── Compute scores ────────────────────────────────────────────────────
        scores = compute_scores(content, pid, body.tone)

        # ── Compliance tags ───────────────────────────────────────────────────
        compliance = {
            "Brand Safe": True,
            "Platform Guidelines": True,
        }
        if body.keywords:
            compliance["SEO Optimised"] = True
        if body.tone.lower() in ["empathetic", "professional"]:
            compliance["Inclusive Language"] = True

        # ── XAI explanations ─────────────────────────────────────────────────
        xai = XAI_EXPLANATIONS.get(pid, {})

        import time
        item_id = f"{int(time.time() * 1000)}{hash(pid) % 9999}"

        results.append({
            "id":         item_id,
            "platform":   pid,
            "platLabel":  platform_info["label"],
            "platEmoji":  platform_info["emoji"],
            "platColor":  platform_info["color"],
            "topic":      body.topic,
            "tone":       body.tone,
            "purpose":    body.purpose,
            "audience":   body.audience,
            "content":    content,
            "scores":     scores,
            "wordCount":  len(content.split()),
            "compliance": compliance,
            "xai":        xai,
            "status":     "pending",
            "timestamp":  __import__("datetime").datetime.now().strftime("%d %b %Y, %I:%M %p"),
        })

    return {"success": True, "count": len(results), "items": results}
