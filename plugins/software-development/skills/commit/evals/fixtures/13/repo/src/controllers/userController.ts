import { formatUserLabel } from "../services/userService";
import type { User } from "../models/user";

export function renderUser(user: User): string {
  return `<span>${formatUserLabel(user)}</span>`;
}
