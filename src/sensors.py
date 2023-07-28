from micropython import const
import ustruct

# LSM6DSM Constants

FREQ_26 = const(0x02)
FREQ_208 = const(0x05)
FREQ_416 = const(0x06)
FREQ_833 = const(0x07)

ACEL_RANGE_2G = const(0x00)
ACEL_RANGE_4G = const(0x02)
ACEL_RANGE_8G = const(0x03)
ACEL_RANGE_16G = const(0x01)

GYRO_RANGE_125 = const(0x01)
GYRO_RANGE_250 = const(0x00)
GYRO_RANGE_500 = const(0x02)
GYRO_RANGE_1000 = const(0x04)
GYRO_RANGE_2000 = const(0x06)

# LSM6DSM Registers

STATUS_REG = const(0x1e) # 0,0,0,0,0, New Temp, New Gyro, New Accel
OUT_TEMP = const(0x20) # 2 words, 16 bit signed
OUTX_G = const(0x22) # 2 words, 16 bit signed
OUTY_G = const(0x24) # 2 words, 16 bit signed
OUTZ_G = const(0x26) # 2 words, 16 bit signed
OUTX_XL = const(0x28) # 2 words, 16 bit signed
OUTY_XL = const(0x2a) # 2 words, 16 bit signed
OUTZ_XL = const(0x2c) # 2 words, 16 bit signed

#LPS22DF Constants

LPS_OFF = const(0x00)
LPS_FREQ_25 = const(0x04)
LPS_FREQ_50 = const(0x05)
LPS_FREQ_75 = const(0x06)
LPS_FREQ_100 = const(0x07)
LPS_FREQ_200 = const(0x08)

#Note that if taking single shot samples (Bit in CTRL_REG2) at 4x oversampling the max ODR is 500Hz

LPS_AVG_4 = const(0x00)     
LPS_AVG_8 = const(0x01)
LPS_AVG_16 = const(0x02)
LPS_AVG_32 = const(0x03)    #Max ODR is 200Hz   (Pressure noise 1.64)
LPS_AVG_64 = const(0x04)    #Max ODR is 100Hz
LPS_AVG_128 = const(0x05)   #Max ODR is 75Hz
LPS_AVG_512 = const(0x06)   #Max ODR is 25Hz


class LSM6DSM:
    def __init__(self, i2c, addr=0x6a):
        self.i2c = i2c
        self.addr = addr
        self.gyro_correction = 0.0175        #For 500dps range
        self.xl_correction = 0.488         #For 16g range
        self.buf12 = bytearray(12)
        self.buf6 = bytearray(6)

        if self.i2c.readfrom_mem(self.addr, 0x0f, 1) != b'\x6a':
            raise OSError("LSM6DSM not found on I2C bus")
        
        self._init()

    def _init(self):
        self.write_reg(0x0a, b'\x00')                                    # FIFO_CTRL5 -> Disables FIFO
        #self.write_reg(0x12, b'\x00')                                    # CTRL3_C -> Sets the interrupts to push-pull and active high, also could reset or change LSB to MSB
        self.write_reg(0x13, b'\x00')                                    # CTRL4_C -> Could disable i2c
        self.write_reg(0x14, b'\x00')                                    # CTRL5_C -> Self tests
        self.write_reg(0x15, b'\x00')                                    # CTRL6_C -> High performance accelerometer enabled and gyro LPF bandwidth
        self.write_reg(0x16, b'\x00')                                    # CTRL7_G -> Gyro high performance mode enabled and gyro HPF off
        self.write_reg(0x17, b'\x00')                                    # CTRL8_XL -> Accelerometer filter settings
        self.write_reg(0x18, b'\x00')                                    # CTRL9_XL -> Digital enable wierd stuff, 0x00 isn't default
        self.write_reg(0x19, b'\x00')                                    # CTRL10_C -> Extended functionality
        self.set_refresh(26)                                             # Sets the refresh rate to 26Hz

    def set_refresh(self, freq):
        if freq == 26:
            set_freq = FREQ_26
        elif freq == 416:
            set_freq = FREQ_416
        elif freq == 833:
            set_freq = FREQ_833
        else:
            set_freq = FREQ_208
        
        self.write_reg(0x10, ((set_freq << 4) | (ACEL_RANGE_16G << 2)))   # CTRL1_XL -> Sets the accelerometer to 26Hz and range to 16G
        self.write_reg(0x11, ((set_freq << 4) | (GYRO_RANGE_500 << 1)))   # CTRL2_G -> Sets the gyroscope to 26Hz and range to 500dps
        

    def read_human(self):
        is_new = self.i2c.readfrom_mem(self.addr, STATUS_REG, 1)[0]
        is_new = (is_new) & 0x01 == 0x01

        if is_new:
            self.i2c.readfrom_mem_into(self.addr, OUTX_XL, self.buf6)
            accel = bytes([self.buf6[1], self.buf6[0], self.buf6[3], self.buf6[2], self.buf6[5], self.buf6[4]])
            ax, ay, az = ustruct.unpack(">hhh", accel)
        
            self.i2c.readfrom_mem_into(self.addr, OUTX_G, self.buf6)
            gyro = bytes([self.buf6[1], self.buf6[0], self.buf6[3], self.buf6[2], self.buf6[5], self.buf6[4]])
            gx, gy, gz = ustruct.unpack(">hhh", gyro)
        else:
            raise RuntimeError("No new data available")
        return (ax, ay, az, gx, gy, gz)
    
    @micropython.viper
    def read_hs(self):
        self.i2c.readfrom_mem_into(self.addr, OUTX_G, self.buf12)
        return self.buf12



    def write_reg(self, reg, data):
        if isinstance(data, int):  # Convert single integer to bytes
            data = bytes([data])
        self.i2c.writeto_mem(self.addr, reg, data)




