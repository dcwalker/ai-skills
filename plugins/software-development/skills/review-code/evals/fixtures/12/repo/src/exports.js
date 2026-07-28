const db = require('./db');

// New endpoint: exports all orders as CSV. No test file added for this yet.
async function exportOrdersCsv(req, res) {
  const orders = await db.query('SELECT * FROM orders');
  const csv = orders.map((o) => `${o.id},${o.sku},${o.quantity}`).join('\n');
  res.set('Content-Type', 'text/csv');
  res.send(csv);
}

module.exports = { exportOrdersCsv };
