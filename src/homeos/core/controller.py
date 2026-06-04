import numpy as np
from homeos.core.state import HomeosState

class Controller:
    def __init__(self, mechanical_gain: float = -0.1, thermal_gain: float = 0.05):
        self.k_m = mechanical_gain
        self.k_t = thermal_gain

    def compute(self, state: HomeosState) -> dict:
        """
        Evaluates system parameters to produce rule-based control vectors.
        """
        return {
            "force": self.k_m * state.mechanical,
            "heat": self.k_t * state.thermal,
        }