class LPS22DF:
    def __init__(self, i2c, addr=0x5c):
        self.i2c = i2c
        self.addr = addr
        self.buf5 = bytearray(5)
        self.buf3 = bytearray(3)
        self.buf2 = bytearray(2)

        if self.i2c.readfrom_mem(self.addr, 0x0f, 1) != b'\xb4':
            raise OSError("LPS22DF not found on I2C bus")

        self._init()
    
    def _init(self):
        self.set_refresh(20)                                                          # Sets the refresh rate to 20Hz
        self.write_reg(0x11, 0x00)                                   # CTRL_REG2 -> Bit 0 for one shot, bit 4 enables low pass filter

    def set_refresh(self, freq):
        if freq == 25:
            set_freq = LPS_FREQ_25
        elif freq == 50:
            set_freq = LPS_FREQ_50
        elif freq == 75:
            set_freq = LPS_FREQ_75
        elif freq == 100:
            set_freq = LPS_FREQ_100
        elif freq == 200:
            set_freq = LPS_FREQ_200
        else:
            set_freq = LPS_FREQ_200
        
        self.write_reg(0x10, (set_freq << 3) | LPS_AVG_32)           # CTRL_REG1 -> Sets the refresh rate and oversampling to 32x

    def read_human(self):
        status = self.i2c.readfrom_mem(self.addr, 0x27, 1)[0]
        is_new_pres = (status & 0x01) == 0x01
        is_new_temp = ((status >> 1) & 0x01) == 0x01

        if is_new_pres:
            pres = self.i2c.readfrom_mem_into(self.addr, 0x28, self.buf3)
            pres = bytes([0, self.buf3[2], self.buf3[1], self.buf3[0]])
            p = ustruct.unpack(">i", pres)[0]
            temp = self.i2c.readfrom_mem_into(self.addr, 0x2b, self.buf2)
            temp = bytes([self.buf2[1], self.buf2[0]])
            t = ustruct.unpack(">h", temp)[0] / 100
        else:
            raise RuntimeError("No new data available")

        return (p, t)
    
    @micropython.viper
    def read_hs(self):
        self.i2c.readfrom_mem_into(self.addr, 0x28, self.buf5)
        return self.buf5

    def write_reg(self, reg, data):
        if isinstance(data, int):  # Convert single integer to bytes
            data = bytes([data])
        self.i2c.writeto_mem(self.addr, reg, data)

        


