import numpy as np
from core.state import HomeosState
from sensors.noise_models import SeededNoiseEngine

class SimulationEngine:
    def __init__(self, physics_pipeline, controller, base_dt=0.01):
        """
        Manages state propagation across the decoupled physical solver modules.
        """
        self.physics = physics_pipeline
        self.controller = controller
        self.dt = base_dt

    def step(self, current_state: HomeosState, timestep_index: int, seed: int) -> HomeosState:
        """
        Executes a deterministic state space update transformation over delta time (dt).
        """
        # 1. Enforce strict array dim verification checks
        current_state.validate_dimensions()
        
        # 2. Extract control directives from the tracking policy engine
        # Map state parameters into traditional scalar variables for controller evaluation
        strain_val = float(current_state.mechanical[0])
        core_temp = float(current_state.thermal[0])
        leakage_val = float(current_state.electromagnetic[2])
        
        directives = self.controller.evaluate_sensory_matrix(
            active_strain=strain_val,
            core_temp=core_temp,
            battery_temp=core_temp,
            field_leakage=leakage_val,
            proximity_to_living=10.0 # Bounded environmental condition
        )
        
        # 3. Process time transitions across independent physical layers
        next_mechanical = self.physics.mechanics.update(current_state, directives, self.dt)
        next_electromagnetic = self.physics.electromagnetics.update(current_state, directives, self.dt)
        next_thermal = self.physics.thermal.update(current_state, directives, self.dt)
        
        # 4. Generate sensor feedback profiles using the seeded noise injection engine
        raw_strain_voltage = (next_mechanical[0] / 0.005) * 3.3
        perturbed_voltage = SeededNoiseEngine.inject_gaussian_noise(
            true_value=raw_strain_voltage,
            scale=1e-4,
            step_index=timestep_index,
            base_seed=seed
        )
        
        next_sensor = np.array([round(perturbed_voltage, 4), round(next_electromagnetic[2] * 20.0, 4)])
        
        return HomeosState(
            mechanical=next_mechanical,
            electromagnetic=next_electromagnetic,
            thermal=next_thermal,
            sensor=next_sensor
        )
