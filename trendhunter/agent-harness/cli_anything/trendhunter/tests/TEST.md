# TrendHunter — Test Plan

## Unit Tests (`test_core.py`)

### YouTubeVideo
| Test | Status |
|------|--------|
| to_dict returns all fields | PASS |
| URL included in dict | PASS |

### extract_hashtags_from_videos
| Test | Status |
|------|--------|
| Counts and ranks by frequency | PASS |
| Respects top_n limit | PASS |

### TikTokHashtag
| Test | Status |
|------|--------|
| to_dict includes proper URL | PASS |
| Fallback list returns evergreen tags | PASS |

### TrendAnalyzer
| Test | Status |
|------|--------|
| Cross-platform bonus increases score | PASS |
| Score capped at 100 | PASS |
| Niche detection — fitness | PASS |
| Multi-niche detection | PASS |
| analyze_trends returns TrendReport | PASS |
| Cross-platform tags appear on both platforms | PASS |
| Music merged from both sources | PASS |
| Viral hooks generated | PASS |
| get_recommended_hashtags respects count | PASS |
| All tags start with # | PASS |

### AccountOptimizer
| Test | Status |
|------|--------|
| Posting schedule returns time slots | PASS |
| All bio formulas are strings | PASS |
| Engagement tactics have required keys | PASS |
| Platform filter works | PASS |
| Growth increases followers | PASS |
| More posts = more growth | PASS |
| Content pillars returned for known niche | PASS |
| Unknown niche falls back gracefully | PASS |
| Full optimize_account report generated | PASS |

### ThemePage
| Test | Status |
|------|--------|
| Finance niche has high monetization score | PASS |
| Partial niche match works | PASS |
| Unknown niche fallback | PASS |
| Conversion funnel has 5 stages | PASS |
| Each stage has KPI + tactics | PASS |
| Link-in-bio tools listed | PASS |
| Monetization strategies ≥ 5 | PASS |
| All strategies have required fields | PASS |
| CTA templates ≥ 5 | PASS |
| YouTube gets extra CTAs | PASS |
| Growth playbook has 5 phases | PASS |
| Each phase has ≥ 3 actions | PASS |
| Conversion rate calculation correct | PASS |
| Zero followers returns empty | PASS |

## Run Tests

```bash
cd trendhunter/agent-harness
pip install -e .
pytest cli_anything/trendhunter/tests/ -v
```
