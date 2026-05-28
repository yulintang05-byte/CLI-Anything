"""Cross-platform trend analysis and content idea generator.

Synthesizes data from YouTube + TikTok scrapers to surface cross-platform
opportunities and generate content ideas around viral topics.
"""

from typing import Any

from cli_anything.social_trends.platforms import youtube as yt
from cli_anything.social_trends.platforms import tiktok as tt


def get_cross_platform_trends(limit: int = 15) -> list[dict]:
    """Find topics trending on BOTH YouTube and TikTok simultaneously."""
    yt_videos = yt.get_trending_videos(limit=30)
    yt_keywords = {kw["keyword"]: kw["frequency"] for kw in yt.get_viral_keywords(limit=40)}

    tt_hashtags = tt.get_trending_hashtags(limit=30)
    tt_tag_words = set()
    for tag in tt_hashtags:
        words = tag["hashtag"].lstrip("#").lower().split()
        tt_tag_words.update(words)

    cross_hits: list[dict] = []
    seen: set[str] = set()

    for kw, freq in sorted(yt_keywords.items(), key=lambda x: x[1], reverse=True):
        if kw.lower() in tt_tag_words and kw not in seen:
            seen.add(kw)
            # Find matching TikTok hashtag
            matching_tags = [
                t["hashtag"] for t in tt_hashtags
                if kw.lower() in t["hashtag"].lower()
            ]
            # Find matching YouTube videos
            matching_videos = [
                v["title"] for v in yt_videos
                if kw.lower() in v["title"].lower()
            ][:3]

            cross_hits.append({
                "keyword": kw,
                "youtube_frequency": freq,
                "tiktok_hashtags": matching_tags[:3],
                "youtube_examples": matching_videos,
                "opportunity_score": freq * len(matching_tags),
                "platforms": ["youtube", "tiktok"],
                "content_idea": _generate_idea(kw),
            })

        if len(cross_hits) >= limit:
            break

    return cross_hits[:limit]


def generate_content_ideas(niche: str, count: int = 10) -> list[dict]:
    """Generate viral-optimized content ideas for a specific niche."""
    yt_vids = yt.get_trending_videos(limit=30)
    tt_tags = tt.get_niche_hashtags(niche, limit=15)
    tt_sounds = tt.get_trending_sounds(limit=10)

    ideas: list[dict] = []

    # Ideas from YouTube trending in niche
    niche_videos = [v for v in yt_vids if niche.lower() in v["title"].lower()][:5]
    for vid in niche_videos:
        ideas.append({
            "idea": f"TikTok-style breakdown: '{vid['title']}'",
            "format": "Reaction/Commentary Reel",
            "inspired_by": "YouTube Trending",
            "suggested_audio": tt_sounds[0]["sound"] if tt_sounds else "trending sound",
            "hashtags": [t["hashtag"] for t in tt_tags[:5]],
            "hook": f"Did you know {vid['title'].split(' ')[0]}...?",
        })

    # Template-based ideas for niche
    templates = _niche_templates(niche)
    for i, tpl in enumerate(templates[:count - len(ideas)]):
        ideas.append({
            "idea": tpl["idea"],
            "format": tpl["format"],
            "inspired_by": "trend_template",
            "suggested_audio": tt_sounds[i % len(tt_sounds)]["sound"] if tt_sounds else "trending sound",
            "hashtags": [t["hashtag"] for t in tt_tags[:5]] + ["#fyp", "#foryoupage"],
            "hook": tpl["hook"],
        })

    return ideas[:count]


