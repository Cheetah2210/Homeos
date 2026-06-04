from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class HomeosState:
    """
    Immutable snapshot of the multi-physics state vector at discrete timestep t.
    Prevents thread mutation or unintended domain contamination.
    """
    mechanical: np.ndarray       # Vector x_m: [strain, displacement, velocity]
    electromagnetic: np.ndarray  # Vector x_e: [current_i, flux_b0, leakage]
    thermal: np.ndarray          # Vector x_t: [temp_c, phase_fraction_phi]
    sensor: np.ndarray           # Vector x_s: [strain_voltage, leakage_signal]

    def __post_init__(self):
        """Enforce strict read-only flags across all internal arrays."""
        for vec in [self.mechanical, self.electromagnetic, self.thermal, self.sensor]:
            if hasattr(vec, 'flags'):
                vec.flags.writeable = False

    def validate_dimensions(self, m_dim=3, e_dim=3, t_dim=2, s_dim=2):
        """Validates shape consistency before updating independent numerical layers."""
        assert self.mechanical.shape == (m_dim,), f"Mechanical dimension layout mismatch: {self.mechanical.shape}"
        assert self.electromagnetic.shape == (e_dim,), f"EM dimension layout mismatch: {self.electromagnetic.shape}"
        assert self.thermal.shape == (t_dim,), f"Thermal dimension layout mismatch: {self.thermal.shape}"
        assert self.sensor.shape == (s_dim,), f"Sensor dimension layout mismatch: {self.sensor.shape}"

    def copy_with_update(self, mechanical=None, electromagnetic=None, thermal=None, sensor=None):
        """Generates a fresh, unmutated state vector block for timestep t+1."""
        return HomeosState(
            mechanical=np.copy(mechanical) if mechanical is not None else np.copy(self.mechanical),
            electromagnetic=np.copy(electromagnetic) if electromagnetic is not None else np.copy(self.electromagnetic),
            thermal=np.copy(thermal) if thermal is not None else np.copy(self.thermal),
            sensor=np.copy(sensor) if sensor is not None else np.copy(self.sensor)
        )
