"""
Theme page creation and monetization framework.

A 'theme page' (also called a 'faceless account' or 'niche page') curates
and reposts content around a single topic without showing the creator's face.
This module provides a complete playbook for building converting theme pages.
"""
from typing import Dict, List, Optional


# ─── Top converting theme page niches ────────────────────────────────────────

TOP_NICHES: List[Dict] = [
    {
        "niche":         "Luxury Lifestyle",
        "description":   "Supercars, mansions, private jets, yachts, designer goods",
        "audience":      "18-35 male, aspirational",
        "monetization":  ["Dropshipping luxury accessories", "Affiliate (Amazon luxury)", "Sponsored posts", "Course on wealth-building"],
        "avg_cpm":       "$8-15",
        "competition":   "HIGH",
        "difficulty":    "Easy content, hard to stand out",
        "example_pages": ["luxuryglobal", "wealthylifestyle"],
    },
    {
        "niche":         "Motivational Quotes",
        "description":   "Daily motivation, success mindset, hustle culture",
        "audience":      "18-40 mixed, entrepreneurs",
        "monetization":  ["Ebooks", "Course sales", "Coaching", "Affiliate (Audible, courses)"],
        "avg_cpm":       "$5-12",
        "competition":   "VERY HIGH",
        "difficulty":    "Easy to start, hard to differentiate",
        "example_pages": ["goalcast", "motiversity"],
    },
    {
        "niche":         "Finance Tips",
        "description":   "Investing, crypto, budgeting, passive income",
        "audience":      "22-45 mixed, financially curious",
        "monetization":  ["Affiliate (Robinhood, Coinbase, credit cards)", "Newsletter", "Course"],
        "avg_cpm":       "$15-40",
        "competition":   "HIGH",
        "difficulty":    "Requires credibility or research. VERY high CPM.",
        "example_pages": ["humphreytalks", "minoritymindset"],
    },
    {
        "niche":         "Nature & Scenery",
        "description":   "Landscapes, wildlife, ocean, mountains, ASMR nature",
        "audience":      "25-55 mixed, relaxation-seekers",
        "monetization":  ["Print-on-demand (Redbubble, Society6)", "AdSense (YouTube)", "Stock footage sales"],
        "avg_cpm":       "$3-8",
        "competition":   "MED",
        "difficulty":    "Need quality footage. Slow to monetize.",
        "example_pages": ["nature", "earthpix"],
    },
    {
        "niche":         "Dog/Pet Content",
        "description":   "Cute dog videos, training tips, pet care",
        "audience":      "18-55 female-leaning, pet owners",
        "monetization":  ["Pet affiliate (Chewy, Amazon Pets)", "Brand deals", "Merch"],
        "avg_cpm":       "$5-10",
        "competition":   "HIGH",
        "difficulty":    "Easy to source content. Engagement is very high.",
        "example_pages": ["9gag.dog", "dogsofinsta"],
    },
    {
        "niche":         "Cooking & Recipes",
        "description":   "Quick recipes, meal prep, food hacks",
        "audience":      "25-50 mixed",
        "monetization":  ["Cookbook affiliate", "Kitchen affiliate (Amazon)", "AdSense", "Brand deals with food brands"],
        "avg_cpm":       "$6-14",
        "competition":   "VERY HIGH",
        "difficulty":    "Content is abundant. Niche down (keto, vegan, budget).",
        "example_pages": ["tasty", "buzzfeedtasty"],
    },
    {
        "niche":         "Relationship / Dating",
        "description":   "Dating tips, red flags, psychology, self-improvement",
        "audience":      "18-35 mixed",
        "monetization":  ["Dating app affiliate", "Course/ebook", "Coaching"],
        "avg_cpm":       "$10-20",
        "competition":   "MED",
        "difficulty":    "Controversial topics drive engagement. Stay ethical.",
        "example_pages": ["modernrelationship", "dating.decoded"],
    },
    {
        "niche":         "Study & Productivity",
        "description":   "Study with me, Pomodoro timers, productivity hacks",
        "audience":      "14-25 students",
        "monetization":  ["Notion templates", "Study planner affiliate", "AdSense (YouTube long-form)"],
        "avg_cpm":       "$4-9",
        "competition":   "MED",
        "difficulty":    "Low barrier. YouTube is especially strong for this niche.",
        "example_pages": ["studyquill", "studytoker"],
    },
    {
        "niche":         "Horror & Paranormal",
        "description":   "Scary stories, ghost videos, conspiracy theories",
        "audience":      "15-30 mixed",
        "monetization":  ["AdSense", "Merch", "Patreon"],
        "avg_cpm":       "$5-12",
        "competition":   "MED",
        "difficulty":    "Viral potential is high. Great for faceless YouTube.",
        "example_pages": ["mrballen", "bedtimestories"],
    },
    {
        "niche":         "AI & Tech News",
        "description":   "AI tools, ChatGPT tutorials, tech news breakdowns",
        "audience":      "18-40 male-leaning, tech-curious",
        "monetization":  ["AI tool affiliate (Jasper, Midjourney)", "Course", "Newsletter"],
        "avg_cpm":       "$15-35",
        "competition":   "HIGH but growing fast",
        "difficulty":    "High demand right now. Niche is exploding.",
        "example_pages": ["aivalley", "futuretools"],
    },
]


