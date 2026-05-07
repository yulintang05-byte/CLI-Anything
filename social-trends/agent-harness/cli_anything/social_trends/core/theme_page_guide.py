"""Theme page creation, conversion, and monetization playbook."""

from datetime import datetime, timezone
from typing import Optional


# Profitable niches ranked by revenue potential and competition
THEME_PAGE_NICHES: list[dict] = [
    {
        "niche": "Luxury Lifestyle",
        "handle_format": "@luxury.{keyword} / @{keyword}.luxe",
        "difficulty": "Low",
        "revenue_potential": "High",
        "avg_monthly_revenue": "$2,000-15,000",
        "content_sources": ["Pinterest", "YouTube clips", "Unsplash", "luxury brand social"],
        "monetization": ["Affiliate links (luxury products)", "Shoutouts ($50-500/post)", "Amazon luxury storefronts", "Luxury brand partnerships"],
        "audience_demographics": "25-45, aspirational middle class, brand-aware",
        "best_platforms": ["Instagram", "TikTok", "Pinterest"],
        "content_ideas": ["Luxury car reveals", "mansion tours", "designer unboxings", "wealth motivation quotes", "billionaire quotes"],
        "example_accounts": ["@luxury", "@richlife", "@millionaire.mindset"],
        "growth_speed": "Fast (1-3 months to 10K)",
        "notes": "Extremely broad appeal. Best for beginners. Partner with luxury affiliate programs early.",
    },
    {
        "niche": "Fitness Motivation",
        "handle_format": "@{keyword}.gains / @lift.{keyword}",
        "difficulty": "Medium",
        "revenue_potential": "Very High",
        "avg_monthly_revenue": "$3,000-25,000",
        "content_sources": ["YouTube fitness channels", "Reddit r/fitness", "fitness influencer reposts"],
        "monetization": ["Supplement affiliates (20-30% commission)", "Online coaching upsell", "Fitness app partnerships", "Merchandise"],
        "audience_demographics": "18-35, gym-goers, health-conscious",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_ideas": ["Transformation reveals", "workout tips", "gym fails", "diet advice", "athlete highlights"],
        "example_accounts": ["@gymtok", "@fitnessmotivation", "@gains.daily"],
        "growth_speed": "Medium (3-6 months to 10K)",
        "notes": "Supplement brands pay highest affiliate rates. Build trust before promoting products.",
    },
    {
        "niche": "Aesthetic / Minimalist",
        "handle_format": "@.{keyword}.aesthetic / @{keyword}.vibes",
        "difficulty": "Low",
        "revenue_potential": "Medium",
        "avg_monthly_revenue": "$500-5,000",
        "content_sources": ["Pinterest", "Unsplash", "Pexels", "Tumblr archives", "aesthetic photographers"],
        "monetization": ["Shoutouts", "Digital presets/filters", "Print-on-demand (aesthetic posters)", "Home decor affiliates"],
        "audience_demographics": "15-25, female-skewing, style-conscious",
        "best_platforms": ["Instagram", "Pinterest", "TikTok"],
        "content_ideas": ["Room aesthetics", "outfit moodboards", "color palette collections", "lo-fi study content", "aesthetic quotes"],
        "example_accounts": ["@softgirl.aesthetic", "@dark.academia", "@cottagecore.daily"],
        "growth_speed": "Fast (1-2 months to 10K with consistent posting)",
        "notes": "Low barrier to entry. Grow fast by reposting curated Pinterest content. Monetize via shoutouts first.",
    },
    {
        "niche": "Finance / Money",
        "handle_format": "@{keyword}.money / @make.{keyword}",
        "difficulty": "Medium",
        "revenue_potential": "Very High",
        "avg_monthly_revenue": "$5,000-50,000",
        "content_sources": ["Finance YouTube (Graham Stephan, Andrei Jikh)", "Reddit r/personalfinance", "Investopedia"],
        "monetization": ["Brokerage affiliates ($50-200 per signup)", "Credit card affiliates ($100-500 per approval)", "Course sales", "Financial newsletter"],
        "audience_demographics": "22-40, career-focused, wants financial freedom",
        "best_platforms": ["TikTok", "YouTube", "Instagram"],
        "content_ideas": ["Budget breakdowns", "investing 101", "passive income ideas", "debt payoff stories", "side hustles"],
        "example_accounts": ["@financewithsharan", "@wealthbuilder", "@investingtips"],
        "growth_speed": "Slow (6-12 months due to trust requirement)",
        "notes": "Highest CPM on YouTube ($15-50). Build authority slowly. FinCEN compliance required for financial advice.",
    },
    {
        "niche": "Food & Recipes",
        "handle_format": "@{keyword}.eats / @{keyword}.kitchen",
        "difficulty": "Medium",
        "revenue_potential": "High",
        "avg_monthly_revenue": "$1,000-10,000",
        "content_sources": ["YouTube recipe channels", "TikTok food creators", "Pinterest", "food blogs"],
        "monetization": ["Kitchen affiliate products (Amazon)", "Meal kit affiliates (HelloFresh, $20-40/signup)", "Cookbook promotions", "Brand partnerships"],
        "audience_demographics": "25-50, home cooks, food enthusiasts",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_ideas": ["Viral recipe recreations", "food hacks", "restaurant reviews", "mukbang clips", "ingredient substitutions"],
        "example_accounts": ["@foodtok", "@easyrecipes", "@chefpov"],
        "growth_speed": "Fast (2-4 months to 10K)",
        "notes": "Food content goes viral easily. Always credit original creators. Meal kit programs have highest EPC.",
    },
    {
        "niche": "Motivation / Mindset",
        "handle_format": "@{keyword}.mindset / @daily.{keyword}",
        "difficulty": "Low",
        "revenue_potential": "Medium-High",
        "avg_monthly_revenue": "$1,000-8,000",
        "content_sources": ["YouTube (David Goggins, Jocko Willink, Hormozi)", "Podcasts clips", "TED Talks", "quotes databases"],
        "monetization": ["Productivity app affiliates", "Book affiliates", "Shoutouts", "Own e-book/course", "Coaching"],
        "audience_demographics": "18-35, self-improvement focused, entrepreneurial",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_ideas": ["Motivational speech clips", "success quotes", "entrepreneur stories", "daily challenges", "discipline content"],
        "example_accounts": ["@dailymotivation", "@mindset.daily", "@entrepreneurquotes"],
        "growth_speed": "Fast (1-3 months to 10K)",
        "notes": "Oversaturated but still profitable. Differentiate with a specific sub-niche (e.g., military discipline, female entrepreneurship).",
    },
    {
        "niche": "Travel",
        "handle_format": "@{keyword}.travel / @explore.{keyword}",
        "difficulty": "Medium",
        "revenue_potential": "High",
        "avg_monthly_revenue": "$2,000-20,000",
        "content_sources": ["YouTube travel vloggers", "Drone footage (royalty-free)", "Travel photographers", "Airbnb listings"],
        "monetization": ["Travel credit card affiliates ($100-500/signup)", "Hotel/booking affiliates", "Travel insurance affiliates", "Tourism board partnerships"],
        "audience_demographics": "20-40, travel dreamers, experiences-over-things mindset",
        "best_platforms": ["Instagram", "TikTok", "YouTube"],
        "content_ideas": ["Hidden gems in [country]", "travel hacks", "budget travel", "luxury travel", "solo travel tips"],
        "example_accounts": ["@travel", "@worldwanderer", "@nomadic.daily"],
        "growth_speed": "Medium (3-6 months to 10K)",
        "notes": "Best affiliate commissions from credit cards and booking platforms. Geographic niching (e.g., only Southeast Asia) grows faster.",
    },
    {
        "niche": "Pet / Animals",
        "handle_format": "@{keyword}.pets / @{animal}.daily",
        "difficulty": "Low",
        "revenue_potential": "Medium",
        "avg_monthly_revenue": "$500-4,000",
        "content_sources": ["Reddit r/aww", "YouTube pet channels", "Instagram pet accounts"],
        "monetization": ["Pet food affiliates (Chewy 4% commission)", "Pet product affiliates", "Shoutouts", "NFT pet art"],
        "audience_demographics": "All ages, heavy female skew, high emotional engagement",
        "best_platforms": ["TikTok", "Instagram", "YouTube Shorts"],
        "content_ideas": ["Funny pet compilations", "pet transformation", "pet reaction videos", "animal rescues", "exotic pets"],
        "example_accounts": ["@pettok", "@dogsoftiktok", "@animalsbeingbros"],
        "growth_speed": "Very Fast (under 1 month to 10K with viral content)",
        "notes": "Viral potential is very high. Low monetization per follower. Build large audiences quickly and monetize via merch or shoutouts.",
    },
]

