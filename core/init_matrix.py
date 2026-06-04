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
        Applies non-linear scaling laws to materials based on structural volume.
        """
        scaled_matrix = {}
        
        # Calculate scale factor relative to the base Tier 1 micro unit
        # Radius ratio gives us a geometric scaling baseline
        base_radius = 0.15 / 2.0
        current_radius = self.tier['core_diameter_meters'] / 2.0
        scale_factor = current_radius / base_radius
        
        for mat_name, properties in self.raw_materials.items():
            scaled_props = properties.copy()
            
            # --- RULE 1: STRUCTURAL DERATING (WEAVE VOLUMETRICS) ---
            # As carbon-ceramic structures grow larger, the probability of micro-voids
            # in the composite increases. We apply a structural derating factor.
            if "tensile_strength_mpa" in properties:
                if scale_factor > 1.0:
                    # Structural strength scales down slightly as volume increases to maintain a safety margin
                    derating = 1.0 - (0.05 * math.log(scale_factor))
                    scaled_props["tensile_strength_mpa"] = round(properties["tensile_strength_mpa"] * derating, 2)
                    
            # --- RULE 2: THERMAL MASS DISSIPATION SCALING ---
            # Heat dissipation drops relative to volume because volume scales cubically (r^3)
            # while surface area only scales quadratically (r^2).
            if "thermal_conductivity_w_mk" in properties:
                # Large systems require the AI to be more sensitive to heat traps
                thermal_retention_factor = 1.0 / (1.0 + (0.02 * (scale_factor - 1.0)))
                scaled_props["effective_thermal_dissipation_factor"] = round(thermal_retention_factor, 4)
            elif "thermal_conductivity_horizontal_w_mk" in properties:
                thermal_retention_factor = 1.0 / (1.0 + (0.02 * (scale_factor - 1.0)))
                scaled_props["effective_thermal_dissipation_factor"] = round(thermal_retention_factor, 4)

            # --- RULE 3: ELECTRICAL PAIN SENSITIVITY ---
            # For massive tiers, structural strain takes longer to propagate through the chassis.
            # We lower the pain threshold slightly for macro units so the AI reacts proactively.
            if "pain_threshold_strain" in properties:
                scaled_props["pain_threshold_strain"] = round(properties["pain_threshold_strain"] * (1.0 / math.sqrt(scale_factor)), 6)

            scaled_matrix[mat_name] = scaled_props
            
        return scaled_matrix
