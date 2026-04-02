# Hermes 14-Day Marketing Playbook

> Zero to revenue. One terminal product. Two weeks.

---

## Before You Start: Setup Checklist

- [ ] `cp .env.example .env` and fill in `ANTHROPIC_API_KEY`
- [ ] Create Reddit app at reddit.com/prefs/apps (free, takes 2 min)
- [ ] Apply for Twitter/X developer account at developer.twitter.com
- [ ] Get Dev.to API key at dev.to/settings/extensions
- [ ] Run `./run.sh` once manually, review `output/` folder
- [ ] Bookmark: whop.com/sell → create product before Day 1

---

## Day 1–2: Foundation

**Goal:** Everything is live, one piece of real content posted.

### Tasks
- [ ] Publish landing page at hermes.sh (Cloudflare Pages, free)
- [ ] Create Whop product — 3 tiers: Free (trial), Pro $12/mo, Ultra $29/mo
- [ ] Write license key delivery webhook in Whop dashboard
- [ ] Post the HN "Show HN" — run `./run.sh` and copy `output/hn_*.md`
  - Post at **9 AM PST Tuesday or Wednesday** (peak HN traffic)
  - Stick around for 2 hours to reply to every comment personally
- [ ] Start the marketing daemon: `./run.sh --daemon`

**Time:** ~4 hours  
**Success metric:** HN post live, at least 10 upvotes, 1 paying customer

---

## Day 3–5: Reddit Blitz

**Goal:** Organic developer discovery across 5 subreddits.

### Subreddit order + angle
| Day | Subreddit | Post type | Best time (PST) |
|-----|-----------|-----------|-----------------|
| 3 | r/rust | Technical deep-dive on crates used | Tue 8 AM |
| 3 | r/commandline | Showcase with install demo | Tue 12 PM |
| 4 | r/SideProject | Honest launch post with metrics | Wed 9 AM |
| 5 | r/devops | Tool post — AI in the terminal | Thu 10 AM |
| 5 | r/programming | Link to HN thread or blog post | Thu 2 PM |

### Rules
- Read each subreddit's sidebar rules before posting
- Never post the same content twice
- Reply to every comment within 1 hour on launch day
- Don't mention pricing in the title — leads with value

**Time:** 30 min/day  
**Success metric:** At least one post reaches top 10 of the day in its sub

---

## Day 6–7: Twitter/X Launch Threads

**Goal:** Developer Twitter awareness, thread virality.

### Tasks
- [ ] Post the "Speed thread" (benchmarks) — Monday 9 AM PST
- [ ] Post the "Story thread" (origin story) — Tuesday 10 AM PST
- [ ] Manually engage: reply to anyone who quotes/likes, ask a question
- [ ] Find 10 developer accounts (CLI/Rust/AI tools) and reply with value
- [ ] DM 3-5 developer influencers with a genuine note (not a pitch)

**What NOT to do:**
- Don't post all 5 threads in one day — looks like spam
- Don't buy followers or engagement pods
- Don't auto-DM people who follow you

**Time:** 1 hour/day  
**Success metric:** One thread gets 50+ likes organically

---

## Day 8–9: Dev.to Article

**Goal:** Evergreen SEO content + Dev.to community discovery.

### Tasks
- [ ] Run `./run.sh` once — `DevToAgent` generates and publishes the article
- [ ] Review the draft at dev.to/dashboard before it goes public
- [ ] Add 2-3 screenshots (terminal output, TUI) to the article
- [ ] Share the published URL on Twitter, Reddit (r/rust, r/programming)
- [ ] Cross-post to Hashnode if you have an account there

**Article angle:** "I built a Rust terminal for Claude AI — here's what I learned"  
This performs well because it's technical, personal, and searchable.

**Time:** 2 hours (review + share)  
**Success metric:** Article gets 500+ views on Dev.to in first 48h

---

## Day 10: ProductHunt Prep

**Goal:** Everything ready for a clean PH launch.

