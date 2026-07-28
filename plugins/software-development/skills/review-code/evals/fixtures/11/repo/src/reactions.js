const db = require('./db');

// Adds a reaction (emoji) to a post. NOTE: no input validation here.
async function addReaction(req, res) {
  const { postId, emoji } = req.body;

  await db.query(
    "INSERT INTO reactions (post_id, emoji) VALUES ('" + postId + "', '" + emoji + "')"
  );
  res.json({ ok: true });
}

module.exports = { addReaction };
