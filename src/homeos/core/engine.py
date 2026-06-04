import numpy as np
from homeos.core.state import HomeosState
from homeos.physics.mechanics import update_mechanics
from homeos.physics.electromagnetics import update_electromagnetics
from homeos.physics.thermal import update_thermal

class SimulationEngine:
    def __init__(self, controller, dt: float = 0.01):
        self.controller = controller
        self.dt = dt

    def step(self, state: HomeosState) -> HomeosState:
        """
        Advances the coupled structural layers by a single fixed time increment (dt).
        """
        state.validate_dimensions()
        
        # 1. Gather active controller targets
        u = self.controller.compute(state)

        # 2. Process independent system updates sequentially
        next_mech = update_mechanics(state.mechanical, u["force"], self.dt)
        next_em = update_electromagnetics(state.electromagnetic, u, self.dt)
        next_thermal = update_thermal(state.thermal, u["heat"], state.electromagnetic[0], self.dt)
        
        # 3. Formulate sensor readout tracking metrics
        next_sensor = np.array([round((next_mech[0] / 0.0035) * 3.3, 4), round(next_em[2] * 20.0, 4)])

        return state.copy_with_update(
            mechanical=next_mech,
            electromagnetic=next_em,
            thermal=next_thermal,
            sensor=next_sensor
        )