# Step-by-step page setup guide
PAGE_SETUP_CHECKLIST = [
    {
        "phase": "1. Niche Selection & Validation",
        "steps": [
            "Choose a niche with 500K+ hashtag posts — confirms active audience",
            "Verify 5+ monetization methods exist before committing",
            "Identify your top 5 competitor accounts — note their follower count and engagement",
            "Check if the niche has a dedicated community (subreddit, Facebook group, Discord)",
            "Validate with 10 test posts across 2 weeks before full commitment",
        ],
    },
    {
        "phase": "2. Account & Brand Setup",
        "steps": [
            "Choose a handle: [niche].[keyword] format (e.g., @luxury.daily, @fitness.hq)",
            "Create a logo: Canva free tier, keep it simple (icon + niche word)",
            "Write your optimized bio (see: social-trends bio optimize command)",
            "Set up link-in-bio: Stan.store (best for monetization) or Linktree (free)",
            "Connect Instagram, TikTok, and YouTube as a trio from day 1",
            "Set up a business email (Gmail with niche domain or simple format)",
        ],
    },
    {
        "phase": "3. Content Sourcing System",
        "steps": [
            "Create a 'swipe file' folder: save 50 pieces of viral content in your niche",
            "Set up Google Alerts for your niche keywords (free trend monitoring)",
            "Follow 20 seed accounts in your niche and save their top posts",
            "Build a content calendar: plan 30 days of content in one sitting",
            "Source content from: Pinterest, YouTube (Creative Commons), Pexels, Unsplash, Reddit",
            "ALWAYS credit original creators — DM for permission on best content",
        ],
    },
    {
        "phase": "4. Content Repurposing Workflow",
        "steps": [
            "Download source content (yt-dlp for YouTube, SnapTik for TikTok)",
            "Edit: add your watermark/overlay, change music to trending sound, add captions",
            "Batch create 7 days of content in one 2-hour session",
            "Use CapCut (free) or Premiere Rush for quick mobile edits",
            "Apply consistent color grade/filter for brand cohesion",
            "Add text overlays with your niche's common pain points or desires",
        ],
    },
    {
        "phase": "5. Growth Execution",
        "steps": [
            "Post at optimal times (see: social-trends schedule command)",
            "Use the right hashtag mix (see: social-trends hashtags niche command)",
            "Engage with 30 posts in your niche daily (comment, like, follow)",
            "Respond to every comment on your posts within 60 minutes",
            "Run weekly engagement pods (DM 5 similar accounts to like/comment each other's posts)",
            "Do 2 Duets/Stitches per week with viral content in your niche",
        ],
    },
    {
        "phase": "6. Monetization Activation",
        "steps": [
            "At 1K followers: Start shoutouts ($5-20/post) via SocialBook or direct DMs",
            "At 5K followers: Apply to affiliate programs in your niche",
            "At 10K followers: Launch digital product (template, guide, preset)",
            "At 25K followers: Pitch brand deals proactively (email template below)",
            "At 50K followers: Apply for TikTok Creator Fund and YouTube Partner Program",
            "At 100K followers: Launch paid community or online course",
        ],
    },
]

