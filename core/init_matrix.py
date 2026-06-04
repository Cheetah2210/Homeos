import os
import json
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosMatrixScaler")

class HomeosMatrixScaler:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the Structural Matrix Scaler.
        Loads physical properties and calculates scale-dependent stress thresholds.
        """
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base_path, 'config/materials_matrix.json')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Critical configuration manifest missing at: {config_path}")
            
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            
        if tier_profile not in config_data['system_scale_profiles']:
            raise ValueError(f"Target scale profile '{tier_profile}' not found in configuration scopes.")
            
        self.tier = config_data['system_scale_profiles'][tier_profile]
        self.raw_materials = config_data['materials']
        
        # Reference baseline radius (Tier 1 baseline = 0.075m)
        self.r0 = 0.075
        self.scale_factor = self.tier['outer_radius_meters'] / self.r0
        self.chi = 0.12  # Mathematical logarithmic strength derating coefficient
        logger.info(f"Matrix Scaler initialized for {tier_profile}. Scale factor lambda: {self.scale_factor:.3f}")

    def get_scaled_matrix(self):
        """
        Applies non-linear volumetric scale-up transformations to the software twin material limits.
        Enforces logarithmic tensile-derating as structural mass expands.
        """
        scaled_materials = json.loads(json.dumps(self.raw_materials))
        
        if self.scale_factor > 1.0:
            # Volumetric Micro-Void Tensile Strength Derating Heuristic: sigma = sigma_0 * (1 - chi * ln(lambda))
            derating_multiplier = 1.0 - self.chi * math.log(self.scale_factor)
            base_strain = scaled_materials['carbon_ceramic_matrix']['pain_threshold_strain']
            
            # Bound the minimum structural strain threshold to prevent mathematical clipping
            adjusted_strain = max(base_strain * derating_multiplier, 0.0005)
            scaled_materials['carbon_ceramic_matrix']['pain_threshold_strain'] = round(adjusted_strain, 6)
            logger.info(f"Volumetric derating applied. Strain threshold adjusted from {base_strain} to {adjusted_strain:.6f}")
        else:
            logger.info("System operating at or below baseline parameters. Volumetric scaling bypass active.")
            
        return scaled_materials
