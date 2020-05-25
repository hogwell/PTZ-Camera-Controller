'''
    Arducam programable zoom-lens control component.

    Copyright (c) 2019-4 Arducam <http://www.arducam.com>.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
    OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import time
class Focuser:
    bus = None
    CHIP_I2C_ADDR = 0x0C
    BUSY_REG_ADDR = 0x04

    starting_point = [
        11000, 10000, 18800,
        14800, 12200, 9700,
        7500, 6000, 4900,
        3900, 3200, 2500,
        2200, 1900, 1700,
        1500, 1500, 1500, 1500
    ]
    end_point = [
        19500, 19500, 19300,
        15800, 12800, 10500,
        8400, 7000, 5400,
        4400, 4000, 3500,
        2500, 2200, 2100,
        2000, 2000, 2000, 2000
    ]
    def __init__(self,bus):
        try:
            import smbus
            self.bus = smbus.SMBus(bus)
        except:
            sys.exit(0)

    def read(self,chip_addr,reg_addr):
        value = self.bus.read_word_data(chip_addr,reg_addr)
        value = ((value & 0x00FF)<< 8) | ((value & 0xFF00) >> 8)
        return value
    def write(self,chip_addr,reg_addr,value):
        if value < 0:
            value = 0
        value = ((value & 0x00FF)<< 8) | ((value & 0xFF00) >> 8)
        return self.bus.write_word_data(chip_addr,reg_addr,value)
    def isBusy(self):
        return self.read(self.CHIP_I2C_ADDR,self.BUSY_REG_ADDR) != 0
    def waitingForFree(self):
        count = 0
        begin = time.time()
        while self.isBusy() and count < (5 / 0.01):
            count += 1
            time.sleep(0.01)
        # if count >= (5 / 0.01):
        #     print "wait timeout."
        # elif count != 0:
        #     print "wait time = %lf"%(time.time() - begin)

    OPT_BASE    = 0x1000
    OPT_FOCUS   = OPT_BASE | 0x01
    OPT_ZOOM    = OPT_BASE | 0x02
    OPT_MOTOR_X = OPT_BASE | 0x03
    OPT_MOTOR_Y = OPT_BASE | 0x04
    OPT_IRCUT   = OPT_BASE | 0x05
    opts = {
        OPT_FOCUS : {
            "REG_ADDR" : 0x01,
#            "MAX_VALUE": 18000,
            "MAX_VALUE": 20000,
            "RESET_ADDR": 0x01 + 0x0A,
            "MIN_VALUE": 1500,
        },
        OPT_ZOOM  : {
            "REG_ADDR" : 0x00,
            "MAX_VALUE": 18000,
            "RESET_ADDR": 0x00 + 0x0A,
            "MIN_VALUE": 1700,
        },
        OPT_MOTOR_X : {
            "REG_ADDR" : 0x05,
            "MAX_VALUE": 180,
            "RESET_ADDR": None,
            "MIN_VALUE": 0,
        },
        OPT_MOTOR_Y : {
            "REG_ADDR" : 0x06,
            "MAX_VALUE": 180,
            "RESET_ADDR": None,
            "MIN_VALUE": 0,
        },
        OPT_IRCUT : {
            "REG_ADDR" : 0x0C, 
            "MAX_VALUE": 0x01,   #0x0001 open, 0x0000 close
            "RESET_ADDR": None,
            "MIN_VALUE": 0,
        }
    }
    def reset(self,opt,flag = 1):
        self.waitingForFree()
        info = self.opts[opt]
        if info == None or info["RESET_ADDR"] == None:
            return
        self.write(self.CHIP_I2C_ADDR,info["RESET_ADDR"],0x0000)
        if flag & 0x01 != 0:
            self.waitingForFree()

    def get(self,opt,flag = 0):
        self.waitingForFree()
        info = self.opts[opt]
        return self.read(self.CHIP_I2C_ADDR,info["REG_ADDR"])

    def set(self,opt,value,flag = 1):
#	print("Focuser.set(%d,%d,%d)" % (opt,value,flag))
        self.waitingForFree()
        info = self.opts[opt]
#        print "maxvalue="+str(info["MAX_VALUE"])
        if value > info["MAX_VALUE"]:
            value = info["MAX_VALUE"]
        if value < info["MIN_VALUE"]:
            value = info["MIN_VALUE"]
        self.write(self.CHIP_I2C_ADDR,info["REG_ADDR"],value)
        if flag & 0x01 != 0:
            self.waitingForFree()

pass 


def test():
    focuser = Focuser(1)
    focuser.reset(Focuser.OPT_FOCUS)
    while focuser.get(Focuser.OPT_FOCUS) < 18000:
        focuser.set(Focuser.OPT_FOCUS,focuser.get(Focuser.OPT_FOCUS) + 50)
    focuser.set(Focuser.OPT_FOCUS,0)
    focuser.set(Focuser.OPT_FOCUS,10000)
pass

if __name__ == "__main__":
    test()
