# Social Trends CLI Harness

Agent-native CLI for scraping YouTube + TikTok viral trends, optimizing social media accounts, and building converting theme pages.

## Commands

### YouTube
```bash
social-trends youtube trending [--category all|music|gaming|movies|news] [--limit 20]
social-trends youtube hashtags [--limit 30]
social-trends youtube music [--limit 20]
social-trends youtube keywords [--limit 25]
```

### TikTok
```bash
social-trends tiktok hashtags [--limit 30] [--category NAME]
social-trends tiktok sounds [--limit 20]
social-trends tiktok effects [--limit 15]
social-trends tiktok niche NICHE [--limit 20]   # e.g. fitness, food, beauty, gaming
```

### Cross-Platform Analysis
```bash
social-trends analyze cross-platform [--limit 15]
social-trends analyze ideas NICHE [--count 10]
social-trends analyze viral-formulas [--type all|hook|structure|cta]
```

### Account Optimization
```bash
social-trends optimize checklist [--platform all|tiktok|youtube|instagram]
social-trends optimize posting-times [--platform all|tiktok|youtube|instagram|twitter]
social-trends optimize hacks [--platform tiktok|youtube|instagram]
social-trends optimize calendar [--platform tiktok|youtube|instagram] [--posts-per-week 7]
```

### Theme Pages
```bash
social-trends theme-pages [--section all|concept|niches|steps|sourcing|converting|funnel]
```

### Quick Shortcuts
```bash
social-trends viral [--type all|hook|structure|cta]
social-trends hacks [--platform tiktok|youtube|instagram]
```

## JSON Output (Agent Mode)
```bash
social-trends --json tiktok hashtags --limit 10
social-trends --json optimize calendar --platform tiktok
social-trends --json theme-pages --section niches
```

## REPL Mode
```bash
social-trends   # launches interactive REPL
```
