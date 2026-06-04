import numpy as np
from homeos.core.state import HomeosState

class Controller:
    def __init__(self, mechanical_gain: float = -0.1, thermal_gain: float = 0.05):
        self.k_m = mechanical_gain
        self.k_t = thermal_gain

    def compute(self, state: HomeosState) -> dict:
        """
        Generates deterministic physical actuation directives from state snapshots.
        """
        return {
            "force": self.k_m * state.mechanical,
            "heat": self.k_t * state.thermal,
            "target_gyro_output_pct": 100.0,
            "active_phase_cancellation": False
        }
