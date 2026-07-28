async function chargeCard(cardToken, amountCents) {
  const result = await gateway.authorize(cardToken, amountCents);
  if (!result.approved) {
    console.error(`ERROR [PaymentService] Failed to charge card: card_declined (operation=chargeCard reason=${result.reason})`);
    throw new Error('card_declined');
  }
  return result;
}

module.exports = { chargeCard };
