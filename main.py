import socket
from threading import Thread, Lock
import json
import time
import requests # type: ignore
import importlib
import subprocess

# Load balancer configuration
LOAD_BALANCER_HOST = "127.0.0.1"
LOAD_BALANCER_PORT = 8080
CONFIG_FILE = "config.json"
HEALTH_CHECK_INTERVAL = 10  # seconds
HEALTH_CHECK_URL = "/health"  # Endpoint for health checks

# Global variables
servers = []
healthy_servers = []
lock = Lock()
load_balancing_algorithm = "round_robin"

# Function to load backend servers from configuration file
def load_config():
    global servers, healthy_servers, load_balancing_algorithm
    with lock:
        try:
            with open(CONFIG_FILE, "r") as config_file:
                config = json.load(config_file)
                servers = [(server["host"], server["port"]) for server in config.get("servers", [])]
                healthy_servers = servers.copy()  # Initially assume all servers are healthy
                load_balancing_algorithm = config.get("algorithm", "round_robin")
                print(f"Loaded servers: {servers}")
                print(f"Using load balancing algorithm: {load_balancing_algorithm}")
        except Exception as e:
            print(f"Failed to load configuration: {e}")

# Function to start backend servers dynamically
def start_backend_servers():
    processes = []
    for host, port in servers:
        print(f"Starting backend server on {host}:{port}")
        process = subprocess.Popen(
            ["python", "-m", "http.server", str(port), "--bind", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(process)
    return processes

# Function to perform health checks
def health_check():
    global healthy_servers
    while True:
        with lock:
            updated_healthy_servers = []
            for host, port in servers:
                try:
                    response = requests.get(f"http://{host}:{port}{HEALTH_CHECK_URL}", timeout=2)
                    if response.status_code == 200:
                        updated_healthy_servers.append((host, port))
                except requests.RequestException:
                    print(f"Health check failed for server {host}:{port}")

            healthy_servers = updated_healthy_servers
            print(f"Healthy servers: {healthy_servers}")

        time.sleep(HEALTH_CHECK_INTERVAL)

# Function to dynamically import the chosen algorithm
def select_backend_algorithm():
    try:
        algorithm_module = importlib.import_module(f"algo.{load_balancing_algorithm}")
        return algorithm_module.select_server
    except ModuleNotFoundError:
        print(f"Algorithm '{load_balancing_algorithm}' not found. Defaulting to round_robin.")
        from algo.round_robin import select_server
        return select_server

# Function to handle client connections
def handle_client(client_socket):
    with lock:
        if not healthy_servers:
            print("No healthy backend servers available")
            client_socket.close()
            return

        # Use the selected algorithm to choose a backend server
        select_server = select_backend_algorithm()
        backend_server = select_server(healthy_servers)

        if backend_server is None:
            print("Failed to select a backend server")
            client_socket.close()
            return

        backend_host, backend_port = backend_server

    # Forward the client request to the backend server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_socket:
        try:
            backend_socket.connect((backend_host, backend_port))

            # Receive client request and send to backend
            client_request = client_socket.recv(4096)
            backend_socket.sendall(client_request)

            # Receive backend response and send back to client
            backend_response = backend_socket.recv(4096)
            client_socket.sendall(backend_response)

        except Exception as e:
            print(f"Error forwarding request to {backend_host}:{backend_port} - {e}")

    # Close the client connection
    client_socket.close()

# Main function to start the load balancer
def main():
    # Load the initial configuration
    load_config()

    # Start backend servers
    backend_processes = start_backend_servers()

    # Start a thread to perform health checks periodically
    health_thread = Thread(target=health_check, daemon=True)
    health_thread.start()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lb_socket:
            lb_socket.bind((LOAD_BALANCER_HOST, LOAD_BALANCER_PORT))
            lb_socket.listen(5)
            print(f"Load Balancer listening on {LOAD_BALANCER_HOST}:{LOAD_BALANCER_PORT}")

            while True:
                client_socket, client_address = lb_socket.accept()
                print(f"Received connection from {client_address}")

                # Handle the client connection in a separate thread
                client_thread = Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
    finally:
        # Terminate all backend processes
        for process in backend_processes:
            process.terminate()

if __name__ == "__main__":
    main()
