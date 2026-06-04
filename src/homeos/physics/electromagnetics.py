import numpy as np

def lorentz_force(charge: float, velocity: np.ndarray, magnetic_field: np.ndarray) -> np.ndarray:
    """
    Computes standard cross-product vector force components.
    F = q * (v x B)
    """
    return charge * np.cross(velocity, magnetic_field)
