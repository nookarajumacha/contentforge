[READMEE.md](https://github.com/user-attachments/files/25658276/READMEE.md)
# ⚡ ContentForge — AI Content Intelligence Platform

<div align="center">

![ContentForge Banner](https://img.shields.io/badge/ContentForge-AI%20Content%20Platform-7c5cff?style=for-the-badge&logo=lightning&logoColor=white)

[![HTML](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Google Translate](https://img.shields.io/badge/Google%20Translate-4285F4?style=flat-square&logo=googletranslate&logoColor=white)](https://translate.google.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**One idea → 6 platform-ready content pieces. Zero backend required.**

[Features](#-features) · [Demo](#-demo) · [Getting Started](#-getting-started) · [Pages](#-pages--modules) · [Tech Stack](#-tech-stack) · [Contributing](#-contributing)

</div>

---

## 📖 Overview

**ContentForge** is a fully frontend-only, single-file AI content intelligence platform built with pure HTML, CSS, and JavaScript. It simulates a complete SaaS content creation workflow — from brief to publish — including AI generation, plagiarism checking, grammar fixing, humanization, multi-platform support, analytics, and a full admin panel.

> 🚀 No backend. No Node.js. No build step. Just open the HTML file and go.

---

## ✨ Features

### 🔐 Authentication System
- **Login** with email & password (stored in `localStorage`)
- **Create Account** with a 3-step onboarding flow (basic info → role selection → platform preferences)
- **Admin Portal** with 2FA access code (`ADMIN2025`)
- **Google OAuth** integration via Google Identity Services (GSI)
- Role-based access: Creator, Editor, Marketer, Analyst, Admin

### 🏷️ Brand Workspaces
- Create and manage multiple brand identities
- Define brand voice, tone, target audience, and language per brand
- All brands persist in memory for the session

### ⚡ Campaigns
- Create campaigns with goals, timelines, and target platforms
- Visual progress bars and platform-colour-coded cards
- Campaign types: Brand Awareness, Product Launch, Lead Generation, Community Building

### 📅 Content Calendar
- 30-day AI-generated content schedule
- Platform-specific scheduling (Twitter, LinkedIn, Blog, Email, Instagram, YouTube)
- Interactive calendar grid with colour-coded platform legend

### ✨ AI Generate
- **Intent & Context Analysis → Brand Voice Mapping → SEO Enhancement → Compliance Pre-check → Performance Scoring** — 8-step animated AI pipeline
- Supports 6 platforms simultaneously: Twitter/X, LinkedIn, Instagram, Email, Blog, YouTube
- Configurable: Topic, Purpose, Audience, Tone, SEO Keywords
- Per-piece scores: Engagement, SEO, Readability
- Explainable AI (XAI) section — reveals tone, structure, and headline decisions
- Compliance panel: bias check, toxicity check, plagiarism flag, policy status
- One-click copy for each generated piece
- Connects to real **Anthropic Claude API** when an API key is provided

### ⚡ Bulk Generate
- Enter multiple topics (one per line)
- Select platform and tone, generate all at once
- Batch results view with per-topic status

### 🔧 Content Tools *(New)*
Three tabbed tools in one place:

| Tool | What it does |
|------|-------------|
| 🔍 **Plagiarism Check** | Analyses pasted content and returns a similarity score (0–100%) with a verdict |
| 🤖 **Humanize** | Rewrites AI-generated content at Light / Medium / Deep intensity to reduce AI-detection risk |
| ✅ **Grammar Fix** | Detects and fixes capitalisation, spacing, punctuation, and style issues with a corrections log |

### ✅ Review & Approve
- Queue of all pending content pieces
- Approve → moves to Publish; Reject → flags for revision
- "View Full" opens a detail modal with inline editing and score display

### 📤 Publish & Export
- Export all approved content as `.TXT`, `.JSON`, or `.CSV`
- Schedule publish with date + time picker
- Per-piece download button

### 📊 Analytics
- Weekly engagement score bar chart
- Platform performance progress bars (Twitter, LinkedIn, Instagram, Email)
- AI Continuous Learning insights panel (actionable tips based on patterns)

### 🕑 Content History
- Full log of every generated piece with platform, tone, word count, timestamp, and status badge
- Filter by platform
- Click any row to open the detail/edit modal

### 🧬 Knowledge Graph
- Topics Covered — colour-coded nodes from generation history
- Platform Memory — post count per platform
- Brand Preferences — best tone, avg score, total words
- Repetition Guard — topics to avoid repeating

### ⚙️ Settings
- Profile management (name, email)
- 🌙 Dark / ☀️ Light mode toggle
- 🌐 **Multi-language translation** — translates the entire website into 9 languages via Google Translate:
  English, Hindi, Spanish, French, German, Arabic, Chinese, Japanese, Portuguese
- AI Configuration: API key input, Auto SEO toggle, AI Feedback Loop toggle
- Danger Zone: delete all content history

### 🛡️ Admin Panel *(Admin-only)*
- System stats: Total Users, Content Generated, Pipeline Uptime
- Pipeline controls with live toggles
- Model selection: Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku

---

## 🖥️ Demo

> Since this is a single HTML file, no hosting is needed — but you can host it anywhere.

**Live preview options:**
- Drop the file into [GitHub Pages](https://pages.github.com/)
- Open with [VSCode Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer)
- Simply double-click `index.html` in your browser

**Demo credentials:**
```
Create any account via the "Create Account" tab
Admin access code: ADMIN2025
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/contentforge.git
cd contentforge
```

### 2. Open the app
```bash
# Option A — just open in browser
open index.html

# Option B — serve locally
npx serve .
# or
python -m http.server 8080
```

### 3. (Optional) Connect real AI generation
1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Log in → Settings → AI Configuration → paste your API key
3. Click **Save Settings**
4. All future generations will use Claude 3.5 Sonnet (falls back to mock content if no key)

### 4. (Optional) Enable Google Login
Replace `YOUR_GOOGLE_CLIENT_ID` in the HTML with your OAuth 2.0 Client ID from [Google Cloud Console](https://console.cloud.google.com/apis/credentials).

---

## 📁 Project Structure

```
contentforge/
│
├── index.html          # The entire application — HTML + CSS + JS in one file
└── README.md           # This file
```

> ContentForge is intentionally a single-file app — zero dependencies, zero build tools, maximum portability.

---

## 📄 Pages & Modules

| Page | Route (nav) | Description |
|------|-------------|-------------|
| Dashboard | `dashboard` | Stats overview, recent content, quick actions |
| Brand Workspace | `brands` | Create & manage brand identities |
| Campaigns | `campaigns` | Group content by campaign with goals & timelines |
| Content Calendar | `calendar` | 30-day scheduled content plan |
| AI Generate | `generate` | Main content generation interface |
| Bulk Generate | `bulk` | Multi-topic batch generation |
| Content Tools | `tools` | Plagiarism, Humanize, Grammar Fix |
| Review & Approve | `review` | Editorial queue |
| Publish & Export | `publish` | Export formats + scheduling |
| Analytics | `analytics` | Charts and platform performance |
| Content History | `history` | Full generation log |
| Knowledge Graph | `knowledge` | Memory & pattern visualiser |
| Settings | `settings` | Profile, theme, language, AI config |
| Admin Panel | `admin` | System controls (admin-only) |

---

## 🌐 Language Support

ContentForge supports **9 languages** via Google Translate integration:

| Flag | Language | Code |
|------|----------|------|
| 🇬🇧 | English | `en` |
| 🇮🇳 | Hindi | `hi` |
| 🇪🇸 | Spanish | `es` |
| 🇫🇷 | French | `fr` |
| 🇩🇪 | German | `de` |
| 🇸🇦 | Arabic | `ar` |
| 🇨🇳 | Chinese | `zh-CN` |
| 🇯🇵 | Japanese | `ja` |
| 🇧🇷 | Portuguese | `pt` |

Language preference is saved to `localStorage` and persists across page reloads.

---

## 🛠️ Tech Stack

| Technology | Usage |
|-----------|-------|
| **HTML5** | Application structure and markup |
| **CSS3** | Custom design system with CSS variables, animations, dark/light themes |
| **Vanilla JavaScript** | All app logic, state management, routing |
| **Google Fonts** | Syne (headings), Plus Jakarta Sans (body), Space Mono (labels) |
| **Google Identity Services** | OAuth 2.0 Google Login |
| **Google Translate Widget** | Full-site language translation |
| **Anthropic Claude API** | AI content generation (optional, with API key) |
| **localStorage** | User accounts, language preferences |
| **Web Crypto / Clipboard API** | Copy-to-clipboard functionality |

**Zero npm packages. Zero frameworks. Zero build pipeline.**

---

## 🎨 Design System

ContentForge uses a fully custom CSS variable-based design system:

```css
/* Dark Theme (default) */
--bg: #06060e
--accent: #7c5cff        /* Purple — primary actions */
--accent2: #ff5f7e       /* Pink — errors, rejections */
--accent3: #00e5b0       /* Teal — success, approvals */
--gold: #ffd166          /* Gold — pending, warnings */

/* Light Theme (toggleable) */
--bg: #f4f4ff
--accent: #6c47ff
```

**Animations used:** `fadeUp`, `float`, `gradShift`, `orb1/2/3`, `particles`, `pulse` — all CSS-only.

---

## 🤝 Contributing

Contributions are welcome! Here's how:

```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes to index.html
# 4. Test in multiple browsers (Chrome, Firefox, Safari)

# 5. Commit with a clear message
git commit -m "feat: add [your feature]"

# 6. Push and open a Pull Request
git push origin feature/your-feature-name
```

### Ideas for contributions
- [ ] Real persistent storage (Firebase / Supabase integration)
- [ ] More platform support (TikTok, Pinterest, Threads)
- [ ] PDF export of content history
- [ ] CSV import for bulk topics
- [ ] Webhook integration for auto-publishing
- [ ] More languages

---

## 📋 Known Limitations

- **No persistent backend** — all data (content history, brands, campaigns) resets on page refresh
- **Google Translate** requires an active internet connection
- **AI generation** requires a valid Anthropic API key; mock content is used as fallback
- **Google Login** requires a configured OAuth 2.0 Client ID to function

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Built with ❤️ as a full-featured frontend demo of an AI content SaaS platform.

---

<div align="center">

**ContentForge** — *The AI Engine for Scalable Content.*

⭐ Star this repo if you found it useful!

</div>
