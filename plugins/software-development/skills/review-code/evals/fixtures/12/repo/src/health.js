// Existing endpoint, already has test coverage.
function healthCheck(req, res) {
  res.json({ status: 'ok' });
}
module.exports = { healthCheck };
