async function capturePayment(orderId) {
  try {
    await gateway.capture(orderId);
  } catch (err) {
    console.error(`ERROR [PaymentCapture] Failed to capture payment for order ${orderId}: gateway rejected transaction`);
  }
}
module.exports = { capturePayment };
