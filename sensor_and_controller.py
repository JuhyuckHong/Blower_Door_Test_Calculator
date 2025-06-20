import re
import serial
import crcmod
import struct
import time
import pigpio



def temperature_and_humidity(port='/dev/ttyUSB1', baudrate=9600):
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    return ser


def pressure_read(average_time=0.1, port='/dev/ttyUSB0', baudrate=9600, test=True):
    # 테스트 모드
    if test:
        import random
        return random.randrange(0, 100)
    # 시리얼 연결
    ser = serial.Serial(port=port,
                        baudrate=baudrate,
                        timeout=1)
    # 측정 시작 시간
    time_start = time.time()
    # 평균 값을 위한 변수 선언
    average = []
    # 데이터 요청 값
    data = b'\x01\x03\x00\x01\x00\x01'
    # 모드버스 통신을 위한 CRC 계산
    crc16 = crcmod.predefined.Crc('modbus')
    crc16.update(data)
    crc_bytes = crc16.digest()
    crc_bytes_reversed = crc_bytes[::-1]
    # 데이터 요청 값 + CRC
    data += crc_bytes_reversed
    # 반복 측정
    while True:
        # 데이터 송신
        ser.write(data)
        # 데이터 수신
        response = ser.read(7)
        try:
            # 데이터 분해
            _, _, _, value, _ = struct.unpack('>BBBhH', response)
            # 데이터 축적
            average.append(value)
        except struct.error:
            pass

        # 데이터 평균값 계산
        if time.time() - time_start >= average_time and len(average):
            ser.close()
            average_pressure = sum(average) / len(average)
            # 소수점 1자리까지 값을 반환하는 Lefoo 압력 센서이므로
            # 결과값을 10으로 나눈 값으로 반환
            return average_pressure/10

def duty_set(duty, test=True):
    # 테스트 모드
    if test:
        return 0
    
    # 입력 문자열 확인
    if not isinstance(duty, str):
        duty = str(duty)
    
    # 문자열인 경우 스페이스 제거
    duty = duty.strip()
    
    # 입력 패턴 확인(0~100)
    duty_pattern = r'^(?:100|[1-9]\d|\d)$'
    try:
        # 정규식 검토
        if not re.match(duty_pattern, duty):
            raise ValueError("입력 값 오류로 duty를 0으로 설정합니다.")
    except ValueError:
        duty = '50'
        
    # Connect to pigpio
    pi = pigpio.pi()

    # Define the GPIO pin for PWM and the frequency in Hertz (1kHz)
    gpio_pin = 18  # Example GPIO pin
    frequency = 1000  # 1kHz

    # Set the hardware PWM
    # The range of duty cycle is from 0 to 1,000,000 (representing 0% to 100%)
    duty_cycle = int(duty) * 10_000  # 50% duty cycle as an example

    # Initialize the PWM on the specified pin
    pi.hardware_PWM(gpio_pin, frequency, duty_cycle)

    # Disconnect from pigpio
    pi.stop()
    return 0


def fan_power(set=1):
    # Connect to pigpio
    pi = pigpio.pi()
    
    # Define the GPIO pin for power relay for the Fan
    gpio_pin = 23
    # To set the relay
    pi.write(gpio_pin, set)

    # Disconnect from pigpio
    pi.stop()
    return 0


if __name__ == '__main__':
    pressure_read()
    duty_set(0)
