import numpy as np
from core.state import HomeosState

class ElectromagneticsSolver:
    def __init__(self, core_radius=0.075):
        self.r_core = core_radius

    def update(self, state: HomeosState, control_directives: dict, dt: float) -> np.ndarray:
        """
        Updates the electromagnetic state vector.
        Calculates active Lorentz interactions and fields.
        """
        current_em = state.electromagnetic.copy()
        
        # Map target gyro outputs directly into active driving variables
        target_output = control_directives.get("target_gyro_output_pct", 100.0)
        
        # Calculate standard current ramp-up profiles
        target_current = (target_output / 100.0) * 150.0
        current_i = current_em[0] + (target_current - current_em[0]) * (dt / 0.05)
        
        # Ideal magnetic flux density baseline projection
        flux_b0 = 1.5 if current_i > 10.0 else 0.0
        
        # Local field leakage calculations altered by active cancellation loops
        base_leakage = 0.045 if current_i > 50.0 else 0.001
        if control_directives.get("active_phase_cancellation", False):
            base_leakage *= 0.05  # Containment isolation attenuation factor
            
        return np.array([current_i, flux_b0, base_leakage])
