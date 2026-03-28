# /remember — Empire Brain Remember

After successfully completing a task, store the winning pattern in Empire Brain so every future agent session (and every other agent) can benefit from it.

## When to Use
- After solving a bug or error that took more than 2 steps
- After completing an integration (OAuth, API, deploy)
- After finding the right sequence of commands that worked
- After fixing a recurring problem

## How to Execute

1. Summarize what was just accomplished in 1-2 sentences
2. Extract tags (keywords): tool names, error types, task category
3. Write the solution: the exact steps / commands / approach that worked
4. Note the outcome: what success looked like
5. POST to Empire Brain:
   ```bash
   curl -s -X POST "https://empire-brain.<account>.workers.dev/remember" \
     -H "Content-Type: application/json" \
     -d '{
       "task_summary": "Short description of what was done",
       "tags": "tiktok,oauth,token,python,ngrok",
       "solution": "Exact steps that worked...",
       "outcome": "What success looked like",
       "token_estimate": 1200
     }'
   ```
6. Confirm: "Stored in Empire Brain ✓"

## Rules
- Be specific in `solution` — future agents need to reproduce this exactly
- Use consistent tags so `/recall` can find it (tool names, error names, task type)
- If a pattern was already stored, the server auto-reinforces its success count
- Never store failed approaches — only what actually worked

## Example
```json
{
  "task_summary": "TikTok OAuth token exchange via ngrok callback",
  "tags": "tiktok,oauth,ngrok,python,flask,token,callback",
  "solution": "1. Start oauth_server.py (Flask on port 9090)\n2. Run: ngrok http 9090\n3. Copy HTTPS URL → set as redirect_uri in .env\n4. User visits auth URL, approves, code hits /callback\n5. Server exchanges code for token, saves to tiktok_token.json\n6. Verify: cat tiktok_token.json shows access_token + refresh_token",
  "outcome": "tiktok_token.json created with valid access_token",
  "token_estimate": 800
}
```
