import ustruct as struct
from machine import Pin, SPI, I2C
from nrf24l01 import NRF24L01
from micropython import const
import sys

WIDTH = 128
HEIGHT= 32

LED = Pin(8, Pin.OUT)

spi = SPI(0, sck=Pin(6), mosi=Pin(7), miso=Pin(4))
cfg = {"spi": spi, "miso": 4, "mosi": 7, "sck": 6, "csn": 3, "ce": 5}

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

_RX_POLL_DELAY = const(1)

def oled_display(oled, message):
    oled.fill(0)
    for i, line in enumerate(message):
        oled.text(line, 0, i*8)
    oled.show()

def ping():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    nrf = NRF24L01(cfg["spi"], csn, ce)

    nrf.open_tx_pipe(pipes[0])
    nrf.open_rx_pipe(1, pipes[1])
    nrf.stop_listening()

    count = 0

    while True:
        print(count)
        try:
            LED.on()
            nrf.send(struct.pack("Q", count))
            LED.off()
        except OSError:
            pass

        # start listening again
        count += 1

        # # wait for response, with 5ms timeout
        # start_time = utime.ticks_ms()
        # timeout = False
        # while not nrf.any() and not timeout:
        #     if utime.ticks_diff(utime.ticks_ms(), start_time) > 5:
        #         timeout = True

        # if timeout:
        #     num_failures += 1
        # else:
        #     num_successes += 1

ping()