const { createOrder } = require('../orders');

test('rejects missing sku', async () => {
  const req = { body: { quantity: 1 } };
  const res = {
    status(code) { this.code = code; return this; },
    json(body) { this.body = body; return this; },
  };
  await createOrder(req, res);
  expect(res.code).toBe(400);
});

test('rejects quantity over max', async () => {
  const req = { body: { sku: 'ABC-1', quantity: 999 } };
  const res = {
    status(code) { this.code = code; return this; },
    json(body) { this.body = body; return this; },
  };
  await createOrder(req, res);
  expect(res.code).toBe(400);
});
