# __init__.py for the algo package

# Optionally import all algorithms for convenience
from .round_robin import select_server as round_robin
from .least_connections import select_server as least_connections
from .hashing import select_server as hashing