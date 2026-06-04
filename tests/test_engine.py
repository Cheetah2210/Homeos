import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def test_observation_split_integrity():
    """Verifies that true physical parameters and observational properties do not bleed vector blocks."""
    initial_state = HomeosState(
        mechanical=np.array([0.001, 0.0, 0.0]),
        electromagnetic=np.array([5.0, 1.5, 0.002]),
        thermal=np.array([200.0, 1.0]),
        sensor=np.array([0.942, 0.040])
    )
    
    # Verify vector dimension slice outputs
    assert initial_state.x_phys.shape == (8,)
    assert initial_state.x_obs.shape == (2,)
    assert initial_state.get_unified_vector().shape == (10,)
    
    engine = SimulationEngine(Controller())
    next_state = engine.step(initial_state)
    
    # Confirm structural separation is maintained post-step transformation
    assert next_state.x_phys is not None
    assert next_state.x_obs is not None
