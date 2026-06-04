import numpy as np
from homeos.core.state import HomeosState
from homeos.sensors.noise import SensorInstrumentationModel
from homeos.physics.mechanics import update_mechanics
from homeos.physics.electromagnetics import update_electromagnetics
from homeos.physics.thermal import update_thermal

class SimulationEngine:
    def __init__(self, controller, dt: float = 0.01, base_seed: int = 42):
        self.controller = controller
        self.dt = dt
        self.base_seed = base_seed
        self.step_index = 0
        
        # Instantiate the explicit telemetry instrumentation layer
        self.instrumentation = SensorInstrumentationModel(dt=self.dt)
        
        # Fixed physical normalization invariants
        self.EPSILON_MAX = 0.0035
        self.GAIN_HALL = 20.0

    def step(self, state: HomeosState) -> HomeosState:
        """
        Advances the coupled multi-physics system by one deterministic timestep dt.
        Enforces a clean physical transition prior to instrument tracking loops.
        """
        state.validate_dimensions()
        
        # 1. Evaluate control laws using only degraded sensor observations (x_obs)
        u = self.controller.compute(state.x_obs)

        # 2. Compute true physical state space updates (x_phys)
        next_mech = update_mechanics(state.mechanical, u["force"], self.dt)
        next_em = update_electromagnetics(state.electromagnetic, u, self.dt)
        next_thermal = update_thermal(state.thermal, u["heat"], next_em[0], self.dt)
        
        # 3. Explicit Transform Layer: H(x_phys)
        # Standardizes mixed physical dimensions into normalized ideal volts
        ideal_v_strain = (next_mech[0] / self.EPSILON_MAX) * 3.3
        ideal_v_leakage = next_em[2] * self.GAIN_HALL
        ideal_h = np.array([ideal_v_strain, ideal_v_leakage])
        
        # 4. Degrade observations through the explicit sensor error model
        next_sensor = self.instrumentation.apply_instrument_effects(
            raw_h=ideal_h,
            step_index=self.step_index,
            base_seed=self.base_seed
        )
        
        # Increment internal discrete execution step tracker
        self.step_index += 1

        return state.copy_with_update(
            mechanical=next_mech,
            electromagnetic=next_em,
            thermal=next_thermal,
            sensor=next_sensor
        )
