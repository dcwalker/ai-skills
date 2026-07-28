const fs = require('fs/promises');
const fetchClient = require('./fetch-client');

// Generates a nightly report and writes it to disk.
async function generateNightlyReport() {
  const data = await fetchClient.get('/api/metrics/daily');
  const report = formatReport(data);
  await fs.writeFile('/var/reports/nightly.json', JSON.stringify(report));
  return report;
}

function formatReport(data) {
  return { generatedAt: new Date().toISOString(), ...data };
}

module.exports = { generateNightlyReport };
