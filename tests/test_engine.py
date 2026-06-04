import numpy as np
from homeos.core.state import HomeosState
from homeos.core.controller import Controller
from homeos.core.engine import SimulationEngine

def test_instrumentation_quantization_limits():
    """Verifies that sensor observations show realistic quantization steps and bias features."""
    initial_state = HomeosState(
        mechanical=np.array([0.0, 0.0, 0.0]),
        electromagnetic=np.array([0.0, 0.0, 0.0]),
        thermal=np.array([20.0, 0.0]),
        sensor=np.array([0.0, 0.0])
    )
    
    engine = SimulationEngine(Controller(), dt=0.01, base_seed=1337)
    next_state = engine.step(initial_state)
    
    # Static bias values check: Initial step error yields non-zero baseline telemetry
    # Strain bias: 5mV + noise/quantization. Leakage bias: -12mV clipped to 0V rail or slightly shifted
    assert next_state.x_obs[0] > 0.0, "Sensor channel failed to account for static hardware bias offsets."
    
    # Enforce that outputs strictly match digital 12-bit and 16-bit resolution grids
    q_step_strain = 3.3 / 4096.0
    remainder = next_state.x_obs[0] % q_step_strain
    assert np.isclose(remainder, 0.0) or np.isclose(remainder, q_step_strain), "Telemetry channel bypassed bitwise quantization filters."
