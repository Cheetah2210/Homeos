import numpy as np
from homeos.core.state import HomeosState

class Controller:
    def __init__(self, mechanical_gain: float = -0.1, thermal_gain: float = 0.05):
        self.k_m = mechanical_gain
        self.k_t = thermal_gain

    def compute(self, obs_state: np.ndarray) -> dict:
        """
        Computes control directives using ONLY the decoupled observation vector x_obs.
        Prevents state-estimation leaking or non-causal tracking loops.
        """
        # obs_state[0] = v_strain_measurement, obs_state[1] = v_leakage_measurement
        return {
            "force": self.k_m * np.array([obs_state[0], 0.0, 0.0]),
            "heat": self.k_t * np.array([obs_state[1], 0.0]),
            "target_gyro_output_pct": 100.0,
            "active_phase_cancellation": True if obs_state[1] > 0.5 else False
        }
