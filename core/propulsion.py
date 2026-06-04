import json
import os
import math
from core.init_matrix import HomeosMatrixScaler

class HomeosPropulsion:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes propulsion drive mechanics and electrodynamics using scaled boundaries.
        """
        scaler = HomeosMatrixScaler(tier_profile=tier_profile)
        self.profile = scaler.tier
        self.materials = scaler.get_scaled_matrix()

        self.radius = self.profile['core_diameter_meters'] / 2.0
        self.current_gyro_rpm = 0.0
        self.ring_alpha_tilt_deg = 0.0  
        self.ring_beta_tilt_deg = 0.0   
        
        self.magnetic_flux_density_b = self.materials['powdered_iron_flux_guides']['magnetic_permeability_relative'] * 1.2e-5
        self.channel_length_meters = self.radius * 0.8

    def calculate_kinetic_buffer(self):
        """
        Calculates energy stored within the rotating carbon core: E_k = 0.5 * I * w^2
        """
        volume = math.pi * (self.radius ** 2) * (self.radius * 0.3)
        density = self.materials['carbon_ceramic_matrix']['density_kg_m3']
        mass = volume * density
        
        moment_of_inertia = 0.5 * mass * (self.radius ** 2)
        angular_velocity_rad_s = (self.current_gyro_rpm * 2 * math.pi) / 60.0
        
        return 0.5 * moment_of_inertia * (angular_velocity_rad_s ** 2)

    def compute_lorentz_push(self, target_output_pct, phase_cancellation_active):
        """
        Computes forward thrust vectors using the Lorentz Force Equation: F = I * L * B
        Bypasses magnetic locking via time-variant delta adjustments.
        """
        if target_output_pct <= 0.0:
            return {"thrust_newtons": 0.0, "eddy_current_loss_watts": 0.0, "field_asymmetry_index": 1.0}

        max_current = 50.0 if self.profile['target_power_output_kw'] <= 5.0 else 400.0
        input_current = max_current * (target_output_pct / 100.0)

        effective_b_field = self.magnetic_flux_density_b
        if phase_cancellation_active:
            effective_b_field *= 0.85

        time_variant_delta = math.sin(self.current_gyro_rpm * 0.01) * 0.05
        field_asymmetry_index = 1.0 + time_variant_delta

        base_thrust = input_current * self.channel_length_meters * effective_b_field
        net_thrust_newtons = base_thrust * field_asymmetry_index
        eddy_loss_watts = (input_current ** 2) * 0.02 * (1.0 - time_variant_delta)

        return {
            "thrust_newtons": round(net_thrust_newtons, 2),
            "eddy_current_loss_watts": round(eddy_loss_watts, 2),
            "field_asymmetry_index": round(field_asymmetry_index, 4)
        }

    def adjust_gyroscopic_gimbals(self, thrust_vector_newtons):
        """
        Dynamically tilts the stabilizer rings to counteract torque reactions.
        """
        if thrust_vector_newtons == 0:
            self.ring_alpha_tilt_deg = 0.0
            self.ring_beta_tilt_deg = 0.0
            return {"alpha_gimbal_deg": 0.0, "beta_gimbal_deg": 0.0}

        reaction_torque = thrust_vector_newtons * self.radius
        compensation_factor = reaction_torque * 0.1
        self.ring_alpha_tilt_deg = min(max(compensation_factor, -45.0), 45.0)
        self.ring_beta_tilt_deg = min(max(-compensation_factor * 0.5, -45.0), 45.0)

        return {
            "alpha_gimbal_deg": round(self.ring_alpha_tilt_deg, 2),
            "beta_gimbal_deg": round(self.ring_beta_tilt_deg, 2)
        }
