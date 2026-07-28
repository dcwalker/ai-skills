import type { User } from "../models/user";

export function formatUserLabel(user: User): string {
  return user.fullName;
}
