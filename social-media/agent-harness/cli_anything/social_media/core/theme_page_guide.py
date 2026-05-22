"""Theme page conversion playbook.

Covers everything needed to convert a personal or blank account
into a profitable theme/niche page: niche selection, content curation,
monetization, and growth systems.
"""

import time

# Monetization revenue ranges (monthly, USD) — conservative estimates
_MONETIZATION = {
    "affiliate_marketing": {
        "description": "Promote products via affiliate links (Amazon, ClickBank, ShareASale)",
        "start_followers": 0,
        "monthly_range": "$100-$5,000+",
        "effort": "Medium",
        "setup": [
            "Join Amazon Associates (instant approval) or ClickBank",
            "Find products relevant to your niche with 20-50% commission",
            "Create review/recommendation content around those products",
            "Add link-in-bio tool (Linktree, Stan Store) to host multiple links",
            "Disclose affiliate relationships per FTC guidelines",
        ],
    },
    "shoutouts_sponsored_posts": {
        "description": "Charge other accounts/brands to be promoted to your audience",
        "start_followers": 5000,
        "monthly_range": "$200-$10,000+",
        "effort": "Low",
        "setup": [
            "Set up a rate sheet: $X per story, $Y per post, $Z per dedicated video",
            "Typical rate: $10-20 per 1K followers for a post",
            "Use platforms: Shoutcart, GrapeSocial, or direct DM inquiries",
            "Only promote relevant, quality brands to maintain trust",
            "Track performance for each sponsor to build case studies",
        ],
    },
    "digital_products": {
        "description": "Sell PDFs, courses, templates, presets, eBooks",
        "start_followers": 1000,
        "monthly_range": "$500-$20,000+",
        "effort": "High upfront, low ongoing",
        "setup": [
            "Create a simple PDF guide or template related to your niche (1-3 days)",
            "Host on Gumroad (free), Stan Store, or Payhip",
            "Price between $7-$97 depending on depth",
            "Promote in every post caption and Story",
            "Build an email list to own your audience (Beehiiv, ConvertKit free tier)",
        ],
    },
    "brand_deals": {
        "description": "Long-term sponsorships with brands in your niche",
        "start_followers": 10000,
        "monthly_range": "$500-$50,000+",
        "effort": "Medium",
        "setup": [
            "Build a media kit (1-page PDF with stats, audience demo, rates)",
            "Reach out proactively to 10 brands/week",
            "Use platforms: AspireIQ, Grin, Creator.co, or direct email",
            "Negotiate: Usage rights, exclusivity, deliverables, timeline",
            "Always get a contract — even for barter deals",
        ],
    },
    "tiktok_creator_fund": {
        "description": "TikTok pays per 1K views (low, but passive)",
        "start_followers": 10000,
        "monthly_range": "$20-$200",
        "effort": "None (just post)",
        "setup": [
            "Requires 10K followers + 100K views in last 30 days",
            "Apply in TikTok Creator Marketplace",
            "Rate: ~$0.02-$0.04 per 1K views",
            "Better to use TikTok Series or LIVE gifting for more income",
        ],
    },
    "instagram_reels_bonus": {
        "description": "Instagram pays creators for Reels performance (invite-only)",
        "start_followers": 1000,
        "monthly_range": "$0-$35,000",
        "effort": "None (just post)",
        "setup": [
            "Must be invited by Instagram (US only currently)",
            "Keep posting Reels consistently to get noticed",
            "Rates vary wildly based on engagement and views",
        ],
    },
    "youtube_adsense": {
        "description": "Revenue share from ads shown on your videos",
        "start_followers": 1000,
        "monthly_range": "$100-$10,000+",
        "effort": "Low ongoing",
        "setup": [
            "Qualify: 1,000 subscribers + 4,000 watch hours (or 10M Shorts views)",
            "Apply for YouTube Partner Program (YPP)",
            "RPM (revenue per 1K views) averages $2-$10 depending on niche",
            "Finance/business niches earn $15-$50 RPM",
        ],
    },
}

