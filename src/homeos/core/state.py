from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class HomeosState:
    """
    Explicitly Decoupled Multi-Physics State Vector for Homeos v1.1.
    Separates the True Physical Universe from the Telemetry/Measurement Domain.
    
    Structure:
        x(t) = [ x_phys(t), x_obs(t) ]^T
    """
    # --- TRUE PHYSICAL STATE SPACE (x_phys) ---
    mechanical: np.ndarray       # Shape (3,) -> [strain_epsilon, displacement_z, velocity_v]
    electromagnetic: np.ndarray  # Shape (3,) -> [current_i, flux_b0, leakage_lambda]
    thermal: np.ndarray          # Shape (2,) -> [temp_c, phase_fraction_phi]

    # --- OBSERVATION SPACE / TELEMETRY DOMAIN (x_obs) ---
    sensor: np.ndarray           # Shape (2,) -> [v_strain_measurement, v_leakage_measurement]

    def __post_init__(self):
        """Enforce strict dimension rules and freeze array states to maintain determinism."""
        self.validate_dimensions()
        for vec in [self.mechanical, self.electromagnetic, self.thermal, self.sensor]:
            if hasattr(vec, 'flags'):
                vec.flags.writeable = False

    def validate_dimensions(self, m_dim=3, e_dim=3, t_dim=2, s_dim=2):
        """Maintains compliance with the unified R^10 state profile constraints."""
        assert self.mechanical.shape == (m_dim,), f"x_phys (mech) profile anomaly: {self.mechanical.shape}"
        assert self.electromagnetic.shape == (e_dim,), f"x_phys (em) profile anomaly: {self.electromagnetic.shape}"
        assert self.thermal.shape == (t_dim,), f"x_phys (thermal) profile anomaly: {self.thermal.shape}"
        assert self.sensor.shape == (s_dim,), f"x_obs (sensor) profile anomaly: {self.sensor.shape}"

    @property
    def x_phys(self) -> np.ndarray:
        """
        Extracts the explicit True Physical State vector vector block.
        Shape: (8,) -> Completely isolated from sensor distortion parameters.
        """
        phys_vector = np.concatenate([self.mechanical, self.electromagnetic, self.thermal])
        phys_vector.flags.writeable = False
        return phys_vector

    @property
    def x_obs(self) -> np.ndarray:
        """
        Extracts the explicit Measurement Domain / Observation vector block.
        Shape: (2,) -> The only information space visible to control law algorithms.
        """
        return self.sensor

    def get_unified_vector(self) -> np.ndarray:
        """Flattens the domain into an explicit 1D column vector matching x(t) in R^10."""
        unified = np.concatenate([self.mechanical, self.electromagnetic, self.thermal, self.sensor])
        unified.flags.writeable = False
        return unified

    @classmethod
    def from_unified_vector(cls, vec: np.ndarray, m_dim=3, e_dim=3, t_dim=2, s_dim=2):
        """Reconstructs the structural domains explicitly from a flat math vector."""
        total_expected = m_dim + e_dim + t_dim + s_dim
        assert vec.shape == (total_expected,), f"Dimensionality error. Expected {total_expected}, got {vec.shape}"
        
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
        """Generates a fresh, unmutated state snapshot for timestep t+1."""
        return HomeosState(
            mechanical=np.copy(mechanical) if mechanical is not None else np.copy(self.mechanical),
            electromagnetic=np.copy(electromagnetic) if electromagnetic is not None else np.copy(self.electromagnetic),
            thermal=np.copy(thermal) if thermal is not None else np.copy(self.thermal),
            sensor=np.copy(sensor) if sensor is not None else np.copy(self.sensor)
        )
