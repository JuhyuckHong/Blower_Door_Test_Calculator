import serial
import crcmod.predefined
import struct
from simple_pid import PID


def pressure_read(port='dev/ttyUSB0', baudrate=9600):
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    
    return ser

def duty_control(duty, port='dev/ttyS0', baudrate=9600):
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    
    return ser


if __name__ == '__main__':
    pressure_read()
    duty_control(10)
