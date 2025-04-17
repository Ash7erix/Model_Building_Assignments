import pandas as pd
import gurobipy as gp
import json
from gurobipy import GRB

#Data Handling
with open("data.json", "r") as f:
    data = json.load(f)
Mines = data["Mines"]
Years = data["Years"]
Next_Year = data["Next_Year"]
Royalties = data["Royalties"]
Ore_Limit = data["Ore_Limit"]
Ore_Quality = data["Ore_Quality"]
Req_Quality = data["Required_Quality"]
Year_Disc = data["Year_Discount"]
Blend_Price = data["Blend_Price"]
Discount_Rate = data["Discount_Rate"]
pd.set_option('future.no_silent_downcasting', True)


model = gp.Model('Mining')

# Variables
extract = model.addVars(Mines, Years, name='extract')
make = model.addVars(Years, name='make')
used = model.addVars(Mines, Years, name='used', vtype=gp.GRB.BINARY)
active = model.addVars(Mines, Years, name='active', vtype=gp.GRB.BINARY)


# objective function
model.setObjective(gp.quicksum(Blend_Price*Year_Disc[t]*make[t] for t in Years)
                   - gp.quicksum(Royalties[m]*Year_Disc[t]*active[m,t] for m in Mines for t in Years),
                   GRB.MAXIMIZE)


# add constraints
model.addConstrs((gp.quicksum(used[m,t] for m in Mines) <= 3 for t in Years), name='mines_limit')
model.addConstrs((extract[m,t] - Ore_Limit[m]*used[m,t] <= 0 for m in Mines for t in Years), name='extract_then_used')
model.addConstrs((used[m,t] - active[m,t] <= 0 for m in Mines for t in Years), name='notactive_then_cantbeused')
model.addConstrs((active[m,Next_Year[t]] - active[m,t] <= 0 for m in Mines for t in Years[:4]), name='notactive_then_notactiveanymore')
model.addConstrs((gp.quicksum(Ore_Quality[m]*extract[m,t] for m in Mines) - Req_Quality[t]*make[t] == 0 for t in Years), name='quality')
model.addConstrs((gp.quicksum(extract[m,t] for m in Mines) - make[t] == 0 for t in Years), name='mass_conservation')


model.optimize()


#Output Results
with open("Solution.txt", "w", encoding="utf-8") as file:
    print('Profit of \033[92m£{:.2f}\033[0m'.format(model.objVal))
    file.write(f'Profit of £{model.objVal:.2f}')
    print('\033[94m\n\nWORKING MINES PLAN\033[0m')
    file.write('\n\nWORKING MINES PLAN\n')
    working_mines = {t: [] for t in Years}
    for m, t in used.keys():
        if used[m, t].x > 0.5:  # Binary variable, threshold at 0.5 for robustness
            working_mines[t].append(m)
    for t in Years:
        print(f"{t}: {', '.join(working_mines[t]) if working_mines[t] else 'None'}")
        file.write(f"{t}: {', '.join(working_mines[t]) if working_mines[t] else 'None'}\n")

    extract_solution = pd.DataFrame([], columns=Mines, index=Years)
    extract_solution = extract_solution.fillna(0).infer_objects(copy=False)
    for m, t in extract.keys():
        extract_solution.loc[t, m] = int(extract[m, t].x)
    extract_solution = extract_solution.astype(int)
    print('\033[94m\n\nEXTRACTION PLAN\033[0m')
    file.write('\n\nEXTRACTION PLAN\n')
    print(extract_solution)
    file.write(extract_solution.to_string())
    file.write('\n')

    make_solution = pd.DataFrame([], columns=['Tons'], index=Years)
    make_solution = make_solution.fillna(0).infer_objects(copy=False)
    for t in make.keys():
        make_solution.loc[t, 'Tons'] = int(make[t].x)
    make_solution = make_solution.astype(int)
    print('\033[94m\n\nPRODUCING PLAN\033[0m')
    file.write('\n\nPRODUCING PLAN\n')
    print(make_solution)
    file.write(make_solution.to_string())
    file.write('\n')