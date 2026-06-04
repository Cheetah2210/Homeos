import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def test_step_runs():
    """Validates engine step transitions without modifying active base references."""
    initial_state = HomeosState(
        mechanical=np.array([0.0, 0.0, 0.0]),
        electromagnetic=np.array([0.0, 0.0, 0.0]),
        thermal=np.array([20.0, 0.0]),
        sensor=np.array([0.0, 0.0])
    )
    
    engine = SimulationEngine(Controller())
    next_state = engine.step(initial_state)
    
    assert next_state is not initial_state
    assert initial_state.thermal[0] == 20.0
