# Hermes Marketing Playbook — 14-Day Launch Plan

A focused, realistic 14-day playbook for launching a developer CLI tool.
No growth-hacking tricks, no purchased engagement. Just honest distribution
in the communities that actually use these tools.

---

## Day 1–2: Setup & First Manual Run

### Tasks
- [ ] Copy `.env.example` to `.env` and fill in at minimum `ANTHROPIC_API_KEY`
- [ ] Run the agent once manually: `bash run.sh`
- [ ] Read every piece of generated content in `output/` before posting anything
- [ ] Edit and polish the generated Hacker News "Show HN" post
- [ ] Post the Show HN: `Show HN: CLI-Anything – [one-line description]`
  - Post between 9–11 AM PST on a weekday for best visibility
  - Use a personal account with post history, not a throwaway
  - Your first comment should be a genuine explanation of why you built it

### Time estimate
2–3 hours over two days

### Success metric
- HN post reaches the "Show HN" front page (top ~30) or receives ≥10 genuine comments
- At least 1 person says "I'd use this"

---

## Day 3–5: Reddit Blitz

### Subreddits (in priority order)
1. **r/rust** — if any Rust is involved; highest-quality developer audience
2. **r/commandline** — natural home for CLI tools
3. **r/SideProject** — tolerant of self-promotion when genuine
4. **r/devops** — relevant if the tool touches automation or pipelines

### Tasks
- [ ] Write a separate, community-tailored post for each subreddit
  - Do NOT cross-post the exact same text — each community notices
  - r/rust: focus on performance and correctness
  - r/commandline: focus on UX, keybindings, composability with other tools
  - r/SideProject: tell the personal story of building it
  - r/devops: focus on automation use cases and scripting
- [ ] Post one per day maximum; space them out so you can respond to comments
- [ ] Reply to every comment within 4 hours of posting — engagement lifts visibility
- [ ] Do NOT post the same day as your HN post — spread the surface area

### Time estimate
45–60 minutes per post including comment responses

### Success metric
- Each post reaches the subreddit's "Hot" page for at least a few hours
- Combined: ≥20 upvotes and ≥5 substantive comments across all posts

---

## Day 6–7: Twitter/X Launch Threads

### Tasks
- [ ] Review and edit the agent-generated thread drafts in `output/`
- [ ] Thread 1 (Day 6): The "why I built this" story thread — personal, specific, honest
  - Hook tweet must be a statement or question, not "I built a thing"
  - 6–10 tweets maximum; quality over quantity
- [ ] Thread 2 (Day 7): The "here's what it actually does" demo thread
  - Include a GIF or short screen recording of a real workflow
  - Show the before/after — what was annoying, what is now fast
- [ ] After posting each thread: engage replies for at least 2 hours
- [ ] Quote-tweet any positive replies to amplify the signal
- [ ] Manually reach out (DM) to 3–5 developer-focused accounts who might genuinely care

### Time estimate
2–3 hours per day

### Success metric
- Thread 1: ≥50 impressions per tweet, ≥5 genuine replies
- Thread 2: at least one person asks a detailed question about the tool

---

## Day 8–9: Dev.to Article

### Tasks
- [ ] Review the agent-generated Dev.to article draft in `output/`
- [ ] Rewrite the introduction in your own voice — generated intros are easy to spot
- [ ] Add a real personal anecdote or failure story; it improves read-through rate
- [ ] Include at least one code block showing a real, non-trivial use case
- [ ] Add tags: `cli`, `productivity`, `opensource` (and one language-specific tag)
- [ ] Publish on Day 8 at 8–10 AM UTC (peak Dev.to traffic window)
- [ ] On Day 9: share the published article link on Twitter and in any relevant Reddit
  threads you started — frame it as "wrote a longer explanation"
- [ ] Respond to every comment on the article

### Time estimate
3–4 hours to edit and publish, 1 hour for follow-up

### Success metric
- Article reaches Dev.to's "Top 7 days" list in its primary tag
- ≥3 comments from readers who have a specific question or use case

---

## Day 10: ProductHunt Preparation

