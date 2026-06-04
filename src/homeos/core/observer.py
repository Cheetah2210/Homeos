import numpy as np
from homeos.core.state import HomeosState

class Observer:
    def evaluate(self, state: HomeosState) -> dict:
        """
        Evaluates raw physical inputs against material boundaries to determine stability profiles.
        """
        return {
            "health": float(-abs(state.mechanical).mean()),
            "thermal_stability": float(-abs(state.thermal).mean()),
        }
