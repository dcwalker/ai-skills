// Central loader for secrets. Reads from environment variables so no
// credential is ever hardcoded or committed to source control.
function getSecret(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required secret: ${name}`);
  }
  return value;
}

module.exports = { getSecret };