### Tasks
- [ ] Prepare all ProductHunt assets:
  - Tagline: ≤60 characters, no buzzwords, describes what it does literally
  - Thumbnail: 240×240 px, legible at small size
  - Gallery: 3–5 screenshots or GIFs showing real usage (not marketing slides)
  - Description: 2–3 short paragraphs; first sentence is your only hook
- [ ] Write your "maker's first comment" — post this within the first minute of launch
  - Explain honestly what you built, why, and what's still rough
  - Invite specific feedback ("I'm especially unsure about X")
- [ ] Identify 10–20 real people (friends, colleagues, past users) who will genuinely
  upvote and comment if they find it useful — **do not ask people to upvote blindly**
  (see "What NOT to do")
- [ ] Schedule the post to go live at 12:01 AM PST on Day 11

### Time estimate
3–4 hours

### Success metric
- All assets ready and approved by ProductHunt before midnight

---

## Day 11: ProductHunt Launch Day

### Tasks
- [ ] Post goes live at 12:01 AM PST (set by scheduler or post manually)
- [ ] Post your maker's first comment immediately
- [ ] Share link in relevant Slack/Discord communities you are already a member of
  — only in channels where self-promotion is explicitly allowed
- [ ] Tweet about the launch from your personal account; link to PH page
- [ ] Check ProductHunt every 1–2 hours and respond to every comment same-day
- [ ] Do not refresh the leaderboard obsessively — focus on engagement quality

### Time estimate
Full day of on-and-off monitoring; budget 4–6 hours active time

### Success metric
- Top 10 in its category by end of day
- ≥15 genuine comments with specific feedback

---

## Day 12–13: Follow-Up Content & Comment Responses

### Tasks
- [ ] Respond to every outstanding comment across all platforms (HN, Reddit, Dev.to, PH)
- [ ] Post a Twitter/X update: "Day 2 of launch — here's what people are asking about most"
  - This is authentic content and keeps the conversation alive
- [ ] If a user reported a bug or limitation publicly: fix it and reply publicly with the fix
  - "Thanks — pushed a fix in v0.x.y" does more for trust than any marketing copy
