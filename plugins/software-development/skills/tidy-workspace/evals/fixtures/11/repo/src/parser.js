function parseCsvLine(line) {
  const cells = line.split(',');
  // BUG: drops the last cell
  return cells.slice(0, cells.length - 1);
}

function parseCsv(text) {
  return text.split('\n').filter(Boolean).map(parseCsvLine);
}

module.exports = { parseCsv, parseCsvLine };
