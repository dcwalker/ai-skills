const http = require('http');

const server = http.createServer((req, res) => {
  res.end('Taskboard running');
});

server.listen(3000, () => console.log('listening on 3000'));
