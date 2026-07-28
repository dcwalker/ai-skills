// Applies a percentage discount to a price.
function applyDiscount(price, percentOff) {
  const discounted = price - (price * percentOff) / 100;
  return discounted;
}

module.exports = { applyDiscount };
