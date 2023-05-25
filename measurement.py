import serial
import crcmod.predefined
import struct
import time


def pressure_read(average_time=0.1, port='dev/ttyUSB0', baudrate=9600):
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    time.sleep(average_time)
    return ser

def duty_set(duty, port='dev/ttyS0', baudrate=9600):
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    
    return ser


if __name__ == '__main__':
    pressure_read()
    duty_set(0)