# Brand pitch email template
BRAND_PITCH_TEMPLATE = """Subject: Partnership Opportunity — @{handle} x {brand_name}

Hi {brand_name} Team,

I run @{handle}, a {niche} page with {followers} followers and {avg_engagement}% engagement rate on {platform}.

My audience is {demographic} — highly aligned with {brand_name}'s target customer.

I'd love to explore a partnership. I'm proposing:
- {post_count} sponsored post(s) on {platform}
- Estimated reach: {estimated_reach}+ views
- Rate: ${rate} (negotiable)

Happy to share my media kit and analytics. Let me know if you'd like to connect.

Best,
{name}
@{handle}
{email}
"""

# Content transformation techniques (for legal/ethical repurposing)
CONTENT_TRANSFORMATION_METHODS = [
    {
        "method": "Commentary Overlay",
        "description": "Add your reaction text or voiceover on top of viral clips",
        "legality": "Protected as transformative use (Fair Use)",
        "tools": ["CapCut", "Premiere Rush", "DaVinci Resolve"],
        "effort": "Low",
    },
    {
        "method": "Compilation Format",
        "description": "Curate 5-10 clips into a themed compilation with your branding",
        "legality": "Get permission from creators via DM — most will say yes for credit",
        "tools": ["CapCut", "iMovie", "Premiere"],
        "effort": "Medium",
    },
    {
        "method": "Quote Graphics",
        "description": "Turn viral quotes from videos/podcasts into static or animated posts",
        "legality": "Quotes under 250 words with attribution are generally safe",
        "tools": ["Canva", "Adobe Express", "Mojo"],
        "effort": "Very Low",
    },
    {
        "method": "Trend Recreation",
        "description": "Recreate a viral trend in your niche with your own footage/voiceover",
        "legality": "Fully original — you own this content",
        "tools": ["Smartphone + CapCut"],
        "effort": "Medium",
    },
    {
        "method": "Screen Recording + Commentary",
        "description": "Screen-record interesting content with your live audio commentary",
        "legality": "Commentary qualifies as transformative under Fair Use",
        "tools": ["iPhone built-in recorder", "OBS Studio"],
        "effort": "Low",
    },
    {
        "method": "AI-Generated Graphics",
        "description": "Generate niche-relevant images with Midjourney/DALL-E, add to posts",
        "legality": "100% original — you own the output (check ToS per platform)",
        "tools": ["Midjourney", "DALL-E 3", "Adobe Firefly"],
        "effort": "Low",
    },
]


