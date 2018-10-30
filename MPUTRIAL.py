import time
from threading import Thread
import smbus


class MPU9255(Thread):
    PWR_M = 0x6B  #
    DIV = 0x19  #
    CONFIG = 0x1A  #
    GYRO_CONFIG = 0x1B  #
    ACCEL_CONFIG = 0x1C  #
    INT_EN = 0x38  #
    ACCEL_X = 0x3B  #
    ACCEL_Y = 0x3D  #
    ACCEL_Z = 0x3F  #
    GYRO_X = 0x43  #
    GYRO_Y = 0x45  #
    GYRO_Z = 0x47  #
    TEMP = 0x41  #

    MAG_X = 0x03
    MAG_Y = 0x05
    MAG_Z = 0x07
    ST_1 = 0x02
    ST_2 = 0x09
    MAG_ADDRESS = 0x0C

    bus = smbus.SMBus(1)
    Device_Address = 0x68  # device address

    AxCal = -2520
    AyCal = 4395
    AzCal = 1577
    GxCal = 130
    GyCal = 189
    GzCal = -17
    MxCal = 0
    MyCal = 0
    MzCal = 0

    dt = .02


    def __init__(self):
        # pass
        super(MPU9255, self).__init__()
        self.gyroAngle = 0
        self.magAngle = 0
        self.accelAngle = 0
        self.running = True
        self.data = []
        self.initMPU()
        self.calibrate()
		
    def run(self):
        while self.running:
            self.data.append(self.getInfo())
            time.sleep(self.dt)



    def initMPU(self):
        self.bus.write_byte_data(self.Device_Address, self.DIV, 7)
        self.bus.write_byte_data(self.Device_Address, self.PWR_M, 1)
        self.bus.write_byte_data(self.Device_Address, self.CONFIG, 0)
        self.bus.write_byte_data(self.Device_Address, self.GYRO_CONFIG, 24)
        self.bus.write_byte_data(self.Device_Address, self.INT_EN, 1)
        self.bus.write_byte_data(self.Device_Address, 0x37, 0x22)
        self.bus.write_byte_data(self.Device_Address, 0x36, 0x01)
        self.bus.write_byte_data(self.MAG_ADDRESS, 0x0A, 0x00)
        time.sleep(.05)
        self.bus.write_byte_data(self.MAG_ADDRESS, 0x0A, 0x0F)
        time.sleep(.05)
        self.bus.write_byte_data(self.MAG_ADDRESS, 0x0A, 0x00)
        time.sleep(.05)
        self.bus.write_byte_data(self.MAG_ADDRESS, 0x0A, 0x06)
        time.sleep(1)

    def readMPU(self, addr, dev_add=Device_Address):
        high = self.bus.read_byte_data(dev_add, addr)
        low = self.bus.read_byte_data(dev_add, addr + 1)
        value = ((high << 8) | low)
        if (value > 32768):
            value = value - 65536
        return value

    def readMPUAddress(self, addr, dev_add=Device_Address):
        return self.bus.read_byte_data(dev_add, addr)

    def accel(self):
        global AxCal
        global AyCal
        global AzCal
        x = self.readMPU(self.ACCEL_X, self.Device_Address)
        y = self.readMPU(self.ACCEL_Y, self.Device_Address)
        z = self.readMPU(self.ACCEL_Z, self.Device_Address)

        Ax = (x / 16384.0 - AxCal)
        Ay = (y / 16384.0 - AyCal)
        Az = (z / 16384.0 - AzCal)

        # print "X="+str(Ax)
        return {"AX": Ax, "AY": Ay, "AZ": Az}

    def gyro(self):
        global GxCal
        global GyCal
        global GzCal
        x = self.readMPU(self.GYRO_X, self.Device_Address)
        y = self.readMPU(self.GYRO_Y, self.Device_Address)
        z = self.readMPU(self.GYRO_Z, self.Device_Address)
        Gx = x / 131.0 - GxCal
        Gy = y / 131.0 - GyCal
        Gz = z / 131.0 - GzCal
        # print "X="+str(Gx)
        return {"GX": Gx, "GY": Gy, "GZ": Gz}

    def mag(self):
        global MxCal
        global MyCal
        global MzCal

        self.readMPUAddress(self.ST_1, self.MAG_ADDRESS)
        x = self.readMPU(self.MAG_X, self.MAG_ADDRESS)
        y = self.readMPU(self.MAG_Y, self.MAG_ADDRESS)
        z = self.readMPU(self.MAG_Z, self.MAG_ADDRESS)
        self.readMPUAddress(self.ST_2, self.MAG_ADDRESS)

        # calibration
        Mx = x
        My = y
        Mz = z
        return {"MX": Mx, "MY": My, "MZ": Mz}

    def temp(self):
        tempRow = self.readMPU(self.TEMP, self.Device_Address)
        tempC = (tempRow / 340.0) + 36.53
        tempC = "%.2f" % tempC
        return {"TEMP": tempC}

    def calibrate(self):
        global AxCal
        global AyCal
        global AzCal
        x = 0
        y = 0
        z = 0
        ra = 100
        for i in range(ra):
            x = x + self.readMPU(self.ACCEL_X, self.Device_Address)
            y = y + self.readMPU(self.ACCEL_Y, self.Device_Address)
            z = z + self.readMPU(self.ACCEL_Z, self.Device_Address)
        x = x / ra
        y = y / ra
        z = z / ra
        AxCal = x / 16384.0
        AyCal = y / 16384.0
        AzCal = z / 16384.0

        print
        AxCal
        print
        AyCal
        print
        AzCal

        global GxCal
        global GyCal
        global GzCal
        x = 0
        y = 0
        z = 0
        for i in range(ra):
            x = x + self.readMPU(self.GYRO_X, self.Device_Address)
            y = y + self.readMPU(self.GYRO_Y, self.Device_Address)
            z = z + self.readMPU(self.GYRO_Z, self.Device_Address)
        x = x / ra
        y = y / ra
        z = z / ra
        GxCal = x / 131.0
        GyCal = y / 131.0
        GzCal = z / 131.0
        print
        GxCal
        print
        GyCal
        print
        GzCal

    # calibrate magnetometer

    def getData(self):
        li = self.data.copy()
        self.data = []
        return li

    def getInfo(self):
        imu = IMU()
        print(self.temp()["TEMP"])
        imu.setTemp(self.temp()["TEMP"])
        imu.setAccel(self.accel())
        imu.setGyro(self.gyro())
        imu.setMag(self.mag())
        return imu

class IMU:
    def __init__(self):
        pass

    def setTemp(self, temp):
        self.temp = temp
    def setGyro(self, gx, gy, gz):
        self.gx = gx
        self.gy = gy
        self.gz = gz
    def setGyro(self, data):
        self.gx = data["GX"]
        self.gy = data["GY"]
        self.gz = data["GZ"]
    def setAccel(self, ax, ay, az):
        self.ax = ax
        self.ay = ay
        self.az = az
    def setAccel(self, data):
        self.ax = data["AX"]
        self.ay = data["AY"]
        self.az = data["AZ"]
    def setMag(self, mx, my, mz):
        self.mx = mx
        self.my = my
        self.mz = mz
    def setMag(self, data):
        self.mx = data["MX"]
        self.my = data["MY"]
        self.mz = data["MZ"]
    def getGyro(self):
        return [self.gx, self.gy, self.gz]
    def getAccel(self):
        return [self.ax, self.ay, self.az]
    def getMag(self):
        return [self.mx, self.my, self.mz]
    def getTemp(self):
        return self.temp
    def getAll(self):
        li = self.getAccel()
        li.append(self.getGyro())
        li.append(self.getMag())
        li.append(self.getTemp())
        return li

