import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def test_step_runs():
    """Verifies that the multi-physics engine maps structural steps without modifying original references."""
    initial_state = HomeosState(
        mechanical=np.array([1.0, 2.0, 3.0]),
        electromagnetic=np.array([0.0, 0.0, 0.0]),
        thermal=np.array([300.0]),
        sensor=np.array([0.0]),
    )

    engine = SimulationEngine(Controller())
    updated_state = engine.step(initial_state)

    # Assert new container generation
    assert updated_state is not initial_state
    
    # Verify that initial state tensors remained unmutated and clean
    assert initial_state.mechanical[0] == 1.0
    assert initial_state.thermal[0] == 300.0
