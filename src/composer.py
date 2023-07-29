import sensors
from machine import Pin, I2C, Timer, WDT, PWM
from time import ticks_us, ticks_ms, ticks_diff, sleep_ms
import ubinascii
from micropython import const
from sys import exit

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=1000000)
imu = sensors.LSM6DSM(i2c)
pres = sensors.LPS22DF(i2c)

STATE_POWERUP = const(0)
STATE_LOWPOWER = const(1)
STATE_LAUNCH = const(2)
STATE_LANDED = const(3)
STATE_POFF = const(4)

LED1 = Pin(8, Pin.OUT)
LED2 = Pin(9, Pin.OUT)
LED3 = Pin(10, Pin.OUT)
BUZZER = PWM(Pin(11))
BUZZER.freq(500)

LAUNCH_DELAY = 30000
RECORD_TIME = 30000
LANDED_DELAY = 30000
INIT_TIME = ticks_ms()

tick_timer = False

get_pres = True

#wdt = WDT(timeout=3000)

class fwrite:
    def __init__(self) -> None:
        self.file_imu = "log_imu.txt"
        self.file_pres = "log_pres.txt"
        self.log_imu = open(self.file_imu, "a")
        self.log_pres = open(self.file_pres, "a")

    @micropython.viper
    def write_imu(self, data):
        self.log_imu.write(ubinascii.b2a_base64(data))

    @micropython.viper
    def write_pres(self, data):
        self.log_pres.write(ubinascii.b2a_base64(data))

    def close(self) -> None:
        self.log_imu.close()
        self.log_pres.close()

LOG = fwrite()

class State:
    def __init__(self) -> None:
        LED1.off()
        LED2.off()
        LED3.off()
        self.state_file = "state"
        self.state = STATE_POWERUP
        self.launch_time = 0
        self.landed_time = 0
        self.timer = Timer()
        self.log = LOG
        try:
            with open(self.state_file, 'r') as f:
                state = int(f.read())
        except:
            state = STATE_LOWPOWER
        if state == STATE_LAUNCH:
            self.setstate_launch()
        elif state == STATE_POFF:
            tones(3)
            with open(self.state_file, 'w') as f:
                f.write(str(STATE_LOWPOWER)) 
        else:
            self.setstate_lowpower()
        tones(0)

    @micropython.native()
    def tick(self):
        #wdt.feed()
        if self.state == STATE_LAUNCH:
            #try:
            if ticks_diff(ticks_ms(), self.launch_time) > RECORD_TIME:
                self.setstate_landed()
                return
            run_launch()
            #except:
            #    tones(3)
            
        elif self.state == STATE_LOWPOWER:
            LED3.on()
            tones(1)
            try:
                time = ticks_ms().to_bytes(3, 'big')
                imu_read = imu.read_hs()
                pres_read = pres.read_hs()
                self.log.write_imu(time + imu_read)
                self.log.write_pres(time + pres_read)
            except:
                tones(3)
            LED3.off()
            if ticks_diff(ticks_ms(), INIT_TIME) > LAUNCH_DELAY:
                self.setstate_launch()

        elif self.state == STATE_LANDED:
            LED3.on()
            tones(1)
            try:
                time = ticks_ms().to_bytes(3, 'big')
                imu_read = imu.read_hs()
                pres_read = pres.read_hs()
                self.log.write_imu(time + imu_read)
                self.log.write_pres(time + pres_read)
            except:
                tones(3)
            LED3.off()
            if ticks_diff(ticks_ms(), self.landed_time) > LANDED_DELAY:
                    self.setstate_poff()

    def setstate_lowpower(self):
        LED1.on()
        LED2.off()
        LED3.off()
        self.state = STATE_LOWPOWER
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_LOWPOWER))
        imu.set_refresh(26)
        pres.set_refresh(20)
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_callback)

    def setstate_launch(self):
        LED1.off()
        LED2.on()
        LED3.off()
        self.state = STATE_LAUNCH
        self.launch_time = ticks_ms()
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_LAUNCH))
        tones(2)
        imu.set_refresh(833)
        pres.set_refresh(200)
        self.timer.init(freq=400, mode=Timer.PERIODIC, callback=timer_callback)

    def setstate_landed(self):
        LED1.on()
        LED2.on()
        LED3.off()
        self.landed_time = ticks_ms()
        self.state = STATE_LANDED
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_LANDED))
        imu.set_refresh(26)
        pres.set_refresh(20)
        self.timer.init(period=2000, mode=Timer.PERIODIC, callback=timer_callback)

    def setstate_poff(self):
        LED1.off()
        LED2.off()
        LED3.off()
        self.state = STATE_POFF
        self.log.close()
        self.timer.deinit()
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_POFF))


def tones(tone):
    if tone == 0:
        BUZZER.freq(450)
        BUZZER.duty_u16(10000)
        sleep_ms(450)
        BUZZER.freq(700)
        sleep_ms(250)
        BUZZER.freq(1000)
        sleep_ms(150)
        BUZZER.duty_u16(0)
    if tone == 1:
        BUZZER.freq(800)
        BUZZER.duty_u16(10000)
        sleep_ms(20)
        BUZZER.duty_u16(0)
    if tone == 2:
        BUZZER.freq(2000)
        BUZZER.duty_u16(10000)
        sleep_ms(2000)
        BUZZER.duty_u16(0)
    if tone == 3:
        BUZZER.freq(1500)
        BUZZER.duty_u16(10000)
        sleep_ms(5)
        BUZZER.duty_u16(0)

@micropython.viper
def run_launch():
    global get_pres
    LED3.on()
    time = ticks_ms().to_bytes(3, 'big')
    imu_read = imu.read_hs()
    LOG.write_imu(time + imu_read)
    if get_pres:
        pres_read = pres.read_hs()
        LOG.write_pres(time + pres_read)
    get_pres = not get_pres
    LED3.off()
    
def timer_callback(timer):
    global tick_timer
    tick_timer = True
    

def run():
    global tick_timer
    state = State()
    while True:
        if tick_timer:
            state.tick()
            tick_timer = False
    
if __name__ == "__main__":
    run()
    



