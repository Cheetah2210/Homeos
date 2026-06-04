import json
import os
import math

class HomeosStorage:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the scalable molten-salt battery storage matrix.
        Loads chemical boundary thresholds and thermal baselines.
        """
        config_path = os.path.join(os.path.dirname(__file__), '../config')
        
        with open(os.path.join(config_path, 'materials_matrix.json'), 'r') as f:
            self.materials = json.load(f)['materials']
            
        with open(os.path.join(config_path, 'system_profiles.json'), 'r') as f:
            self.profile = json.load(f)['tiers'][tier_profile]

        # Scaled Volumetric Battery Dimensions
        # Battery tank volume scales proportionally to the total hull footprint
        self.tank_volume_m3 = (self.profile['hull_thickness_meters'] ** 3) * 4.0
        
        # Chemical State Baselines
        self.salt_config = self.materials['molten_salt_electrolyte']
        self.current_temperature_celsius = 20.0  # Starts at ambient room temperature
        self.state_of_charge_pct = 50.0          # Safe storage baseline charge
        self.is_electrolyte_liquid = False

    def calculate_phase_dynamics(self, external_thermal_input_watts, duration_seconds):
        """
        Models the phase change of the NaCl-AlCl3 electrolyte.
        Determines if the salt is solid (inert/safe) or liquid (mobile/active).
        """
        # Specific heat capacity proxy for sodium-aluminum chloride matrix
        # Solid phase requires more localized thermal mass to break lattice bonds
        specific_heat_solid = 1200.0  # J/kg·K
        specific_heat_liquid = 1350.0 # J/kg·K
        approx_salt_mass_kg = self.tank_volume_m3 * 1650.0  # Density approximation

        # Calculate internal resistive heat generation (I^2 * R metabolic heat)
        # Large scale units generate enough internal resistance during cycles to self-sustain
        internal_metabolic_heat_watts = 0.0
        if self.is_electrolyte_liquid and self.state_of_charge_pct > 0.0:
            internal_metabolic_heat_watts = (self.profile['target_power_output_kw'] * 1000.0) * 0.03

        total_thermal_energy_joules = (external_thermal_input_watts + internal_metabolic_heat_watts) * duration_seconds

        # Temperature Delta calculation
        shc = specific_heat_liquid if self.is_electrolyte_liquid else \
              specific_heat_solid
        temperature_delta = total_thermal_energy_joules / \
            (approx_salt_mass_kg * shc)
        self.current_temperature_celsius += temperature_delta

        # Evaluate Phase Transition State
        melting_point = self.salt_config['melting_point_celsius']
        if self.current_temperature_celsius >= melting_point:
            self.is_electrolyte_liquid = True
        else:
            # If temp drops below melting point, the salt freezes solid.
            # Ions lock in place, zero self-discharge, completely inert.
            self.is_electrolyte_liquid = False

        return {
            "current_temp_c": round(self.current_temperature_celsius, 2),
            "electrolyte_state": "LIQUID_ACTIVE" if self.is_electrolyte_liquid else "SOLID_INERT"
        }

    def execute_charge_cycle(self, input_power_watts, duration_seconds):
        """
        Simulates charging the cell. Ions pass through the beta-alumina ceramic barrier.
        Fails safely if the salt is solid.
        """
        if not self.is_electrolyte_liquid:
            # If the salt is solid, ions cannot physically migrate. Charging is locked out.
            return {"error": "CHARGE_BLOCKED: Electrolyte is solid. Pre-heating sequence required."}

        # Calculate energy injected in Watt-hours
        energy_injected_wh = (input_power_watts * duration_seconds) / 3600.0
        
        # Total storage capacity scaled to tank size (Approx 180 Wh/kg)
        approx_salt_mass_kg = self.tank_volume_m3 * 1650.0
        total_capacity_wh = approx_salt_mass_kg * 180.0

        added_charge_pct = (energy_injected_wh / total_capacity_wh) * 100.0
        
        # Account for standard electrochemical efficiency (round-trip efficiency ~85%)
        self.state_of_charge_pct = min(self.state_of_charge_pct + (added_charge_pct * 0.85), 100.0)

        return {
            "state_of_charge_pct": round(self.state_of_charge_pct, 2),
            "internal_resistive_losses_watts": round(input_power_watts * 0.05, 2)
        }

    def execute_thermal_absorption_dump(self, core_waste_joules):
        """
        The Homeostatic Safety Override: Absorbs extreme kinetic/thermal dumps 
        from a braking or failing propulsion core straight into the salt matrix.
        """
        approx_salt_mass_kg = self.tank_volume_m3 * 1650.0
        shc = specific_heat_liquid = 1350.0
        
        # Directly translate the incoming energy shockwave into a temperature increase
        temperature_rise = core_waste_joules / (approx_salt_mass_kg * shc)
        self.current_temperature_celsius += temperature_rise
        
        # Verify if the thermal dump pushes the battery into critical structural failure
        max_ceramic_limit = self.materials['carbon_ceramic_matrix']['max_temp_celsius']
        
        status = "THERMAL_DUMP_ABSORBED_SUCCESSFULLY"
        if self.current_temperature_celsius > max_ceramic_limit:
            status = "CRITICAL_OVERHEATING_STRUCTURAL_RISK"
            
        return {
            "battery_new_temp_c": round(self.current_temperature_celsius, 2),
            "absorption_status": status
        }
