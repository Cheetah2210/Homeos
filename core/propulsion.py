import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosPropulsion")

class HomeosPropulsion:
    def __init__(self, target_radius=0.075):
        """
        Initializes the Propulsion Controller.
        
        Parameters:
            target_radius (float): The physical outer boundary of the cylindrical core (R_c) in meters.
        """
        self.r_core = target_radius
        self.mu_0 = 4 * math.pi * 1e-7  # Permeability of free space (H/m)
        logger.info(f"Propulsion Controller initialized with core boundary constraint: {self.r_core} meters.")

    def calculate_ideal_thrust(self, current, ambient_flux_b0):
        """
        Executes the closed-form definite integral analytical solution derived in VAL-ANALYTICAL-001.
        Assumes an idealized boundary condition where flux density falls to zero at r = r_core.
        
        Formula: F = (2/3) * I * B_0 * R_c
        
        Parameters:
            current (float): Active channel injection current (Amperes).
            ambient_flux_b0 (float): Peak central magnetic flux density (Tesla).
            
        Returns:
            float: Theoretical integrated radial containment force vector in Newtons.
        """
        if current <= 0.0 or ambient_flux_b0 <= 0.0:
            return 0.0
            
        analytical_force = (2.0 / 3.0) * current * ambient_flux_b0 * self.r_core
        return round(analytical_force, 6)

    def execute_numerical_solver(self, current, ambient_flux_b0, intervals=1001):
        """
        Computes the real-time force integration across a discrete grid mesh using 
        Simpson's Rule to cross-check computational twin scaling behavior against theory.
        
        Parameters:
            current (float): Active channel injection current (Amperes).
            ambient_flux_b0 (float): Peak central magnetic flux density (Tesla).
            intervals (int): Number of discrete grid sample nodes (must be odd).
            
        Returns:
            dict: Core metrics detailing numerical force, analytical targets, and absolute error delta.
        """
        if intervals % 2 == 0:
            intervals += 1  # Simpson's rule requires an odd number of intervals
            
        if current <= 0.0 or ambient_flux_b0 <= 0.0:
            return {"numerical_force_n": 0.0, "error_percentage": 0.0, "status": "IDLE"}

        dr = self.r_core / (intervals - 1)
        forces = []
        
        # Calculate local differential force vectors across the spatial matrix slices
        for i in range(intervals):
            r = i * dr
            # Local field profile calculation: B(r) = B_0 * (1 - (r^2 / R_c^2))
            b_local = ambient_flux_b0 * (1.0 - (r ** 2 / self.r_core ** 2))
            # dF = I * B(r)
            forces.append(current * b_local)
            
        # Execute discrete Simpson composite integration
        numerical_integral = forces[0] + forces[-1]
        for i in range(1, intervals - 1):
            if i % 2 == 1:
                numerical_integral += 4.0 * forces[i]
            else:
                numerical_integral += 2.0 * forces[i]
                
        numerical_integral = (dr / 3.0) * numerical_integral
        analytical_target = self.calculate_ideal_thrust(current, ambient_flux_b0)
        
        # Determine strict percentage error deviation margin
        error_percentage = abs((numerical_integral - analytical_target) / analytical_target) * 100.0
        status = "VERIFIED_COMPUTATIONAL_PASS" if error_percentage <= 0.001 else "CONVERGENCE_FAIL"
        
        return {
            "numerical_force_n": round(numerical_integral, 6),
            "analytical_target_n": analytical_target,
            "error_percentage": round(error_percentage, 6),
            "status": status
        }
