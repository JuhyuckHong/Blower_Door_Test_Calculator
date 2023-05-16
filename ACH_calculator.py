import math
import json
import os
from pprint import pprint
from scipy.stats import t


'''
measured_data = {"interior_volume": float,          # (㎥)
                 "temperature": float,              # (℃)
                 "relative_humidity": float,        # (%)
                 "atmospheric_pressure": float,     # (Pa)
                 "measured_value": [
                   (∆P_i: float,                    # (Pa)
                    V ̇_i: float)                    # (㎥/s)
                   ]
                 }
'''

class BlowerDoorTestCalculator:
    def __init__(self, measured_data):
        self.measured_data = measured_data

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return cls(data)
    
    
    def calculate_results(self):
        interior_volume = self.measured_data["interior_volume"]
        temperature = self.measured_data["temperature"]
        relative_humidity = self.measured_data["relative_humidity"]
        atmospheric_pressure = self.measured_data["atmospheric_pressure"]
        measured_values = self.measured_data["measured_value"]

        # Here, Blower Door Test Calculation code will be implemented
        # alpha = 0.025 # 95% two-sided test
        # T(p_r, N-2) = t.ppf(1-alpha, 11))

        results = {"ACH50" : "",
                   "ACH50 with 95% confidence": ("",""),
                   "Air leakage at 50Pa": "",
                   "Air leakage at 50Pa with 95% confidence": "",
                   "C_0": 7.8408,
                   "n": 1.0891,
                   "Leakage Area": 13.70}

        return results
    
# TestResultsCalculator 클래스의 인스턴스를 data.json 파일로부터 생성
calculator = BlowerDoorTestCalculator.from_file('data_20230515_142310.json')

# 기밀시험 결과 계산
results = calculator.calculate_results()

# 결과 출력
pprint(results)