def get_viral_formula(format_type: str = "all") -> list[dict]:
    """Return proven viral content formulas for different video formats."""
    formulas: dict[str, list[dict]] = {
        "hook": [
            {
                "formula": "Controversial Statement",
                "template": "Unpopular opinion: [your_niche_claim]",
                "why_it_works": "Triggers disagreement = comments = algorithm boost",
                "example": "Unpopular opinion: you don't need to go to the gym to get shredded",
            },
            {
                "formula": "Curiosity Gap",
                "template": "The reason [common_belief] is actually [surprising_truth]",
                "why_it_works": "Brain seeks closure — must watch to end",
                "example": "The reason posting more often is killing your TikTok growth",
            },
            {
                "formula": "Number Hook",
                "template": "I made $[X] in [Y] days doing [Z]",
                "why_it_works": "Specificity = credibility, numbers stop scroll",
                "example": "I made $4,200 in 11 days with this TikTok theme page",
            },
            {
                "formula": "Story Open",
                "template": "3 years ago I was [relatable_struggle]. Today [transformation].",
                "why_it_works": "Triggers empathy + aspiration simultaneously",
                "example": "3 years ago I had 0 followers. Today I have 2M across platforms.",
            },
            {
                "formula": "Warning/Alert",
                "template": "Stop doing [X] if you want [Y]",
                "why_it_works": "Loss aversion — fear of missing out on improvement",
                "example": "Stop using these hashtags if you want TikTok views",
            },
        ],
        "structure": [
            {
                "formula": "Problem-Agitate-Solve",
                "template": "Problem (3s) → Make it worse (5s) → Your solution (10s) → CTA (2s)",
                "platforms": ["TikTok", "Instagram Reels", "YouTube Shorts"],
                "ideal_length": "20-30 seconds",
            },
            {
                "formula": "Tutorial Reveal",
                "template": "Show end result first (3s) → Process (20s) → Result again + CTA (5s)",
                "platforms": ["TikTok", "YouTube", "Instagram"],
                "ideal_length": "30-60 seconds",
            },
            {
                "formula": "Listicle Fast-Cut",
                "template": "Hook: 'X things about Y' → Quick-cut numbered list → Final CTA",
                "platforms": ["TikTok", "YouTube Shorts", "Instagram Reels"],
                "ideal_length": "30-60 seconds",
            },
            {
                "formula": "Story Arc",
                "template": "Setup (relatable moment) → Conflict → Resolution → Moral/CTA",
                "platforms": ["TikTok", "YouTube", "Instagram Reels"],
                "ideal_length": "60-180 seconds",
            },
        ],
        "cta": [
            {"cta": "Follow for [specific value]", "placement": "End card", "conversion": "Follow"},
            {"cta": "Comment [keyword] for [resource]", "placement": "Caption + verbal", "conversion": "Comment → DM"},
            {"cta": "Share this with [specific person]", "placement": "Verbal at 70% mark", "conversion": "Share"},
            {"cta": "Save this for later", "placement": "Caption", "conversion": "Save (boosts algorithm)"},
            {"cta": "Watch part 2 [link in bio]", "placement": "End of video", "conversion": "Profile visit"},
        ],
    }

    if format_type == "all":
        return [{"type": k, "formulas": v} for k, v in formulas.items()]
    return [{"type": format_type, "formulas": formulas.get(format_type, [])}]


def _generate_idea(keyword: str) -> str:
    templates = [
        f"React to the most viral {keyword} content this week",
        f"The truth about {keyword} no one talks about",
        f"How I used {keyword} to grow 10K followers",
        f"Top 5 {keyword} tips that actually work",
        f"POV: You discover {keyword} for the first time",
    ]
    idx = abs(hash(keyword)) % len(templates)
    return templates[idx]


def _niche_templates(niche: str) -> list[dict]:
    return [
        {
            "idea": f"Day in my life as a {niche} creator",
            "format": "Vlog-style montage",
            "hook": f"What it's actually like being in {niche}",
        },
        {
            "idea": f"Top 5 mistakes people make in {niche}",
            "format": "Talking head + text overlay",
            "hook": f"Stop making these {niche} mistakes",
        },
        {
            "idea": f"I tried {niche} for 30 days — here's what happened",
            "format": "Before/after montage",
            "hook": "30 day {niche} challenge results",
        },
        {
            "idea": f"The {niche} routine that changed my life",
            "format": "Step-by-step tutorial",
            "hook": f"This {niche} routine hits different",
        },
        {
            "idea": f"Reacting to viral {niche} videos",
            "format": "Stitch/Reaction",
            "hook": f"This {niche} video has 10M views for a reason",
        },
        {
            "idea": f"Beginner's guide to {niche} in 60 seconds",
            "format": "Fast-cut educational",
            "hook": f"Everything you need to know about {niche}",
        },
        {
            "idea": f"Hot takes on {niche} trends in 2025",
            "format": "Talking head / opinion",
            "hook": f"Controversial {niche} opinion incoming",
        },
        {
            "idea": f"How I make money with {niche}",
            "format": "Storytelling + screen record",
            "hook": f"Making $X/month from {niche}",
        },
    ]
