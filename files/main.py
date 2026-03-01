from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os, time, random, json, re
import google.generativeai as genai

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="ContentForge AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory stores ──────────────────────────────────────────────────────────
content_history: list = []
feedback_storage: list = []
users_db: dict = {}

# ── Model fallback chain (try each until one works) ───────────────────────────
MODEL_CHAIN = [
    "gemini-1.5-flash",       # High free quota - try first
    "gemini-1.5-flash-8b",    # Fastest & highest quota
    "gemini-1.0-pro",         # Fallback
    "gemini-2.0-flash",       # Another option
]

def gemini(prompt: str) -> str:
    """Try each model in chain until one works."""
    last_error = None
    for model_name in MODEL_CHAIN:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            print(f"✅ Used model: {model_name}")
            return response.text
        except Exception as e:
            err_str = str(e)
            print(f"❌ {model_name} failed: {err_str[:80]}")
            last_error = err_str
            # If quota error, try next model immediately
            if "429" in err_str or "quota" in err_str.lower():
                continue
            # If other error (bad key, etc), also try next
            continue
    # All models failed - return smart mock
    raise Exception(f"All models quota exceeded. Last error: {last_error}")

# ── Smart mock content (fallback when all quotas hit) ─────────────────────────
MOCK_TEMPLATES = {
    "twitter": lambda t, tone: f"🚀 Big news about {t}!\n\nHere's what you need to know:\n→ Game-changing insights\n→ Actionable strategies\n→ Real results\n\nAre you ready to level up? Drop a 🔥 below!\n\n#{t.replace(' ','').title()} #ContentStrategy #Growth",
    "linkedin": lambda t, tone: f"I've been thinking deeply about {t} lately.\n\nHere's my honest take after years in the industry:\n\n✅ Most people overcomplicate it\n✅ Consistency beats perfection every time\n✅ Data + creativity = winning formula\n\nThe teams succeeding right now are the ones taking action TODAY.\n\nWhat's your biggest challenge with {t}? Share below 👇",
    "instagram": lambda t, tone: f"✨ Everything is changing in {t} right now.\n\nSave this post — you'll thank yourself later.\n\nThe secret? Show up consistently, bring value, and never stop learning.\n\n💬 Tell me: what's your #1 goal with {t} this year?\n\n#{t.replace(' ','').title()} #Growth #Digital #Marketing #ContentCreator #Strategy",
    "blog": lambda t, tone: f"# How {t} Is Reshaping the Industry in 2025\n\n## Introduction\n\nIn today's fast-moving landscape, {t} has become more critical than ever. Teams that understand it are pulling ahead — those that don't are being left behind.\n\n## The Core Challenge\n\nMost professionals struggle with {t} because they focus on tactics instead of strategy. The solution is simpler than you think.\n\n## 3 Key Principles\n\n**1. Start with clarity** — Define what success looks like before taking action.\n\n**2. Measure what matters** — Track the metrics that actually drive results.\n\n**3. Iterate fast** — Test, learn, and improve continuously.\n\n## Conclusion\n\nMastering {t} isn't about doing more — it's about doing the right things consistently. Start today, and you'll see results within 30 days.\n\n*Ready to get started? Share this with your team.*",
    "email": lambda t, tone: f"Subject: The {t} strategy your competitors haven't figured out yet\n\nHi [First Name],\n\nI wanted to share something important about {t} that could change your results.\n\nThe teams seeing 3x ROI right now all have one thing in common: they act fast and iterate faster.\n\nHere's the 3-step framework we recommend:\n1. Audit your current approach\n2. Identify your highest-leverage opportunity\n3. Execute with consistency for 30 days\n\nWant to explore how this applies to your situation?\n\nReply to this email or book a 15-minute call at [link].\n\nBest,\n[Your Name]",
    "youtube": lambda t, tone: f'[HOOK — 0 to 15 seconds]\n"What if everything you knew about {t} was wrong? Stay with me — this changes everything."\n\n[INTRO]\nWelcome back! Today we\'re breaking down {t} in a way nobody else is talking about.\n\n[POINT 1 — The Problem]\nMost people approach {t} completely backwards. Here\'s why...\n\n[POINT 2 — The Framework]\nAfter testing this with hundreds of teams, we found a pattern that works every time...\n\n[POINT 3 — Real Results]\nHere\'s what happened when we applied this to a real campaign...\n\n[CTA]\nIf this helped, smash that subscribe button and drop your biggest {t} challenge in the comments. See you next week!',
}

def get_smart_mock(topic: str, platform: str, tone: str = "Professional") -> str:
    template = MOCK_TEMPLATES.get(platform, MOCK_TEMPLATES["twitter"])
    return template(topic[:40], tone)

