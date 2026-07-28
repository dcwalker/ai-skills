const http = require('http');

// Proxies a request to the internal recommendations service.
async function proxyToRecommendations(req, res) {
  let response = await fetch('http://internal-recs.local/api/recommend', {
    method: 'POST',
    body: JSON.stringify(req.body),
  });

  const data = await response.json();
  res.json(data);
}

module.exports = { proxyToRecommendations };
