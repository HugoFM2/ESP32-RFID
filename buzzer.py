from machine import Pin, PWM

import uasyncio


class Buzzer():
    def __init__(self,pin,enable=True):
        self._pin = Pin(pin)
        self._enable = enable

    async def somCerto(self,duration=200,freq=880,duty=512):
        if self._enable:
            beeper = PWM(self._pin, freq=freq, duty=duty)
            await uasyncio.sleep_ms(duration)
            beeper.deinit()

    async def somErrado(self,duration=200,freq=440,duty=512):
        if self._enable:
            beeper = PWM(self._pin, freq=freq, duty=duty)
            await uasyncio.sleep_ms(duration)
            beeper.deinit()