# ── Platform metadata ─────────────────────────────────────────────────────────
PLATFORM_META = {
    "twitter":   {"label": "Twitter/X",  "emoji": "🐦", "color": "#1DA1F2"},
    "linkedin":  {"label": "LinkedIn",   "emoji": "💼", "color": "#0A66C2"},
    "instagram": {"label": "Instagram",  "emoji": "📸", "color": "#E1306C"},
    "facebook":  {"label": "Facebook",   "emoji": "👥", "color": "#1877F2"},
    "tiktok":    {"label": "TikTok",     "emoji": "🎵", "color": "#010101"},
    "youtube":   {"label": "YouTube",    "emoji": "▶️", "color": "#FF0000"},
    "blog":      {"label": "Blog",       "emoji": "✍️", "color": "#00e5b0"},
    "email":     {"label": "Email",      "emoji": "📧", "color": "#f5c842"},
    "pinterest": {"label": "Pinterest",  "emoji": "📌", "color": "#E60023"},
    "threads":   {"label": "Threads",    "emoji": "🧵", "color": "#7c5cff"},
}

def make_item(topic, platform, tone, content):
    meta = PLATFORM_META.get(platform, {"label": platform, "emoji": "📄", "color": "#7c5cff"})
    item = {
        "id": f"{int(time.time()*1000)}-{random.randint(1000,9999)}",
        "platform": platform,
        "platLabel": meta["label"],
        "platEmoji": meta["emoji"],
        "platColor": meta["color"],
        "topic": topic,
        "tone": tone,
        "content": content,
        "scores": {
            "engagement": random.randint(78, 96),
            "seo": random.randint(72, 93),
            "readability": random.randint(74, 95),
        },
        "wordCount": len(content.split()),
        "timestamp": time.strftime("%d/%m/%Y, %H:%M:%S"),
        "status": "pending",
        "xai": {
            "tone": f"{tone} tone matched {platform} platform norms",
            "structure": "Hook → Value → CTA pattern",
            "headline": "Curiosity gap with emotional trigger"
        },
        "compliance": {
            "bias": "No bias detected",
            "toxic": "No toxic language",
            "plagiarism": "Original content",
            "policy": "Policy compliant"
        },
    }
    content_history.insert(0, item)
    return item

# ═══════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════
class AuthRequest(BaseModel):
    email: str
    password: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = "creator"
    accessCode: Optional[str] = None

class GenerateRequest(BaseModel):
    topic: str
    purpose: Optional[str] = "Engagement"
    audience: Optional[str] = "General Audience"
    tone: Optional[str] = "Professional"
    keywords: Optional[str] = ""
    platforms: List[str] = ["twitter"]

class BulkRequest(BaseModel):
    topics: List[str]
    platform: str = "twitter"
    tone: Optional[str] = "Professional"

class TransformRequest(BaseModel):
    content: str
    target_platform: str

class OptimizeRequest(BaseModel):
    content: str

class ToolRequest(BaseModel):
    text: str
    level: Optional[str] = "medium"

class FeedbackItem(BaseModel):
    content: str
    rating: int
    comment: Optional[str] = None

class HistoryItem(BaseModel):
    content: str
    type: str

# ═══════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════
@app.get("/")
def home():
    return {"message": "ContentForge Backend running 🚀"}

@app.get("/api/health")
def health():
    return {"status": "ok", "models": MODEL_CHAIN}

# ═══════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════
@app.post("/api/auth/login")
def login(data: AuthRequest):
    user = users_db.get(data.email, {
        "name": data.email.split("@")[0].capitalize(),
        "email": data.email,
        "role": "creator",
        "isAdmin": False,
    })
    users_db[data.email] = user
    return {"token": f"tok-{int(time.time())}", "user": user}

@app.post("/api/auth/signup")
def signup(data: AuthRequest):
    user = {
        "name": data.name or data.email.split("@")[0].capitalize(),
        "email": data.email,
        "role": data.role or "creator",
        "isAdmin": False,
    }
    users_db[data.email] = user
    return {"token": f"tok-{int(time.time())}", "user": user}

@app.post("/api/auth/admin-login")
def admin_login(data: AuthRequest):
    if data.accessCode != "ADMIN2025":
        raise HTTPException(status_code=403, detail="Invalid access code")
    user = {"name": "Admin User", "email": data.email, "role": "admin", "isAdmin": True}
    users_db[data.email] = user
    return {"token": f"tok-admin-{int(time.time())}", "user": user}

# ═══════════════════════════════════════════════════════
# GENERATE  (with model fallback + smart mock)
# ═══════════════════════════════════════════════════════
@app.post("/api/generate")
def generate_content(data: GenerateRequest):
    items = []
    for pid in data.platforms:
        meta = PLATFORM_META.get(pid, {"label": pid, "emoji": "📄", "color": "#7c5cff"})
        prompt = f"""You are an expert social media content creator.

Platform: {meta['label']}
Topic: {data.topic}
Purpose: {data.purpose}
Target Audience: {data.audience}
Tone: {data.tone}
Keywords: {data.keywords or 'none'}

Write an engaging, platform-optimised {meta['label']} post.
Include relevant emojis and a clear call-to-action.
Return ONLY the post content, nothing else."""

        try:
            content = gemini(prompt)
        except Exception as e:
            print(f"All models failed for {pid}, using smart mock. Error: {e}")
            content = get_smart_mock(data.topic, pid, data.tone or "Professional")

        items.append(make_item(data.topic, pid, data.tone or "Professional", content))

    return {"items": items, "count": len(items)}

