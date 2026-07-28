async function chargeUser(userId, txnId) {
  try {
    await gateway.charge(userId, txnId);
  } catch (err) {
    console.error(`ERROR [BillingService] Failed to process payment for user ${userId} (txnId=${txnId}): gateway timeout`);
  }
}
module.exports = { chargeUser };
