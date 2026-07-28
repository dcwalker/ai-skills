const http = require('http');

const server = http.createServer((req, res) => {
  res.end('pong');
});

server.listen(4000, () => console.log('pingpong listening on 4000'));
