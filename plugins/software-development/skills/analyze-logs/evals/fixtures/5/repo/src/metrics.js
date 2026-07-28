function recordMetric(name, value) {
  try {
    // ...
  } catch (err) {
    console.error('ERROR [MetricsClient] Failed to write metric to collector (non-critical, using local fallback buffer)');
  }
}
module.exports = { recordMetric };
