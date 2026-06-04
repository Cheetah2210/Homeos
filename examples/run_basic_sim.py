import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def run(seed: int = 42) -> HomeosState:
    """Initializes and tracks a completely reproducible system run pipeline."""
    rng = np.random.default_rng(seed=seed)
    
    state = HomeosState(
        mechanical=np.array([0.0005, 0.0, 0.0]),
        electromagnetic=np.array([10.0, 1.5, 0.002]),
        thermal=np.array([215.0, 1.0]),
        sensor=np.array([0.0, 0.0])
    )
    
    engine = SimulationEngine(Controller(), dt=0.01)
    
    for _ in range(100):
        state = engine.step(state)
        
    return state

if __name__ == "__main__":
    final_state = run(seed=42)
    print("--- SIMULATION COMPLETE ---")
    print(f"Mechanical Vector: {final_state.mechanical}")
    print(f"Thermal Vector:    {final_state.thermal}")
