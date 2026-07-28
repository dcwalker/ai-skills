const sessions = require('./session-store');

// Returns the display name for the current session's user.
function getCurrentUserDisplayName(sessionId) {
  const session = sessions.get(sessionId);
  return session.user.displayName.toUpperCase();
}

module.exports = { getCurrentUserDisplayName };
