function acquire() {
  if (pool.utilization() > 0.9) {
    console.warn('WARN [ConnectionPool] Connection pool at 95% capacity');
  }
  if (pool.isFull()) {
    console.error('ERROR [ConnectionPool] Connection pool exhausted, request rejected');
    throw new Error('pool_exhausted');
  }
}
module.exports = { acquire };
