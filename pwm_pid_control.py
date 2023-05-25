import time
from simple_pid import PID
import measurement

def get_duty(target, delay, average_time, control_limit):
    # 현재 압력 값 측정 및 초기값 세팅
    current = measurement.pressure_read(0.1)
    duty = 0

    # 수렴 조건
    convergence_time = 0
    convergence_threshold = target/10
    duration = 10

    # 실패 조건
    failure_time = 0
    failure_threshold = 10

    # 종료 측정 조건
    final_measure_time = 5

    # PID 컨트롤러 생성
    pid = PID(1, 0, 0, setpoint=target)
    pid.auto_mode = True
    pid.output_limits = (-control_limit, control_limit)

    while True:
        # 제어 시작 시간
        time_start = time.time()
        # PID 계산
        control = pid(current)
        # duty 업데이트 및 상하한 설정
        duty += control 
        duty = max(0, min(100, duty))
        # duty 값 적용
        measurement.duty_set(duty)
        # 압력 변화 대기
        time.sleep(delay)
        # 압력 값 측정
        current = measurement.pressure_read(average_time)
        # 제어 종료 시간
        time_diff = time.time() - time_start
        # 오차
        error = abs(target - current)
        if error < convergence_threshold:
            convergence_time += time_diff
        else:
            convergence_time = 0
        
        if convergence_time >= duration:
            current = measurement.pressure_read(final_measure_time)
            return (duty, True, current)

        # duty 100으로 설정해도 목표 압력에 도달하지 못하는 경우
        if duty == 100 and error > failure_threshold:
            failure_time += time_diff
        else:
            failure_time = 0

        # duty 0으로 설정해도 목표 압력 값을 초과하는 경우
        if duty == 0 and error > failure_threshold:
            failure_time += time_diff
        else:
            failure_time = 0

        if failure_time >= duration:
            current = measurement.pressure_read(final_measure_time)
            return (duty, False, current)