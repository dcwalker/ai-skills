const { chargeGateway } = require('./payment-gateway');

async function submitOrder(orderId, cart) {
  try {
    await chargeGateway(orderId, cart.total);
  } catch (err) {
    console.error(`ERROR [OrderService] Connection timeout calling payment-gateway (orderId=${orderId})`);
    throw err;
  }
}

module.exports = { submitOrder };
