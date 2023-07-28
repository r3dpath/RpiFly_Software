import ustruct as struct
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from time import sleep_ms, ticks_ms

class Radio:
    # Function is either Rocket (0) or Reciever (1)
    def __init__(self, function, spi=0, sck=6, mosi=7, miso=4, cs=3, che=5):
        csn = Pin(cs, mode=Pin.OUT, value=1)
        ce = Pin(che, mode=Pin.OUT, value=0)
        self.nrf = NRF24L01(spi=SPI(spi, sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso)), cs=csn, ce=ce, channel=60, payload_size=21)
        self.pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
        
        if function == 0:
            self.nrf.open_tx_pipe(self.pipes[0])
            self.nrf.open_rx_pipe(1, self.pipes[1])
        elif function == 1:
            self.nrf.open_tx_pipe(self.pipes[1])
            self.nrf.open_rx_pipe(1, self.pipes[0])
        
        self.lasttrans = ticks_ms()

    def send(self, data, mode = 0):
        # Prepares and sends packet
        self.stop_listening()
        self.nrf.send(data)
        self.lasttrans = ticks_ms()
        
        # The mode gives the current operation, if zero will start listening again
        if mode == 1:
            self.start_listening()

    def send_nb(self, data):
        self.nrf.send_start(data)
        self.nrf.send_done(False)

    def recv(self):
        # If a packet is ready decodeds and returns all packets
        packets = []
        if self.nrf.any():
            while self.nrf.any():
                buf = self.nrf.recv()
                packets.append(buf)
        else:
            return [None]
        
        return packets
    
    def wait_recv(self):
        self.start_listening()
        sleep_ms(10)
        command = self.recv()
        self.stop_listening()
        return command


    def stop_listening(self):
        self.nrf.stop_listening()

    def start_listening(self):  
        self.nrf.start_listening()


