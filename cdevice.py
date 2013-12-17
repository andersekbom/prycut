#import d2xx
import time
from pyxxtea import raw_xxtea
from struct import pack

KEY0 = [0x272D6C37, 0x342A6173, 0x3663255B, 0x2B265A4D]
KEY1 = [0x7D316E22, 0x4A4A7133, 0x5A3C5C5F, 0x78613A61]
KEY2 = [0x47302A23, 0x5D31482F, 0x3B257A61, 0x3671382F]
KEY3 = [0x303F6863, 0x71646D30, 0x4769457B, 0x6D342569]
KEY4 = [0x45356650, 0x3A386D69, 0x575A7037, 0x335F357D]
KEY5 = [0x343A2148, 0x614F3925, 0x753F6953, 0x47463626]
KEY6 = [0x3F62626D, 0x7E555F44, 0x7E29425A, 0x52246268]
KEY7 = [0x47302A23, 0x342A6173, 0x4769457B, 0x335F357D]

class Cplotter:
    a = None
    timeout = 10.0
    
    def connect(self):
        d = d2xx.listDevices() # implicit d2xx.OPEN_BY_SERIAL_NUMBER
        if (len(d) == 0):
            # no devices found!
            return 0
        else:
            #open the first on the list
            self.a = d2xx.open(0)

            # set baud rate
            self.a.setBaudRate(200000)

            # set RX/TX timeouts
            self.a.setTimeouts(100,100)

            # set port to 8N1
            self.a.setDataCharacteristics(8, 0, 0)
            
    def disconnect(self):
        self.a.close()

    def mat_loaded(self):
        command = chr(4) + chr(0x14) + chr(0) + chr(0) + chr(0)
        self.write_command(command)
        reply = self.get_reply(5)

        if (len(reply) == 5 and reply[4] == chr(1)):
            return True
        else:
            return False

    def send_start(self):
        command = chr(4) + chr(0x21) + chr(0x0) + chr(0x0) + chr(0x0)
        return self.write_command(command)

    def send_stop(self):
        command = chr(4) + chr(0x22) + chr(0x0) + chr(0x0) + chr(0x0)
        return self.write_command(command)

    def send_move_pen_up(self, x, y):
        v = [ 12345, int(x), int(y) ]
        k = KEY2
        raw_xxtea(v, 3, k)
        command = pack('III', v[0], v[1], v[2])
        command = chr(13) + chr(0x40) + command
        self.write_command(command)
        reply = self.get_reply(5)
        
        return (len(reply) == 5)
    
    def send_move_pen_down(self, x, y):
        v = [ 12345, int(x), int(y) ]
        k = KEY3
        raw_xxtea(v, 3, k)
        command = pack('III', v[0], v[1], v[2])
        command = chr(13) + chr(0x40) + command
        self.write_command(command)

        reply = self.get_reply(5)
        
        return (len(reply) == 5)

    def write_command(self, command):
        # send a command 1 byte at a time
        for x in range(len(command)):
            self.a.write(command[x])
            
        return True

    def get_reply(self, num_bytes):
        #wait for specified number of bytes or timeout
        start = time.clock()
        while (time.clock() < (start + self.timeout)):
            if (self.a.getQueueStatus() >= num_bytes):
                break

        if (self.a.getQueueStatus() > 1):
            return self.a.read(self.a.getQueueStatus())
        else:
            return ''