# Niche evaluation criteria
_NICHE_DATA = {
    "luxury": {
        "monetization_score": 9,
        "competition": "Medium",
        "cpm": "High",
        "audience_size": "Large",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Lifestyle showcases", "Car reveals", "Property tours",
                          "Expensive item reviews", "Wealth mindset"],
        "best_monetization": ["affiliate_marketing", "shoutouts_sponsored_posts", "brand_deals"],
    },
    "finance": {
        "monetization_score": 10,
        "competition": "High",
        "cpm": "Very High",
        "audience_size": "Large",
        "best_platforms": ["YouTube", "TikTok", "Twitter"],
        "content_types": ["Tips/Hacks", "Investing 101", "Side hustle ideas",
                          "Budget breakdowns", "Success stories"],
        "best_monetization": ["affiliate_marketing", "digital_products", "brand_deals", "youtube_adsense"],
    },
    "fitness": {
        "monetization_score": 8,
        "competition": "Very High",
        "cpm": "Medium",
        "audience_size": "Very Large",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Workout routines", "Transformation content",
                          "Nutrition tips", "Gym advice", "Challenges"],
        "best_monetization": ["affiliate_marketing", "digital_products", "shoutouts_sponsored_posts"],
    },
    "fashion": {
        "monetization_score": 7,
        "competition": "Very High",
        "cpm": "Medium",
        "audience_size": "Very Large",
        "best_platforms": ["TikTok", "Instagram", "Pinterest"],
        "content_types": ["OOTD", "Hauls", "Styling tips", "Trend breakdowns", "Outfit dupes"],
        "best_monetization": ["affiliate_marketing", "brand_deals", "instagram_reels_bonus"],
    },
    "comedy": {
        "monetization_score": 6,
        "competition": "High",
        "cpm": "Low",
        "audience_size": "Very Large",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Skits", "POV videos", "Relatable content", "Parody", "Reactions"],
        "best_monetization": ["shoutouts_sponsored_posts", "brand_deals", "tiktok_creator_fund"],
    },
    "food": {
        "monetization_score": 7,
        "competition": "Very High",
        "cpm": "Medium",
        "audience_size": "Very Large",
        "best_platforms": ["TikTok", "Instagram", "YouTube"],
        "content_types": ["Quick recipes", "Restaurant reviews", "Cooking tips",
                          "Food reviews", "Mukbang"],
        "best_monetization": ["affiliate_marketing", "brand_deals", "digital_products"],
    },
    "travel": {
        "monetization_score": 7,
        "competition": "High",
        "cpm": "Medium-High",
        "audience_size": "Large",
        "best_platforms": ["Instagram", "YouTube", "TikTok"],
        "content_types": ["Destination guides", "Budget tips", "Vlog highlights",
                          "Hotel reviews", "Hidden gems"],
        "best_monetization": ["affiliate_marketing", "brand_deals", "digital_products"],
    },
    "cars": {
        "monetization_score": 8,
        "competition": "Medium",
        "cpm": "High",
        "audience_size": "Large",
        "best_platforms": ["YouTube", "TikTok", "Instagram"],
        "content_types": ["Car reviews", "Modification showcases", "Drag races",
                          "Buying guides", "Dream car content"],
        "best_monetization": ["affiliate_marketing", "brand_deals", "youtube_adsense"],
    },
}

_DEFAULT_NICHE = {
    "monetization_score": 6,
    "competition": "Medium",
    "cpm": "Medium",
    "audience_size": "Medium",
    "best_platforms": ["TikTok", "Instagram", "YouTube"],
    "content_types": ["Educational tips", "Entertainment", "Behind-the-scenes",
                      "Trending reactions", "Product reviews"],
    "best_monetization": ["affiliate_marketing", "shoutouts_sponsored_posts"],
}


def evaluate_niche(niche: str) -> dict:
    """Evaluate a niche for theme page viability."""
    data = _NICHE_DATA.get(niche.lower(), _DEFAULT_NICHE)

    # Calculate overall opportunity score
    score = data["monetization_score"]
    competition_penalty = {"Low": 0, "Medium": -1, "High": -2, "Very High": -3}.get(
        data["competition"], -1
    )
    final_score = max(1, score + competition_penalty)

    verdict = (
        "Excellent opportunity" if final_score >= 8 else
        "Good opportunity" if final_score >= 6 else
        "Viable but competitive" if final_score >= 4 else
        "Consider a sub-niche for less competition"
    )

    return {
        "niche": niche,
        "evaluation": {
            "monetization_potential": f"{data['monetization_score']}/10",
            "competition_level": data["competition"],
            "average_cpm": data["cpm"],
            "audience_size": data["audience_size"],
            "opportunity_score": f"{final_score}/10",
            "verdict": verdict,
        },
        "best_platforms": data["best_platforms"],
        "content_types": data["content_types"],
        "recommended_monetization": [
            _MONETIZATION[m]["description"]
            for m in data["best_monetization"]
            if m in _MONETIZATION
        ],
        "sub_niche_ideas": _sub_niche_ideas(niche),
        "differentiation_angles": [
            f"Focus on a specific sub-audience (e.g., '{niche} for beginners')",
            f"Pick an underserved format (e.g., '{niche} in 60 seconds')",
            f"Geographic angle (e.g., '{niche} in [your city]')",
            f"Persona-based (e.g., 'Budget {niche} king/queen')",
        ],
    }


