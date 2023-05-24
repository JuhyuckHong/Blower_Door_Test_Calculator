import time
from simple_pid import PID
import measurement

def get_duty(target, delay, average_time, control_limit):
    # 현재 압력 값 측정 및 초기값 세팅
    current = measurement.pressure_read(0.1)
    duty = 0

    # 수렴 조건
    converged_time = 0
    threshold = target/10
    duration = 10

    # PID 컨트롤러 생성
    pid = PID(1, 0, 0, setpoint=target)
    pid.auto_mode = True
    pid.output_limits = (-control_limit, control_limit)

    while True:
        # 제어 시작 시간
        time_start = time.time()
        # PID 계산
        control = pid(current)
        # duty 업데이트
        duty += control
        # duty 값 세팅
        measurement.duty_set(duty)
        # 압력 변화 대기
        time.sleep(delay)
        # 압력 값 측정
        current = measurement.pressure_read(average_time)
        # 제어 종료 시간
        time_diff = time.time() - time_start
        # 오차
        error = abs(target - current)
        if error < threshold:
            converged_time += time_diff
        else:
            converged_time = 0
        
        if converged_time >= duration:
            break
    
    return duty
