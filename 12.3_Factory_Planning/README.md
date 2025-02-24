# Mathematical Formulation

## Decision Variables:

\[
MPROD_{i,t} = \text{Units of product } i \text{ manufactured in month } t
\]

\[
SPROD_{i,t} = \text{Units of product } i \text{ sold in month } t
\]

\[
HPROD_{i,t} = \text{Units of product } i \text{ held in inventory at the end of month } t
\]

## Objective Function:

\[
\max \sum_{i,t} profit_i \cdot SPROD_{i,t} - storageCost \cdot \sum_{i,t} HPROD_{i,t}
\]

## Subject to:

### 1. Machine Capacity Constraints (for each machine \(m\), month \(t\)):

\[
\sum_{i} processingTime_{m,i} \cdot MPROD_{i,t} \leq machineAvailability_{m,t}
\]

### 2. Market Demand Constraints (for each product \(i\), month \(t\)):

\[
SPROD_{i,t} \leq marketDemand_{i,t}
\]

### 3. Sales Limitation (for each product \(i\), month \(t\)):

\[
SPROD_{i,t} \leq MPROD_{i,t} + HPROD_{i,t}
\]

### 4. Inventory Balance (for each product \(i\), month \(t\)):

\[
HPROD_{i,t-1} + MPROD_{i,t} - SPROD_{i,t} - HPROD_{i,t} = 0
\]

### 5. Final Inventory Condition (for each product \(i\)):

\[
HPROD_{i,6} = finalInventory_i
\]

### 6. Initial Inventory Condition (for each product \(i\)):

\[
HPROD_{i,1} = initialInventory_i
\]

### 7. Storage Limits (for each product \(i\), month \(t\)):

\[
HPROD_{i,t} \leq maxInventory
\]

### 8. Non-Negativity Constraints:

\[
MPROD_{i,t}, SPROD_{i,t}, HPROD_{i,t} \geq 0
\]
