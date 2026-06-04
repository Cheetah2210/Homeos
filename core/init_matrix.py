import os
import json
import math

class HomeosMatrixScaler:
    def __init__(self, tier_profile="tier_1_micro"):
        """Initializes the structural translator and computes dynamic material bounds."""
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base_path, 'config/materials_matrix.json')
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        if tier_profile not in config_data['system_scale_profiles']:
            raise ValueError(f"Target profile '{tier_profile}' not found in configuration scopes.")
            
        self.tier = config_data['system_scale_profiles'][tier_profile]
        self.raw_materials = config_data['materials']
        
        # Determine scaling scale factor (lambda) relative to Tier 1 baseline
        self.r0 = 0.075
        self.scale_factor = self.tier['outer_radius_meters'] / self.r0
        self.chi = 0.12  # Logarithmic strength derating coefficient

    get_scaled_matrix(self):
        """Applies non-linear scaling transformations to simulation envelopes."""
        scaled = json.loads(json.dumps(self.raw_materials))
        
        if self.scale_factor > 1.0:
            # Domain 2 Model: Volumetric strength reduction due to micro-void probability distribution
            derating_multiplier = 1.0 - self.chi * math.log(self.scale_factor)
            base_strain = scaled['carbon_ceramic_matrix']['pain_threshold_strain']
            scaled['carbon_ceramic_matrix']['pain_threshold_strain'] = round(base_strain * derating_multiplier, 6)
            
        return scaled
