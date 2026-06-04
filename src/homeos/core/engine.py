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
        Advances the entire multi-physics system deterministically.
        Separates physical state transitions from observation telemetry generation.
        """
        state.validate_dimensions()
        
        # 1. Controller only sees the observation domain vector (x_obs)
        u = self.controller.compute(state.x_obs)

        # 2. Advance the True Physical States (x_phys)
        next_mech = update_mechanics(state.mechanical, u["force"], self.dt)
        next_em = update_electromagnetics(state.electromagnetic, u, self.dt)
        next_thermal = update_thermal(state.thermal, u["heat"], next_em[0], self.dt)
        
        # 3. Process the Measurement Domain Transform Matrix (x_obs)
        # Translates physical states into voltage registers with zero back-coupling to physics
        raw_strain_voltage = (next_mech[0] / 0.0035) * 3.3
        raw_leakage_voltage = next_em[2] * 20.0
        
        next_sensor = np.array([round(raw_strain_voltage, 4), round(raw_leakage_voltage, 4)])

        return state.copy_with_update(
            mechanical=next_mech,
            electromagnetic=next_em,
            thermal=next_thermal,
            sensor=next_sensor
        )
