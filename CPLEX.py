import random
import math

# Problem parameters
DCs = {"DC1": (0, 0), "DC2": (10, 10)}
Satellites = {"S1": (5, 5)}
Customers = {
    "C1": {"location": (2, 3), "demand": 2, "time_window": [10, 12]},
    "C2": {"location": (3, 7), "demand": 3, "time_window": [11, 13]},
    "C3": {"location": (6, 2), "demand": 4, "time_window": [14, 16]},
    "C4": {"location": (8, 9), "demand": 5, "time_window": [15, 17]},
}
vehicle_capacity = 10
truck_capacity = 15
U_v = 10  # Cost per unit distance for vehicles
U_s = 20  # Cost per unit distance for semitrailer trucks

# Map node names to coordinates
node_coordinates = {
    "DC1": (0, 0),
    "DC2": (10, 10),
    "S1": (5, 5),
    "C1": (2, 3),
    "C2": (3, 7),
    "C3": (6, 2),
    "C4": (8, 9),
}

# Helper functions
def euclidean_distance(loc1, loc2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((loc1[0] - loc2[0])*2 + (loc1[1] - loc2[1])*2)

def calculate_route_cost(route, is_first_echelon=False):
    """Calculate the cost of a given route."""
    cost = 0
    for i in range(len(route) - 1):
        # Map node names to coordinates
        loc1 = node_coordinates[route[i]]
        loc2 = node_coordinates[route[i + 1]]
        cost += euclidean_distance(loc1, loc2) * (U_s if is_first_echelon else U_v)
    return cost

def evaluate_solution(solution):
    """Evaluate a solution for cost, time, and vehicles."""
    first_echelon_routes, second_echelon_routes = solution
    cost = 0
    vehicles = len(second_echelon_routes)
    for route in first_echelon_routes:
        cost += calculate_route_cost(route, is_first_echelon=True)
    for route in second_echelon_routes:
        cost += calculate_route_cost(route)
    time = sum([len(route) for route in second_echelon_routes])  # Placeholder for time
    return cost, time, vehicles

def is_feasible(solution):
    """Check if a solution is feasible (capacity, time windows, etc.)."""
    _, second_echelon_routes = solution
    for route in second_echelon_routes:
        load = sum([Customers[node]["demand"] for node in route if node in Customers])
        if load > vehicle_capacity:
            return False
    return True

def generate_initial_solution():
    """Generate an initial feasible solution."""
    # First echelon: DCs to satellites
    first_echelon_routes = [["DC1", "S1"], ["DC2", "S1"]]
    # Second echelon: Satellites to customers
    second_echelon_routes = [
        ["C1", "C2"],
        ["C3", "C4"]
    ]
    return first_echelon_routes, second_echelon_routes

def apply_neighborhood_operator(solution, operator):
    """Apply a neighborhood operator to modify the solution."""
    first_echelon, second_echelon = solution
    if operator == "swap":
        if len(second_echelon) > 1:
            # Swap two customers between routes
            r1, r2 = random.sample(range(len(second_echelon)), 2)
            if len(second_echelon[r1]) > 0 and len(second_echelon[r2]) > 0:
                i1, i2 = random.randint(0, len(second_echelon[r1]) - 1), random.randint(0, len(second_echelon[r2]) - 1)
                second_echelon[r1][i1], second_echelon[r2][i2] = second_echelon[r2][i2], second_echelon[r1][i1]
    elif operator == "split":
        # Split a route into two
        if len(second_echelon) > 0:
            route = random.choice(second_echelon)
            if len(route) > 1:
                split_point = random.randint(1, len(route) - 1)
                second_echelon.remove(route)
                second_echelon.append(route[:split_point])
                second_echelon.append(route[split_point:])
    return first_echelon, second_echelon

def non_dominated_sorting(population):
    """Perform non-dominated sorting to find Pareto-optimal solutions."""
    pareto_front = []
    for solution in population:
        dominated = False
        for other in population:
            if other != solution and dominates(other, solution):
                dominated = True
                break
        if not dominated:
            pareto_front.append(solution)
    return pareto_front

def dominates(sol1, sol2):
    """Check if sol1 dominates sol2."""
    obj1 = evaluate_solution(sol1)
    obj2 = evaluate_solution(sol2)
    return all(o1 <= o2 for o1, o2 in zip(obj1, obj2)) and any(o1 < o2 for o1, o2 in zip(obj1, obj2))

# Main algorithm
def moalns_sa():
    """Main Multi-Objective Adaptive Large Neighborhood Search with Split Algorithm."""
    # Step 1: Initialization
    population = [generate_initial_solution() for _ in range(5)]
    pareto_front = []

    # Step 2: Iterative improvement
    for iteration in range(50):
        for solution in population:
            # Apply a random neighborhood operator
            operator = random.choice(["swap", "split"])
            new_solution = apply_neighborhood_operator(solution, operator)

            # Check feasibility and evaluate
            if is_feasible(new_solution):
                pareto_front = non_dominated_sorting(pareto_front + [new_solution])

    return pareto_front

# Run the algorithm
pareto_solutions = moalns_sa()

# Output the Pareto-optimal solutions
for solution in pareto_solutions:
    print("Solution:", solution, "Objectives:", evaluate_solution(solution))