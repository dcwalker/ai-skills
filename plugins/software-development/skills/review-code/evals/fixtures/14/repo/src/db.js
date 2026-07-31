function query(sql, params) {
  // Placeholder driver used by the fixture; real implementation not needed.
  return Promise.resolve({ sql, params, rows: [] });
}

module.exports = { query };
