function removeItem(cart, sku) {
  return cart.filter((i) => i.sku != sku);
}

module.exports = { removeItem };
