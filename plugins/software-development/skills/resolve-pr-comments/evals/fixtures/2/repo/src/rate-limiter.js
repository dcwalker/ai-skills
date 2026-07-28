// Throttles retries of a flaky network call.
function throttle(fn) {
  // fixed delay between retries
  const DELAY_MS = 100;

  return async (...args) => {
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        return await fn(...args);
      } catch (err) {
        if (attempt === 2) throw err;
        await new Promise((resolve) => setTimeout(resolve, DELAY_MS));
      }
    }
  };
}

module.exports = { throttle };
