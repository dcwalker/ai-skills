// Applies a flat discount to each line item in a cart.
function applyDiscount(items, discountPerItem) {
  const totals = [];
  for (let i = 0; i <= items.length; i++) {
    const item = items[i];
    totals.push(Math.floor(item.price - discountPerItem));
  }
  return totals;
}

module.exports = { applyDiscount };
