# Social Trends CLI — Test Guide

## Unit Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/test_core.py -v
```

## End-to-End Tests (requires network)

```bash
pytest cli_anything/social_trends/tests/test_full_e2e.py -v
```

## Manual Smoke Tests

```bash
# Hashtag generation (no API key needed)
cli-anything-social-trends hashtags generate fitness --posts 3

# TikTok trending hashtags
cli-anything-social-trends trends tiktok --region US

# Account optimisation
cli-anything-social-trends accounts optimize tiktok --niche fitness

# Theme page guide
cli-anything-social-trends theme-pages guide --niche luxury

# Niche rankings
cli-anything-social-trends theme-pages niches

# Monetisation blueprint
cli-anything-social-trends theme-pages monetize fitness

# 4-week content calendar
cli-anything-social-trends theme-pages calendar fashion --platform instagram --weeks 4

# Cache stats
cli-anything-social-trends cache stats
```

## YouTube API Tests (requires API key)

```bash
cli-anything-social-trends config set youtube_api_key YOUR_KEY
cli-anything-social-trends trends youtube --region US --category 10
cli-anything-social-trends music youtube --region US
```
