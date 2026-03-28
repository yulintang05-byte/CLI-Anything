# /auto-fix — Empire Brain Auto-Fix

Before spending tokens debugging a broken tool/skill/API, check if Empire Brain already has a fix. One agent's painful debugging session becomes every agent's instant fix.

## When to Use
- A tool, script, or skill is throwing an error
- An API call is failing
- A server won't start or crashes on launch
- Same error appeared before and you're not sure what fixed it

## How to Execute

1. Extract the skill/tool name and the key error signature (first line of error, or error code)
2. Query Empire Brain for known fixes:
   ```bash
   curl -s "https://empire-brain.<account>.workers.dev/errors?skill=SKILL_NAME"
   ```
3. If fixes found:
   - Show: "Empire Brain has N known fix(es) for SKILL_NAME:"
   - List each `error_signature` + `fix_applied` + `fixed_count`
   - Apply the most successful fix first (highest `fixed_count`)
4. If fix works: `/remember` the pattern + call `/reinforce` on the error fix:
   ```bash
   curl -s -X POST "https://empire-brain.<account>.workers.dev/reinforce?id=N"
   ```
5. If fix doesn't work OR no fix found:
   - Debug normally
   - When fixed, store the new fix:
   ```bash
   curl -s -X POST "https://empire-brain.<account>.workers.dev/error" \
     -H "Content-Type: application/json" \
     -d '{
       "skill_name": "tiktok-oauth",
       "error_signature": "redirect_uri_mismatch",
       "fix_applied": "Remove trailing space from redirect_uri in .env. Must exactly match TikTok dev portal."
     }'
   ```

## Output Format
```
🔧 Empire Brain Auto-Fix — 1 known fix for oauth_server:

Error: redirect_uri_mismatch [fixed 2x]
Fix:   Remove trailing space from redirect_uri in .env
       Must exactly match string in TikTok developer portal

Applying fix... ✓
```
