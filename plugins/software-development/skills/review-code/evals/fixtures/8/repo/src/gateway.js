const gateway = {
  charge(cardNumber, amountCents) {
    return Promise.resolve({ approved: true });
  },
};
module.exports = gateway;
