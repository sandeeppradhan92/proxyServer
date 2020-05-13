import signal
import socket
import sys
import threading


class Proxy:
    def __init__(self, config):
        # Shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.shutdown)
        self.buffer_size = config["BUFFER_SIZE"]
        try:
            # Create a TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Re-use the socket
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # bind the socket to a public host, and a port
            self.server_socket.bind((config["HOST_NAME"], config["BIND_PORT"]))

            self.server_socket.listen(10)  # become a server socket
            self.__clients = {}
        except socket.error:
            print("Error while creating proxy server")
            sys.exit(1)

    def shutdown(self, *args):
        print("Executing shutdown process ... ")
        self.server_socket.close()
        sys.exit(0)

    def _getClientName(self, client_address):
        return "client-{}".format(client_address)

    def _handle_request_thread(self, client_socket, client_address):
        client_request = client_socket.recv(self.buffer_size)
        # Convert byte string to utf-8
        data = str(client_request, "utf-8")
        print(data)
        first_line = data.split("\n")[0]
        url = first_line.split(" ")[1]
        remote_host = ""
        remote_port = 80
        rh_position = url.find("://")
        if rh_position == -1:
            remote_host, remote_port = url.split(":")
        else:
            remote_host = url[(rh_position + 3) : (len(url) - 1)]
        print(
            f"client_ip : {client_address[0]}, client_port: {client_address[1]}, remote_host : {remote_host}, remote_port : {remote_port}"
        )
        self._proxy_request(remote_host, remote_port, client_socket, client_request)

    def _proxy_request(self, remote_host, remote_port, client_socket, client_request):
        try:
            # Create a TCP socket
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((remote_host, int(remote_port)))
            remote_socket.send(client_request)
            while 1:
                # read response data from remote_socket server
                reply = remote_socket.recv(self.buffer_size)
                if len(reply) > 0:
                    client_socket.send(reply)
                else:
                    client_socket.send(b"server does not respond")
                    break

        except socket.error:
            print("Error while connecting to remote host from proxy server")
            sys.exit(1)

        finally:
            # Close remote_socket
            remote_socket.close()
            # Close client_socket
            client_socket.close()

    def run(self):
        while True:
            # Establish the connection
            client_socket, client_address = self.server_socket.accept()

            d = threading.Thread(
                name=self._getClientName(client_address),
                target=self._handle_request_thread,
                args=(client_socket, client_address),
            )
            d.setDaemon(True)
            d.start()
