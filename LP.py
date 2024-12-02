import pulp
import math

# Problem Data (hardcoded)
locations = {
    "DC1": (0, 0),
    "DC2": (10, 10),
    "S1": (5, 5),
    "C1": (2, 3),
    "C2": (3, 7),
    "C3": (6, 2),
    "C4": (8, 9)
}

demand = {
    "C1": 2, "C2": 3, "C3": 4, "C4": 5
}

vehicle_capacity = 10
truck_capacity = 15
U_v = 10  # Vehicle cost per unit distance
U_s = 20  # Semitrailer cost per unit distance

# Euclidean distance function
def euclidean_distance(i, j):
    return math.sqrt((locations[i][0] - locations[j][0])**2 + (locations[i][1] - locations[j][1])**2)

# Create the ILP problem
problem = pulp.LpProblem("Two_Echelon_VRP", pulp.LpMinimize)

# Decision variables
x = pulp.LpVariable.dicts("x", ((i, j, v) for i in locations for j in locations if i != j for v in ["V1", "V2"]), cat='Binary')
y = pulp.LpVariable.dicts("y", ((p, s) for p in ["DC1", "DC2"] for s in ["S1"]), cat='Binary')

# Objective 1: Minimize cost
# Total cost is the sum of transportation costs for vehicles and semitrailer trucks
cost = pulp.lpSum([euclidean_distance(i, j) * (U_v if v == "V1" else U_s) * x[(i, j, v)] for i in locations for j in locations if i != j for v in ["V1", "V2"]])

# Objective 2: Minimize delivery time
# For simplicity, assuming time is directly proportional to distance
time = pulp.lpSum([euclidean_distance(i, j) * x[(i, j, v)] for i in locations for j in locations if i != j for v in ["V1", "V2"]])

# Objective 3: Minimize the number of vehicles
vehicles_used = pulp.lpSum([y[(p, s)] for p in ["DC1", "DC2"] for s in ["S1"]])

# Set the objective function to minimize total cost, time, and vehicles used
problem += cost + time + vehicles_used

# Constraints

# 1. Capacity constraints (vehicles and semitrailers)
for i in locations:
    for j in locations:
        if i != j:
            for v in ["V1", "V2"]:
                problem += pulp.lpSum([x[(i, j, v)])]) <= vehicle_capacity, f"Capacity constraint {i}-{j}"

# 2. Flow conservation
for i in locations:
    problem += pulp.lpSum([x[(i, j, v)] for j in locations if i != j for v in ["V1", "V2"]]) == 1, f"Flow conservation at {i}"

# 3. Non-negativity and binary variables
for var in x.values():
    var.lowBound = 0
    var.upBound = 1

for var in y.values():
    var.lowBound = 0
    var.upBound = 1

# Solve the problem
problem.solve()

# Output the results
print(f"Status: {pulp.LpStatus[problem.status]}")
print("Objective Value (Total Cost, Time, Vehicles): ", pulp.value(problem.objective))
for var in x:
    print(f"{var}: {x[var].varValue}")
