const net = require('net');

//Create Proxy server
const server = net.createServer();

server.on('connection', (clientToProxySocket) => {
  console.log('Client Connected To Proxy');
  // We need only the data once, when the client will connect (first packet only)
  clientToProxySocket.once('data', (data) => {
    // Get Pckate details
    console.log(data.toString());

    let isTLSConnection = data.toString().indexOf('CONNECT') !== -1;

    // By Default et the port to 80
    let serverPort = 80;
    let serverAddress;
    if (isTLSConnection) {
      // If TLS change the port from the received data packet
      serverPort = data.toString()
                          .split('CONNECT ')[1].split(' ')[0].split(':')[1];;
      serverAddress = data.toString()
                          .split('CONNECT ')[1].split(' ')[0].split(':')[0];
    } else {
      serverAddress = data.toString().split('Host: ')[1].split('\r\n')[0];
    }

    console.log(serverAddress);

    // Create socket connection to the server
    let proxyToServerSocket = net.createConnection({
      host: serverAddress,
      port: serverPort
    }, () => {
      console.log('PROXY TO SERVER SET UP');
      if (isTLSConnection) {
        //Send Back OK to HTTPS CONNECT Request
        clientToProxySocket.write('HTTP/1.1 200 OK\r\n\n');
      } else {
        //Send Back OK to HTTP Request
        proxyToServerSocket.write(data);
      }
      
      // Pipe the sockets -- Needs clarification
      clientToProxySocket.pipe(proxyToServerSocket);
      proxyToServerSocket.pipe(clientToProxySocket);

      proxyToServerSocket.on('error', (err) => {
        console.log('PROXY TO SERVER ERROR');
        console.log(err);
      });
      
    });
    clientToProxySocket.on('error', err => {
      console.log('CLIENT TO PROXY ERROR');
      console.log(err);
    });
  });
});

server.on('error', (err) => {
  console.log('SERVER ERROR');
  console.log(err);
  throw err;
});

server.on('close', () => {
  console.log('Client Disconnected');
});

server.listen(8124, () => {
  console.log('Proxy server runnig at http://localhost:' + 8124);
});
