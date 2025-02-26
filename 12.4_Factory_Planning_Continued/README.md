## Additional Constraints for Machine Maintenance Scheduling

9. Machine Capacity Constraints with Maintenance Scheduling

$$
\sum_{i} processingTime_{m,i} \cdot MPROD_{i,t} \leq \sum_{n} machineAvailability_{m,t} \cdot totalHrsPerMachine \text{ -} \sum_{n} MDown_{m,n,t} \cdot machineAvailability_{m,t} \cdot totalHrsPerMachine
$$

10. Maintenance Scheduling Constraints
    
$$ 
\text{Each machine (except grinding machines) must undergo maintenance **exactly once** over six months.}
$$
$$
\sum_{t=1}^{6} MDown_{m,n,t} = 1, \quad \forall m \neq GR, \forall n
$$

$$
\text{Exactly **two out of four grinders** undergo maintenance over six months.}
$$
$$
\sum_{n=1}^{4} \sum_{t=1}^{6} MDown_{GR,n,t} = 2
$$

11. Binary Constraints on Machine Downtime Variables

$$
MDown_{m,n,t} \in \{0,1\}, \quad \forall m, n, t
$$


Where,

𝑖 :	Product type (e.g., Product A, Product B, etc.)

𝑚 : Machine type (e.g., Grinder, Driller, Borer, etc.)

𝑛 : Machine index (individual machine within type)

𝑡 : Month (time period) (1 to 6)
