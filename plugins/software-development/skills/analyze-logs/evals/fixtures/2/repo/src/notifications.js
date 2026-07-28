async function sendEmail(userId) {
  // ...
  console.error(`ERROR [EmailWorker] Failed to send email notification (userId=${userId})`);
}

module.exports = { sendEmail };
