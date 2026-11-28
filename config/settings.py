
# Traflo - Simulation Configuration

SIMULATION_DURATION = 120

# Fixed traffic signal timings (seconds)
NORTH_SOUTH_GREEN = 30
EAST_WEST_GREEN = 30
CLEARANCE_TIME = 4

# Time needed for one vehicle to cross
SECONDS_PER_VEHICLE = 2

# Starting number of vehicles on each road
INITIAL_VEHICLES = {
    "North": 12,
    "South": 8,
    "East": 6,
    "West": 10
}

# One new vehicle arrives every N seconds
ARRIVAL_INTERVALS = {
    "North": 3,
    "South": 4,
    "East": 5,
    "West": 4
}
