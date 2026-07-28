export function resolveRedirect(path: string): string {
  if (path === "/old-login") {
    return "/login";
  }
  return path;
}
