function getConnection() {
  // ...
  console.error('ERROR [DbPool] Database connection pool exhausted, no connections available');
}

module.exports = { getConnection };
