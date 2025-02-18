import json
from gurobipy import Model, GRB

# Load data from JSON file
with open("data.json", "r") as file:
    data = json.load(file)

# Extract data
months = data["months"]
veg_oils = data["veg_oils"]
oil_oils = data["oil_oils"]
all_oils = veg_oils + oil_oils
prices = data["prices"]
hardness = data["hardness"]
max_refining = data["max_refining"]

# Extract parameters
params = data["parameters"]
refine_cap_veg = params["refine_cap_veg"]
refine_cap_oil = params["refine_cap_oil"]
storage_cap = params["storage_cap"]
storage_cost = params["storage_cost"]
sell_price = params["sell_price"]
h_min, h_max = params["h_min"], params["h_max"]
initial_stock = params["initial_stock"]

# Model
model = Model("Oil Blending Extended")

# Decision variables
purchase = model.addVars(months, all_oils, lb=0, name="purchase")
storage = model.addVars(months, all_oils, lb=0, name="storage")
refine = model.addVars(months, all_oils, lb=0, name="refine")
production = model.addVars(months, lb=0, name="production")
use = model.addVars(months, all_oils, vtype=GRB.BINARY, name="use")  # Binary variables

# Objective: Maximize profit
model.setObjective(
    sum(sell_price * production[m] - sum(prices[m][i] * purchase[m, oil] for i, oil in enumerate(all_oils))
        - sum(storage_cost * storage[m, oil] for oil in all_oils) for m in months),
    GRB.MAXIMIZE
)

# Constraints

# Inventory balance
for i, oil in enumerate(all_oils):
    for t, month in enumerate(months):
        prev_stock = initial_stock if t == 0 else storage[months[t - 1], oil]
        model.addConstr(storage[month, oil] == prev_stock + purchase[month, oil] - refine[month, oil])

# Refining capacity constraints
for m in months:
    model.addConstr(sum(refine[m, oil] for oil in veg_oils) <= refine_cap_veg)
    model.addConstr(sum(refine[m, oil] for oil in oil_oils) <= refine_cap_oil)

# Production balance
for m in months:
    model.addConstr(production[m] == sum(refine[m, oil] for oil in all_oils))

# Hardness constraints
for m in months:
    model.addConstr(
        h_min * production[m] <= sum(hardness[oil] * refine[m, oil] for oil in all_oils)
    )
    model.addConstr(
        h_max * production[m] >= sum(hardness[oil] * refine[m, oil] for oil in all_oils)
    )

# Storage limits
for m in months:
    for oil in all_oils:
        model.addConstr(storage[m, oil] <= storage_cap)

# # Final stock requirement
for oil in all_oils:
    model.addConstr(storage["Jun", oil] == initial_stock)

# **Additional Constraints**

# (1) At most 3 oils are used in a month
for m in months:
    model.addConstr(sum(use[m, oil] for oil in all_oils) <= 3)

# (2) If an oil is used, at least 20 tons must be refined
for m in months:
    for oil in all_oils:
        model.addConstr(refine[m, oil] >= 20 * use[m, oil])
        model.addConstr(refine[m, oil] <= max_refining[oil] * use[m, oil])  # Using Mi instead of a single M

# (3) If VEG1 or VEG2 is used, then OIL3 must also be used
for m in months:
    model.addConstr(use[m, "VEG1"] + use[m, "VEG2"] <= use[m, "OIL3"])

# Solve the model
model.optimize()

# Print results
if model.status == GRB.OPTIMAL:
    print(f"\n===========================")
    print(f"Optimal Total Profit: £{model.objVal:.2f}")
    print(f"===========================")

    for t, m in enumerate(months):
        # Compute monthly profit
        revenue = sell_price * production[m].x
        cost_oil = sum(prices[m][i] * purchase[m, oil].x for i, oil in enumerate(all_oils))
        cost_storage = sum(storage_cost * storage[months[t - 1], oil].x for oil in all_oils) if t > 0 else 0
        profit_t = revenue - cost_oil - cost_storage

        print(f"\nMonth: {m}")
        print(f"  Profit: £{profit_t:.2f}")
        print(f"  Production: {production[m].x:.2f} tons")

        used_oils = []
        for oil in all_oils:
            if use[m, oil].x > 0.5:  # Used in the blend
                used_oils.append(oil)
                print(f"  Purchase {oil}: {purchase[m, oil].x:.2f} tons")
                print(f"  Refine {oil}: {refine[m, oil].x:.2f} tons")
                print(f"  Storage {oil}: {storage[m, oil].x:.2f} tons")

        print(f"  Oils Used: {used_oils}")


file.close()
print("\nResults saved to solution.txt ✅")
print(f"\n===========================")
print(f"Optimal Total Profit: £{model.objVal:.2f}")
print(f"===========================")