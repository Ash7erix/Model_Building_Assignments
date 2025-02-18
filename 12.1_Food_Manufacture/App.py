import streamlit as st
from gurobipy import Model, GRB
import matplotlib.pyplot as plt
import pandas as pd
import json


#**********************************************#
# Data Handling
#**********************************************#
# Load data from JSON file
with open("data.json", "r") as file:
    data = json.load(file)
# Extract data
months = data["months"]
veg_oils = data["veg_oils"]
non_veg_oils = data["oil_oils"]
oils = veg_oils + non_veg_oils
cost = data["prices"]
hardness = data["hardness"]
max_refining = data["max_refining"]
parameters = data["parameters"]
params = data["parameters"]
veg_capacity = params["refine_cap_veg"]
non_veg_capacity = params["refine_cap_oil"]
max_storage = params["storage_cap"]
storage_cost = params["storage_cost"]
selling_price = params["sell_price"]
h_min, h_max = params["h_min"], params["h_max"]
initial_inventory = params["initial_stock"]
final_inventory = params["final_stock"]
updated_parameters = {
    "Max Storage (/month)": parameters["storage_cap"],
    "Storage Cost (/month)": parameters["storage_cost"],
    "Selling Price (£)": parameters["sell_price"],
    "Hardness Min": parameters["h_min"],
    "Hardness Max": parameters["h_max"],
    "Initial Stock (ton)": parameters["initial_stock"],
    "Final Stock (ton)": parameters["final_stock"]
}
updated_refining_capacity = {
    "VEG1, VEG2 (tons)": parameters["refine_cap_veg"],
    "OIL1, OIL2, OIL3 (tons)": parameters["refine_cap_oil"],
}


#**********************************************#
# === Streamlit Layout ===
#**********************************************#
st.set_page_config(page_title="Food Manufacturing Optimization", page_icon=":bar_chart:", layout="wide")
st.markdown("""
    <style>
        .title-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f4f4f9;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            color: #333;
        }
        .title-bar h1 {
            margin: 0;
            font-size: 49px;
            color: #333;
            margin-left: 20px;
        }
        .title-bar .logo1 {
            max-width: auto;
            height: 60px;
            margin-right: 20px;
        }
        .title-bar a {
            text-decoration: none;
            color: #0073e6;
            font-size: 16px;
        }
        .footer-text {
            font-size: 20px;
            background-color: #f4f4f9;
            text-align: left;
            color: #333;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
        }
    </style>
    <div class="title-bar">
        <h1>Problem 12.1 <br> Food Manufacture</h1>
        <div>
            <a href="https://decisionopt.com" target="_blank">
                <img src="https://decisionopt.com/static/media/DecisionOptLogo.7023a4e646b230de9fb8ff2717782860.svg" class="logo1" alt="Logo"/>
            </a>
        </div>
    </div>
    <div class="footer-text">
    <p style="margin-left:20px;">  'Model Building in Mathematical Programming, Fifth Edition' by H. Paul Williams</p>
    </div>    
""", unsafe_allow_html=True)
st.markdown("""
    <style>
        .container-c1 p {
            font-size: 20px;
        }
    </style>
    <div class="container-c1">
        <br><p >This app optimizes the food manufacturing process by selecting the best oils to refine 
        each month, maximizing profit. It uses <b>Gurobi</b> for optimization, considering factors like oil 
        costs, refining capacities, storage limits, and hardness constraints.</p> 
        <br><p>You can also adjust the parameters like refining capacities, storage costs, and oil prices, 
        using the options on the left side and the app provides detailed results including oil purchase, 
        refining, storage, and production data for each month.</p>
    </div>
""", unsafe_allow_html=True)




#**********************************************#
# Convert the prices dictionary into a DataFrame for display
#**********************************************#
prices_df = pd.DataFrame(cost, index=["VEG1", "VEG2", "OIL1", "OIL2", "OIL3"]).T
st.title("Optimization Data and Constraints:")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("Monthly Oil Prices (£)")
    st.dataframe(prices_df)
with col4:
    st.subheader("Hardness Values")
    hardness_df = pd.DataFrame(list(hardness.items()), columns=["Oil Type", "Hardness"])
    hardness_df.index = range(1, len(hardness_df) + 1)
    st.dataframe(hardness_df)
with col2:
    st.subheader("Parameters")
    parameters_df = pd.DataFrame(list(updated_parameters.items()), columns=["Parameter", "Value"])
    parameters_df.index = range(1, len(parameters_df) + 1)
    st.dataframe(parameters_df)
