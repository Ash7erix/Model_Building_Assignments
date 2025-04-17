# Mathematical Formulation

## Decision Variables:

$extract_{m,t} = \text{Tons of ore extracted from mine } m \text{ in year } t$

$make_t = \text{Total tons of blended ore produced in year } t$

$used_{m,t} \in \{0,1\}$ — 1 if mine *m* is used in year *t*, 0 otherwise.  

$active_{m,t} \in \{0,1\}$ — 1 if mine *m* is kept open (active) in year *t*, 0 otherwise.


## Objective Function:

Maximize total **discounted profit**:

$$
\max \sum_{t \in T} \delta_t \cdot p \cdot make_t - \sum_{m \in M} \sum_{t \in T} \delta_t \cdot R_m \cdot active_{m,t}
$$

Where:  
- $\delta_t = \frac{1}{(1 + r)^t}$ is the discount factor for year $t$  
- $p$ is the price per ton of blended ore  
- $R_m$ is the annual royalty for keeping mine $m$ active  


## Subject to:

### 1. Mine Operation Limit  
No more than 3 mines can operate in any year:

$$
\sum_{m \in M} used_{m,t} \leq 3 \quad \forall t \in T
$$


### 2. Ore Extraction Limit  
Mines can only extract if they are used:

$$
extract_{m,t} \leq L_m \cdot used_{m,t} \quad \forall m \in M, \, t \in T
$$

Where $L_m$ is the ore extraction limit of mine $m$.


### 3. Usage Requires Activation  
A mine can be used only if it's active:

$$
used_{m,t} \leq active_{m,t} \quad \forall m \in M, \, t \in T
$$


### 4. Irreversibility of Closure  
If a mine is inactive in one year, it cannot be reopened:

$$
active_{m,t+1} \leq active_{m,t} \quad \forall m \in M, \, t \in \{1,2,3,4\}
$$


### 5. Quality Constraint  
The weighted average quality of the extracted ore must meet the required target:

$$
\sum_{m \in M} Q_m \cdot extract_{m,t} = q_t \cdot make_t \quad \forall t \in T
$$

Where:  
- $Q_m$ is the quality of ore from mine $m$  
- $q_t$ is the required quality for year $t$


### 6. Mass Conservation  
The total extracted ore must equal the produced blended ore:

$$
\sum_{m \in M} extract_{m,t} = make_t \quad \forall t \in T
$$

