import json
import os
import math

class HomeosObserver:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the unified hybrid AI brainstem.
        Loads material bounds and sets baseline operational targets.
        """
        config_path = os.path.join(os.path.dirname(__file__), '../config')
        
        with open(os.path.join(config_path, 'materials_matrix.json'), 'r') as f:
            self.materials = json.load(f)['materials']
            
        with open(os.path.join(config_path, 'system_profiles.json'), 'r') as f:
            self.profile = json.load(f)['tiers'][tier_profile]
            
        # Core Internal Variables (The Identity Matrix)
        self.system_tier = tier_profile
        self.internal_pain_score = 0.0
        self.environmental_anxiety = 0.0
        self.global_equilibrium = 1.0  # 1.0 is perfect homeostasis

    def evaluate_sensory_matrix(self, active_strain, core_temp, battery_temp, field_leakage, proximity_to_living):
        """
        Processes real-time telemetry from the carbon hull, quartz shield, and salt vault.
        Returns an actionable system directive.
        """
        # 1. Read Carbon-Ceramic Matrix Strain (The Pain Loop)
        max_allowed_strain = self.materials['carbon_ceramic_matrix']['pain_threshold_strain']
        if active_strain > max_allowed_strain:
            # Linear scaling of pain above threshold
            self.internal_pain_score = min((active_strain - max_allowed_strain) / max_allowed_strain, 1.0)
        else:
            self.internal_pain_score = 0.0

        # 2. Read Molten-Salt State (The Energetic Metabolism)
        optimal_salt_temp = self.materials['molten_salt_electrolyte']['optimal_operating_temp_celsius']
        critical_freeze = self.materials['molten_salt_electrolyte']['critical_freeze_temp_celsius']
        
        # Calculate metabolic deviation
        if battery_temp < critical_freeze:
            # Electrolyte is freezing; system must dump thermal energy back into the vault
            metabolic_threat = 0.8
        else:
            metabolic_threat = abs(battery_temp - optimal_salt_temp) / optimal_salt_temp

        # 3. Read Environmental Proximity (The Shadow Loop)
        if proximity_to_living < self.profile['environmental_shadow_radius_meters']:
            # Living tissue or sensitive infrastructure is inside our bubble
            target_leakage = 0.001  # Clamped to safe micro-tesla limits
            self.environmental_anxiety = min(field_leakage / 0.01, 1.0)
        else:
            target_leakage = 0.05
            self.environmental_anxiety = 0.0

        # 4. Calculate Unified Equilibrium (Global Health Vector)
        # Total threat aggregates all vectors. If threat reaches 1.0, system survival is compromised.
        total_threat = (self.internal_pain_score * 0.4) + (metabolic_threat * 0.2) + (self.environmental_anxiety * 0.4)
        self.global_equilibrium = max(1.0 - total_threat, 0.0)

        # 5. Hybrid Brainstem Decision Tree
        return self.compute_system_directive(target_leakage)

    def compute_system_directive(self, target_leakage):
        """
        Translates equilibrium values into physical mechanical instructions.
        """
        directive = {
            "equilibrium_index": round(self.global_equilibrium, 4),
            "target_gyro_output_pct": 100.0,
            "active_phase_cancellation": False,
            "thermal_reroute_target": "none"
        }

        # Handle Immediate Overrides
        if self.global_equilibrium < 0.3:
            # CRITICAL STATE: Emergency structural/environmental dump
            directive["target_gyro_output_pct"] = 0.0
            directive["active_phase_cancellation"] = True
            directive["thermal_reroute_target"] = "salt_vault_maximum"
            directive["status_flag"] = "EMERGENCY_SHUTDOWN_ABSORPTION"
            
        elif self.internal_pain_score > 0.0:
            # Moderate Pain: Throttle down gyro to let carbon-ceramic cool and cross-link
            directive["target_gyro_output_pct"] = max(100.0 - (self.internal_pain_score * 100.0), 20.0)
            directive["thermal_reroute_target"] = "localized_cnt_mesh"
            directive["status_flag"] = "ACTIVE_STRUCTURAL_HEALING"
            
        elif self.environmental_anxiety > 0.0:
            # Environmental Threat: Maintain power but immediately phase-cancel external leakage
            directive["active_phase_cancellation"] = True
            directive["target_gyro_output_pct"] = 80.0  # Slight safety back-off
            directive["status_flag"] = "SHADOW_CONTAINMENT_ACTIVE"
            
        else:
            directive["status_flag"] = "SYSTEM_OPTIMAL_HOMEOSTASIS"

        return directive
