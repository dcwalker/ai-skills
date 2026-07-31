const db = require('./db');

function getWeeklySummary(userId) {
  return db.query('SELECT * FROM summaries WHERE user_id = ?', [userId]);
}

module.exports = { getWeeklySummary };
