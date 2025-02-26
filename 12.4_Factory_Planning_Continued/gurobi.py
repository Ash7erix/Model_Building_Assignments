from gurobipy import Model, GRB, quicksum
import json

# Load Data
with open("data.json", "r") as file:
    data = json.load(file)

# Data Handling
months = range(0, 7)
products = data["products"]
demand = data["demand"]
time_req = data["time_required"]
profit = {i + 1: data["profit"][i] for i in range(len(data["profit"]))}
name_to_abbreviation = {"Grinding": "GR", "VerticalDrilling": "VD", "HorizontalDrilling": "HD", "Boring": "BR", "Planing": "PL"}
machine_types = {name_to_abbreviation.get(key, key): value for key, value in data["machine_types"].items()}
machine_names = {"GR": "Grinder", "VD": "Vertical Drill", "HD": "Horizontal Drill", "BR": "Borer", "PL":  "Planer"}
name_to_abbreviation = {"Grinding": "GR", "VerticalDrilling": "VD", "HorizontalDrilling": "HD", "Boring": "BR", "Planing": "PL"}
processing_time = {name_to_abbreviation[key]: {i + 1: time_req[key][i] for i in range(len(time_req[key]))} for key in time_req}
machine_availability = {name_to_abbreviation[key]: value for key, value in data["machine_availability"].items()}
working_hours_per_day = data["working_hours_per_day"]
working_days_per_month = data["working_days_per_month"]
total_hours_per_machine = working_hours_per_day * working_days_per_month

# Market demand
market_demand = {i + 1: {t: demand[i][t] for t in months} for i in range(len(demand))}

# Create Gurobi model
model = Model("Factory_Production_Optimization")

# Decision variables
MPROD = model.addVars(products, months, lb=0, name="MPROD")  # Manufactured
SPROD = model.addVars(products, months, lb=0, name="SPROD")  # Sold
HPROD = model.addVars(products, months, lb=0, name="HPROD")  # Held

# Binary maintenance decision variables
MDown = model.addVars(machine_types.keys(), range(1, max(machine_types.values())+1), months[1:], vtype=GRB.BINARY, name="MDown")

# Objective function: Maximize total profit
model.setObjective(
    quicksum(profit[i] * SPROD[i, t] for i in products for t in months) -
    0.5 * quicksum(HPROD[i, t] for i in products for t in months),
    GRB.MAXIMIZE
)

# Machine capacity constraints (accounting for availability and maintenance)
for machine, count in machine_types.items():
    for t in months[1:]:
        available_capacity = sum(machine_availability[machine][t-1] * total_hours_per_machine for _ in range(count))
        model.addConstr(
            quicksum(processing_time.get(machine, {}).get(i, 0) * MPROD[i, t] for i in products)
            <= available_capacity - quicksum(MDown[machine, n, t] * machine_availability[machine][t-1] * total_hours_per_machine for n in range(1, count + 1)),
            f"{machine}_capacity_month_{t}"
        )

# Maintenance scheduling constraints
for machine, count in machine_types.items():
    if machine == "GR":
        model.addConstr(quicksum(MDown[machine, n, t] for n in range(1, count + 1) for t in months[1:]) == 2, f"Two_maintenance_{machine}")
    else:
        for n in range(1, count + 1):
            model.addConstr(quicksum(MDown[machine, n, t] for t in months[1:]) == 1, f"One_maintenance_{machine}_{n}")

# Market demand constraints
for i in products:
    for t in months:
        model.addConstr(SPROD[i, t] <= market_demand[i][t], f"Market_demand_{i}_month_{t}")

# Sales limit constraints
for i in products:
    for t in months:
        model.addConstr(SPROD[i, t] <= MPROD[i, t] + HPROD[i, t], f"Sales_limit_{i}_month_{t}")

# Inventory balance constraints
for i in products:
    for t in range(1, 7):
        model.addConstr(HPROD[i, t-1] + MPROD[i, t] - SPROD[i, t] - HPROD[i, t] == 0, f"Stock_balance_{i}_month_{t}")

# Ensure final inventory is 50 at month 6
for i in products:
    model.addConstr(HPROD[i, 6] == 50, f"End_inventory_{i}")

# Initial inventory constraints
for i in products:
    model.addConstr(HPROD[i, 1] == 0, f"Initial_inventory_{i}")

# Maximum holding inventory constraint
for i in products:
    for t in months:
        model.addConstr(HPROD[i, t] <= 100, f"Max_hold_{i}_month_{t}")

# Solve the model
model.optimize()

# Print and Save Results
with open('solution.txt', 'w', encoding="utf-8") as file:
    if model.status == GRB.OPTIMAL:
        print(f"\n===========================")
        print(f"Optimal Total Profit: £{model.objVal:.2f}")
        file.write(f"Optimal Total Profit: £{model.objVal:.2f}\n")
        print(f"===========================")
        print()
        for t in months[1:]:
            print(f"\n\nMonth {t}:")
            file.write(f"\n\nMonth {t}:\n")
            monthly_profit = 0

            for machine, count in machine_types.items():
                for n in range(1, count + 1):
                    if MDown[machine, n, t].x > 0.5:
                        print(f"🚧 {machine_names[machine]} #{n} is down for maintenance")
                        file.write(f"🚧 {machine_names[machine]} #{n} is down for maintenance\n")

            for i in products:
                manufactured = MPROD[i, t].x
                sold = SPROD[i, t].x
                held = HPROD[i, t].x
                product_profit = profit[i] * sold - 0.5 * held
                monthly_profit += product_profit

                print(f"Product {i}, Manufactured = {round(manufactured,1)}, Stored = {round(HPROD[i, t-1].x,1)}, Sold = {round(sold,1)}, Held = {round(held,1)}")
                file.write(f"Product {i}, Manufactured = {round(manufactured,1)}, Stored = {round(HPROD[i, t-1].x,1)}, Sold = {round(sold,1)}, Held = {round(held,1)}\n")

            print(f"Total profit for Month {t} = £{round(monthly_profit,1)}")
            file.write(f"Total profit for Month {t} = £{round(monthly_profit,1)}\n")

        print("\nResults saved to solution.txt ✅")

    else:
        print("No optimal solution found!")
        file.write("No optimal solution found!")
