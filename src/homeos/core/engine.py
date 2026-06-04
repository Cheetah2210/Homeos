from homeos.core.state import HomeosState
from homeos.physics.mechanics import update_mechanics
from homeos.physics.thermal import update_temperature

class SimulationEngine:
    def __init__(self, controller, dt: float = 0.01):
        self.controller = controller
        self.dt = dt

    def step(self, state: HomeosState) -> HomeosState:
        """
        Advances the coupled multi-physics states by one deterministic timestep dt.
        """
        # 1. Evaluate feedback directives from the current immutable snapshot
        u = self.controller.compute(state)

        # 2. Compute state space transitions across independent solvers
        next_mechanical = update_mechanics(
            state.mechanical,
            u["force"],
            self.dt
        )

        next_thermal = update_temperature(
            state.thermal,
            u["heat"],
            self.dt
        )

        # 3. Compile and return a fresh, distinct, immutable state container for timestep t+1
        return state.copy_with_update(
            mechanical=next_mechanical,
            thermal=next_thermal
        )
