connection_counts = {}

def select_server(healthy_servers):
    global connection_counts
    if not healthy_servers:
        return None
    for server in healthy_servers:
        if server not in connection_counts:
            connection_counts[server] = 0
    server = min(healthy_servers, key=lambda s: connection_counts[s])
    connection_counts[server] += 1
    return server