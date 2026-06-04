import time
import math
try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    # Fallback mock for testing environments without GPIO/I2C hardware pins
    SMBus = None

class HomeosHardwareInterface:
    def __init__(self, bus_id=1):
        """
        Initializes the physical I2C connection channel.
        Default bus_id is 1 (Standard on Raspberry Pi and similar single-board computers).
        """
        self.bus_id = bus_id
        self.is_mock = SMBus is None
        
        # Base I2C addresses mapped from hardware/sensor_pin_mapping.csv
        self.ADC_ADDR_HULL = 0x48   # North/South Hull Piezoresistive Mesh
        self.ADC_ADDR_FLUX = 0x4B   # Hall Effect Flux Guides
        
        # ADS1115 Config Register constants
        self.POINTER_CONVERSION = 0x00
        self.POINTER_CONFIG = 0x01
        
        # Config: OS=1 (Single-Shot), MUX=Single-Ended, PGA=4.096V, MODE=Single-Shot, DR=128SPS
        self.ADC_CONFIG_BASE = 0x8183 

    def _read_raw_adc_channel(self, i2c_addr, channel):
        """
        Executes a low-level bitwise write-read transaction to select an ADC channel 
        and extract its 16-bit conversion register value.
        """
        if self.is_mock:
            # Return a baseline safe mock payload if running in a pure simulation environment
            return 16000 

        # Modify the multiplexer bits (bits 14-12) based on target channel (0-3)
        mux_mask = (0x4 + channel) << 12
        config_val = (self.ADC_CONFIG_BASE & 0x8FFF) | mux_mask
        
        config_bytes = [(config_val >> 8) & 0xFF, config_val & 0xFF]
        
        with SMBus(self.bus_id) as bus:
            # 1. Write configuration bytes to initiate conversion
            bus.write_i2c_block_data(i2c_addr, self.POINTER_CONFIG, config_bytes)
            
            # Wait for conversion completion (typically ~8ms at 128SPS)
            time.sleep(0.01)
            
            # 2. Point to the conversion register and read 2 raw data bytes
            raw_data = bus.read_i2c_block_data(i2c_addr, self.POINTER_CONVERSION, 2)
            
        # Reconstruct 16-bit signed integer value
        raw_int = (raw_data[0] << 8) | raw_data[1]
        if raw_int > 32767:
            raw_int -= 65536
        return raw_int

    def sample_structural_strain(self):
        """
        Reads MWCNT_S1 (CH0) and MWCNT_S2 (CH1) to capture the structural load delta.
        Converts raw 16-bit values into normalized microstrain metrics.
        """
        raw_ch0 = self._read_raw_adc_channel(self.ADC_ADDR_HULL, 0)
        
        # Convert 16-bit voltage value to physical resistance strain tracking
        voltage = (raw_ch0 / 32768.0) * 4.096
        
        # Piezoresistive gauge coefficient translation: 
        # Delta-R/R correlates linearly to structural physical strain index
        simulated_strain = max(0.0, (voltage / 3.3) * 0.005)
        return round(simulated_strain, 6)

    def sample_flux_leakage(self):
        """
        Reads FLUX_D1 (CH6) from the powdered iron flux guides.
        Converts ratiometric Hall-effect voltages into absolute Tesla (T).
        """
        raw_ch6 = self._read_raw_adc_channel(self.ADC_ADDR_FLUX, 2)
        voltage = (raw_ch6 / 32768.0) * 4.096
        
        # Hall sensor sensitivity map: 2.5V center bias = 0.0 Tesla
        tesla = abs(voltage - 2.5) * 0.1
        return round(tesla, 4)
