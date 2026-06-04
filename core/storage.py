import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosStorage")

class HomeosStorage:
    def __init__(self):
        """
        Initializes the Thermal Storage Manager.
        Tracks localized energy states relative to molten-salt phase boundaries.
        """
        self.freeze_point_c = 158.0          # Critical crystallization line (Celsius)
        self.optimal_target_c = 220.0        # System set point equilibrium baseline (Celsius)
        self.latent_heat_fusion_j_kg = 315000.0  # Latent heat capacity profile parameter (J/kg)
        
        # Track physical state matrix boundaries
        self.latent_energy_reserve_j = 0.0
        logger.info("Thermal Storage Manager operational. Latent threshold locked at 158.0°C.")

    def compute_thermal_state(self, current_temp, incoming_joules, mass_kg):
        """
        Maps thermal progression steps across specific heat capacity boundaries.
        Accurately transitions between solid, liquid, and latent state storage zones.
        
        Parameters:
            current_temp (float): Initial recorded baseline sensor core temperature (°C).
            incoming_joules (float): Transferred work/heat energy dumped into the matrix (Joules).
            mass_kg (float): Total physical volume weight of active salt mix inside the core.
            
        Returns:
            dict: Complete snapshot of the adjusted thermal parameters.
        """
        if mass_kg <= 0.0:
            logger.error("Thermal update rejected: Zero or negative storage mass matrix footprint.")
            return {"temperature_c": current_temp, "phase_state": "INVALID_MASS"}

        # Define dynamic specific heat coefficients based on material state matrix
        # Solid phase: 1200 J/kg*K | Liquid phase: 1350 J/kg*K
        c_p = 1200.0 if current_temp < self.freeze_point_c else 1350.0
        
        # Handle simple linear thermal routing if no phase changes occur
        if current_temp != self.freeze_point_c:
            delta_t = incoming_joules / (mass_kg * c_p)
            projected_temp = current_temp + delta_t
            
            # Crosses freeze point line while cooling down
            if current_temp > self.freeze_point_c and projected_temp < self.freeze_point_c:
                # Calculate energy consumed to hit the exact transition threshold boundary
                energy_to_freeze = (current_temp - self.freeze_point_c) * mass_kg * 1350.0
                remaining_joules = incoming_joules + energy_to_freeze # incoming is negative
                current_temp = self.freeze_point_c
                incoming_joules = remaining_joules
            
            # Crosses freeze point line while heating up
            elif current_temp < self.freeze_point_c and projected_temp > self.freeze_point_c:
                energy_to_melt = (self.freeze_point_c - current_temp) * mass_kg * 1200.0
                remaining_joules = incoming_joules - energy_to_melt
                current_temp = self.freeze_point_c
                incoming_joules = remaining_joules
            
            else:
                # System remains within a single physical state band
                phase = "LIQUID_STATE" if projected_temp > self.freeze_point_c else "SOLID_STATE"
                return {"temperature_c": round(projected_temp, 2), "phase_state": phase}

        # Handle the Latent Heat Fusion state plateau calculation at exactly 158.0°C
        if current_temp == self.freeze_point_c:
            max_latent_capacity = self.latent_heat_fusion_j_kg * mass_kg
            self.latent_energy_reserve_j += incoming_joules
            
            # Clamp boundaries and process overflow energy if phase change completes
            if self.latent_energy_reserve_j > max_latent_capacity:
                overflow_joules = self.latent_energy_reserve_j - max_latent_capacity
                self.latent_energy_reserve_j = max_latent_capacity
                # Latent phase complete -> Transformed to full liquid status. Melt remaining via liquid c_p
                final_temp = self.freeze_point_c + (overflow_joules / (mass_kg * 1350.0))
                return {"temperature_c": round(final_temp, 2), "phase_state": "LIQUID_STATE"}
                
            elif self.latent_energy_reserve_j < 0.0:
                underflow_joules = self.latent_energy_reserve_j
                self.latent_energy_reserve_j = 0.0
                # Latent phase complete -> Transformed to full solid status. Cool via solid c_p
                final_temp = self.freeze_point_c + (underflow_joules / (mass_kg * 1200.0))
                return {"temperature_c": round(final_temp, 2), "phase_state": "SOLID_STATE"}
                
            else:
                return {"temperature_c": round(self.freeze_point_c, 2), "phase_state": "LATENT_TRANSITION_PLATEAU"}
