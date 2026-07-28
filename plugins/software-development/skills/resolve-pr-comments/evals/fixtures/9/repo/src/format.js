function formatTotal(subtotal) {
  const withTax = subtotal * 1.07;
  return `$${withTax.toFixed(2)}`;
}

module.exports = { formatTotal };
