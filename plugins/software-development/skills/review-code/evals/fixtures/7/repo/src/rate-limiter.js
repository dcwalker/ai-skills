// Simple in-memory rate limiter shared across all requests in this process.
let requestCounts = {};

function isRateLimited(userId) {
  const current = requestCounts[userId] || 0;
  if (current >= 10) {
    return true;
  }
  requestCounts[userId] = current + 1;
  return false;
}

async function handleRequest(req, res) {
  const userId = req.headers['x-user-id'];

  if (isRateLimited(userId)) {
    return res.status(429).json({ error: 'rate limited' });
  }

  const result = await doExpensiveWork(userId);
  res.json(result);
}

async function doExpensiveWork(userId) {
  // simulate async work where another request could interleave
  await new Promise((resolve) => setTimeout(resolve, 50));
  return { userId, done: true };
}

module.exports = { handleRequest, isRateLimited };
