---
math: true
---

# Refinery Optimization Model

## Sets and Indices
$ c \in \{ CrudeOil1, CrudeOil2 \} $ : Crude oil types  
$ f \in \{ light naphtha, medium naphtha, heavy naphtha, light oil, heavy oil, residuum \} $ : Distillation fractions  
$ p \in \{ PremiumPetrol, RegularPetrol \} $ : Petrol types  
$ j \in \{ JetFuel \} $ : Jet fuel  
$ o \in \{ FuelOil \} $ : Fuel oil  
$ l \in \{ LubeOil \} $ : Lube-oil  


## Sets and Indices
- \( c \in \{{CrudeOil1}, {CrudeOil2}} ) : Crude oil types  
- \( f \in \{\text{light naphtha}, \text{medium naphtha}, \text{heavy naphtha}, \text{light oil}, \text{heavy oil}, \text{residuum}\} \) : Distillation fractions  
- \( p \in \{\text{PremiumPetrol}, \text{RegularPetrol}\} \) : Petrol types  
- \( j \in \{\text{JetFuel}\} \) : Jet fuel  
- \( o \in \{\text{FuelOil}\} \) : Fuel oil  
- \( l \in \{\text{LubeOil}\} \) : Lube-oil  

## Decision Variables
- \( x_m \) : Barrels of material \( m \) produced per day  
- \( y_{i, p} \) : Barrels of material \( i \) used in product \( p \)  

## Objective Function

$$
maximize \quad 700 x_{\text{PremiumPetrol}} + 600 x_{\text{RegularPetrol}} + 400 x_{\text{JetFuel}} + 350 x_{\text{FuelOil}} + 150 x_{\text{LubeOil}}
$$
where we maximize the total profit from all final products.

## Constraints

### Distillation Constraints
$$
x_f = \sum_{c} \text{distilYields}(c, f) \cdot x_c, \quad \forall f
$$
ensuring crude oil is converted into its respective fractions.

### Reforming Constraints
$$
x_{\text{ReformedGasoline}} = \sum_{n} \text{reformYields}(n) \cdot y_{n, \text{ReformedGasoline}}, \quad \forall n \in \{\text{light, medium, heavy naphtha}\}
$$

### Cracking Constraints
$$
x_{\text{CrackedGasoline}} = \sum_{o} \text{crackingYields}(o, \text{CrackedGasoline}) \cdot y_{o, \text{Cracked}}, \quad \forall o \in \{\text{light oil}, \text{heavy oil}\}
$$
$$
x_{\text{CrackedOil}} = \sum_{o} \text{crackingYields}(o, \text{CrackedOil}) \cdot y_{o, \text{Cracked}}, \quad \forall o
$$

### Lube-Oil Constraint
$$
x_{\text{LubeOil}} = 0.5 \cdot y_{\text{Residuum}, \text{LubeOil}}
$$

### Blending Constraints
$$
x_m = \sum_{i \in \text{used\_in}[m]} y_{i, m}, \quad \forall m
$$
$$
x_{\text{FuelOil}} = 10 x_{\text{light oil}} + 4 x_{\text{CrackedOil}} + 3 x_{\text{heavy oil}} + 1 x_{\text{Residuum}}
$$

### Quality Constraints
- **Octane Number for Petrol**:
$$
\sum_{i} \text{octane}(i) \cdot y_{i, p} \geq \text{quality}(p) \cdot x_p, \quad \forall p \in \{\text{PremiumPetrol}, \text{RegularPetrol}\}
$$
- **Vapor Pressure for Jet Fuel**:
$$
\sum_{i} \text{pressures}(i) \cdot y_{i, \text{JetFuel}} \leq 1
$$

### Capacity Constraints
$$
x_{\text{CrudeOil1}} \leq 20000, \quad x_{\text{CrudeOil2}} \leq 30000
$$
$$
x_{\text{CrudeOil1}} + x_{\text{CrudeOil2}} \leq 45000
$$
$$
\sum_{n} y_{n, \text{ReformedGasoline}} \leq 10000, \quad \sum_{o} y_{o, \text{Cracked}} \leq 8000
$$
$$
500 \leq x_{\text{LubeOil}} \leq 1000
$$
$$
x_{\text{PremiumPetrol}} \geq 0.4 x_{\text{RegularPetrol}}
$$

### Non-Negativity Constraints
$$
x_m, y_{i, p} \geq 0, \quad \forall m, i, p
$$