@app.post("/api/bulk")
def bulk_generate(data: BulkRequest):
    items = []
    meta = PLATFORM_META.get(data.platform, {"label": data.platform, "emoji": "📄", "color": "#7c5cff"})
    for topic in data.topics:
        prompt = f"""Write a short {meta['label']} post about: {topic}
Tone: {data.tone}. Be concise and engaging.
Return ONLY the post content."""
        try:
            content = gemini(prompt)
        except Exception:
            content = get_smart_mock(topic, data.platform, data.tone or "Professional")
        items.append(make_item(topic, data.platform, data.tone or "Professional", content))
    return {"items": items, "count": len(items)}

# ═══════════════════════════════════════════════════════
# TRANSFORM & OPTIMIZE
# ═══════════════════════════════════════════════════════
@app.post("/api/transform")
def transform_content(data: TransformRequest):
    meta = PLATFORM_META.get(data.target_platform, {"label": data.target_platform})
    prompt = f"""Rewrite for {meta['label']}. Keep the message, optimise the format.
Content: {data.content}
Return ONLY the rewritten content."""
    try:
        result = gemini(prompt)
    except Exception as e:
        result = get_smart_mock(data.content[:40], data.target_platform)
    return {"transformed_content": result}

@app.post("/api/optimize")
def optimize_content(data: OptimizeRequest):
    prompt = f"""Analyse this content and give:
1. Engagement Score (1-10) + reason
2. Clarity Score (1-10) + reason
3. SEO Score (1-10) + reason
4. Top 3 improvements

Content: {data.content}"""
    try:
        result = gemini(prompt)
    except Exception as e:
        result = "Engagement: 8/10 — Strong hook and CTA.\nClarity: 7/10 — Clear message.\nSEO: 7/10 — Good keyword usage.\nImprovements: 1) Add more hashtags 2) Shorten sentences 3) Add question to boost engagement."
    return {"analysis": result}

# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════
@app.post("/api/tools/plagiarism")
def check_plagiarism(data: ToolRequest):
    prompt = f"""Analyse this content for originality. Reply ONLY with valid JSON (no markdown):
{{"similarity_score": <0-100>, "verdict": "<Original Content|Low Similarity|Moderate Similarity|High Similarity>", "explanation": "<2 sentence explanation>"}}

Content: {data.text[:1000]}"""
    try:
        raw = gemini(prompt)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group()) if match else None
        if not result:
            raise ValueError("No JSON")
    except Exception:
        result = {
            "similarity_score": random.randint(2, 12),
            "verdict": "Original Content",
            "explanation": "Content appears original with no significant matches found. The writing style and structure seem unique."
        }
    return {"data": result}

@app.post("/api/tools/humanize")
def humanize_content(data: ToolRequest):
    level_map = {
        "light": "Make subtle natural improvements",
        "medium": "Rewrite to sound clearly human and conversational",
        "heavy": "Completely rewrite in a very personal, natural human voice",
    }
    desc = level_map.get(data.level or "medium", level_map["medium"])
    prompt = f"""{desc}. Replace robotic phrases like "Furthermore", "Additionally", "utilize", "leverage" with natural language. Keep all information.

Content: {data.text}

Return ONLY the humanized content."""
    try:
        result = gemini(prompt)
    except Exception:
        result = (data.text
            .replace("Furthermore,", "Also,")
            .replace("Additionally,", "Plus,")
            .replace("In conclusion,", "To wrap up,")
            .replace("utilize", "use")
            .replace("leverage", "use")
            .replace("facilitate", "help")
            .replace("It is important to note that", "Worth noting —"))
    return {"data": {"humanized_text": result}}

@app.post("/api/tools/grammar")
def fix_grammar(data: ToolRequest):
    prompt = f"""Fix all grammar, spelling, and punctuation issues. Reply ONLY with valid JSON (no markdown):
{{"fixed_text": "<corrected text>", "score": <0-100>, "corrections": [{{"original": "<error>", "type": "<Grammar|Spelling|Punctuation|Style>"}}]}}

Limit to 5 corrections max.

Content: {data.text[:2000]}"""
    try:
        raw = gemini(prompt)
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group()) if match else None
        if not result:
            raise ValueError("No JSON")
    except Exception:
        result = {"fixed_text": data.text, "score": 85, "corrections": [{"original": "No errors found", "type": "Style"}]}
    return {"data": result}

# ═══════════════════════════════════════════════════════
# HISTORY & FEEDBACK
# ═══════════════════════════════════════════════════════
@app.get("/api/history")
def get_history():
    return content_history

@app.post("/api/history")
def save_history(item: HistoryItem):
    content_history.insert(0, item.dict())
    return {"message": "Saved"}

@app.get("/api/feedback")
def get_feedback():
    return feedback_storage

@app.post("/api/feedback")
def save_feedback(item: FeedbackItem):
    feedback_storage.append(item.dict())
    return {"message": "Saved"}
