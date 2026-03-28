# /recall — Empire Brain Recall

Before starting ANY significant task, query the Empire Brain for patterns that already solved this type of problem. Reuse what worked. Skip what failed.

## When to Use
Automatically triggered at the start of tasks involving:
- OAuth / authentication flows
- API integrations (TikTok, Cloudflare, etc.)
- File/server setup
- Any task where "we've done this before" is likely

## How to Execute

1. Extract 3-6 keywords from the current task description
2. Call the Empire Brain:
   ```
   curl -s "https://empire-brain.<account>.workers.dev/recall?q=KEYWORDS&limit=5"
   ```
3. If patterns are returned:
   - Show the user: "Found X matching patterns from Empire Brain:"
   - List each pattern's `task_summary`, `solution`, and `success_count`
   - Ask: "Use pattern #N as a starting point, or start fresh?"
4. If no patterns found:
   - Proceed normally
   - Remind yourself to `/remember` after success

## Worker URL
Set EMPIRE_BRAIN_URL in your environment or CLAUDE.md:
```
EMPIRE_BRAIN_URL=https://empire-brain.<your-subdomain>.workers.dev
```

## Output Format
```
🧠 Empire Brain Recall — found 2 matching patterns:

#1 [success: 3x] TikTok OAuth token exchange
   Solution: Run oauth_server.py on port 9090, use ngrok for callback URL,
             exchange code at /callback endpoint, save to tiktok_token.json

#2 [success: 1x] ngrok tunnel setup for OAuth redirect
   Solution: ngrok http 9090, copy HTTPS URL, update redirect_uri in .env

Use pattern #1, #2, both, or start fresh?
```
