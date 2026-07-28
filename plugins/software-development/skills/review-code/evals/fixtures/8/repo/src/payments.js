async function chargeCard(cardNumber, amountCents) {
  console.log(`Charging card ${cardNumber} for ${amountCents} cents`);
  return gateway.charge(cardNumber, amountCents);
}

module.exports = { chargeCard };
