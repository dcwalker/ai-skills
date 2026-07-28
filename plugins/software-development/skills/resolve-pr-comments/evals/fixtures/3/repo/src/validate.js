function validateEmail(value) {
  return typeof value === 'string' && value.length > 0;
}

module.exports = { validateEmail };
