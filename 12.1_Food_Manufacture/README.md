# Mathematical Formulation
## Decision Variables:
$\text{OilBought}_{i,t} = \text{ Tons of raw oil } i \text{ purchased in month } t$

$\text{Storage}_{i,t} = \text{Tons of raw oil } i \text{ stored at the end of month } t$

$\text{OilRefined}_{i,t} = \text{Tons of raw oil } i \text{ refined in month } t$

$IfUsed_{i,t} = \text{Binary variable, 1 if oil  } i \text{ is used in month } t \text{ , 0 otherwise. }$  

$\text{Produce}_t = \text{Tons of final product produced in month } t$

$\text{OilCost}_{i,t} = \text{Purchase price of oil } i \text{ in month } t$

$Hardness_i = \text{Hardness of oil } i$


## Objective Function:

$$\text{maximize} \sum_{t} 150\ Produce_{t} -\sum_{i,t}^{}OilCost_{i,t}\quad OilBought_{i,t}-\sum_{i,t}^{}5 ‎Storage_{i,t-1}$$

## Subject to:

1. Inventory Balance(for each oil i, month t):

$$
Storage_{i,t} = Storage_{i,t-1} + OilBought_{i,t} - OilRefined_{i,t}
$$


2. Refining Capacity (for each month t):
   
$$
\sum_{i \in \text{VEG}} OilRefined_{i,t} \leq 200
$$
$$
\sum_{i \in \text{OIL}} OilRefined_{i,t} \leq 250
$$


3. Final Product Production (for each month t):
   
$$
Produce_{t}=\sum_{i} OilRefined_{i,t}
$$


4. Hardness Constraint (for each month t):
   
$$
3 \leq \frac{\sum_{i} Hardness_{i} \quad OilRefined_{i,t}}{\sum_{i} OilRefined_{i,t}} \leq 6
$$


5. Storage Limits:
   
$$
Storage_{i,t} \leq 1000 
$$


6. Final Stock Condition:

$$
Storage_{i,6} = 500
$$


7. Non-negativity:

$$
OilBought_{i,t}, Storage_{i,t}, OilRefined_{i,t}, Produce_{t} \geq 0
$$


## Additional Constraints:

8. Max Oils used per month:
   
$$
\sum_{i} IfUsed_{i,t} \leq 3 ,\quad\quad\quad  \forall t
$$


9. Minimum Oil Used if Selected:

$$
OilRefined_{i,t} \geq 20IfUsed_{i,t} ,\quad\quad\quad  \forall i,t
$$


10. Max Oils used per month:
    
$$
IfUsed_{VEG1,t} + IfUsed_{VEG2,t} \leq IfUsed_{OIL3,t}
$$








