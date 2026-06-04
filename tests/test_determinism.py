import numpy as np
from homeos.examples.run_basic_sim import run

def test_determinism():
    """Confirms that runs initialized with identical target seeds produce bitwise equal state vectors."""
    state_a = run(seed=42)
    state_b = run(seed=42)
    
    np.testing.assert_array_equal(state_a.mechanical, state_b.mechanical)
    np.testing.assert_array_equal(state_a.thermal, state_b.thermal)
    np.testing.assert_array_equal(state_a.electromagnetic, state_b.electromagnetic)
