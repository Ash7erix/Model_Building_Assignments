import itertools as it
import gurobipy as gp
from gurobipy import GRB
import json


# DATA HANDLING
with open("data.json", "r") as json_file:
    data = json.load(json_file)
data1 = list(data["distilYields"].values())
data2 = list(data["reformYields"].values())
data3 = list(data["crackingYields"].values())
rawMaterials = data["rawMaterials"]
finalProducts = data["finalProducts"]
productProfit = data["productProfit"]
distilOutputs = data["distilOutputs"]
reformOutputs = data["reformOutputs"]
crackingOutputs = data["crackingOutputs"]
distilYields = dict(zip(it.product(rawMaterials, distilOutputs), data1))
reformYields = dict(zip(it.product(distilOutputs[:3], reformOutputs), data2))
crackingYields = dict(zip(it.product(distilOutputs[3:5], crackingOutputs), data3))
used_in = data["used_in"]
used_to =[tuple(item) for item in data["used_to"]]
propor = data["propor"]
quality = data["quality"]
octane = data["octane"]
pressures = data["pressures"]
ingredient = data["ingredient"]
oils = data["distilOutputs"][3:5]
oils_plus = list(used_in.keys())[3:7]
naphthas = data["distilOutputs"][:3]
all_materials = rawMaterials + finalProducts + distilOutputs + reformOutputs + crackingOutputs
MaxCrudeOil1 = data["MaxCrudeOil1"]
MaxCrudeOil2 = data["MaxCrudeOil2"]
MinLubeOil = data["MinLubeOil"]
MaxLubeOil = data["MaxLubeOil"]


# MODEL SETUP
model = gp.Model('Refinery Optimization')


# DECISION VARIABLES
x = model.addVars(all_materials, name='x')
y = model.addVars(used_to, name='y')
x['CrudeOil1'].ub = MaxCrudeOil1
x['CrudeOil2'].ub = MaxCrudeOil2
x['LubeOil'].ub = MaxLubeOil
x['LubeOil'].lb = MinLubeOil


# OBJECTIVE FUNCTION
model.setObjective((gp.quicksum(productProfit[p] * x[p] for p in finalProducts)), GRB.MAXIMIZE)


# CONSTRAINTS
# Max barrels of Crude that can be distilled per day.
model.addConstr((x['CrudeOil1'] + x['CrudeOil2'] <= 45000), name='distillation')

# Max barrels of naphtha that can be reformed per day.
model.addConstr((gp.quicksum(y[n, 'ReformedGasoline'] for n in naphthas) <= 10000), name='reforming')

# Max barrels of oil that can be cracked per day.
model.addConstr((gp.quicksum(y[o, 'Cracked'] for o in oils) <= 8000), name='cracking')

# Conservation
for p in distilOutputs:
    model.addConstr((x[p] == gp.quicksum(distilYields[m, p] * x[m] for m in rawMaterials)), name='dist' + p)

p = 'ReformedGasoline'
model.addConstr((x[p] == gp.quicksum(reformYields[n, p] * y[n, p] for n in naphthas)), name='refo' + p)

for p in crackingOutputs:
    model.addConstr((x[p] == gp.quicksum(crackingYields[o, p] * y[o, 'Cracked'] for o in oils)), name='cracked' + p)

p = 'LubeOil'
model.addConstr((x[p] == 0.5 * y[('Residuum', p)]), name='lube')

for p in naphthas:
    model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

for p in oils_plus:
    model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p]) + propor[p] * x['FuelOil']), name=p)

p = 'CrackedGasoline'
model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

p = 'ReformedGasoline'
model.addConstr((x[p] == gp.quicksum(y[p, i] for i in used_in[p])), name=p)

for p in ['PremiumPetrol', 'RegularPetrol', 'JetFuel']:
    model.addConstr((x[p] == gp.quicksum(y[i, p] for i in ingredient[p])), name=p)

model.addConstr((x['PremiumPetrol'] >= 0.4 * x['RegularPetrol']), name='40perc')

# Quality
for p in ['PremiumPetrol', 'RegularPetrol']:
    model.addConstr((quality[p] * x[p] <= gp.quicksum(octane[i] * y[i, p] for i in ingredient[p])), name='octa_' + p)

p = 'JetFuel'
model.addConstr((x[p] >= gp.quicksum(pressures[i] * y[i, p] for i in ingredient[p])), name='pres_' + p)

model.optimize()

# Output Results
with open("Solution.txt", "w", encoding="utf-8") as file:
    file.write(f'Profit of $ {model.ObjVal:.2f}')
    print(f"\nProfit of\033[92m $ {model.ObjVal:.2f}\033[0m")
    file.write('\nQuantities of materials and final products:\n')
    print('\nQuantities of materials and final products:\n')
    for p in x.keys():
        print('{:20} {:.1f}'.format(p, x[p].x))
        file.write(f'{p:20} {x[p].x:.1f}\n')