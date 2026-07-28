async function refreshFeedCache() {
  try {
    await cache.refresh('rss');
  } catch (err) {
    console.error('ERROR [FeedCache] Failed to refresh RSS feed cache');
  }
}
module.exports = { refreshFeedCache };