with col3:
    st.subheader("Max Refining Capacity")
    max_refining_df = pd.DataFrame(list(updated_refining_capacity.items()), columns=["Oil Type", "Max"])
    max_refining_df.index = range(1, len(max_refining_df) + 1)
    st.dataframe(max_refining_df)




#**********************************************#
#           Sidebar for user inputs
#**********************************************#
st.sidebar.markdown(f"<h2>Please select the box below to add the additional constraints of the problem:</h2>",unsafe_allow_html=True)
st.sidebar.markdown("""
1. At most 3 oils can be used in a month.
2. If an oil is used, at least 20 tons must be refined.
3. If VEG1 or VEG2 is used, then OIL3 must also be used.
""")

apply_additional_constraints = st.sidebar.checkbox("Apply Additional Constraints", value=False)
st.sidebar.markdown("""---""")
st.sidebar.markdown(f"<h1><b>Optimization Parameters:</b></h1>",unsafe_allow_html=True)
# Purchase costs for each oil per month
cost_input = {}
for i, oil in enumerate(oils):
    cost_input[oil] = []
    for month, value in zip(months, cost.values()):
        cost_input[oil].append(
            st.sidebar.number_input(f"Cost of {oil} in {month} (£/ton)", min_value=0, value=value[oils.index(oil)]))
hardness_input = {oil: st.sidebar.number_input(f"Hardness of {oil}", min_value=0.0, value=hardness[oil]) for oil in
                  oils}
veg_capacity = st.sidebar.number_input("Veg Oil Refining Capacity (tons)", min_value=0, value=veg_capacity)
non_veg_capacity = st.sidebar.number_input("Non-Veg Oil Refining Capacity (tons)", min_value=0, value=non_veg_capacity)
max_storage = st.sidebar.number_input("Max Storage Capacity (tons)", min_value=0, value=max_storage)
storage_cost = st.sidebar.number_input("Storage Cost per Ton (£)", min_value=0, value=storage_cost)
initial_inventory = st.sidebar.number_input("Initial Inventory (tons)", min_value=0, value=initial_inventory)
final_inventory = st.sidebar.number_input("Final Inventory (tons)", min_value=0, value=final_inventory)
selling_price = st.sidebar.number_input("Selling Price per Ton of Final Product (£)", min_value=0, value=selling_price)






#**********************************************#
#              Optimization Model
#**********************************************#
model = Model("Food Manufacturing Optimization")

# Decision Variables
OilBought = model.addVars(oils, months, name="OilBought", lb=0)
OilRefined = model.addVars(oils, months, name="OilRefined", lb=0)
Storage = model.addVars(oils, months, name="Storage", lb=0)
Produce = model.addVars(months, name="Produce", lb=0)
IfUsed = model.addVars(oils, months, vtype=GRB.BINARY, name="IfUsed")

# Objective Function
model.setObjective(
    sum(selling_price * Produce[t] for t in months) -
    sum(cost_input[oil][months.index(t)] * OilBought[oil, t] for oil in oils for t in months) -
    sum(storage_cost * Storage[oil, t] for oil in oils for t in months),
    GRB.MAXIMIZE)

# Constraints
for oil in oils:
    for t in months:
        prev_month = months[months.index(t) - 1] if months.index(t) > 0 else None
        if prev_month:
            model.addConstr(
                Storage[oil, t] == Storage[oil, prev_month] + OilBought[oil, t] - OilRefined[oil, t],
                name=f"InventoryBalance_{oil}_{t}"
            )
        else:
            model.addConstr(
                Storage[oil, t] == initial_inventory + OilBought[oil, t] - OilRefined[oil, t],
                name=f"InventoryBalance_{oil}_{t}"
            )

for oil in oils:
    model.addConstr(Storage[oil, "Jun"] == final_inventory, name=f"FinalInventory_{oil}")

for t in months:
    model.addConstr(sum(OilRefined[oil, t] for oil in veg_oils) <= veg_capacity, name=f"VegRefiningCap_{t}")
    model.addConstr(sum(OilRefined[oil, t] for oil in non_veg_oils) <= non_veg_capacity, name=f"NonVegRefiningCap_{t}")

for t in months:
    model.addConstr(Produce[t] == sum(OilRefined[oil, t] for oil in oils), name=f"FinalProduct_{t}")

