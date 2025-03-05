# Mathematical Formulation
## Decision Variables:

$TotalWorkers_{s,t} = \text{Total workers of skill level } s \text{ at year } t $

$NewWorkers_{s,t} = \text{Newly recruited workers of skill level } s \text{ in year } t $

$RecruitedWorkers_{s,t} = \text{Total recruited workers for skill level } s \text{ in year } t $

$RetrainedWorkers_{t}^{\text{UnskilledToSemi}} = \text{Unskilled workers retrained to Semi-skilled in year } t $

$RetrainedWorkers_{t}^{\text{SemiToSkilled}}  = \text{Semi-skilled workers retrained to Skilled in year } t $

$DowngradedWorkers_{s1,s2,t} = \text{Workers downgraded from skill level } s_1 \text{ to } s_2 \text{ in year } t $

$RedundantWorkers_{s,t} = \text{Workers made redundant in skill level } s \text{ in year } t $

$ShortTimeWorkers_{s,t} = \text{Workers on short-time working in skill level } s \text{ in year } t $

$OvermannedWorkers_{s,t} = \text{Workers overmanned in skill level } s \text{ in year } t $


## Objective Function:


Minimize Total Redundancy:

$$
\text{minimize} \sum_{s \in S} \sum_{t \in T} \text{RedundantWorkers}_{s,t}
$$

Minimize Total Redundancy Cost:

$$
\text{minimize} \sum_{s \in S} \sum_{t \in T} \text{RedundantWorkers}_{s,t} \cdot RedundancyCost _{s}
$$

## Subject to:

1. Workforce Balance Constraints (With Wastage):

  Skilled Workers:
   
  $$
  0.95 \cdot TotalWorkers_{Skilled,t-1} + 0.90 \cdot NewWorkers_{Skilled,t} + 0.95 \cdot RetrainedWorkers_{t}^{SemiToSkilled} -
  DowngradedWorkers_{Skilled,SemiSkilled,t} - DowngradedWorkers_{Skilled,Unskilled,t} - RedundantWorkers_{Skilled,t} 
  = TotalWorkers_{Skilled,t}, \forall t \in T
  $$

  Semi-Skilled Workers:

  $$
  0.95 \cdot TotalWorkers_{SemiSkilled,t-1} + 0.80 \cdot NewWorkers_{SemiSkilled,t} + 0.95 \cdot RetrainedWorkers_{t}^{UnskilledToSemi} -
  RetrainedWorkers_{t}^{SemiToSkilled} + 0.5 \cdot DowngradedWorkers_{Skilled,SemiSkilled,t} - DowngradedWorkers_{SemiSkilled,Unskilled,t} -
  RedundantWorkers_{SemiSkilled,t} = TotalWorkers_{SemiSkilled,t},  \forall t \in T
  $$

  Unskilled Workers:
  
  $$
  0.90 \cdot TotalWorkers_{Unskilled,t-1} + 0.75 \cdot NewWorkers_{Unskilled,t} - RetrainedWorkers_{t}^{UnskilledToSemi} + 0.5 \cdot 
  DowngradedWorkers_{Skilled,Unskilled,t} + 0.5 \cdot DowngradedWorkers_{SemiSkilled,Unskilled,t} - RedundantWorkers_{Unskilled,t} 
  = TotalWorkers_{Unskilled,t},  \forall t \in T
  $$
    

2. Recruitment Constraints:

$$
NewWorkers_{s,t} \leq RecruitmentCapacity_{s},\quad\quad\quad \forall s \in S, \forall t \in T
$$


3. Retraining Constraints:

$$
RetrainedWorkers_{t}^{SemiToSkilled} \leq 0.25 \cdot TotalWorker_{Skilled,t},\quad\quad\quad \forall t \in T  
$$

$$
RetrainedWorkers_t^{UnskilledToSemi} \leq 200, \quad\quad\quad \forall t \in T
$$

4. Downgrading Constraints

$$
DowngradedWorkers_{s1,s2,t} \leq \frac{1}{2} (TotalWorkers_{s1,t}), \quad\quad\quad \forall s1, s2 \in S, \forall t \in T
$$

5. Overmanning Constraint

$$
\sum_{s \in S} OvermannedWorkers_{s,t} \leq 150, \quad\quad\quad \forall t \in T
$$

6. Short-Time Working Constraint

$$
ShortTimeWorkers_{s,t} \leq 50, \quad\quad\quad \forall s \in S, \forall t \in T
$$

7. Workforce Requirement Constraints

$$
TotalWorkers_{s,t} - OvermannedWorkers_{s,t} - 0.5 \cdot ShortTimeWorkers_{s,t} = ManpowerRequirements_{s,t}, \quad\quad\quad \forall s \in S, \forall t \in T
$$


