from gurobipy import Model, GRB, quicksum
import json

with open("data.json", "r") as file:
    data = json.load(file)

#Data Handling
months = range(0, 7)
products = data["products"]
demand = data["demand"]
time_req = data["time_required"]
monthname = {i + 1: data["months"][i] for i in range(len(data["months"]))}
profit = {i + 1: data["profit"][i] for i in range(len(data["profit"]))}
name_to_abbreviation = {"Grinding": "GR", "VerticalDrilling": "VD", "HorizontalDrilling": "HD", "Boring": "BR", "Planing": "PL"}
processing_time = {name_to_abbreviation[key]: {i + 1: time_req[key][i] for i in range(len(time_req[key]))} for key in time_req}
machine_availability = {name_to_abbreviation[key]: value for key, value in data["machine_availability"].items()}
initial_inventory=data["initial_inventory"]
final_inventory=data["final_inventory"]
working_hours_per_day = data["working_hours_per_day"]
working_days_per_month = data["working_days_per_month"]
total_hours_per_machine = working_hours_per_day * working_days_per_month
market_demand = {}
for index, row in enumerate(demand, start=1):
    market_demand[index] = {i: row[i] for i in range(len(row))}

# Create the Gurobi model
model = Model("Factory_Production_Optimization")

# Decision variables
MPROD = model.addVars(products, months, lb=0, name="MPROD")  # Manufactured quantities
SPROD = model.addVars(products, months, lb=0, name="SPROD")  # Sold quantities
HPROD = model.addVars(products, months, lb=0, name="HPROD")  # Held quantities

# Objective function: Maximize total profit
model.setObjective(
    quicksum(profit[i] * SPROD[i, t] for i in products for t in months) -
    0.5 * quicksum(HPROD[i, t] for i in products for t in months),
    GRB.MAXIMIZE
)

# Constraints for machine capacity based on availability
# Constraints for machine capacity based on availability
for machine in ["GR", "VD", "HD", "BR", "PL"]:
    for t in months:
        if t == 0:  # Handle month 0 separately, as machine availability starts from month 1
            available_capacity = machine_availability[machine][0] * total_hours_per_machine
        else:
            available_capacity = machine_availability[machine][t-1] * total_hours_per_machine
        model.addConstr(
            quicksum(processing_time.get(machine, {}).get(i, 0) * MPROD[i, t] for i in products) <= available_capacity,
            f"{machine}_capacity_month_{t}"
        )


# Market demand constraints (upper bounds)
for i in products:
    for t in months:
        model.addConstr(SPROD[i, t] <= market_demand[i][t], f"Market_demand_{i}_month_{t}")

# Sales cannot exceed the sum of production and held stock
for i in products:
    for t in months:
        model.addConstr(SPROD[i, t] <= MPROD[i, t] + HPROD[i, t], f"Sales_limit_{i}_month_{t}")

# Inventory balance constraints (from previous month to the next month)
for i in products:
    for t in range(1, 7):  # From month 1 to month 6
        model.addConstr(HPROD[i, t-1] + MPROD[i, t] - SPROD[i, t] - HPROD[i, t] == 0, f"Stock_balance_{i}_month_{t}")

# Ensure there is inventory of 50 at the end of month 6
for i in products:
    model.addConstr(HPROD[i, 6] == 50, f"End_inventory_{i}")

# Add the initial inventory constraint for Month 0 to be 0 (no stock in the start month)
for i in products:
    model.addConstr(HPROD[i, 1] == 0, f"Initial_inventory_{i}")

# Max inventory constraint (max 100 units held in any month)
for i in products:
    for t in months:
        model.addConstr(HPROD[i, t] <= 100, f"Max_hold_{i}_month_{t}")

# Solve the model
model.optimize()

# Print the results
total_profit_per_month = [0] * 7  # To store total profit for each month

with open('solution.txt', 'w') as file:
    if model.status == GRB.OPTIMAL:
        print(f"\n===========================")
        print(f"Optimal Total Profit: £{model.objVal:.2f}")
        file.write(f"Optimal Total Profit: £{model.objVal:.2f}\n")
        print(f"===========================")
        for t in months:
            if t > 0:
                print(f"\n\nMonth {t}:")
                file.write(f"\n\nMonth {t}:\n")
                monthly_profit = 0  # To store profit for the current month
                for i in products:
                    manufactured = MPROD[i, t].x
                    sold = SPROD[i, t].x
                    held = HPROD[i, t].x
                    product_profit = profit[i] * sold - 0.5 * held  # Profit for each product
                    monthly_profit += product_profit  # Add to monthly profit
                    total_profit_per_month[t] = monthly_profit
                    print(f"Product {i}, Manufactured = {round(manufactured,1)}, Previously Stored = {round(HPROD[i, t-1].x,1)}, Sold = {round(sold,1)}, Held = {round(held,1)}")
                    file.write(f"Product {i}, Manufactured = {round(manufactured,1)}, Previously Stored = {round(HPROD[i, t-1].x,1)}, Sold = {round(sold,1)}, Held = {round(held,1)}\n")
                total_profit_per_month[t] = monthly_profit
                print(f"Total profit for Month {t} = {round(monthly_profit,1)}")
                file.write(f"Total profit for Month {t} = {round(monthly_profit,1)}\n")


        # Print the objective value
        total_profit = sum(total_profit_per_month)
        print(f"\nOverall Total Profit (calculated manually) = £ {round(total_profit,1)}")
        print(f"Total Profit = £ {round(model.objVal,1)}")
        file.write(f"\nOverall Total Profit (calculated manually) = £ {round(total_profit,1)}\n")
        file.write(f"Total Profit = £ {round(model.objVal,1)}")
        file.close()
        print("\nResults saved to solution.txt ✅")
    else:
        print("No optimal Solution Found!")
        file.write(f"No optimal Solution Found!")