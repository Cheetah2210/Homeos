from core.init_matrix import HomeosMatrixScaler

class HomeosObserver:
    def __init__(self, tier_profile="tier_1_micro"):
        scaler = HomeosMatrixScaler(tier_profile=tier_profile)
        self.profile = scaler.tier
        self.materials = scaler.get_scaled_matrix()
        
        self.internal_pain_score = 0.0
        self.environmental_anxiety = 0.0
        self.global_equilibrium = 1.0

    def evaluate_sensory_matrix(self, active_strain, core_temp, battery_temp, field_leakage, proximity_to_living):
        """Processes real-time Sensor Fusion metrics against localized scaling limits."""
        scaled_pain_threshold = self.materials['carbon_ceramic_matrix']['pain_threshold_strain']
        
        # 1. Structural Load Delta Evaluation
        if active_strain > scaled_pain_threshold:
            self.internal_pain_score = min((active_strain - scaled_pain_threshold) / scaled_pain_threshold, 1.0)
        else:
            self.internal_pain_score = 0.0

        # 2. Thermal Phase-Change Assessment
        optimal_salt = self.materials['molten_salt_electrolyte']['optimal_operating_temp_celsius']
        critical_freeze = self.materials['molten_salt_electrolyte']['critical_freeze_temp_celsius']
        
        if battery_temp < critical_freeze:
            metabolic_threat = 0.85
        else:
            metabolic_threat = min(abs(battery_temp - optimal_salt) / optimal_salt, 1.0)

        # 3. Environmental Field Convergence Model
        if proximity_to_living < self.profile['environmental_shadow_radius_meters']:
            target_leakage = 0.001
            self.environmental_anxiety = min(field_leakage / 0.01, 1.0)
        else:
            target_leakage = 0.05
            self.environmental_anxiety = 0.0

        # Weighted Equilibrium Assembly
        total_threat = (self.internal_pain_score * 0.4) + (metabolic_threat * 0.2) + (self.environmental_anxiety * 0.4)
        self.global_equilibrium = max(1.0 - total_threat, 0.0)

        return self._generate_directives(target_leakage, core_temp)

    def _generate_directives(self, target_leakage, core_temp):
        directive = {
            "equilibrium_index": round(self.global_equilibrium, 4),
            "target_gyro_output_pct": 100.0,
            "active_phase_cancellation": False,
            "thermal_reroute_target": "none",
            "status_flag": "SYSTEM_OPTIMAL_HOMEOSTASIS"
        }

        if self.global_equilibrium < 0.35:
            directive["target_gyro_output_pct"] = 0.0
            directive["active_phase_cancellation"] = True
            directive["thermal_reroute_target"] = "salt_vault_maximum"
            directive["status_flag"] = "EMERGENCY_SHUTDOWN_ABSORPTION"
        elif self.internal_pain_score > 0.0:
            directive["target_gyro_output_pct"] = max(100.0 - (self.internal_pain_score * 100.0), 15.0)
            directive["thermal_reroute_target"] = "localized_cnt_mesh"
            directive["status_flag"] = "ACTIVE_STRUCTURAL_HEALING"
        elif self.environmental_anxiety > 0.0:
            directive["active_phase_cancellation"] = True
            directive["target_gyro_output_pct"] = 75.0
            directive["status_flag"] = "SHADOW_CONTAINMENT_ACTIVE"

        return directive
