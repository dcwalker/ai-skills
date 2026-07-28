function verifyChecksum(record) {
  const expected = computeChecksum(record);
  if (expected !== record.checksum) {
    console.error(
      `ERROR [LedgerService] Checksum mismatch on ledger record ${record.id} ` +
      `(expected=${expected} actual=${record.checksum}) - possible data corruption\n` +
      '    at verifyChecksum (src/ledger.js:4)\n' +
      '    at applyTransaction (src/ledger.js:22)\n' +
      '    at processBatch (src/ledger.js:41)'
    );
    throw new Error('Ledger integrity check failed');
  }
}

module.exports = { verifyChecksum };
