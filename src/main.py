import composer
from machine import Pin
pT = Pin(13, Pin.OUT)
pR = Pin(14, Pin.IN)
pT.on()
if not pR.value():
    pT.off()
    composer.run()
