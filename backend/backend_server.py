import threading
import socket

class BackendServer:
    def __init__(self, id_, host, port):
        self.id = id_
        self.host = host
        self.port = port
        self.is_alive = True
        self.lock = threading.Lock()
        self.num_connections = 0

    def update_health_status(self, is_alive):
        """Update the server's health status."""
        with self.lock:
            self.is_alive = is_alive

    def increment_connections(self):
        """Increment the number of active connections."""
        with self.lock:
            self.num_connections += 1

    def decrement_connections(self):
        """Decrement the number of active connections."""
        with self.lock:
            self.num_connections -= 1

    def reverse_proxy(self, client_conn):
        """Handles reverse proxying between client and backend server."""
        def forward_request(source, destination):
            try:
                while True:
                    data = source.recv(1024)
                    if not data:
                        break
                    destination.send(data)
            except Exception as e:
                print(f"Error forwarding request: {e}")

        try:
            # Establish connection to the backend server
            backend_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            backend_conn.connect((self.host, self.port))

            # Start forwarding threads
            client_to_backend = threading.Thread(target=forward_request, args=(client_conn, backend_conn))
            backend_to_client = threading.Thread(target=forward_request, args=(backend_conn, client_conn))

            client_to_backend.start()
            backend_to_client.start()

            client_to_backend.join()
            backend_to_client.join()
        except Exception as e:
            print(f"Error during reverse proxy: {e}")
        finally:
            client_conn.close()
            if backend_conn:
                backend_conn.close()