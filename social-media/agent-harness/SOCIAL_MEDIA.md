# social-cli Agent Harness

Agent-native CLI for social media automation: viral trend scraping (YouTube + TikTok), account optimization, and theme page strategy.

## Setup

```bash
cd social-media/agent-harness
pip install -e .
social-cli --help
```

## Agent Task Examples

### Fetch viral trends and implement to accounts

```bash
# Step 1: Get TikTok trending data for finance niche
social-cli --json trends tiktok --niche finance > tiktok_trends.json

# Step 2: Get YouTube trending (no API key needed)
social-cli --json trends youtube --no-api --region US > yt_trends.json

# Step 3: Combined report
social-cli --json trends all --niche finance > combined_trends.json
```

### Optimize all accounts

```bash
# Create accounts config
cat > accounts.json << 'EOF'
[
  {"platform": "tiktok", "username": "mypage1", "followers": 3200, "niche": "finance"},
  {"platform": "youtube", "username": "mychannel", "followers": 850, "niche": "finance"},
  {"platform": "instagram", "username": "myig", "followers": 1200, "niche": "lifestyle"}
]
EOF

# Run full optimization across all accounts
social-cli --json optimize all --config accounts.json > optimization_report.json
```

### Build theme page strategy

```bash
# Get full blueprint for a finance theme page
social-cli --json theme blueprint --niche finance > finance_blueprint.json

# Get conversion funnel strategy
social-cli --json theme convert --niche finance --followers 5000 --page-type theme_page
```

## Output Format (JSON)

All commands support `--json` flag for structured output compatible with agent pipelines.

```bash
social-cli --json trends tiktok --niche fitness
# Returns: {"platform":"tiktok","fetched_at":"...","trending_hashtags":[...],"trending_sounds":[...],...}
```

## Environment Variables

```bash
export YOUTUBE_API_KEY="YOUR_KEY"  # Optional: enables full YouTube Data API v3
```
