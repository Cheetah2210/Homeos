import numpy as np

class SensorInstrumentationModel:
    def __init__(self, dt: float = 0.01):
        self.dt = dt
        
        # --- Channel Parameters: [Strain_V, Leakage_V] ---
        self.sigma = np.array([0.001, 0.0025])      # Gaussian white noise standard deviation
        self.bias = np.array([0.005, -0.012])       # Initial channel instrument bias
        self.drift_rate = np.array([0.0001, 0.00005]) # Drift accumulation per second
        
        # ADC Quantization step limits (V_max / 2^bits)
        self.q_steps = np.array([3.3 / 4096.0, 3.3 / 65536.0]) 

    def apply_instrument_effects(self, raw_h: np.ndarray, step_index: int, base_seed: int) -> np.ndarray:
        """
        Transforms clean physics observations into a degraded measurement domain.
        Applies bias, random walk drift, Gaussian noise, and bitwise ADC quantization.
        """
        # 1. Deterministic PRNG seeding tied directly to the simulation step
        isolated_seed = int(base_seed + step_index) & 0xFFFFFFFF
        rng = np.random.default_rng(seed=isolated_seed)
        
        # 2. Accumulate time-variant sensor drift vectors
        elapsed_time = step_index * self.dt
        active_drift = self.drift_rate * elapsed_time
        
        # 3. Sample Gaussian white noise perturbations
        gaussian_perturbation = rng.normal(loc=0.0, scale=self.sigma, size=2)
        
        # 4. Synthesize real measurement voltage: H(x) + bias + drift + noise
        observed_voltage = raw_h + self.bias + active_drift + gaussian_perturbation
        
        # 5. Enforce saturation limits matching physical hardware rails
        observed_voltage = np.clip(observed_voltage, 0.0, 3.3)
        
        # 6. Apply discrete bitwise quantization steps
        quantized_voltage = np.round(observed_voltage / self.q_steps) * self.q_steps
        return quantized_voltage
