def select_server(healthy_servers, client_ip=None):
    if not healthy_servers:
        return None
    if client_ip is None:
        return healthy_servers[0]  # Fallback to the first server if IP is not provided
    index = hash(client_ip) % len(healthy_servers)
    return healthy_servers[index]