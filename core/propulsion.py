import json
import os
import math

class HomeosPropulsion:
    def __init__(self, tier_profile="tier_1_micro"):
        """
        Initializes the propulsion drive mechanics and electrodynamics.
        Loads physical boundary limits for the selected scale tier.
        """
        config_path = os.path.join(os.path.dirname(__file__), '../config')
        
        with open(os.path.join(config_path, 'materials_matrix.json'), 'r') as f:
            self.materials = json.load(f)['materials']
            
        with open(os.path.join(config_path, 'system_profiles.json'), 'r') as f:
            self.profile = json.load(f)['tiers'][tier_profile]

        # Physical Constants
        self.radius = self.profile['core_diameter_meters'] / 2.0
        
        # Real-Time Mechanical States
        self.current_gyro_rpm = 0.0
        self.ring_alpha_tilt_deg = 0.0  # Outer gyroscopic gimbal angle
        self.ring_beta_tilt_deg = 0.0   # Inner gyroscopic gimbal angle
        
        # Real-Time Electrodynamic States
        self.magnetic_flux_density_b = 1.2  # Base Tesla rating of local iron-core magnets
        self.channel_length_meters = self.radius * 0.8  # Solid-state acceleration track length

    def calculate_kinetic_buffer(self):
        """
        Calculates the current energy capacity stored within the spinning carbon core.
        Equation: E_k = 0.5 * I * w^2
        """
        # Model the carbon gyro-core as a solid cylinder for moment of inertia: I = 0.5 * m * r^2
        # Approximate mass based on scale volume and carbon-ceramic matrix density
        volume = math.pi * (self.radius ** 2) * (self.radius * 0.3)
        density = self.materials['carbon_ceramic_matrix']['density_kg_m3']
        mass = volume * density
        
        moment_of_inertia = 0.5 * mass * (self.radius ** 2)
        
        # Convert RPM to angular velocity (radians per second)
        angular_velocity_rad_s = (self.current_gyro_rpm * 2 * math.pi) / 60.0
        
        # Kinetic Energy in Joules
        kinetic_energy_joules = 0.5 * moment_of_inertia * (angular_velocity_rad_s ** 2)
        return kinetic_energy_joules

    def compute_lorentz_push(self, target_output_pct, phase_cancellation_active):
        """
        Computes the net forward thrust vector using the Lorentz Force Equation.
        F = I * L * B
        Bypasses magnetic equilibrium locking via time-variant delta adjustments.
        """
        if target_output_pct <= 0.0:
            return {"thrust_newtons": 0.0, "eddy_current_loss_watts": 0.0, "field_asymmetry_index": 0.0}

        # Scale input current based on the AI observer's target allocation
        # Max prototyping current capped at 50 Amps for Tier 1, scales up for Tiers 2 & 3
        max_current = 50.0 if self.profile['target_power_output_kw'] <= 5.0 else 400.0
        input_current = max_current * (target_output_pct / 100.0)

        # Environmental Protection Check: Adjust flux density if active phase-cancellation is triggered
        effective_b_field = self.magnetic_flux_density_b
        if phase_cancellation_active:
            # Peripheral counter-coils fire to loop field lines tightly inside the carbon frame
            # This restricts external leakage but introduces a minor 15% drop in internal thrust efficiency
            effective_b_field *= 0.85

        # --- BYPASSING THE STICKY POINTS ---
        # Traditional fixed-magnet configurations experience a locking equilibrium point where net force collapses.
        # The AI introduces a rapid micro-pulsing wave to the electrical channels (time-variant delta) 
        # to ensure the force vector remains permanently asymmetric.
        time_variant_delta = math.sin(self.current_gyro_rpm * 0.01) * 0.05
        field_asymmetry_index = 1.0 + time_variant_delta

        # Base Lorentz calculation: F = I * L * B
        base_thrust = input_current * self.channel_length_meters * effective_b_field
        net_thrust_newtons = base_thrust * field_asymmetry_index

        # Calculate parasitic eddy current losses within the local iron-infused matrix
        eddy_loss_watts = (input_current ** 2) * 0.02 * (1.0 - time_variant_delta)

        return {
            "thrust_newtons": round(net_thrust_newtons, 2),
            "eddy_current_loss_watts": round(eddy_loss_watts, 2),
            "field_asymmetry_index": round(field_asymmetry_index, 4)
        }

    def adjust_gyroscopic_gimbals(self, thrust_vector_newtons):
        """
        Dynamically tilts the dual gyroscopic stabilizer rings to counteract 
        counter-torque reactions, preventing structural shear in the carbon-ceramic hull.
        """
        if thrust_vector_newtons == 0:
            self.ring_alpha_tilt_deg = 0.0
            self.ring_beta_tilt_deg = 0.0
            return

        # Calculate torque reaction based on thrust force and core radius
        reaction_torque = thrust_vector_newtons * self.radius
        
        # Compensate for torque by tilting the rings. 
        # Angles are clamped strictly to a maximum of 45 degrees to maintain internal clearance.
        compensation_factor = reaction_torque * 0.1
        self.ring_alpha_tilt_deg = min(max(compensation_factor, -45.0), 45.0)
        self.ring_beta_tilt_deg = min(max(-compensation_factor * 0.5, -45.0), 45.0)

        return {
            "alpha_gimbal_deg": round(self.ring_alpha_tilt_deg, 2),
            "beta_gimbal_deg": round(self.ring_beta_tilt_deg, 2)
        }
