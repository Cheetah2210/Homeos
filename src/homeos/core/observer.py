import os
import json
import numpy as np
from homeos.core.state import HomeosState

class Observer:
    def __init__(self, tier_profile: str = "tier_1_micro"):
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
        config_path = os.path.join(base_path, 'config/materials_matrix.json')
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        self.profile = config_data['system_scale_profiles'][tier_profile]
        self.materials = config_data['materials']

    def evaluate(self, state: HomeosState) -> dict:
        """
        Compares active state matrices directly against configuration boundaries.
        """
        strain_limit = self.materials['carbon_ceramic_matrix']['pain_threshold_strain']
        current_strain = abs(state.mechanical[0])
        
        health_score = 1.0 - (current_strain / strain_limit if current_strain < strain_limit else 1.0)
        thermal_drift = abs(state.thermal[0] - self.materials['molten_salt_electrolyte']['optimal_operating_temp_celsius'])
        
        return {
            "health": float(health_score),
            "thermal_stability": float(-thermal_drift),
            "status_flag": "SYSTEM_OPTIMAL" if health_score > 0.5 else "CRITICAL_STRAIN_ALERT"
        }
