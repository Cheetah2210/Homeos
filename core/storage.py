import json
import os
import math
from core.init_matrix import HomeosMatrixScaler

class HomeosStorage:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the scalable molten-salt storage matrix.
        """
        scaler = HomeosMatrixScaler(tier_profile=tier_profile)
        self.profile = scaler.tier
        self.materials = scaler.get_scaled_matrix()

        self.tank_volume_m3 = (self.profile['hull_thickness_meters'] ** 3) * 4.0
        self.salt_config = self.materials['molten_salt_electrolyte']
        self.current_temperature_celsius = 20.0  
        self.state_of_charge_pct = 50.0          
        self.is_electrolyte_liquid = False

    def calculate_phase_dynamics(self, external_thermal_input_watts, duration_seconds):
        """
        Models phase changes and metabolic self-sustaining heating values.
        """
        specific_heat_solid = self.salt_config['specific_heat_solid_j_kgk']
        specific_heat_liquid = self.salt_config['specific_heat_liquid_j_kgk']
        approx_salt_mass_kg = self.tank_volume_m3 * self.salt_config['density_liquid_kg_m3']

        internal_metabolic_heat_watts = 0.0
        if self.is_electrolyte_liquid and self.state_of_charge_pct > 0.0:
            internal_metabolic_heat_watts = (self.profile['target_power_output_kw'] * 1000.0) * 0.03

        total_thermal_energy_joules = (external_thermal_input_watts + internal_metabolic_heat_watts) * duration_seconds
        shc = specific_heat_liquid if self.is_electrolyte_liquid else specific_heat_solid
        
        self.current_temperature_celsius += total_thermal_energy_joules / (approx_salt_mass_kg * shc)

        if self.current_temperature_celsius >= self.salt_config['melting_point_celsius']:
            self.is_electrolyte_liquid = True
        else:
            self.is_electrolyte_liquid = False

        return {
            "current_temp_c": round(self.current_temperature_celsius, 2),
            "electrolyte_state": "LIQUID_ACTIVE" if self.is_electrolyte_liquid else "SOLID_INERT"
        }

    def execute_charge_cycle(self, input_power_watts, duration_seconds):
        """
        Charges the cell by migrating ions through the beta-alumina ceramic wall.
        """
        if not self.is_electrolyte_liquid:
            return {"error": "CHARGE_BLOCKED: Electrolyte is solid. Pre-heating sequence required."}

        energy_injected_wh = (input_power_watts * duration_seconds) / 3600.0
        approx_salt_mass_kg = self.tank_volume_m3 * self.salt_config['density_liquid_kg_m3']
        total_capacity_wh = approx_salt_mass_kg * 180.0

        self.state_of_charge_pct = min(self.state_of_charge_pct + ((energy_injected_wh / total_capacity_wh) * 100.0 * 0.85), 100.0)

        return {
            "state_of_charge_pct": round(self.state_of_charge_pct, 2),
            "internal_resistive_losses_watts": round(input_power_watts * 0.05, 2)
        }

    def execute_thermal_absorption_dump(self, core_waste_joules):
        """
        Absorbs kinetic braking or electromagnetic energy directly into the salt storage.
        """
        approx_salt_mass_kg = self.tank_volume_m3 * self.salt_config['density_liquid_kg_m3']
        shc = self.salt_config['specific_heat_liquid_j_kgk']
        
        self.current_temperature_celsius += core_waste_joules / (approx_salt_mass_kg * shc)
        max_ceramic_limit = self.materials['carbon_ceramic_matrix']['max_temp_celsius']
        
        status = "THERMAL_DUMP_ABSORBED_SUCCESSFULLY"
        if self.current_temperature_celsius > max_ceramic_limit:
            status = "CRITICAL_OVERHEATING_STRUCTURAL_RISK"
            
        return {
            "battery_new_temp_c": round(self.current_temperature_celsius, 2),
            "absorption_status": status
        }