def get_niche_guide(niche: Optional[str] = None) -> dict:
    """Return detailed guide for a specific niche or all niches ranked."""
    if niche:
        niche_lower = niche.lower()
        matches = [n for n in THEME_PAGE_NICHES if niche_lower in n["niche"].lower()]
        if matches:
            result = matches[0].copy()
            result["setup_checklist"] = PAGE_SETUP_CHECKLIST
            result["brand_pitch_template"] = BRAND_PITCH_TEMPLATE
            return result
        return {
            "error": f"Niche '{niche}' not found",
            "available_niches": [n["niche"] for n in THEME_PAGE_NICHES],
        }

    return {
        "niches": THEME_PAGE_NICHES,
        "total": len(THEME_PAGE_NICHES),
        "sorted_by": "revenue potential",
        "recommendation": "Start with Aesthetic or Motivation for fastest growth with lowest barrier. Pivot to Finance or Fitness once you understand content marketing.",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def get_setup_checklist(phase: Optional[int] = None) -> dict:
    """Return the complete page setup checklist or a specific phase."""
    if phase is not None and 1 <= phase <= len(PAGE_SETUP_CHECKLIST):
        return {
            "phase": PAGE_SETUP_CHECKLIST[phase - 1],
            "total_phases": len(PAGE_SETUP_CHECKLIST),
            "completion_tip": "Complete each phase fully before moving to the next.",
        }
    return {
        "checklist": PAGE_SETUP_CHECKLIST,
        "total_phases": len(PAGE_SETUP_CHECKLIST),
        "estimated_time": "2-4 weeks to complete all phases and see first monetization",
        "success_factors": [
            "Consistency (posting daily for 90 days minimum)",
            "Niche specificity (the narrower, the faster you grow)",
            "Quality over quantity after 1K followers",
            "Community engagement every single day",
            "Testing and doubling down on what works",
        ],
    }


def get_content_transformation_guide() -> dict:
    """Return methods for legally and ethically repurposing content."""
    return {
        "methods": CONTENT_TRANSFORMATION_METHODS,
        "legal_disclaimer": (
            "Always credit original creators. Fair Use is a defense, not a right — "
            "if a creator asks you to remove content, do so immediately. "
            "Building your own original content over time reduces legal risk to zero."
        ),
        "best_practice": "Ask permission first via DM. Most small creators will say yes in exchange for credit and exposure.",
        "dmca_protection": [
            "Don't repost content from verified/large creators without explicit permission",
            "Transform content — don't just re-upload raw clips",
            "Always add significant value (commentary, editing, context)",
            "Keep records of permission messages you receive",
        ],
    }


def generate_brand_pitch(
    handle: str,
    brand_name: str,
    niche: str,
    followers: int,
    platform: str,
    avg_engagement: float,
    rate: int,
    name: str,
    email: str,
    demographic: str = "engaged followers interested in {niche}",
) -> dict:
    """Generate a customized brand partnership pitch email."""
    est_reach = int(followers * (avg_engagement / 100) * 3.5)
    post_count = 1 if followers < 50000 else 3

    filled = BRAND_PITCH_TEMPLATE.format(
        handle=handle,
        brand_name=brand_name,
        niche=niche,
        followers=f"{followers:,}",
        avg_engagement=f"{avg_engagement:.1f}",
        platform=platform,
        demographic=demographic.format(niche=niche),
        post_count=post_count,
        estimated_reach=f"{est_reach:,}",
        rate=f"{rate:,}",
        name=name,
        email=email,
    )

    return {
        "pitch_email": filled,
        "tips": [
            "Send on Tuesday or Wednesday morning for highest open rates",
            "Follow up exactly 7 days later if no response",
            "Include a 1-page media kit PDF with your top 3 posts and analytics screenshot",
            "Price your first deals 30% lower to build a portfolio of brand partnerships",
            f"Target estimated rate range for {followers:,} followers: ${followers // 1000 * 10}-${followers // 1000 * 30}/post",
        ],
    }
