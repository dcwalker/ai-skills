const db = require('./db');

// Searches users by name for the admin panel.
async function searchUsers(req, res) {
  const { name } = req.query;

  const rows = await db.query(
    "SELECT id, email, role FROM users WHERE name LIKE '%" + name + "%'"
  );

  res.json(rows);
}

module.exports = { searchUsers };
