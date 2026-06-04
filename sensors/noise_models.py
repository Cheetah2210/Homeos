import numpy as np

class SeededNoiseEngine:
    @staticmethod
    def inject_gaussian_noise(true_value: float, scale: float, step_index: int, base_seed: int) -> float:
        """
        Generates deterministic noise parameters derived predictably from a frozen seed value.
        Prevents implicit tracking environment drift across automated test sweeps.
        """
        # Formulate a unique step-wise seed identifier
        isolated_seed = int(base_seed + step_index) & 0xFFFFFFFF
        rng = np.random.default_rng(seed=isolated_seed)
        
        noise_deviation = rng.normal(loc=0.0, scale=scale)
        return float(true_value + noise_deviation)
