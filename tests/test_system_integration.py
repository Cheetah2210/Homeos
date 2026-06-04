import unittest
import os
import sys

# Ensure the root directory is in the path so we can import our core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.observer import HomeosObserver
from core.propulsion import HomeosPropulsion
from core.storage import HomeosStorage

class TestHomeosFullIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up a unified Tier 1 Prototyping system."""
        self.tier = "tier_1_micro"
        self.observer = HomeosObserver(tier_profile=self.tier)
        self.propulsion = HomeosPropulsion(tier_profile=self.tier)
        self.storage = HomeosStorage(tier_profile=self.tier)

    def test_cold_start_to_emergency_dump_sequence(self):
        """
        Simulates a continuous 4-stage real-world operational cycle:
        Stage 1: Cold Start (Battery is frozen solid, charging locked)
        Stage 2: Thermal Priming (Core heat dumps into salt vault to melt it)
        Stage 3: High-Output Cruise encountering an External Presence
        Stage 4: Structural Anomaly forcing an Emergency Kinetic Dump
        """
        print(f"\n=== STARTING INTEGRATION TEST BENCH: SYSTEM SCALE [{self.tier.upper()}] ===")
        
        # ---------------------------------------------------------
        # STAGE 1: COLD START AUDIT
        # ---------------------------------------------------------
        # The system is sitting in a cold environment (e.g., 20°C ambient)
        self.storage.current_temperature_celsius = 20.0
        self.storage.is_electrolyte_liquid = False
        
        # Brain stem reads the initial frozen state
        directive = self.observer.evaluate_sensory_matrix(
            active_strain=0.0005,      # Nominal structural strain
            core_temp=20.0,
            battery_temp=self.storage.current_temperature_celsius,
            field_leakage=0.0,
            proximity_to_living=10.0   # Clear environment
        )
        
        print(f"Stage 1 [Cold]: Status = {directive['status_flag']}, Equilibrium = {directive['equilibrium_index']}")
        # Verify the brain stem flags a metabolic threat due to frozen salt
        self.assertLess(directive['equilibrium_index'], 1.0)
        
        # Verify that attempting to charge a frozen solid battery safely fails
        charge_attempt = self.storage.execute_charge_cycle(input_power_watts=2000, duration_seconds=60)
        self.assertIn("error", charge_attempt)
        print("Stage 1 Pass: Charge cycle successfully blocked while electrolyte is solid.")

        # ---------------------------------------------------------
        # STAGE 2: THERMAL PRIMING LOOP
        # ---------------------------------------------------------
        # We simulate routing an external pre-heater element or localized induction loop
        # dumping 1500 Watts directly into the salt storage matrix for 15 minutes (900 seconds)
        print("\nStage 2: Initiating thermal priming sequence...")
        phase_state = self.storage.calculate_phase_dynamics(
            external_thermal_input_watts=1500, 
            duration_seconds=900
        )
        
        print(f"Stage 2 [Primed]: Salt Temp = {phase_state['current_temp_c']}°C, State = {phase_state['electrolyte_state']}")
        self.assertTrue(self.storage.is_electrolyte_liquid)
        self.assertEqual(phase_state['electrolyte_state'], "LIQUID_ACTIVE")

        # Re-evaluate brain stem now that metabolism is active
        directive = self.observer.evaluate_sensory_matrix(
            active_strain=0.0005,
            core_temp=60.0,
            battery_temp=self.storage.current_temperature_celsius,
            field_leakage=0.0,
            proximity_to_living=10.0
        )
        self.assertEqual(directive['status_flag'], "SYSTEM_OPTIMAL_HOMEOSTASIS")
        print("Stage 2 Pass: Electrolyte liquefied. System achieves nominal homeostasis.")

        # ---------------------------------------------------------
        # STAGE 3: HIGH-OUTPUT CRUISE & FIELD SHADOWING
        # ---------------------------------------------------------
        print("\nStage 3: Transitioning to active propulsion...")
        # Spool up the carbon flywheel
        self.propulsion.current_gyro_rpm = 95000 
        
        # Simulate moving into a sensitive perimeter (Proximity dropped to 0.8 meters)
        # Baseline leakage without suppression is high (0.04 Tesla)
        directive = self.observer.evaluate_sensory_matrix(
            active_strain=0.0012,
            core_temp=85.0,
            battery_temp=self.storage.current_temperature_celsius,
            field_leakage=0.04,
            proximity_to_living=0.8
        )
        
        # The AI must recognize the proximity breach and activate the environmental shadow loops
        self.assertEqual(directive['status_flag'], "SHADOW_CONTAINMENT_ACTIVE")
        self.assertTrue(directive['active_phase_cancellation'])
        
        # Pass the phase cancellation directive down to the Lorentz vector calculations
        thrust_data = self.propulsion.compute_lorentz_push(
            target_output_pct=directive['target_gyro_output_pct'],
            phase_cancellation_active=directive['active_phase_cancellation']
        )
        
        print(f"Stage 3 [Shadow Active]: Target Power = {directive['target_gyro_output_pct']}%, Net Thrust = {thrust_data['thrust_newtons']} N")
        self.assertLess(directive['target_gyro_output_pct'], 100.0) # AI throttled down slightly for safety shadow
        print("Stage 3 Pass: Environmental shadow verified. Phase cancellation active, thrust safe.")

        # ---------------------------------------------------------
        # STAGE 4: CRITICAL ANOMALY & KINETIC THERMAL DUMP
        # ---------------------------------------------------------
        print("\nStage 4: Injecting a severe structural shear anomaly...")
        # Simulate an impact or structural failure causing the carbon hull strain to skyrocket
        extreme_strain = 0.0065  # Well past our 0.0045 pain threshold
        
        directive = self.observer.evaluate_sensory_matrix(
            active_strain=extreme_strain,
            core_temp=110.0,
            battery_temp=self.storage.current_temperature_celsius,
            field_leakage=0.0005,
            proximity_to_living=10.0
        )
        
        print(f"Stage 4 [Anomaly]: Threat detected! Status = {directive['status_flag']}")
        self.assertEqual(directive['status_flag'], "EMERGENCY_SHUTDOWN_ABSORPTION")
        self.assertEqual(directive['target_gyro_output_pct'], 0.0)
        
        # Calculate the massive kinetic energy load stored in the spinning carbon core that must be dumped
        kinetic_energy_to_dump = self.propulsion.calculate_kinetic_buffer()
        print(f"Stage 4 [Kinetic Buffer]: Core Kinetic Energy to neutralize = {round(kinetic_energy_to_dump, 2)} Joules")
        
        # Execute the absolute safety override: dump the kinetic energy as raw heat directly into the salt matrix
        dump_result = self.storage.execute_thermal_absorption_dump(core_waste_joules=kinetic_energy_to_dump)
        print(f"Stage 4 [Absorption]: Battery Absorbed Load. New Salt Temp = {dump_result['battery_new_temp_c']}°C")
        
        # Verify the containment holds and doesn't exceed our carbon-ceramic structural ceiling (2200°C)
        self.assertEqual(dump_result['absorption_status'], "THERMAL_DUMP_ABSORBED_SUCCESSFULLY")
        self.assertLess(dump_result['battery_new_temp_c'], 2200.0)
        print("Stage 4 Pass: Emergency kinetic dump absorbed cleanly. Zero environmental rupture.")
        
        print("=== ALL INTEGRATION SCENARIOS PASSED SUCCESSFULLY ===\n")

if __name__ == '__main__':
    unittest.main()
