const { healthCheck } = require('../health');

test('returns ok status', () => {
  const res = { json(body) { this.body = body; } };
  healthCheck({}, res);
  expect(res.body.status).toBe('ok');
});
