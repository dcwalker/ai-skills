const SLACK_TOKEN = 'xoxb-hardcoded-token-do-not-ship';

function notify(message) {
  return fetch('https://slack.com/api/chat.postMessage', {
    method: 'POST',
    headers: { Authorization: `Bearer ${SLACK_TOKEN}` },
    body: JSON.stringify({ text: message }),
  });
}

module.exports = { notify };
