import sensors
from machine import Pin, I2C, Timer, WDT, PWM
from time import ticks_us, ticks_ms, ticks_diff, sleep_ms
import ubinascii
import radio
from micropython import const

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=1000000)
imu = sensors.LSM6DSM(i2c)
pres = sensors.LPS22DF(i2c)
nrf = radio.Radio(0)

STATE_POWERUP = const(0)
STATE_LOWPOWER = const(1)
STATE_LAUNCH = const(2)
STATE_LANDED = const(3)
STATE_POFF = const(4)

COM_RECV_GOOD = const(0x0)
COM_PING = const(0x1)
COM_LAUNCH = const(0x2)
COM_POFF = const(0xFF)

LED1 = Pin(8, Pin.OUT)
LED2 = Pin(9, Pin.OUT)
LED3 = Pin(10, Pin.OUT)
BUZZER = PWM(Pin(11))
BUZZER.freq(500)

tick_timer = False

try:
    with open("state", 'r') as f:
        if (int(f.read()) == STATE_POFF):
            exit()
except:
    pass
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
        self.force_launch = False
        self.timer = Timer()
        self.recvfail = 0
        self.log = LOG
        with open(self.state_file, 'r') as f:
            try:
                state = int(f.read())
            except:
                state = STATE_LOWPOWER
        if state == STATE_LAUNCH or self.force_launch:
            self.setstate_launch()
        elif state == STATE_POFF:
            exit()
        else:
            self.setstate_lowpower()
        tones(0)



    def tick(self):
        #wdt.feed()
        print('Tick')
        print(self.state)
        if self.state == STATE_LAUNCH:
            if ticks_diff(ticks_ms(), self.launch_time) > 120000:
                if not self.force_launch:
                    self.setstate_landed()
                    return
            run_launch(self.state, nrf.lasttrans)
            
        elif self.state == STATE_LOWPOWER:
            print('LP')
            tones(1)
            LED3.on()
            time = ticks_ms().to_bytes(3, 'big')
            imu_read = imu.read_hs()
            pres_read = pres.read_hs()
            self.log.write_imu(time + imu_read)
            self.log.write_pres(time + pres_read)
            LED3.off()
            try:
                nrf.send(bytes([self.state])+time+imu_read+pres_read)
                self.recvfail = 0
            except:
                self.recvfail += 1
                print("RECV FAIL")
            commands = nrf.wait_recv()
            print(commands)
            if commands[0] == None:
                tones(3)
                print("Failed to revieve reply")
            else:
                self.recvfail = 0
                instructions = set()
                for command in commands:
                    instructions.add(command)
                if COM_LAUNCH in instructions:
                    self.setstate_launch()
                    return
                elif COM_PING in instructions:
                    nrf.send(bytes(1))
                elif COM_POFF in instructions:
                    self.setstate_poff()
#             except:
#                 print("DECODE FAIL")
#                 pass
                    
            #except:
            #   self.recvfail += 1
            #    print("RECV FAIL")

            if self.recvfail >= 30:
                self.setstate_launch()
                self.force_launch = True

        elif self.state == STATE_LANDED:
            try:
                time = ticks_ms().to_bytes(3, 'big')
                imu_read = imu.read_hs()
                pres_read = pres.read_hs()
                self.log.write_imu(time + imu_read)
                self.log.write_pres(time + pres_read)

                nrf.send(self.state+time+imu_read+pres_read)
            except:
                pass

    def setstate_lowpower(self):
        LED1.on()
        LED2.off()
        LED3.off()
        self.state = STATE_LOWPOWER
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_LOWPOWER))
        imu.set_refresh(26)
        pres.set_refresh(20)
        self.timer.init(period=2000, mode=Timer.PERIODIC, callback=timer_callback)

    def setstate_launch(self):
        LED1.off()
        LED2.on()
        LED3.off()
        self.state = STATE_LAUNCH
        with open(self.state_file, 'w') as f:
            f.write(str(STATE_LAUNCH))
        tones(2)
        imu.set_refresh(833)
        pres.set_refresh(200)
        self.timer.init(freq=400, mode=Timer.PERIODIC, callback=timer_callback)

    def setstate_landed(self):
        LED1.off()
        LED2.off()
        LED3.on()
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
def run_launch(state, last: int):
    LED3.on()
    time = ticks_ms().to_bytes(3, 'big')
    imu_read = imu.read_hs()
    pres_read = pres.read_hs()
    LOG.write_imu(time + imu_read)
    LOG.write_pres(time + pres_read)
    times = int(ticks_ms()) - last
    if times > 2000:
        try:
            nrf.send_nb(state+time+imu_read+pres_read)
        except:
            pass
    LED3.off()
    
def timer_callback(timer):
    global tick_timer
    tick_timer = True
    
if __name__ == "__main__":
    state = State()
    while True:
        if tick_timer:
            state.tick()
            tick_timer = False
    



