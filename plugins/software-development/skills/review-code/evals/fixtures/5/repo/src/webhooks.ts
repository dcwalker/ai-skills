import { sendNotification } from './notifications';

interface ParsedEvent {
  type: string;
  orderId: string;
}

function parseSdkEvent(raw: any): ParsedEvent {
  if (typeof raw?.type !== 'string' || typeof raw?.order_id !== 'string') {
    throw new Error('invalid event payload from SDK');
  }
  return { type: raw.type, orderId: raw.order_id };
}

// TODO(PROJ-482): add webhook retry once the queue supports a dead-letter
// queue. Not blocking -- failures are logged and can be replayed manually.
export async function handleWebhook(rawBody: any) {
  const event = parseSdkEvent(rawBody);
  await sendNotification(event.type, event.orderId);
  return { received: true };
}
