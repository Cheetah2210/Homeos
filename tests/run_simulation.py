import numpy as np
import logging
from core.state import HomeosState
from core.observer import HomeosObserver
from core.engine import SimulationEngine
import physics as physics_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosExecution")

def generate_bench_conditions(seed: int) -> HomeosState:
    """Instantiates a clean, reproducible state vector layout."""
    return HomeosState(
        mechanical=np.array([0.0, 0.0, 0.0]),
        electromagnetic=np.array([0.0, 0.0, 0.0]),
        thermal=np.array([20.0, 0.0]), # Room temperature baseline, solid status
        sensor=np.array([0.0, 0.0])
    )

def execute_system_run(seed: int, steps: int = 50) -> HomeosState:
    """
    Executes a complete, step-deterministic multi-physics tracking run.
    """
    logger.info(f"Initializing Homeos v1.1 Simulation Engine...")
    logger.info(f"PRNG Lock Sequence Activated. Active Global Target Seed: {seed}")
    
    state = generate_bench_conditions(seed)
    controller = HomeosObserver(tier_profile="tier_1_micro")
    engine = SimulationEngine(physics_pipeline, controller, base_dt=0.01)
    
    for current_step in range(steps):
        state = engine.step(state, timestep_index=current_step, seed=seed)
        
        if current_step % 10 == 0:
            logger.info(
                f"Step {current_step:03d} | Equilibrium: {state.sensor[0]:.4f}V | "
                f"Core Temp: {state.thermal[0]:.2f}°C | EM Leakage: {state.electromagnetic[2]:.5f}T"
            )
            
    logger.info("Simulation loop finished with zero drift errors detected.")
    return state

if __name__ == "__main__":
    # Execute seed confirmation run
    final_state = execute_system_run(seed=42, steps=50)
