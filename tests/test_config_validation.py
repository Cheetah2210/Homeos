import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.init_matrix import HomeosMatrixScaler

class TestHomeosConfigValidation(unittest.TestCase):
    
    def setUp(self):
        """Loads configuration maps and maturity taxonomy profiles."""
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        with open(os.path.join(self.base_path, 'config/materials_matrix.json'), 'r') as f:
            self.materials = json.load(f)['materials']
            
        with open(os.path.join(self.base_path, 'validation/verification_taxonomy.json'), 'r') as f:
            self.taxonomy = json.load(f)['parameters']

    def test_materials_laws_of_physics(self):
        """Audits the raw materials matrix against verified theoretical limits."""
        for mat_name, props in self.materials.items():
            if "density_kg_m3" in props:
                self.assertGreater(props["density_kg_m3"], 0.0, f"{mat_name} density must be greater than zero.")
            if "max_temp_celsius" in props:
                self.assertGreater(props["max_temp_celsius"], 0.0, f"{mat_name} temperature bounds must be positive.")

    def test_architectural_maturity_isolation(self):
        """
        Ensures simulation assumptions are locked below safe maturity confidence scores 
        so unverified assertions cannot be compiled into production environments.
        """
        # Ensure the piezoresistive mesh is correctly isolated as an unverified hypothesis
        cnt_param = self.taxonomy['mwcnt_mesh_piezoresistive_gauge']
        self.assertEqual(cnt_param['domain'], "Simulation Assumption")
        self.assertEqual(cnt_param['maturity_level'], "UNVERIFIED_HYPOTHESIS")
        self.assertLessEqual(cnt_param['confidence_index'], 0.50, 
                             "Unverified simulation parameters cannot hold high confidence index ratings.")

        # Ensure demonstrated physical hardware parameters hold absolute validation status
        ceramic_param = self.taxonomy['alumina_silicate_kiln_profile']
        self.assertEqual(ceramic_param['domain'], "Demonstrated Hardware Capability")
        self.assertEqual(ceramic_param['maturity_level'], "PHYSICALLY_DEMONSTRATED")
        self.assertEqual(ceramic_param['confidence_index'], 1.0)

    def test_dynamic_scaling_derating_curves(self):
        """Verifies that scaling configurations are treated as unverified hypotheses."""
        derating_param = self.taxonomy['volumetric_tensile_derating_curve']
        self.assertEqual(derating_param['maturity_level'], "UNVERIFIED_HYPOTHESIS",
                         "Macro-scale tensile derating curve parameters must be flagged as unverified simulation models.")

if __name__ == '__main__':
    unittest.main()
