/**
 * Empire Brain - Cloudflare Worker
 * Self-evolving knowledge store for AI agents.
 * Reverse-engineered from OpenSpace concepts.
 *
 * Endpoints:
 *   GET  /recall?q=keywords&limit=5   → top matching patterns
 *   POST /remember                    → store a new pattern
 *   POST /reinforce?id=N              → increment success count on pattern N
 *   GET  /errors?skill=name           → known fixes for a skill
 *   POST /error                       → store a new error fix
 *   GET  /health                      → status check
 */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { 'Content-Type': 'application/json', ...CORS },
  });
}

async function handleRecall(request, env) {
  const url = new URL(request.url);
  const q = url.searchParams.get('q') || '';
  const limit = Math.min(parseInt(url.searchParams.get('limit') || '5'), 20);

  if (!q.trim()) return json({ patterns: [], message: 'No query provided' });

  // Build keyword search across tags + task_summary
  const keywords = q.toLowerCase().split(/\s+/).filter(Boolean).slice(0, 8);
  const conditions = keywords.map(() => `(LOWER(tags) LIKE ? OR LOWER(task_summary) LIKE ?)`).join(' OR ');
  const params = keywords.flatMap(k => [`%${k}%`, `%${k}%`]);

  const { results } = await env.DB.prepare(
    `SELECT id, task_summary, tags, solution, outcome, success_count, token_estimate
     FROM patterns
     WHERE ${conditions}
     ORDER BY success_count DESC, updated_at DESC
     LIMIT ?`
  ).bind(...params, limit).all();

  return json({ patterns: results || [], count: results?.length || 0 });
}

async function handleRemember(request, env) {
  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  const { task_summary, tags, solution, outcome, token_estimate } = body;
  if (!task_summary || !solution) {
    return json({ error: 'task_summary and solution are required' }, 400);
  }

  // Check if very similar pattern already exists — if so, reinforce it
  const tagStr = Array.isArray(tags) ? tags.join(',') : (tags || '');
  const existing = await env.DB.prepare(
    `SELECT id FROM patterns WHERE LOWER(task_summary) LIKE ? LIMIT 1`
  ).bind(`%${task_summary.toLowerCase().slice(0, 40)}%`).first();

  if (existing) {
    await env.DB.prepare(
      `UPDATE patterns SET success_count = success_count + 1, updated_at = datetime('now') WHERE id = ?`
    ).bind(existing.id).run();
    return json({ action: 'reinforced', id: existing.id });
  }

  const result = await env.DB.prepare(
    `INSERT INTO patterns (task_summary, tags, solution, outcome, token_estimate)
     VALUES (?, ?, ?, ?, ?) RETURNING id`
  ).bind(task_summary, tagStr, solution, outcome || '', token_estimate || 0).first();

  return json({ action: 'stored', id: result?.id });
}

async function handleReinforce(request, env) {
  const url = new URL(request.url);
  const id = parseInt(url.searchParams.get('id'));
  if (!id) return json({ error: 'id required' }, 400);

  await env.DB.prepare(
    `UPDATE patterns SET success_count = success_count + 1, updated_at = datetime('now') WHERE id = ?`
  ).bind(id).run();

  return json({ action: 'reinforced', id });
}

async function handleGetErrors(request, env) {
  const url = new URL(request.url);
  const skill = url.searchParams.get('skill') || '';

  const { results } = await env.DB.prepare(
    `SELECT skill_name, error_signature, fix_applied, fixed_count
     FROM errors
     WHERE LOWER(skill_name) LIKE ?
     ORDER BY fixed_count DESC LIMIT 10`
  ).bind(`%${skill.toLowerCase()}%`).all();

  return json({ fixes: results || [], count: results?.length || 0 });
}

async function handlePostError(request, env) {
  let body;
  try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400); }

  const { skill_name, error_signature, fix_applied } = body;
  if (!skill_name || !error_signature || !fix_applied) {
    return json({ error: 'skill_name, error_signature, fix_applied are required' }, 400);
  }

  // Reinforce if this fix already exists
  const existing = await env.DB.prepare(
    `SELECT id FROM errors WHERE skill_name = ? AND LOWER(error_signature) LIKE ? LIMIT 1`
  ).bind(skill_name, `%${error_signature.toLowerCase().slice(0, 60)}%`).first();

  if (existing) {
    await env.DB.prepare(
      `UPDATE errors SET fixed_count = fixed_count + 1 WHERE id = ?`
    ).bind(existing.id).run();
    return json({ action: 'reinforced', id: existing.id });
  }

  const result = await env.DB.prepare(
    `INSERT INTO errors (skill_name, error_signature, fix_applied) VALUES (?, ?, ?) RETURNING id`
  ).bind(skill_name, error_signature, fix_applied).first();

  return json({ action: 'stored', id: result?.id });
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    // Initialize schema on first use
    try {
      await env.DB.prepare(`SELECT 1 FROM patterns LIMIT 1`).first();
    } catch {
      // Tables don't exist yet — run schema
      await env.DB.exec(`
        CREATE TABLE IF NOT EXISTS patterns (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_summary TEXT NOT NULL,
          tags TEXT NOT NULL DEFAULT '',
          solution TEXT NOT NULL,
          outcome TEXT NOT NULL DEFAULT '',
          success_count INTEGER DEFAULT 1,
          token_estimate INTEGER DEFAULT 0,
          created_at TEXT DEFAULT (datetime('now')),
          updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS errors (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          skill_name TEXT NOT NULL,
          error_signature TEXT NOT NULL,
          fix_applied TEXT NOT NULL,
          fixed_count INTEGER DEFAULT 1,
          created_at TEXT DEFAULT (datetime('now'))
        );
      `);
    }

    if (path === '/recall' && request.method === 'GET') return handleRecall(request, env);
    if (path === '/remember' && request.method === 'POST') return handleRemember(request, env);
    if (path === '/reinforce' && request.method === 'POST') return handleReinforce(request, env);
    if (path === '/errors' && request.method === 'GET') return handleGetErrors(request, env);
    if (path === '/error' && request.method === 'POST') return handlePostError(request, env);
    if (path === '/health') return json({ status: 'ok', version: '1.0.0', name: 'empire-brain' });

    return json({ error: 'Not found', available: ['/recall', '/remember', '/reinforce', '/errors', '/error', '/health'] }, 404);
  }
};
