const db = require('./db');

// Updates a user's display name from an incoming request body.
async function updateDisplayName(req, res) {
  const { userId, displayName } = req.body;

  await db.run(
    'UPDATE users SET display_name = ? WHERE id = ?',
    [displayName, userId]
  );

  res.json({ ok: true });
}

module.exports = { updateDisplayName };
