# Homeos: Simulation Envelope & Parameter Boundaries

This document defines the computational boundaries, idealized conditions, and variable states utilized across the `homeos` simulation twin.

---

## 1. Fixed Environmental Constants (Immutables)
The following properties are hardcoded within the simulation engine and represent the stable operating domain. They do not dynamically adapt during runtime:

* **Permeability of Free Space ($\mu_0$):** $4\pi \times 10^{-7} \ \text{H/m}$
* **Base Conductivity of Copper Core Pins:** $5.8 \times 10^7 \ \text{S/m}$ at $20^\circ\text{C}$
* **Idealized Ground Plane Boundary:** $\hat{n} \cdot \mathbf{B} = 0$ at the outer radius perimeter ($R_c$).

## 2. Dynamic Free Variables (Runtime Ingestion)
These parameters are streamed directly into the `Control Engine` via the `Sensor Fusion Layer` (`core/hardware_interface.py`) or simulated by the test harness:

* **Active Hull Strain ($\epsilon$):** Ingested in real-time ($0.0 \le \epsilon \le 0.005$). Drives the structural "pain" response loop.
* **Channel Current Input ($I$):** Dynamically modulated by the propulsion loop ($0.0\text{A} \le I \le 150.0\text{A}$).
* **Core Temperature Vector ($T$):** Monitored to calculate thermal expansion mismatch ($20^\circ\text{C} \le T \le 600^\circ\text{C}$).

## 3. Idealized Assumptions vs. Physical Limitations
To maintain algorithmic stability, the software twin utilizes three core idealizations:

| Simulated Attribute | Idealized Software Assumption | Real-World Hardware Limit / Risk |
| :--- | :--- | :--- |
| **Magnetic Saturation** | Core flux guides exhibit linear permeability up to $1.8\text{ T}$. | Hysteresis losses and thermal magnetic saturation will cause non-linear force drop-offs. |
| **Thermal Conduction** | Perfect spatial uniformity across the molten-salt thermal storage vault. | Micro-scale thermal gradients and cold-spot crystallization could restrict local ion mobility. |
| **Structural Feedback** | CNT mesh piezoresistive gauge factor is perfectly linear across cyclic loads. | Interfacial resistance degradation at metal pins will cause signal drift over time. |