- [ ] Review the most common questions across all channels and update the README FAQ
- [ ] Draft a short "lessons learned" note for yourself (not for publishing — just to capture
  while it's fresh)

### Time estimate
2–3 hours per day

### Success metric
- Zero unanswered comments or questions across all platforms

---

## Day 14: Metrics Review & Pricing Adjustment

### Tasks
- [ ] Collect numbers from all channels:
  - GitHub: stars, forks, new issues opened
  - HN: final score, comment sentiment
  - Reddit: combined upvotes and comments per post
  - Twitter: impressions, profile clicks, new followers
  - Dev.to: reads, reactions, comments
  - ProductHunt: final rank, upvote count, reviews
- [ ] Identify which channel drove the most actual GitHub stars (not just traffic)
- [ ] If you have a paid tier: review conversion rate
  - If < 1% of free users converted: the pricing, not the product, may be the obstacle
  - Consider adjusting price or adding a clear free-to-paid upgrade trigger
- [ ] Decide on next 14-day focus based on what worked
- [ ] Archive all generated content from `output/` with a date stamp

### Time estimate
2–3 hours

### Success metric
- Clear picture of which channels are worth continuing vs. dropping
- A written decision on whether pricing needs adjustment

---

## Channels Ranked by ROI for Developer Tools

These estimates assume a CLI tool with a technical audience and no existing audience.

| Rank | Channel | Effort | Typical reach | Notes |
|------|---------|--------|---------------|-------|
| 1 | **Hacker News Show HN** | Low–Medium | High ceiling, high variance | Best single shot at a large technical audience. One good post can drive hundreds of GitHub stars in 24 hours. Zero cost. Works once per major version. |
| 2 | **Reddit (r/rust, r/commandline)** | Medium | Moderate, consistent | More predictable than HN. A decent post in r/commandline reliably reaches its audience. Requires community-native tone. |
| 3 | **Dev.to article** | Medium–High | Low-to-moderate | Slower burn. A well-written article ranks in Google within weeks, generating passive traffic long after launch. Worth the investment for evergreen content. |
| 4 | **Twitter/X threads** | Medium | Low without existing following | Requires an account with ≥500 engaged followers to see meaningful organic reach. Without that, it's mostly signaling to people you already know. |
| 5 | **ProductHunt** | High | High on launch day only | Significant preparation overhead. Great for a one-day spike and credibility signal, but rarely drives sustained usage on its own. |
| 6 | **YouTube demo video** | Very high | Low initially | Highest long-term ROI if the tool has a visual workflow — but videos take days to produce well and months to surface in search. Not a launch tactic. |

**Realistic expectations for a solo developer launch:**
- A successful HN Show HN: 100–400 GitHub stars in 48 hours
- A successful Reddit campaign: 20–80 stars across a week
- ProductHunt top 5 in category: 50–200 stars on launch day
- Total from a well-executed 14-day campaign: 200–600 stars is a realistic good outcome

---

## What NOT to Do

**Buy fake upvotes, followers, or reviews.**
ProductHunt, Reddit, and HN all have detection for coordinated voting. A single
flag can get your account banned and your post removed. Beyond the practical risk:
your metrics will be meaningless and you will make decisions based on false signals.

**Spam communities.**
Posting the same link in 10 subreddits on the same day, or posting in communities
you have no history with, will result in removal and shadow-banning. Distribute over
days. Build at least a minimal post history before promoting.

**Ask people to upvote without using the product.**
"Please upvote my PH launch" messages to friends who haven't tried the tool produce
low-quality votes that do not convert to users. Ask people to upvote only if they
genuinely found it useful.

**Promise features you don't have.**
If your launch post describes a feature that isn't in the current release, someone
will clone the repo within hours and call it out. Ship what you describe. Describe
only what you've shipped.

**Over-automate your presence.**
Automated replies, auto-DMs, and bot-generated comments are immediately recognizable
to technical audiences and destroy credibility. The Hermes agent drafts content for
you to review and post — do not configure it to post autonomously to live communities
without a human reviewing every piece of output.

**Disappear after launch day.**
The second-biggest mistake after fake engagement is going silent after you post.
The comments you don't answer are the ones that cost you the most.

---

## Handling Negative Comments

### HN Cynics: "Why not just use X / write a shell script / use Claude Code CLI?"

This is the most common class of HN comment for CLI tools. Do not get defensive.

**Template response:**
> "Fair question. For [specific use case], a shell script works fine. Where this
> becomes useful is [specific scenario that a shell script handles poorly]. If your
> workflow doesn't hit that case, you probably don't need this — and that's fine."

Key principles:
- Acknowledge the valid core of the criticism before defending
- Be specific about the use case, not abstract ("it's more powerful")
- Never attack the competing tool or the person suggesting it
- If you genuinely don't have a good answer, say so: "You might be right for that
  use case — I built this primarily for X"

### "Why not just use Claude Code CLI directly?"

This will come up. It is a legitimate question if your tool wraps or competes with it.

**Template response:**
> "Claude Code CLI is a great tool for interactive coding sessions. CLI-Anything is
> optimized for [specific non-overlapping use case: scripting / automation / headless
> pipeline use / different interface paradigm]. If you're already happy with your
> workflow, there's no reason to switch. This exists for people who need [specific thing]."

Do not claim superiority. Claim specificity.

### "This is just a wrapper around the API"

**Template response:**
> "Yes, at its core it is. The value is in [the specific decisions made: the UX,
> the composability, the defaults, the integration with X]. If you want to build
> those yourself, the API is right there — that's the point of open source."

### Genuine bugs reported publicly

Never deflect. Never blame the user's environment as a first response.

**Template response:**
> "Thanks for the clear repro. Looking into it now."

Then actually fix it and follow up in the same thread. This single behavior —
publicly fixing bugs fast — does more for credibility than any marketing copy.

### "The docs are terrible"

Agree and ask for specifics.

> "You're right, the docs are a weak point right now. What specifically was unclear
> or missing? That would help me prioritize what to fix first."

Turning a criticism into a conversation makes it visible to everyone reading that
you are responsive and honest.

---

*Last updated: April 2026*
