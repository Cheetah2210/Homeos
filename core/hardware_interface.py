import time

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None

class HomeosHardwareInterface:
    def __init__(self, bus_id=1):
        """Maps physical sensor register layout configurations to I2C slave channels."""
        self.bus_id = bus_id
        self.is_mock = SMBus is None
        self.ADC_ADDR_HULL = 0x48
        self.ADC_ADDR_FLUX = 0x4B
        
        self.POINTER_CONVERSION = 0x00
        self.POINTER_CONFIG = 0x01
        self.ADC_CONFIG_BASE = 0x8183

    def _read_raw_adc_channel(self, i2c_addr, channel):
        if self.is_mock:
            return 16000  # Returns nominal mid-scale reference registry integer
            
        mux_mask = (0x4 + channel) << 12
        config_val = (self.ADC_CONFIG_BASE & 0x8FFF) | mux_mask
        config_bytes = [(config_val >> 8) & 0xFF, config_val & 0xFF]
        
        with SMBus(self.bus_id) as bus:
            bus.write_i2c_block_data(i2c_addr, self.POINTER_CONFIG, config_bytes)
            time.sleep(0.01)
            raw_data = bus.read_i2c_block_data(i2c_addr, self.POINTER_CONVERSION, 2)
            
        raw_int = (raw_data[0] << 8) | raw_data[1]
        if raw_int > 32767:
            raw_int -= 65536
        return raw_int

    def sample_structural_strain(self):
        raw_val = self._read_raw_adc_channel(self.ADC_ADDR_HULL, 0)
        voltage = (raw_val / 32768.0) * 4.096
        return round(max(0.0, (voltage / 3.3) * 0.005), 6)

    def sample_flux_leakage(self):
        raw_val = self._read_raw_adc_channel(self.ADC_ADDR_FLUX, 2)
        voltage = (raw_val / 32768.0) * 4.096
        return round(abs(voltage - 2.5) * 0.1, 4)
