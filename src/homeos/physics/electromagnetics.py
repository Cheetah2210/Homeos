import numpy as np

def update_electromagnetics(em_state: np.ndarray, control_directives: dict, dt: float) -> np.ndarray:
    """Updates Lorentz field parameters and records field containment leakage boundaries."""
    target_output = control_directives.get("target_gyro_output_pct", 100.0)
    target_current = (target_output / 100.0) * 150.0
    
    current_i = em_state[0] + (target_current - em_state[0]) * (dt / 0.05)
    flux_b0 = 1.5 if current_i > 10.0 else 0.0
    base_leakage = 0.045 if current_i > 50.0 else 0.001
    
    if control_directives.get("active_phase_cancellation", False):
        base_leakage *= 0.05
        
    return np.array([current_i, flux_b0, base_leakage])
