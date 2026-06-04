import numpy as np

def update_temperature(temp_state: np.ndarray, heat_input: np.ndarray, dt: float, capacity: float = 1.0) -> np.ndarray:
    """
    Computes localized thermal expansion and heat dissipation transfers.
    dT/dt = Heat_Input / Capacity
    """
    if capacity <= 0.0:
        raise ValueError("Physical thermal matrix heat capacity must be positive and non-zero.")
    next_temp = temp_state + dt * (heat_input / capacity)
    return next_temp
