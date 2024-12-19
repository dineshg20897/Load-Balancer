import requests # type: ignore
import time

class HealthCheck:
    def __init__(self, servers, health_check_url, interval):
        self.servers = servers
        self.health_check_url = health_check_url
        self.interval = interval

    def perform_health_check(self):
        """Periodically checks the health of backend servers."""
        while True:
            for server in self.servers:
                try:
                    response = requests.get(f"http://{server[0]}:{server[1]}{self.health_check_url}", timeout=2)
                    if response.status_code == 200:
                        print(f"Server {server[0]}:{server[1]} is healthy.")
                    else:
                        print(f"Server {server[0]}:{server[1]} is unhealthy.")
                except requests.RequestException:
                    print(f"Server {server[0]}:{server[1]} failed the health check.")

            time.sleep(self.interval)