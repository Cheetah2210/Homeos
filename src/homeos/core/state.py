from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class HomeosState:
    """
    Explicit multi-physics state vector representation for Homeos v1.1.
    Defines x(t) = [mechanical, electromagnetic, thermal, sensor]^T.
    """
    mechanical: np.ndarray       # x_m (Shape: 3) -> [strain, displacement, velocity]
    electromagnetic: np.ndarray  # x_e (Shape: 3) -> [current_i, flux_b0, leakage]
    thermal: np.ndarray          # x_t (Shape: 2) -> [temp_c, phase_fraction_phi]
    sensor: np.ndarray           # x_s (Shape: 2) -> [strain_voltage, leakage_signal]

    def __post_init__(self):
        """Enforce dimensions, value types, and absolute array immutability."""
        self.validate_dimensions()
        for vec in [self.mechanical, self.electromagnetic, self.thermal, self.sensor]:
            if hasattr(vec, 'flags'):
                vec.flags.writeable = False

    def validate_dimensions(self, m_dim=3, e_dim=3, t_dim=2, s_dim=2):
        """Validates shape profiles to protect numerical solver execution gates."""
        assert self.mechanical.shape == (m_dim,), f"x_m shape fault: {self.mechanical.shape}"
        assert self.electromagnetic.shape == (e_dim,), f"x_e shape fault: {self.electromagnetic.shape}"
        assert self.thermal.shape == (t_dim,), f"x_t shape fault: {self.thermal.shape}"
        assert self.sensor.shape == (s_dim,), f"x_s shape fault: {self.sensor.shape}"

    def get_unified_vector(self) -> np.ndarray:
        """
        Flattens and concatenates the sub-vectors into an explicit 1D array.
        Returns the exact mathematical representation: x(t) in R^10.
        """
        unified = np.concatenate([
            self.mechanical, 
            self.electromagnetic, 
            self.thermal, 
            self.sensor
        ])
        unified.flags.writeable = False
        return unified

    @classmethod
    def from_unified_vector(cls, vec: np.ndarray, m_dim=3, e_dim=3, t_dim=2, s_dim=2):
        """
        Reconstructs the explicit decoupled State object from a raw mathematical vector.
        Simplifies validation parsing and solver mapping integrations.
        """
        assert vec.shape == (m_dim + e_dim + t_dim + s_dim,), "Unified vector dimensionality fault."
        
        idx_e = m_dim
        idx_t = idx_e + e_dim
        idx_s = idx_t + t_dim
        
        return cls(
            mechanical=vec[0:idx_e],
            electromagnetic=vec[idx_e:idx_t],
            thermal=vec[idx_t:idx_s],
            sensor=vec[idx_s:]
        )

    def copy_with_update(self, mechanical=None, electromagnetic=None, thermal=None, sensor=None):
        """Generates a fresh, unmutated state vector block for timestep t+1."""
        return HomeosState(
            mechanical=np.copy(mechanical) if mechanical is not None else np.copy(self.mechanical),
            electromagnetic=np.copy(electromagnetic) if electromagnetic is not None else np.copy(self.electromagnetic),
            thermal=np.copy(thermal) if thermal is not None else np.copy(self.thermal),
            sensor=np.copy(sensor) if sensor is not None else np.copy(self.sensor)
        )