### Tasks
- [ ] Create ProductHunt account (if you don't have one)
- [ ] Get a hunter with 500+ followers to post it (or post yourself)
- [ ] Write tagline: "The terminal Claude deserves. Built in Rust."
- [ ] Prepare gallery: 5 screenshots (install, TUI, query, settings, pricing)
- [ ] Write first comment (post immediately at launch): your personal story
- [ ] Line up 20 people who will upvote Day 1 (friends, beta users, Discord)
- [ ] Schedule launch for a Tuesday or Wednesday

**Time:** 3 hours  
**Success metric:** Draft submitted, hunter confirmed, gallery ready

---

## Day 11: ProductHunt Launch

**Goal:** Top 5 Product of the Day.

### Timeline (PST)
- **12:01 AM** — Post goes live (PH resets at midnight PST)
- **12:05 AM** — Post your first comment (personal story + what makes Hermes different)
- **7–9 AM** — Most PH traffic; be online and reply to every comment
- **12 PM** — Share PH link on all channels (Twitter, Reddit, HN)
- **6 PM** — Final push: email your list, post in any Slack/Discord communities
- **11:59 PM** — Check ranking, respond to any final comments

### Do NOT do on launch day
- Don't ask people to "upvote" — say "check it out and let me know what you think"
- Don't buy upvotes — PH detects and bans
- Don't go dark — be responsive all day

**Time:** Full day  
**Success metric:** Top 10 Product of the Day, 5+ new paying customers

---

## Day 12–13: Follow-Up Content

**Goal:** Convert launch momentum to subscribers.

### Tasks
- [ ] Post "we launched" tweet with PH results and metrics
- [ ] Reply to all remaining PH, HN, Reddit comments
- [ ] Post a "lessons learned" Dev.to article (performance well)
- [ ] Email everyone who signed up for trial: offer 30% off Pro for 48h
- [ ] Fix any bugs reported during launch — ship a patch
- [ ] Post in r/SideProject: "Launched on PH, here are the results"

**Time:** 2 hours/day  
**Success metric:** 20+ paying customers, 3 reviews on Whop

---

## Day 14: Metrics Review

**Goal:** Know what worked, double down.

### Metrics to track
| Metric | Where to find it |
|--------|-----------------|
| Installs | GitHub releases download count |
| Trial activations | Whop dashboard → memberships |
| Paid conversions | Whop dashboard → revenue |
| PH ranking | producthunt.com/posts/hermes |
| Reddit traffic | Google Analytics / Cloudflare |
| HN points | news.ycombinator.com |
| Dev.to views | dev.to/dashboard |

### Pricing adjustment rules
- If free→paid conversion < 5%: improve onboarding (Day 1 experience)
- If churn > 20% month 1: talk to churned users, fix the top complaint
- If Ultra is outselling Pro: the tiers may be wrong — consider adjusting

---

## Channels Ranked by ROI (for developer tools)

1. **Hacker News Show HN** — highest quality traffic, brutal but worth it
2. **Reddit r/rust + r/commandline** — tight community, very sticky if they like you
3. **Dev.to** — great for SEO, devs browse it like a magazine
4. **Twitter/X threads** — high reach if even one thread goes semi-viral
5. **ProductHunt** — good for launch spike, rarely sustains traffic
6. **YouTube demos** — slow to build but evergreen; one good video = months of installs
7. **Newsletter sponsorships** — expensive, skip in first 30 days

---

## What NOT to Do

- **Buy fake upvotes/reviews** — platforms ban you and it destroys trust permanently
- **Spam subreddits** — instant ban, ruins your account for future legitimate posts
- **Promise features you don't have** — developers remember, they will call you out
- **Ghost negative comments** — address them directly, even if the criticism is harsh
- **Post at 3 AM PST** — nobody sees it
- **Launch on Monday or Friday** — dead traffic days

---

## Handling Negative Comments

### "Why not just use the official claude-code CLI?"
> "Fair question. claude-code is great if you're already in VS Code. Hermes is for devs who live in the terminal and want a native Rust TUI — faster startup, lower memory, works over SSH. Different tool for a different workflow."

### "This is just a wrapper around the API"
> "So is VS Code's Copilot, Cursor, and Windsurf. The value is the UX, the workflow integration, and the offline license grace period. The binary is 12 MB and starts in 80 ms — that's not nothing."

### "The free tier is too limited"
> "You're right that 50 messages/day is a real limit. It's there to make the business viable so I can keep building. If it's too tight, Pro at $12/mo removes all limits — that's less than a lunch."

### HN cynics: "Why does this need to be a paid product?"
> "I spent months building this. Charging $12/mo is what lets me keep improving it instead of abandoning it like most side projects. The API key is yours — I never touch your data or your Claude bill."

---

## Marketing Daemon Commands

```bash
# Start (foreground, see output live)
cd hermes-infra/marketing && ./run.sh

# Start (background, runs forever)
cd hermes-infra/marketing && ./run.sh --daemon

# Watch logs
tail -f hermes-infra/marketing/output/hermes-marketing.log

# Stop daemon
kill $(cat hermes-infra/marketing/output/hermes.pid)

# View generated content
ls -lt hermes-infra/marketing/output/
```
