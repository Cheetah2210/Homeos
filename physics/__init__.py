from physics.mechanics import MechanicsSolver
from physics.electromagnetics import ElectromagneticsSolver
from physics.thermal import ThermalSolver

class UnifiedPhysicsPipeline:
    def __init__(self, r_core=0.075):
        self.mechanics = MechanicsSolver()
        self.electromagnetics = ElectromagneticsSolver(core_radius=r_core)
        self.thermal = ThermalSolver()

# Instantiate domain Singletons for core.engine loops
mechanics = MechanicsSolver()
electromagnetics = ElectromagneticsSolver()
thermal = ThermalSolver()
