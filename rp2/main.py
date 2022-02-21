
from machine import Pin, Timer
from utime import ticks_ms, ticks_diff


class InputPin (Pin):
    def __init__(self, id, pull=Pin.PULL_UP, *args, **kwargs):
        super().__init__(id, Pin.IN, pull, *args)  # initialize Pin() as input
        self.name = kwargs.get('name', id)

        if pull == Pin.PULL_UP:  # set logic levels
            self.active_level = 0
        else:
            self.active_level = 1

        self._stable = -1  # set debounced value to unstable
        # time in ms to detect stable state
        self.stable_ms = kwargs.get('stable_ms', 100)

        self._sample = super().value()  # actual pin state
        self._sample_ms = ticks_ms()  # time when sample was taken

        self._timer = Timer()
        self._timer.init(
            period=kwargs.get('period', 20),
            mode=Timer.PERIODIC,
            callback=self._timer_callback
        )

        self._debug = kwargs.get('verbose', False)

        if self._debug:
            print(f"{self._sample_ms}ms - InputPin({self.name}) - initialized")

    def __del__(self):
        self._timer.deinit()
        super().__del__()

    def value(self) -> int:
        ''' 
            get debounced logic level of the pin

                - pin level must be stable for at least ``InputPin.stable_ms``
                - returns ``-1`` when a stable state is not detected
                - ``0`` stable with a low logic level
                - ``1`` stable with a high logic level 

        '''
        return self._stable

    def active(self) -> bool:
        '''
            check if the button is pressed or signal active

                - when pull-up is enabled signal is active on ``InputPin.value() == 0``
                - with a pull-down the signal is active when ``InputPin.value() == 1``

        '''
        return self._stable == self.active_level  # active

    def _timer_callback(self, timer):
        '''
            periodic callback from timer to check for if logic level of pin changed
        '''
        sample = super().value()  # get current pin-state
        ticks = ticks_ms()  # time when sample was taken

        if sample == self._sample:  # state has not changed
            if sample != self._stable:  # state is not stable yet
                if ticks_diff(ticks, self._sample_ms) > self.stable_ms:
                    self._stable = sample  # pin state was stable for X milliseconds
                    if self._debug:
                        print(
                            f"{ticks}ms - InputPin({self.name}) = {self.active()}")
        else:
            self._sample = sample  # update state due change
            self._sample_ms = ticks


def InputPin_ePaperTouch(**kwargs):
    '''
        initialize key buttons of waveshare captouch epaper 2.9
    '''

    pins = dict()

    key = 'KEY0'
    pins[key] = InputPin(2, Pin.PULL_UP, name=key, **kwargs)

    key = 'KEY1'
    pins[key] = InputPin(3, Pin.PULL_UP, name=key, **kwargs)

    key = 'KEY2'
    pins[key] = InputPin(15, Pin.PULL_UP, name=key, **kwargs)

    if kwargs.get('verbose', False) == True:
        print(pins)

    return pins


def loop():
    pass


if __name__ == '__main__':

    keys = InputPin_ePaperTouch(verbose=True)


    while True:
        loop()
