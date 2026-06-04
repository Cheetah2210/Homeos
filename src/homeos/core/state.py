from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class HomeosState:
    """
    Immutable multi-physics state vector representation at discrete timestep t.
    Prevents implicit mutation during physical parameter updates.
    """
    mechanical: np.ndarray       # State vector x_m (e.g., [stress, strain, geometry])
    electromagnetic: np.ndarray  # State vector x_e (e.g., [current, field, flux])
    thermal: np.ndarray          # State vector x_t (e.g., [temperature, phase fraction])
    sensor: np.ndarray           # State vector x_s (e.g., noisy state observations)

    def __post_init__(self):
        """Ensure all fields are loaded as read-only NumPy array matrices."""
        if hasattr(self.mechanical, 'flags'):
            self.mechanical.flags.writeable = False
        if hasattr(self.electromagnetic, 'flags'):
            self.electromagnetic.flags.writeable = False
        if hasattr(self.thermal, 'flags'):
            self.thermal.flags.writeable = False
        if hasattr(self.sensor, 'flags'):
            self.sensor.flags.writeable = False

    def copy_with_update(self, mechanical=None, electromagnetic=None, thermal=None, sensor=None):
        """Safely transitions to timestep t+1 using unmutated state vectors."""
        return HomeosState(
            mechanical=np.copy(mechanical) if mechanical is not None else np.copy(self.mechanical),
            electromagnetic=np.copy(electromagnetic) if electromagnetic is not None else np.copy(self.electromagnetic),
            thermal=np.copy(thermal) if thermal is not None else np.copy(self.thermal),
            sensor=np.copy(sensor) if sensor is not None else np.copy(self.sensor)
        )
