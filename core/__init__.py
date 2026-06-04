"""
Homeos Core Subsystems Module
Unifies the homeostatic observer brainstem, Lorentz propulsion vectoring,
molten-salt storage metabolism, physical I2C drivers, and network telemetry.
"""

from core.init_matrix import HomeosMatrixScaler
from core.observer import HomeosObserver
from core.propulsion import HomeosPropulsion
from core.storage import HomeosStorage
from core.hardware_interface import HomeosHardwareInterface
from core.network_interface import HomeosMqttInterface

# Define explicit public interface for clean package-level importing
__all__ = [
    "HomeosMatrixScaler",
    "HomeosObserver",
    "HomeosPropulsion",
    "HomeosStorage",
    "HomeosHardwareInterface",
    "HomeosMqttInterface",
]
