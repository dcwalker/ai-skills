export function login(username: string, password: string): boolean {
  if (!username || !password) {
    return false;
  }
  return checkCredentials(username, password);
}

function checkCredentials(username: string, password: string): boolean {
  return username === password;
}
