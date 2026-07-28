const db = require('./db');

/**
 * Adds a comment to a post. Validates input and uses a parameterized query.
 */
async function addComment(req, res) {
  const { postId, text } = req.body ?? {};

  if (typeof postId !== 'string' || postId.trim().length === 0) {
    return res.status(400).json({ error: 'postId is required' });
  }
  if (typeof text !== 'string' || text.trim().length === 0 || text.length > 2000) {
    return res.status(400).json({ error: 'text must be a non-empty string up to 2000 chars' });
  }

  await db.query('INSERT INTO comments (post_id, text) VALUES (?, ?)', [postId, text]);
  return res.status(201).json({ ok: true });
}

module.exports = { addComment };