def _sub_niche_ideas(niche: str) -> list:
    sub_niches = {
        "fitness": ["Calisthenics", "Home workouts", "Women's lifting", "Senior fitness",
                    "Sports-specific training"],
        "finance": ["Crypto investing", "Real estate", "Teen/student finance", "Side hustles",
                    "FIRE movement"],
        "fashion": ["Thrift/secondhand", "Plus size", "Men's streetwear", "Minimalist capsule",
                    "Sustainable fashion"],
        "food": ["Vegan recipes", "High-protein meals", "Air fryer cooking", "Budget meals",
                 "Meal prep"],
        "travel": ["Solo travel", "Budget backpacking", "Digital nomad", "Luxury travel",
                   "Van life"],
        "luxury": ["Luxury cars", "Watches & accessories", "Private jets", "Mansions & real estate",
                   "Designer fashion"],
    }
    return sub_niches.get(niche.lower(), [
        f"Beginner {niche}",
        f"Advanced {niche}",
        f"Budget {niche}",
        f"{niche} for [specific demographic]",
        f"Daily {niche} tips",
    ])


def get_theme_page_playbook(niche: str, current_followers: int = 0) -> dict:
    """Return a complete step-by-step playbook for building a theme page.

    Covers: setup, content system, growth tactics, monetization roadmap.
    """
    niche_data = _NICHE_DATA.get(niche.lower(), _DEFAULT_NICHE)
    primary_platform = niche_data["best_platforms"][0].lower()

    phase_1 = {
        "name": "Foundation (Days 1-7)",
        "goal": "Set up accounts and post first 7 pieces of content",
        "tasks": [
            f"Create accounts on {', '.join(niche_data['best_platforms'][:3])}",
            "Choose a memorable, keyword-rich username (e.g., daily.{niche}, {niche}.world)",
            "Write bio using formula: [Hook] | [Value] | [CTA]",
            "Create a consistent profile photo (logo or aesthetic photo)",
            "Pick a color palette and aesthetic (use Canva for consistency)",
            f"Research top 10 {niche} accounts — analyze their best content",
            f"Post your first 7 {niche} videos/posts (1 per day)",
            "Follow 100 accounts in your niche and engage genuinely",
        ],
    }

    phase_2 = {
        "name": "Content System (Days 8-30)",
        "goal": "Hit 500+ followers and establish posting rhythm",
        "tasks": [
            "Build a content bank of 30 ideas using the 5 content pillars",
            "Batch create: film/design 1 week of content in 1-2 hour sessions",
            "Post daily at the same time (use scheduling tool: Later, Buffer)",
            "Use trending audio/sounds within 48 hours of them going viral",
            "Engage for 30 minutes/day: reply comments, comment on trending posts",
            "Track what performs — double down on your best-performing content type",
            "Start an email list on Day 14 (Beehiiv free tier, 0 followers needed)",
        ],
    }

    phase_3 = {
        "name": "Growth Acceleration (Days 31-90)",
        "goal": "Hit 2,000-5,000 followers and first monetization",
        "tasks": [
            "Identify your top 3 performing content formats — create 2x more of those",
            "Do 1 collab/duet/stitch per week with a creator in your niche",
            "Start affiliate marketing: join Amazon Associates, ClickBank",
            "Create your first digital product (PDF guide) — price at $7-$27",
            "Add a link-in-bio page (Stan Store has free tier)",
            "Post a 'growth hack' story/post once per week to attract followers",
            "Begin reaching out to brands for shoutout exchanges (no payment yet)",
        ],
    }

    phase_4 = {
        "name": "Monetization (Day 90+)",
        "goal": "Generate first $1,000/month from your theme page",
        "tasks": [
            "Create a rate sheet for sponsored posts based on your engagement rate",
            "Apply for TikTok Creator Marketplace and YouTube YPP if eligible",
            "Launch your second digital product (higher ticket: $47-$97)",
            "Pitch 10 brands per week in your niche for paid collaborations",
            "Build an email list to 500+ subscribers for direct marketing",
            "Consider paid promotion budget: $5-$10/day on best-performing content",
            "Document your theme page journey — meta-content builds massive audiences",
        ],
    }

    # Build the monetization roadmap
    best_monetization = [_MONETIZATION[m] for m in niche_data["best_monetization"] if m in _MONETIZATION]

    return {
        "niche": niche,
        "primary_platform": primary_platform,
        "all_platforms": niche_data["best_platforms"],
        "current_followers": current_followers,
        "phases": [phase_1, phase_2, phase_3, phase_4],
        "content_system": {
            "content_pillars": niche_data["content_types"],
            "posting_frequency": "1x/day minimum, 2-3x/day for fast growth",
            "content_ratio": {
                "educational": "40%",
                "entertainment": "30%",
                "promotional": "10%",
                "trending/reactive": "20%",
            },
            "batch_workflow": [
                "Sunday: plan 7 days of content ideas",
                "Monday: film/create batch (2-3 hours)",
                "Schedule via Later or TikTok's built-in scheduler",
                "Daily: 30min engagement + check analytics",
            ],
        },
        "monetization_roadmap": [
            {
                "method": m["description"],
                "start_at": f"{m['start_followers']}+ followers",
                "potential": m["monthly_range"],
                "effort": m["effort"],
                "first_steps": m["setup"][:3],
            }
            for m in best_monetization
        ],
        "conversion_tips": {
            "from_personal_to_theme": [
                "Archive or delete off-niche personal content",
                "Update username to niche-focused name",
                "Rewrite bio to target audience, not personal branding",
                "Change profile photo to niche-appropriate image",
                "Unfollow all non-niche accounts to reset algorithm signals",
            ],
            "content_curation_sources": [
                "Repost (with credit) trending content in your niche",
                f"Search Reddit r/{niche} for viral questions to answer",
                "Screenshot and react to viral tweets in your niche",
                "Recreate top-performing content from bigger creators",
                "Use AI (Claude, ChatGPT) to generate scripts and captions",
            ],
        },
        "tools_and_resources": {
            "content_creation": ["Canva (graphics)", "CapCut (video editing)", "InShot (mobile video)"],
            "scheduling": ["Later", "Buffer", "TikTok built-in scheduler"],
            "analytics": ["Social Blade", "HypeAuditor", "TikTok Analytics (Creator mode)"],
            "monetization": ["Stan Store", "Gumroad", "Linktree", "Amazon Associates"],
            "trend_research": ["social-media trends (this tool!)", "TikTok Discover", "YouTube Trending"],
        },
    }


def monetization_strategies(niche: str) -> dict:
    """Return all monetization strategies with setup guides for a niche."""
    niche_data = _NICHE_DATA.get(niche.lower(), _DEFAULT_NICHE)

    strategies = []
    for key, m in _MONETIZATION.items():
        relevant = key in niche_data["best_monetization"]
        strategies.append({
            "method": key,
            "description": m["description"],
            "relevant_for_niche": relevant,
            "start_followers_needed": m["start_followers"],
            "monthly_potential": m["monthly_range"],
            "effort_level": m["effort"],
            "setup_steps": m["setup"],
            "priority": "HIGH" if relevant else "MEDIUM",
        })

    strategies.sort(key=lambda x: (0 if x["priority"] == "HIGH" else 1, x["start_followers_needed"]))

    return {
        "niche": niche,
        "strategies": strategies,
        "quick_wins": [s for s in strategies if s["start_followers_needed"] == 0][:3],
        "income_stack_example": {
            "month_1": "Affiliate links in bio ($50-$200)",
            "month_3": "Affiliate + digital product ($300-$1,000)",
            "month_6": "All of above + shoutouts ($1,000-$5,000)",
            "month_12": "Full income stack + brand deals ($3,000-$20,000+)",
        },
    }
