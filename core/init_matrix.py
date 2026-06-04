import json
import os
import math

class HomeosMatrixScaler:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Loads the physical profiles and scales raw material limits 
        to fit the real-world dimensions of the chosen tier.
        """
        config_path = os.path.join(os.path.dirname(__file__), '../config')
        
        with open(os.path.join(config_path, 'materials_matrix.json'), 'r') as f:
            self.raw_materials = json.load(f)['materials']
            
        with open(os.path.join(config_path, 'system_profiles.json'), 'r') as f:
            self.tier = json.load(f)['tiers'][tier_profile]
            
        self.tier_key = tier_profile

    def get_scaled_matrix(self):
        """
        Applies non-linear material scaling laws based on structural volume.
        """
        scaled_matrix = {}
        
        # Calculate scale factor relative to the base Tier 1 micro unit (0.15m)
        base_radius = 0.15 / 2.0
        current_radius = self.tier['core_diameter_meters'] / 2.0
        scale_factor = current_radius / base_radius
        
        for mat_name, properties in self.raw_materials.items():
            scaled_props = properties.copy()
            
            # --- RULE 1: STRUCTURAL DERATING ---
            if "tensile_strength_mpa" in properties:
                if scale_factor > 1.0:
                    derating = 1.0 - (0.05 * math.log(scale_factor))
                    scaled_props["tensile_strength_mpa"] = round(properties["tensile_strength_mpa"] * derating, 2)
                    
            # --- RULE 2: THERMAL MASS DISSIPATION SCALING ---
            if "thermal_conductivity_w_mk" in properties:
                thermal_retention_factor = 1.0 / (1.0 + (0.02 * (scale_factor - 1.0)))
                scaled_props["effective_thermal_dissipation_factor"] = round(thermal_retention_factor, 4)
            elif "thermal_conductivity_horizontal_w_mk" in properties:
                thermal_retention_factor = 1.0 / (1.0 + (0.02 * (scale_factor - 1.0)))
                scaled_props["effective_thermal_dissipation_factor"] = round(thermal_retention_factor, 4)

            # --- RULE 3: ELECTRICAL PAIN SENSITIVITY ---
            if "pain_threshold_strain" in properties:
                scaled_props["pain_threshold_strain"] = round(properties["pain_threshold_strain"] * (1.0 / math.sqrt(scale_factor)), 6)

            scaled_matrix[mat_name] = scaled_props
            
        return scaled_matrix