# ─── Full theme page playbook ─────────────────────────────────────────────────

def theme_page_guide(niche: str = "") -> Dict:
    """Return a complete theme page creation and conversion guide."""
    return {
        "what_is_a_theme_page": (
            "A theme page is a faceless social media account that curates, reposts, "
            "and/or creates content around a single niche topic — without showing the "
            "creator's face or personal brand. The goal is to build an audience around "
            "a topic and monetize through affiliate, ads, products, or sponsorships."
        ),
        "why_theme_pages_work": [
            "No personal brand required — anyone can start one.",
            "Content creation is faster — curate existing viral content + add value.",
            "Scalable — one person can run 5-10 theme pages simultaneously.",
            "Lower burnout — not tied to showing up personally.",
            "Easier to sell — accounts can be sold as assets ($500-$50K+ depending on followers).",
        ],
        "phase_1_setup": {
            "title":   "Account Setup (Days 1-3)",
            "steps": [
                "1. Choose a niche with a clear audience and monetization path (see `social theme-pages niches`).",
                "2. Pick a handle: [Niche][keyword] — e.g., DailyMotivate, LuxuryWorldHQ, FinanceDailyTips.",
                "3. Create a professional logo using Canva (free) — simple, clean, niche-relevant.",
                "4. Write a bio using the formula: [Niche topic] | [Post frequency] | [CTA].",
                "5. Set up a link-in-bio tool: Beacons.ai (free), Stan.store, or Linktree.",
                "6. Create your first 9-12 posts before going public (content bank).",
            ],
        },
        "phase_2_content_strategy": {
            "title": "Content Strategy (Ongoing)",
            "content_types": [
                {
                    "type":       "Reposts with credit",
                    "effort":     "LOW",
                    "risk":       "MEDIUM — some platforms penalize reposts",
                    "best_for":   "Instagram, Twitter/X",
                    "tip":        "Always credit original creator. Build relationships by tagging them.",
                },
                {
                    "type":       "Compilations",
                    "effort":     "MED",
                    "risk":       "LOW — original format",
                    "best_for":   "TikTok, YouTube Shorts",
                    "tip":        "Use Capcut or CapCut to edit. Add text overlay with your branding.",
                },
                {
                    "type":       "AI-generated content",
                    "effort":     "LOW",
                    "risk":       "LOW",
                    "best_for":   "All platforms",
                    "tip":        "Use ChatGPT for captions/scripts, Midjourney for images, ElevenLabs for voiceover.",
                },
                {
                    "type":       "Screen-recorded reactions",
                    "effort":     "LOW",
                    "risk":       "LOW",
                    "best_for":   "TikTok (Stitch/Duet)",
                    "tip":        "React to viral news or viral content in your niche.",
                },
                {
                    "type":       "Original faceless video",
                    "effort":     "HIGH",
                    "risk":       "LOW — most algorithm-favored",
                    "best_for":   "All platforms — highest upside",
                    "tip":        "B-roll footage + AI voiceover + text = full faceless video with no camera.",
                },
            ],
            "content_calendar_template": {
                "monday":    "Educational post (tip, fact, tutorial)",
                "tuesday":   "Inspirational/motivational",
                "wednesday": "Trending topic in your niche",
                "thursday":  "Behind-the-scenes or curator pick",
                "friday":    "Engagement post (poll, question, this vs that)",
                "saturday":  "Entertainment / humor in niche",
                "sunday":    "Recap / weekly roundup",
            },
        },
        "phase_3_growth": {
            "title": "Growth (First 90 Days)",
            "tactics": [
                "Repost the best-performing content from top accounts in your niche (with credit).",
                "Engage daily: like, comment, follow 50-100 accounts in your niche.",
                "Use trending sounds for TikTok/Reels versions of your content.",
                "Run a giveaway at 1K followers — 'Follow + Share to enter'.",
                "Cross-post content to ALL platforms simultaneously (TikTok → IG → Shorts → Twitter).",
                "Collaborate with similar-sized theme pages for shoutout exchanges.",
                "Post 1-3x per day on TikTok/Instagram, 2x per week on YouTube.",
            ],
            "milestones": [
                "0-1K followers: Focus on content quality and niche consistency.",
                "1K-10K: Engage heavily, start building email list, add affiliate links.",
                "10K-50K: Reach out to small brands for deals ($50-500/post).",
                "50K-100K: Negotiate paid sponsorships, launch digital product.",
                "100K+: Full monetization — courses, consulting, account sales.",
            ],
        },
        "phase_4_monetization": {
            "title": "Monetization (Month 2+)",
            "strategies": [
                {
                    "method":   "Affiliate Marketing",
                    "effort":   "LOW",
                    "startup":  "Free",
                    "timeline": "Start immediately",
                    "how_to":   "Sign up for Amazon Associates, ShareASale, Impact, or niche-specific programs. Add links to bio and captions.",
                },
                {
                    "method":   "Digital Products",
                    "effort":   "MED",
                    "startup":  "Free (Gumroad, Stan.store)",
                    "timeline": "Month 2-3",
                    "how_to":   "Create an ebook, template, or guide related to your niche. Price $7-$47. Sell via bio link.",
                },
                {
                    "method":   "Sponsored Posts",
                    "effort":   "LOW",
                    "startup":  "Free",
                    "timeline": "10K+ followers",
                    "how_to":   "Create a media kit (Canva template). Reach out to brands via DM or email. Use Creator Marketplace (TikTok, Instagram).",
                },
                {
                    "method":   "Newsletter",
                    "effort":   "MED",
                    "startup":  "Free (Beehiiv, Substack)",
                    "timeline": "Start from day 1",
                    "how_to":   "Capture emails with a free lead magnet. Monetize via sponsorships or upsell to paid tier.",
                },
                {
                    "method":   "Account Flipping",
                    "effort":   "HIGH",
                    "startup":  "Time only",
                    "timeline": "3-6 months",
                    "how_to":   "Grow account to 10K-100K, then sell on Fameswap, Viral Accounts, or social media marketplaces for $500-$10K+.",
                },
                {
                    "method":   "AdSense (YouTube only)",
                    "effort":   "LOW",
                    "startup":  "Free",
                    "timeline": "After 1K subs + 4K watch hours",
                    "how_to":   "Apply to YouTube Partner Program. Finance, tech, and how-to niches earn $5-40 RPM.",
                },
            ],
        },
        "tools_stack": {
            "content_creation": ["CapCut (video editing)", "Canva (graphics)", "ChatGPT (captions, scripts)", "ElevenLabs (AI voiceover)", "Midjourney (AI images)"],
            "scheduling":       ["Buffer (free tier)", "Later", "TikTok native scheduler", "Meta Business Suite"],
            "analytics":        ["TikTok Analytics (native)", "Instagram Insights (native)", "Social Blade (free)"],
            "monetization":     ["Beacons.ai (bio link + store)", "Stan.store", "Gumroad", "Beehiiv (newsletter)"],
            "research":         ["TikTok Creative Center", "Google Trends", "social CLI (this tool!)"],
        },
        "common_mistakes": [
            "Posting inconsistently — 7 days on, 2 weeks off kills algorithmic momentum.",
            "No clear niche — 'general content' accounts get 0 algorithmic push.",
            "Chasing follower count before setting up monetization infrastructure.",
            "Ignoring analytics — double down on what works, cut what doesn't.",
            "Never testing hooks — the first 3 seconds are everything.",
            "No CTA on posts — always tell people what to do next.",
            "Giving up before 90 days — theme pages are slow in month 1, exponential by month 3.",
        ],
        "selected_niche": _get_niche_detail(niche) if niche else None,
    }


def _get_niche_detail(niche: str) -> Optional[Dict]:
    niche_lower = niche.lower()
    for n in TOP_NICHES:
        if niche_lower in n["niche"].lower():
            return n
    return {"niche": niche, "note": f"'{niche}' not in curated list. Run `social theme-pages niches` to see top options."}


def list_niches() -> List[Dict]:
    return TOP_NICHES
