import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def run(seed: int = 42) -> HomeosState:
    """
    Initializes and executes a completely reproducible multi-physics tracking run.
    """
    # Initialize the pseudo-random generator with an explicit, fixed state seed
    rng = np.random.default_rng(seed=seed)

    # Instantiate initial parameters using predictable PRNG allocations
    initial_mech = np.array([1.0, 0.0, 0.0])
    initial_em = np.array([0.0, 1.0, 0.0])
    initial_thermal = np.array([300.0])
    initial_sensor = np.array([rng.uniform(0.0, 0.1)])  # Seeded deterministic variance

    state = HomeosState(
        mechanical=initial_mech,
        electromagnetic=initial_em,
        thermal=initial_thermal,
        sensor=initial_sensor,
    )

    engine = SimulationEngine(Controller(), dt=0.01)

    # Run the discrete evaluation sequence for 1,000 steps
    for _ in range(1000):
        state = engine.step(state)

    return state

if __name__ == "__main__":
    final_simulation_state = run(seed=42)
    print("Execution Concluded. Output Vectors Verification Baseline:")
    print(f" Mechanical Matrix: {final_simulation_state.mechanical}")
    print(f" Thermal Matrix:    {final_simulation_state.thermal}")
