-- Empire Brain D1 Schema
-- Stores learned task patterns and known error fixes

CREATE TABLE IF NOT EXISTS patterns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_summary TEXT NOT NULL,          -- short description of what was done
  tags TEXT NOT NULL DEFAULT '',       -- comma-separated keywords for recall
  solution TEXT NOT NULL,              -- what worked (commands, approach)
  outcome TEXT NOT NULL DEFAULT '',    -- what the result looked like
  success_count INTEGER DEFAULT 1,     -- times this pattern succeeded
  token_estimate INTEGER DEFAULT 0,   -- approx tokens used
  created_at TEXT DEFAULT (datetime('now')),
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS errors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  skill_name TEXT NOT NULL,            -- which skill/tool broke
  error_signature TEXT NOT NULL,       -- key part of the error message
  fix_applied TEXT NOT NULL,           -- what fixed it
  fixed_count INTEGER DEFAULT 1,       -- times this fix worked
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_patterns_tags ON patterns(tags);
CREATE INDEX IF NOT EXISTS idx_errors_skill ON errors(skill_name);
