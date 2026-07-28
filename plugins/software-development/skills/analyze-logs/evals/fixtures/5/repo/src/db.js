function connect() {
  // ...
  console.error('FATAL [DbCluster] System-wide outage: primary database cluster unreachable, all requests failing');
}
module.exports = { connect };
