import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.init_matrix import HomeosMatrixScaler

class TestHomeosConfigValidation(unittest.TestCase):
    
    def setUp(self):
        """Loads configuration maps for rigorous structural boundary testing."""
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config'))
        
        with open(os.path.join(config_path, 'materials_matrix.json'), 'r') as f:
            self.materials = json.load(f)['materials']
            
        with open(os.path.join(config_path, 'system_profiles.json'), 'r') as f:
            self.tiers = json.load(f)['tiers']

    def test_materials_laws_of_physics(self):
        """Audits the raw materials matrix against non-negotiable physical laws."""
        for mat_name, props in self.materials.items():
            # Verify no impossible negative values exist
            if "density_kg_m3" in props:
                self.assertGreater(props["density_kg_m3"], 0.0, f"{mat_name} density cannot be zero or negative.")
            if "max_temp_celsius" in props:
                self.assertGreater(props["max_temp_celsius"], 0.0, f"{mat_name} thermal degradation limit must be positive.")
            if "pain_threshold_strain" in props:
                self.assertGreater(props["pain_threshold_strain"], 0.0, f"{mat_name} strain limit must be positive.")

        # Specific verification for critical components
        self.assertLess(self.materials['molten_salt_electrolyte']['melting_point_celsius'],
                        self.materials['molten_salt_electrolyte']['optimal_operating_temp_celsius'],
                        "Molten salt melting point must sit below optimal operating boundaries.")

    def test_dynamic_scaling_derating_curves(self):
        """
        Verifies that the HomeosMatrixScaler correctly downrates structural metrics 
        volumetrically when stepping from Tier 1 (Micro) to Tier 3 (Macro).
        """
        micro_scaler = HomeosMatrixScaler(tier_profile="tier_1_micro")
        macro_scaler = HomeosMatrixScaler(tier_profile="tier_3_macro")
        
        micro_matrix = micro_scaler.get_scaled_matrix()
        macro_matrix = macro_scaler.get_scaled_matrix()
        
        micro_strength = micro_matrix['carbon_ceramic_matrix']['tensile_strength_mpa']
        macro_strength = macro_matrix['carbon_ceramic_matrix']['tensile_strength_mpa']
        
        # Macro tiers must show a lower tensile strength limit due to composite volumetric scaling margins
        print(f"\n[CONFIG AUDIT] Scaled Tensile Capacity - Micro: {micro_strength} MPa | Macro: {macro_strength} MPa")
        self.assertLess(macro_strength, micro_strength, "Volumetric structural derating rules failed to apply to Macro tier.")

    def test_pain_sensitivity_escalation(self):
        """
        Verifies that the AI's structural pain sensitivity tightens in larger frameworks 
        to account for acoustic and mechanical delay variables.
        """
        micro_scaler = HomeosMatrixScaler(tier_profile="tier_1_micro")
        macro_scaler = HomeosMatrixScaler(tier_profile="tier_3_macro")
        
        micro_pain_thresh = micro_scaler.get_scaled_matrix()['carbon_ceramic_matrix']['pain_threshold_strain']
        macro_pain_thresh = macro_scaler.get_scaled_matrix()['carbon_ceramic_matrix']['pain_threshold_strain']
        
        # Macro scaling rules must demand higher sensitivity (lower threshold)
        print(f"[CONFIG AUDIT] Scaled Pain Threshold - Micro: {micro_pain_thresh} microstrain | Macro: {macro_pain_thresh} microstrain")
        self.assertLess(macro_pain_thresh, micro_pain_thresh, "Macro scale threshold failed to tighten sensitivity constraints.")

if __name__ == '__main__':
    unittest.main()
