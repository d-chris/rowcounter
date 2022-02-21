
from machine import Pin, Timer
from utime import sleep_ms


class InputPin (Pin):
    def __init__(self, *args):
        super().__init__(*args)
        self.state = -1
        self.count = 0
        self.tim = Timer()
        self.tim.init(freq=20, mode=Timer.PERIODIC, callback=self.__timer)

    def value(self) -> int:
        return self.state

    def __timer(self, timer):
        sample = super().value()
        if sample != self.state:
            self.state = sample
            self.count = 0
        else:
            self.count += 1
            if self.count >= 3:
                self.stable = self.state



def loop():
    pass


if __name__ == '__main__':

    p25 = InputPin(25, Pin.OUT)
    # p25.value(0)

    while True:
        loop()
