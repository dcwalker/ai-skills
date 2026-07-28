export function parseCsvLine(line: string): string[] {
  return line.split(",").map((cell) => cell.trim());
}