for t in months:
    model.addConstr(
        3 * sum(OilRefined[oil, t] for oil in oils) <= sum(hardness_input[oil] * OilRefined[oil, t] for oil in oils),
        name=f"HardnessLowerBound_{t}"
    )
    model.addConstr(
        sum(hardness_input[oil] * OilRefined[oil, t] for oil in oils) <= 6 * sum(OilRefined[oil, t] for oil in oils),
        name=f"HardnessUpperBound_{t}"
    )

for oil in oils:
    for t in months:
        model.addConstr(Storage[oil, t] <= max_storage, name=f"StorageLimit_{oil}_{t}")

# Additional Constraints
if apply_additional_constraints:
    for t in months:
        model.addConstr(sum(IfUsed[oil, t] for oil in oils) <= 3, name=f"MaxOilsUsed_{t}")

        for oil in oils:
            model.addConstr(OilRefined[oil, t] >= 20 * IfUsed[oil, t], name=f"MinOilUsed_{oil}_{t}")
            model.addConstr(OilRefined[oil, t] <= max_refining[oil] * IfUsed[oil, t], name=f"MaxOilUsed_{oil}_{t}")

        model.addConstr(IfUsed["VEG1", t] + IfUsed["VEG2", t] <= IfUsed["OIL3", t], name=f"OilUsageCondition_{t}")
st.markdown("""---""")




