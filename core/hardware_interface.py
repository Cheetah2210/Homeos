import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HomeosHardwareInterface")

try:
    from smbus2 import SMBus
except ImportError:
    SMBus = None
    logger.warning("Physical smbus2 library not detected locally. Hardware-in-the-Loop Mock simulation mode forced.")

class HomeosHardwareInterface:
    def __init__(self, bus_id=1):
        """
        Initializes the Local I2C Sensor Fusion Interface Layer.
        Maps hardware device addresses and internal analog-to-digital converter pointers.
        """
        self.bus_id = bus_id
        self.is_mock = SMBus is None
        
        # Hardware Target Slave I2C Addresses
        self.ADC_ADDR_HULL = 0x48
        self.ADC_ADDR_FLUX = 0x4B
        
        # Texas Instruments ADS1115 Standard Register Pointers
        self.POINTER_CONVERSION = 0x00
        self.POINTER_CONFIG = 0x01
        self.ADC_CONFIG_BASE = 0x8183 # Continuous conversion, +/-4.096V range, 128 SPS

    def _read_raw_adc_channel(self, i2c_addr, channel):
        """
        Executes raw bitwise register reading from the local hardware bus.
        """
        if self.is_mock:
            # Return nominal mid-scale reference registry integer (approx 2.5V center point)
            return 16000 
            
        if not (0 <= channel <= 3):
            raise ValueError("Invalid ADC register channel selection index requested.")

        # Construct configuration byte word with proper multiplexer channel mask bits
        mux_mask = (0x4 + channel) << 12
        config_val = (self.ADC_CONFIG_BASE & 0x8FFF) | mux_mask
        config_bytes = [(config_val >> 8) & 0xFF, config_val & 0xFF]
        
        try:
            with SMBus(self.bus_id) as bus:
                # Write to the device pointer register specifying configuration intentions
                bus.write_i2c_block_data(i2c_addr, self.POINTER_CONFIG, config_bytes)
                time.sleep(0.01) # Allow internal ADC cycle settling time delay
                
                # Retrieve the raw 16-bit conversion register block data
                raw_data = bus.read_i2c_block_data(i2c_addr, self.POINTER_CONVERSION, 2)
                
            # Reconstruct two 8-bit registers into a signed 16-bit integer output
            raw_int = (raw_data[0] << 8) | raw_data[1]
            if raw_int > 32767:
                raw_int -= 65536
            return raw_int
            
        except Exception as e:
            logger.error(f"Hardware bus fault encountered on I2C address {hex(i2c_addr)}: {str(e)}")
            return 0

    def sample_structural_strain(self):
        """
        Polls the hull sensor grid and normalizes the voltage register directly into macroscopic strain values.
        """
        raw_val = self._read_raw_adc_channel(self.ADC_ADDR_HULL, 0)
        voltage = (raw_val / 32768.0) * 4.096
        # Map 0-3.3V input range linearly across the safe macrostrain range (0.0 to 0.005)
        return round(max(0.0, (voltage / 3.3) * 0.005), 6)

    def sample_flux_leakage(self):
        """
        Polls the ratiometric Hall-effect array and maps flux deltas in Tesla.
        """
        raw_val = self._read_raw_adc_channel(self.ADC_ADDR_FLUX, 2)
        voltage = (raw_val / 32768.0) * 4.096
        # Standard conversion matching a 2.5V zero-field center point calibration line
        return round(abs(voltage - 2.5) * 0.1, 4)
