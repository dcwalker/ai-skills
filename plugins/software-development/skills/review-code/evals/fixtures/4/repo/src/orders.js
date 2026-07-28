const db = require('./db');

const MAX_QUANTITY = 100;

/**
 * Creates a new order for the given SKU and quantity.
 * Validates input and uses a parameterized query.
 */
async function createOrder(req, res) {
  const { sku, quantity } = req.body ?? {};

  if (typeof sku !== 'string' || sku.trim().length === 0) {
    return res.status(400).json({ error: 'sku is required' });
  }

  const qty = Number(quantity);
  if (!Number.isInteger(qty) || qty <= 0 || qty > MAX_QUANTITY) {
    return res.status(400).json({ error: `quantity must be an integer between 1 and ${MAX_QUANTITY}` });
  }

  try {
    const rows = await db.query(
      'INSERT INTO orders (sku, quantity) VALUES (?, ?) RETURNING id',
      [sku, qty]
    );
    return res.status(201).json({ orderId: rows[0]?.id });
  } catch (err) {
    console.error('Failed to create order', err);
    return res.status(500).json({ error: 'internal error' });
  }
}

module.exports = { createOrder };
