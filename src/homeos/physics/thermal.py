import numpy as np

def update_thermal(thermal_state: np.ndarray, heat_input: np.ndarray, active_current: float, dt: float) -> np.ndarray:
    """Computes specific heat capacity shifts relative to salt fusion boundaries."""
    ohmic_contribution = (active_current ** 2) * 0.0012
    net_heat = heat_input[0] + ohmic_contribution
    
    next_temp = thermal_state[0] + dt * (net_heat / 1350.0)
    next_phi = 1.0 if next_temp > 158.0 else 0.0
    
    return np.array([next_temp, next_phi])
