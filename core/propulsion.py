import math

class HomeosPropulsion:
    def __init__(self, target_radius=0.075):
        self.r_core = target_radius
        self.mu_0 = 4 * math.pi * 1e-7

    def calculate_ideal_thrust(self, current, ambient_flux_b0):
        """
        Executes nominal definite integral transformation matching VAL-ANALYTICAL-001.
        Output: Force vector result in Newtons.
        """
        if current < 0 or ambient_flux_b0 < 0:
            return 0.0
        return (2.0 / 3.0) * current * ambient_flux_b0 * self.r_core