#**********************************************#
# Solve Model when the button is clicked
#**********************************************#
st.markdown("""
    <style>
        .container-c2 p {
            font-size: 20px;
            margin-bottom: 20px;
        }
    </style>
    <div class="container-c2">
        <br><p>Click on the button below to solve the optimization problem.</p>
    </div>
""", unsafe_allow_html=True)
if st.button("Solve Optimization"):
    model.optimize()
    if model.status == GRB.OPTIMAL:
        st.markdown("""---""")
        total_profit = model.objVal
        st.markdown(f"<h3>Total Profit : <span style='color:rgba(255, 75, 75, 1)  ;'> <b>£{total_profit:.2f}</b></span></h3>", unsafe_allow_html=True)
        st.markdown("""---""")

        # Separate graphs for Bought, Refined, and Stored
        bought_data = {}
        refined_data = {}
        stored_data = {}

        # Collect data for each oil type across months
        for oil in oils:
            bought_data[oil] = [OilBought[oil, t].x for t in months]
            refined_data[oil] = [OilRefined[oil, t].x for t in months]
            stored_data[oil] = [Storage[oil, t].x for t in months]

        # Display Oil Bought Graph
        st.markdown(f"<h1>Oil Buying Trends:</h1>",unsafe_allow_html=True)
        fig_bought, ax_bought = plt.subplots(figsize=(8, 5))
        for oil in oils:
            ax_bought.plot(months, bought_data[oil], label=oil, marker='o', linestyle='-', markersize=6)
        ax_bought.set_title("Oil Bought Over Time", fontsize=16)
        ax_bought.set_xlabel("Months", fontsize=12)
        ax_bought.set_ylabel("Tons", fontsize=12)
        ax_bought.legend(title="Oil Type", fontsize=10)
        ax_bought.grid(True)
        st.pyplot(fig_bought)

        # Display Oil Refined Graph
        st.markdown(f"<h1>Oil Refining Trends:</h1>",unsafe_allow_html=True)
        fig_refined, ax_refined = plt.subplots(figsize=(8, 5))
        for oil in oils:
            ax_refined.plot(months, refined_data[oil], label=oil, marker='o', linestyle='-', markersize=6)
        ax_refined.set_title("Oil Refined Over Time", fontsize=16)
        ax_refined.set_xlabel("Months", fontsize=12)
        ax_refined.set_ylabel("Tons", fontsize=12)
        ax_refined.legend(title="Oil Type", fontsize=10)
        ax_refined.grid(True)
        st.pyplot(fig_refined)

        # Display Oil Stored Graph
        st.markdown(f"<h1>Oil Storing Trends:</h1>",unsafe_allow_html=True)
        fig_stored, ax_stored = plt.subplots(figsize=(8, 5))
        for oil in oils:
            ax_stored.plot(months, stored_data[oil], label=oil, marker='o', linestyle='-', markersize=6)
        ax_stored.set_title("Oil Stored Over Time", fontsize=16)
        ax_stored.set_xlabel("Months", fontsize=12)
        ax_stored.set_ylabel("Tons", fontsize=12)
        ax_stored.legend(title="Oil Type", fontsize=10)
        ax_stored.grid(True)
        st.pyplot(fig_stored)
        st.markdown("""---""")

        for t in months:
            st.subheader(f"**Month :** {t}")
            # Create two columns
            col1, col2 = st.columns(2)

            # Column 1: Display the plot
            with col1:
                fig, ax = plt.subplots(figsize=(3, 2))  # Smaller plot size (6x3)

                # Data for the plot
                oil_data = {
                    "Oil Bought": [OilBought[oil, t].x for oil in oils],
                    "Oil Refined": [OilRefined[oil, t].x for oil in oils],
                    "Oil Stored": [Storage[oil, t].x for oil in oils],
                }
                df = pd.DataFrame(oil_data, index=oils)

                # Plot the bar chart
                df.plot(kind='bar', ax=ax)

                # Adjust font sizes for title, axes labels, and ticks
                ax.set_title(f"Oil Metrics for {t}", fontsize=6)  # Smaller font for title
                ax.set_xlabel("Oil Types", fontsize=6)  # Smaller font for x-axis label
                ax.set_ylabel("Tons", fontsize=6)  # Smaller font for y-axis label
                ax.tick_params(axis='both', labelsize=4)  # Smaller font for axis ticks
                ax.legend(fontsize=6, loc='upper left', bbox_to_anchor=(1, 1))

                # Adjust layout to fit the plot into a smaller space
                plt.tight_layout(pad=1.0)  # This adjusts the padding around the plot for better fit

                # Display the plot in Streamlit with a more compact size
                st.pyplot(fig, use_container_width=False)

            # Column 2: Display the table
            with col2:
                oil_metrics = {
                    "VEG1": [OilBought["VEG1", t].x, OilRefined["VEG1", t].x, Storage["VEG1", t].x],
                    "VEG2": [OilBought["VEG2", t].x, OilRefined["VEG2", t].x, Storage["VEG2", t].x],
                    "OIL1": [OilBought["OIL1", t].x, OilRefined["OIL1", t].x, Storage["OIL1", t].x],
                    "OIL2": [OilBought["OIL2", t].x, OilRefined["OIL2", t].x, Storage["OIL2", t].x],
                    "OIL3": [OilBought["OIL3", t].x, OilRefined["OIL3", t].x, Storage["OIL3", t].x],
                }

                # Create the table
                oil_table_data = pd.DataFrame(oil_metrics, index=["Purchase", "Refine", "Storage"]).T
                st.write(f"**Oil Metrics for {t}:**")
                st.write(oil_table_data)
                month_profit = (
                        selling_price * Produce[t].x -
                        sum(cost_input[oil][months.index(t)] * OilBought[oil, t].x for oil in oils) -
                        sum(storage_cost * Storage[oil, t].x for oil in oils)
                )
                st.write(f"**Profit:** £{month_profit:.2f}")
                st.write(f"**Production:** {Produce[t].x:.2f} tons")
            st.markdown("""---""")


        st.markdown("""
            <style>
                footer {
                    text-align: center;
                    background-color: #f1f1f1;
                    color: #333;
                    font-size: 19px;
                    margin-bottom:0px;
                }
                footer img {
                    width: 44px; /* Adjust size of the logo */
                    height: 44px;
                }
            </style>
            <footer>
                <h1>Author- Ashutosh <a href="https://www.linkedin.com/in/ashutoshpatel24x7/" target="_blank">
                <img src="https://decisionopt.com/static/media/LinkedIn.a6ad49e25c9a6b06030ba1b949fcd1f4.svg" class="img" alt="Logo"/></h1>
            </footer>
        """, unsafe_allow_html=True)
        st.markdown("""---""")
    else:
        st.write("No optimal solution found.")
        st.markdown("""
                    <style>
                        footer {
                            text-align: center;
                            background-color: #f1f1f1;
                            color: #333;
                            font-size: 19px;
                        }
                        footer img {
                            width: 44px; /* Adjust size of the logo */
                            height: 44px;
                        }
                    </style>
                    <footer>
                        <h1>Author- Ashutosh <a href="https://www.linkedin.com/in/ashutoshpatel24x7/" target="_blank">
                        <img src="https://decisionopt.com/static/media/LinkedIn.a6ad49e25c9a6b06030ba1b949fcd1f4.svg" class="img" alt="Logo"/></h1>
                    </footer>
                """, unsafe_allow_html=True)
        st.markdown("""---""")
