current_server = 0

def select_server(healthy_servers):
    global current_server
    if not healthy_servers:
        return None
    server = healthy_servers[current_server]
    current_server = (current_server + 1) % len(healthy_servers)
    return server