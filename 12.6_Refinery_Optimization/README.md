# Mathematical Formulation
## Decision Variables:

- $x_{m} :  \text{Barrels of material } m  \text{ produced per day} $
  
- $y_{i, p} : \text{Barrels of material } i \text{ used in product } p $  

## Objective Function
Maximize total profit:

$$
Maximize \quad 7 x_{\text{PremiumPetrol}} + 6 x_{\text{RegularPetrol}} + 4 x_{\text{JetFuel}} + 3.5 x_{\text{FuelOil}} + 1.5 x_{\text{LubeOil}}
$$

## Subject to:

1. Distillation Constraints:

$$
x_f = \sum_{c} \text{distilYields}(c, f) \cdot x_c, \quad \forall f
$$

2. Reforming Constraints (converting naphtha into high-octane reformed gasoline):

$$
x_{\text{ReformedGasoline}} = \sum_{n} \text{reformYields}(n) \cdot y_{n, \text{ReformedGasoline}}, \quad \forall n \in \{ light naphtha, medium naphtha, heavy naphtha \}
$$

3. Cracking Constraints (Oils into cracked gasoline and cracked oil):

$$
x_{\text{CrackedGasoline}} = \sum_{o} \text{crackingYields}(o, \text{CrackedGasoline}) \cdot y_{o, \text{Cracked}}, \quad \forall o \in \{ light oil, heavy oil \}
$$
$$
x_{\text{CrackedOil}} = \sum_{o} \text{crackingYields}(o, \text{CrackedOil}) \cdot y_{o, \text{Cracked}} \quad ,\forall o
$$

4. Lube-Oil Constraint (Residuum into lube-oil):

$$
x_{\text{LubeOil}} = 0.5 \cdot y_{\text{Residuum}, \text{LubeOil}}
$$

5. Blending Constraints:

$$
x_{m} = \sum_{i \in \text{used in}[m]} y_{i, m}  \quad ,\forall m
$$

$$
x_{\text{FuelOil}} = 10 x_{\text{light oil}} + 4 x_{\text{CrackedOil}} + 3 x_{\text{heavy oil}} + 1 x_{\text{Residuum}} \quad \text{ (Fuel oil blending must follow a fixed ratio)}
$$

6. Quality Constraints:
   
- Octane Number for Petrol
  The octane rating of blended petrol must meet requirements:
  
$$
\sum_{i} \text{octane}(i) \cdot y_{i, p} \geq \text{quality}(p) \cdot x_p, \quad \forall p \in \{ PremiumPetrol, RegularPetrol \}
$$

- Vapor Pressure for Jet Fuel
  Jet fuel must not exceed the allowed vapor pressure:
  
$$
\sum_{i} \text{pressures}(i) \cdot y_{i, \text{JetFuel}} \leq 1
$$

7. Capacity Constraints:
- Maximum availability of crude oils:

$$
x_{\text{CrudeOil1}} \leq 20000, \quad x_{\text{CrudeOil2}} \leq 30000
$$

- Total crude oil refined per day is limited:

$$
x_{\text{CrudeOil1}} + x_{\text{CrudeOil2}} \leq 45000
$$

- Processing limits for refining:

$$
\sum_{n} y_{n, \text{ReformedGasoline}} \leq 10000, \quad \sum_{o} y_{o, \text{Cracked}} \leq 8000
$$

- Lube-oil production must stay within limits:

$$
500 \leq x_{\text{LubeOil}} \leq 1000
$$

- Premium petrol must be at least 40% of regular petrol production:

$$
x_{\text{PremiumPetrol}} \geq 0.4 x_{\text{RegularPetrol}}
$$

8. Non-Negativity Constraints:
All production and blending variables must be non-negative:

$$
x_m, y_{i, p} \geq 0, \quad \forall m, i, p
$$
