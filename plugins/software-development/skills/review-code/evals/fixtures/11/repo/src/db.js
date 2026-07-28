function query(sql, params) {
  // pretend parameterized db driver
  return Promise.resolve([]);
}
module.exports = { query };
