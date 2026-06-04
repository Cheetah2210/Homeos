import numpy as np
from core.state import HomeosState

class ThermalSolver:
    def __init__(self, freeze_point=158.0):
        self.freeze_line = freeze_point
        self.latent_capacity = 315000.0 * 4.25

    def update(self, state: HomeosState, control_directives: dict, dt: float) -> np.ndarray:
        """
        Advances the thermal state using an explicit RK2 method.
        Tracks the latent phase crystallization boundary line.
        """
        current_temp = state.thermal[0]
        current_phi = state.thermal[1]
        
        # Ohmic heating simulation input calculation: P = I^2 * R
        current_i = state.electromagnetic[0]
        generated_joules = (current_i ** 2) * 0.012 * dt
        
        # Check and handle latent phase change plateau zones
        if current_temp >= self.freeze_line and current_phi < 1.0:
            added_phi = generated_joules / self.latent_capacity
            next_phi = min(current_phi + added_phi, 1.0)
            next_temp = self.freeze_line
        else:
            # Standard single phase heat capacity step scaling
            c_p = 1350.0 if current_phi >= 1.0 else 1200.0
            delta_t = generated_joules / (4.25 * c_p)
            next_temp = current_temp + delta_t
            next_phi = 1.0 if next_temp > self.freeze_line else 0.0
            
        return np.array([next_temp, next_phi])
