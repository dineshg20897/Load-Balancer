# Load Balancer

## Overview
This project implements a custom **application-layer load balancer** in Python. The load balancer distributes incoming client requests across multiple backend servers, ensuring:

- Efficient load distribution using algorithms like **Round Robin**, **Least Connections**, and **Hashing**.
- High availability through periodic health checks of backend servers.
- Dynamic addition and removal of backend servers using a configuration file.

---

## Features

1. **Dynamic Load Balancing:**
   - Supports multiple algorithms:
     - **Round Robin**: Distributes requests evenly across servers.
     - **Least Connections**: Routes requests to the server with the fewest active connections.
     - **Hashing**: Uses client IP to deterministically select a backend server.

2. **Health Monitoring:**
   - Periodic health checks ensure only healthy servers handle requests.

3. **Dynamic Configuration:**
   - Backend servers, algorithms, and health-check settings are configurable via `config.json`.

4. **Automatic Backend Server Startup:**
   - Launches backend servers dynamically based on configuration.

---

## Project Structure

```plaintext
.
├── main.py              # Entry point for the load balancer
├── config.json          # Configuration file for servers and settings
├── algo/                # Load balancing algorithms
│   ├── round_robin.py
│   ├── least_connections.py
│   ├── hashing.py
│   └── __init__.py
├── backend/             # Backend server management
│   ├── BackendServer.py
│   └── __init__.py
├── health/              # Health check functionality
│   ├── health_check.py
│   └── __init__.py
├── requirements.txt     # Project dependencies
└── README.md            # Documentation
```

---

## Setup Instructions

### Prerequisites
1. Install Python 3.7 or later.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
Modify the `config.json` file to define backend servers, load balancing algorithm, and health-check settings:

```json
{
    "servers": [
        { "host": "127.0.0.1", "port": 8080 },
        { "host": "127.0.0.1", "port": 8081 }
    ],
    "algorithm": "round_robin",
    "health_check_url": "/health",
    "health_check_interval": 10
}
```

### Running the Load Balancer
Start the load balancer by executing:

```bash
python main.py
```

### Testing
Send requests to the load balancer:
```bash
curl http://127.0.0.1:<LOAD_BALANCER_PORT>
```

- By default, the port is `8080`.
- Responses will alternate between backend servers (e.g., `127.0.0.1:8080` and `127.0.0.1:8081`).

---

## How It Works

1. **Backend Servers:**
   - Automatically started by the load balancer.

2. **Load Balancing:**
   - Routes requests based on the selected algorithm defined in `config.json`.

3. **Health Checks:**
   - Periodically sends HTTP GET requests to the `/health` endpoint of each server.
   - Removes unhealthy servers from the rotation until they recover.

---

## Customization

- Add new algorithms in the `algo/` folder by implementing a `select_server` function.
- Modify health-check logic in `health/health_check.py`.
- Adjust server configuration dynamically via `config.json` without restarting the load balancer.

---