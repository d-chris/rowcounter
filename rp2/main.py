from utime import sleep_ms, ticks_ms
from inputpin import InputPin_ePaperTouch
from machine import Pin, I2C

class ICNT_Development():
    def __init__(self):
        self.Touch = 0
        self.TouchGestureid = 0
        self.TouchCount = 0
        
        self.TouchEvenid = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]
    

class ICNT86():
    def __init__(self, i2c, address=0x48, reset=16, interrupt=17):
        if reset != None:
            self.TRST = Pin(reset, Pin.OUT, value=1)
        if interrupt != None:
            self.INT = Pin(interrupt, Pin.IN)
        
        self.i2c = i2c
        self.address = address

        self.dev = ICNT_Development()
        self.old = ICNT_Development()

        self.ICNT_Init()

    def _delay_ms(self, ms):
        sleep_ms(ms)

    def _i2c_writebyte(self, reg, value):
        wbuf = [(reg>>8)&0xff, reg&0xff, value]
        self.i2c.writeto(self.address, bytearray(wbuf))

    def _i2c_write(self, reg):
        wbuf = [(reg>>8)&0xff, reg&0xff]
        self.i2c.writeto(self.address, bytearray(wbuf))

    def _i2c_readbyte(self, reg, len):
        self._i2c_write(reg)
        rbuf = bytearray(len)
        self.i2c.readfrom_into(self.address, rbuf)
        return rbuf

    def ICNT_Reset(self):
        self.TRST.value(0)
        self._delay_ms(100)
        self.TRST.value(1)
        self._delay_ms(100)

    def ICNT_Write(self, Reg, Data):
        self._i2c_writebyte(Reg, Data)

    def ICNT_Read(self, Reg, len):
        return self._i2c_readbyte(Reg, len)
        
    def ICNT_ReadVersion(self):
        buf = self.ICNT_Read(0x000a, 4)
        return buf

    def ICNT_Init(self):
        self.ICNT_Reset()
        return self.ICNT_ReadVersion()

    def ICNT_Scan(self):
        buf = []
        mask = 0x00
        
        if(self.INT.value() == 0):
            buf = self.ICNT_Read(0x1001, 1)
            
            if(buf[0] == 0x00):
                self.ICNT_Write(0x1001, mask)
                self._delay_ms(1)
                # print("buffers status is 0")
                return
            else:
                self.dev.TouchCount = buf[0]
                
                if(self.dev.TouchCount > 5 or self.dev.TouchCount < 1):
                    self.ICNT_Write(0x1001, mask)
                    self.dev.TouchCount = 0
                    # print("TouchCount number is wrong")
                    return
                    
                buf = self.ICNT_Read(0x1002, self.dev.TouchCount*7)
                self.ICNT_Write(0x1001, mask)
                
                self.old.X[0] = self.dev.X[0]
                self.old.Y[0] = self.dev.Y[0]
                self.old.P[0] = self.dev.P[0]
                self.old.TouchEvenid[0]=self.dev.TouchEvenid[0]
                
                for i in range(0, self.dev.TouchCount, 1):
                    self.dev.TouchEvenid[i] = buf[6 + 7*i] 
                    # ICNT_Dev.X[i] = ((buf[2 + 7*i] << 8) + buf[1 + 7*i])
                    # ICNT_Dev.Y[i] = ((buf[4 + 7*i] << 8) + buf[3 + 7*i])
                    self.dev.X[i] = 127 - ((buf[4 + 7*i] << 8) + buf[3 + 7*i])
                    self.dev.Y[i] = ((buf[2 + 7*i] << 8) + buf[1 + 7*i])
                    self.dev.P[i] = buf[5 + 7*i]

                #print(ticks_ms() ,self.dev.X[0], self.dev.Y[0], self.dev.P[0], self.dev.TouchEvenid[0])

                if self.dev.TouchEvenid[0] == 3 and self.old.TouchEvenid[0]==2:
                    print('fubar', self.dev.X[0], self.dev.Y[0])
                return
        return

def touch():
    print('testing')
    i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100_000)
    return ICNT86(i2c)

def loop():
    pass

def main():
    #keys = InputPin_ePaperTouch(verbose=True)

    tp = touch()

    while True:
        tp.ICNT_Scan()
        loop()


if __name__ == '__main__':
    
    main()