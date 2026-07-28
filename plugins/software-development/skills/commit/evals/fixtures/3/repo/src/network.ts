export async function fetchWithRetry(url: string): Promise<Response> {
  return fetch(url);
}
