from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class HomeosState:
    """
    Immutable snapshot of the unified simulation state space at timestep t.
    Enforces strict tensor mapping across multi-physics domains.
    """
    mechanical: np.ndarray       # Shape (3,): [strain_x, strain_y, load_z]
    electromagnetic: np.ndarray  # Shape (3,): [current_i, flux_b0, leakage]
    thermal: np.ndarray          # Shape (2,): [temp_c, phase_fraction_phi]
    sensor: np.ndarray           # Shape (2,): [adc_voltage_hull, adc_voltage_flux]

    def validate_dimensions(self, expected_m=3, expected_e=3, expected_t=2, expected_s=2):
        """Verifies tensor matrix arrays before executing physics updates."""
        assert self.mechanical.shape == (expected_m,), f"Mechanical state mismatch: {self.mechanical.shape}"
        assert self.electromagnetic.shape == (expected_e,), f"EM state mismatch: {self.electromagnetic.shape}"
        assert self.thermal.shape == (expected_t,), f"Thermal state mismatch: {self.thermal.shape}"
        assert self.sensor.shape == (expected_s,), f"Sensor state mismatch: {self.sensor.shape}"
