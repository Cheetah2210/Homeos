import os
import json
import math
from core.init_matrix import HomeosMatrixScaler

class HomeosObserver:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the unified hybrid AI brainstem.
        Loads dynamically scaled material boundaries and sets tracking variables.
        """
        # Instantiate the scaling engine to pull proportional physical limits
        scaler = HomeosMatrixScaler(tier_profile=tier_profile)
        self.profile = scaler.tier
        self.materials = scaler.get_scaled_matrix()
        
        # System Metrology Identifiers
        self.system_tier = tier_profile
        self.internal_pain_score = 0.0
        self.environmental_anxiety = 0.0
        self.global_equilibrium = 1.0  # 1.0 represents perfect nominal balance

    def evaluate_sensory_matrix(self, active_strain, core_temp, battery_temp, field_leakage, proximity_to_living):
        """
        Processes real-time multi-material telemetry from the carbon-ceramic hull, 
        quartz shield, and molten-salt battery storage.
        
        Returns a unified physical system instruction dictionary.
        """
        # 1. THE STRUCTURAL PAIN LOOP (Carbon-Ceramic Matrix / CNT Mesh)
        # The threshold is dynamically lowered by the scaler as the system size increases
        scaled_pain_threshold = self.materials['carbon_ceramic_matrix']['pain_threshold_strain']
        
        if active_strain > scaled_pain_threshold:
            # Linear normalization of strain exceeding structural limits
            self.internal_pain_score = min((active_strain - scaled_pain_threshold) / scaled_pain_threshold, 1.0)
        else:
            self.internal_pain_score = 0.0

        # 2. THE METABOLIC ENERGETIC LOOP (Molten-Salt Electrolyte Matrix)
        optimal_salt_temp = self.materials['molten_salt_electrolyte']['optimal_operating_temp_celsius']
        critical_freeze = self.materials['molten_salt_electrolyte']['critical_freeze_temp_celsius']
        
        if battery_temp < critical_freeze:
            # Electrolyte is approaching crystallization; immediate thermal dump required to maintain ion mobility
            metabolic_threat = 0.85
        else:
            # Track deviations from optimal liquid performance window
            metabolic_threat = min(abs(battery_temp - optimal_salt_temp) / optimal_salt_temp, 1.0)

        # 3. THE ENVIRONMENTAL SHADOW LOOP (Active Empathy Fields)
        # Check if organic material or sensitive instrumentation breaches our safety envelope
        if proximity_to_living < self.profile['environmental_shadow_radius_meters']:
            target_leakage = 0.001  # Safe micro-Tesla limits for biological protection
            # Calculate anxiety based on how much our field leakage spills over the strict safe limit
            self.environmental_anxiety = min(field_leakage / 0.01, 1.0)
        else:
            target_leakage = 0.05   # Standard operational ambient leakage ceiling
            self.environmental_anxiety = 0.0

        # 4. COMPUTE UNIFIED GLOBAL EQUILIBRIUM
        # Weights: 40% Structural Integrity, 20% Thermal Metabolism, 40% Environmental Shadow Containment
        total_threat = (self.internal_pain_score * 0.4) + (metabolic_threat * 0.2) + (self.environmental_anxiety * 0.4)
        self.global_equilibrium = max(1.0 - total_threat, 0.0)

        # 5. GENERATE HARDCODED OVERRIDE DIRECTIVE
        return self.compute_system_directive(target_leakage, core_temp)

    def compute_system_directive(self, target_leakage, core_temp):
        """
        Translates cognitive equilibrium data into direct, executable mechanical 
        instructions for the propulsion core and thermal loops.
        """
        directive = {
            "equilibrium_index": round(self.global_equilibrium, 4),
            "target_gyro_output_pct": 100.0,
            "active_phase_cancellation": False,
            "thermal_reroute_target": "none",
            "status_flag": "SYSTEM_OPTIMAL_HOMEOSTASIS"
        }

        # --- HEURISTIC HOMEOSTATIC OVERRIDES ---
        
        # CRITICAL
