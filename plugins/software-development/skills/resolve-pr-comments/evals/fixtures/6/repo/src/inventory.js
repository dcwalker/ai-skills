function reserveStock(inventory, sku, qty) {
  inventory[sku] = inventory[sku] - qty;
  return inventory;
}

module.exports = { reserveStock };
