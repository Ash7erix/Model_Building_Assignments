import pandas as pd
import itertools as it
import gurobipy as gp
from gurobipy import GRB
import json


# DATA HANDLING
with open("data.json", "r") as file:
    data = json.load(file)

years = data["years"]
skill_levels = data["skill_levels"]
manpower_requirements = { (skill, year): data["manpower_requirements"][skill][year] for skill in skill_levels for year in range(len(data["manpower_requirements"][skill]))}
wastage_rates = data["wastage_rates"]
recruitment_capacity = data["recruitment_capacity"]
retraining_capacity = data["retraining_capacity"]
retraining_cost = data["retraining_cost"]
downgrade_wastage = data["downgrade_wastage"]
redundancy_cost = data["redundancy_cost"]
overmanning_cost = data["overmanning_cost"]
overmanning_limit = data["overmanning_limit"]
short_time_limit = data["short_time_limit"]
short_time_cost = data["short_time_cost"]


# MODEL SETUP
model = gp.Model('Manpower_Optimization')


# DECISION VARIABLES
TotalWorkers = model.addVars(skill_levels, [0] + list(years), name="TotalWorkers")
RecruitedWorkers = model.addVars(skill_levels, years, name="RecruitedWorkers")
RetrainedWorkers = model.addVars(['UnskilledToSemi', 'SemiToSkilled'], years, name="RetrainedWorkers")
DowngradedWorkers = model.addVars(['SkilledToSemi', 'SkilledToUnskilled', 'SemiToUnskilled'], years, name="DowngradedWorkers")
RedundantWorkers = model.addVars(skill_levels, years, name="RedundantWorkers")
ShortTimeWorkers = model.addVars(skill_levels, years, name="ShortTimeWorkers")
OvermannedWorkers = model.addVars(skill_levels, years, name="OvermannedWorkers")


# CONSTRAINTS
# Initial workforce levels
for skill in skill_levels:
    TotalWorkers[skill, 0] = manpower_requirements[skill, 0]

# Upper bounds on recruitment and short-time working
for year in years:
    for skill in skill_levels:
        RecruitedWorkers[skill, year].ub = recruitment_capacity[skill]
        ShortTimeWorkers[skill, year].ub = short_time_limit
    RetrainedWorkers['UnskilledToSemi', year].ub = retraining_capacity['UnskilledToSemi']

# Workforce continuity constraints
for year in years:
    # Skilled Workforce
    model.addConstr(
        (0.95 * TotalWorkers['Skilled', year - 1] +
         0.90 * RecruitedWorkers['Skilled', year] +
         0.95 * RetrainedWorkers['SemiToSkilled', year] -
         DowngradedWorkers['SkilledToSemi', year] -
         DowngradedWorkers['SkilledToUnskilled', year] -
         RedundantWorkers['Skilled', year]
         == TotalWorkers['Skilled', year]),
        name=f"Skilled_Workforce_Balance_{year}"
    )

    # Semi-Skilled Workforce
    model.addConstr(
        (0.95 * TotalWorkers['SemiSkilled', year - 1] +
         0.80 * RecruitedWorkers['SemiSkilled', year] +
         0.95 * RetrainedWorkers['UnskilledToSemi', year] -
         RetrainedWorkers['SemiToSkilled', year] +
         0.5 * DowngradedWorkers['SkilledToSemi', year] -
         DowngradedWorkers['SemiToUnskilled', year] -
         RedundantWorkers['SemiSkilled', year]
         == TotalWorkers['SemiSkilled', year]),
        name=f"SemiSkilled_Workforce_Balance_{year}"
    )

    # Unskilled Workforce
    model.addConstr(
        (0.90 * TotalWorkers['Unskilled', year - 1] +
         0.75 * RecruitedWorkers['Unskilled', year] -
         RetrainedWorkers['UnskilledToSemi', year] +
         0.5 * DowngradedWorkers['SkilledToUnskilled', year] +
         0.5 * DowngradedWorkers['SemiToUnskilled', year] -
         RedundantWorkers['Unskilled', year]
         == TotalWorkers['Unskilled', year]),
        name=f"Unskilled_Workforce_Balance_{year}"
    )

# Retraining limits
for year in years:
    model.addConstr(RetrainedWorkers['SemiToSkilled', year] <= 0.25 * TotalWorkers['Skilled', year],
                    name=f"SemiToSkilled_Retrain_Limit_{year}")

# Overmanning limit
for year in years:
    model.addConstr(gp.quicksum(OvermannedWorkers[skill, year] for skill in skill_levels) <= overmanning_limit,
                    name=f"Overmanning_Limit_{year}")

# Workforce requirement constraints
for skill in skill_levels:
    for year in years:
        model.addConstr(
            (TotalWorkers[skill, year] - OvermannedWorkers[skill, year] - 0.5 * ShortTimeWorkers[skill, year] ==
             manpower_requirements[skill, year]),
            name=f"Workforce_Requirement_{skill}_{year}"
        )


# OBJECTIVE FUNCTION
model.setObjective(
    gp.quicksum(RedundantWorkers[skill, year] for skill in skill_levels for year in years),
    GRB.MINIMIZE
)


# SOLVE MODEL
model.optimize()


# PRINT RESULTS
def save_results(var_dict, title, file, columns=None):
    file.write(f"\n{title}\n")
    print(f"\n\n\033[94m{title}:\033[0m\n")
    report = pd.DataFrame([], columns=columns if columns else skill_levels, index=years)
    for (skill, year), var in var_dict.items():
        if year > 0:
            report.loc[year, skill] = var.x
    file.write(report.to_string() + "\n\n")
    print(report)


with open("Redundancy_Minimization_Solution.txt", "w", encoding="utf-8") as file:
    file.write(f"Total Redundant Workers: {model.ObjVal:.2f}\n\n")
    print("-"*50)
    print(f"\nTotal Redundant Workers: {model.ObjVal:.2f}")
    save_results(RecruitedWorkers, "Recruitment Plan", file)
    save_results(TotalWorkers, "Available Workforce", file)
    file.write("\n\nTraining & Downgrading Plan\n")
    train_down_columns = ['UnskilledToSemi', 'SemiToSkilled', 'SkilledToSemi', 'SkilledToUnskilled', 'SemiToUnskilled']
    train_down_report = pd.DataFrame([], columns=train_down_columns, index=years)
    for (skill, year), var in RetrainedWorkers.items():
        if year > 0:
            train_down_report.loc[year, skill] = var.x
    for (skill, year), var in DowngradedWorkers.items():
        if year > 0:
            train_down_report.loc[year, skill] = var.x
    file.write(train_down_report.to_string() + "\n")
    print("\n\033[94mTraining & Downgrading Plan:\033[0m")
    print(train_down_report)
    save_results(RedundantWorkers, "Redundancy Plan", file)
    save_results(ShortTimeWorkers, "Short-Time Working Plan", file)
    save_results(OvermannedWorkers, "Overmanning Plan", file)

print("\nResults saved to solution.txt ✅")
