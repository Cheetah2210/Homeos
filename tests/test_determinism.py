import numpy as np
from homeos.examples.run_basic_sim import run

def test_determinism():
    """Validates that execution runs using matching seeds generate identical state spaces."""
    run_alpha = run(seed=42)
    run_beta = run(seed=42)

    # Check for perfect numerical convergence matching a strict bitwise limit
    np.testing.assert_array_equal(run_alpha.mechanical, run_beta.mechanical)
    np.testing.assert_array_equal(run_alpha.thermal, run_beta.thermal)
    np.testing.assert_array_equal(run_alpha.electromagnetic, run_beta.electromagnetic)
    np.testing.assert_array_equal(run_alpha.sensor, run_beta.sensor)

def test_stochastic_separation():
    """Confirms that varying initialization seeds produce distinct vector pathways."""
    run_alpha = run(seed=42)
    run_gamma = run(seed=101)

    assert not np.array_equal(run_alpha.sensor, run_gamma.sensor)
