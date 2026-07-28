function checkout(cart) {
  if (!cart || cart.items.length === 0) {
    throw new Error('Cart is empty');
  }
  return cart.items.reduce((sum, item) => sum + item.price, 0);
}

module.exports = { checkout };
