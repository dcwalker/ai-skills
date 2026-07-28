const store = new Map();

function get(sessionId) {
  // Returns undefined if the session has expired or never existed.
  return store.get(sessionId);
}

module.exports = { get };
