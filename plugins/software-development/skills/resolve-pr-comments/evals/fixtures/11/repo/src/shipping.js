function estimateShipping(items, totalWeight) {
  return totalWeight / items.length;
}

module.exports = { estimateShipping };
