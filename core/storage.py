import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosThermalStorage")

class HomeosStorage:
    def __init__(self):
        """
        Initializes the Thermal Storage Manager.
        Enforces explicit material constraints across solid, liquid, and latent heat zones.
        """
        self.freeze_point_c = 158.0              # Target crystallization line (Celsius)
        self.optimal_target_c = 220.0            # Nominal equilibrium baseline setpoint
        self.latent_heat_fusion_j_kg = 315000.0  # Latent heat of fusion variable capacity constant
        
        # State Tracking Invariants
        self.latent_energy_reserve_j = 0.0
        logger.info("Thermal Storage Manager fully operational.")

    def compute_thermal_state(self, current_temp, incoming_joules, mass_kg):
        """
        Tracks thermodynamic step shifts across heat capacity boundaries, 
        accounting for latent plateau thresholds.
        """
        if mass_kg <= 0.0:
            logger.error("State calculation rejected: Zero or negative storage mass footprint.")
            return {"temperature_c": current_temp, "phase_state": "INVALID_MASS"}

        # Dynamic specific heat routing: Solid phase = 1200 J/kg*K | Liquid phase = 1350 J/kg*K
        c_p = 1200.0 if current_temp < self.freeze_point_c else 1350.0
        
        # Linear tracking loop if operating outside of the transition baseline
        if current_temp != self.freeze_point_c:
            delta_t = incoming_joules / (mass_kg * c_p)
            projected_temp = current_temp + delta_t
            
            # Scenario A: Crosses freeze point boundary line while cooling down
            if current_temp > self.freeze_point_c and projected_temp < self.freeze_point_c:
                energy_to_freeze = (current_temp - self.freeze_point_c) * mass_kg * 1350.0
                remaining_joules = incoming_joules + energy_to_freeze # incoming energy is negative
                current_temp = self.freeze_point_c
                incoming_joules = remaining_joules
            
            # Scenario B: Crosses freeze point boundary line while heating up
            elif current_temp < self.freeze_point_c and projected_temp > self.freeze_point_c:
                energy_to_melt = (self.freeze_point_c - current_temp) * mass_kg * 1200.0
                remaining_joules = incoming_joules - energy_to_melt
                current_temp = self.freeze_point_c
                incoming_joules = remaining_joules
            
            else:
                # Core remains stable within a single physical phase zone
                phase = "LIQUID_STATE" if projected_temp > self.freeze_point_c else "SOLID_STATE"
                return {"temperature_c": round(projected_temp, 2), "phase_state": phase}

        # Handle the Latent Heat Fusion plateau calculations at precisely 158.0°C
        if current_temp == self.freeze_point_c:
            max_latent_capacity = self.latent_heat_fusion_j_kg * mass_kg
            self.latent_energy_reserve_j += incoming_joules
            
            # Manage phase escape boundaries and route residual overflow work values
            if self.latent_energy_reserve_j > max_latent_capacity:
                overflow_joules = self.latent_energy_reserve_j - max_latent_capacity
                self.latent_energy_reserve_j = max_latent_capacity
                # Phase change complete -> Liquid transition. Melt remaining energy via liquid c_p
                final_temp = self.freeze_point_c + (overflow_joules / (mass_kg * 1350.0))
                return {"temperature_c": round(final_temp, 2), "phase_state": "LIQUID_STATE"}
                
            elif self.latent_energy_reserve_j < 0.0:
                underflow_joules = self.latent_energy_reserve_j
                self.latent_energy_reserve_j = 0.0
                # Phase change complete -> Solid transition. Cool remaining energy via solid c_p
                final_temp = self.freeze_point_c + (underflow_joules / (mass_kg * 1200.0))
                return {"temperature_c": round(final_temp, 2), "phase_state": "SOLID_STATE"}
                
            else:
                return {"temperature_c": round(self.freeze_point_c, 2), "phase_state": "LATENT_TRANSITION_PLATEAU"}
