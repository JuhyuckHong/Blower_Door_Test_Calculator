import math
import json
import statistics
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
        # 측정 값
        self.measured_data = measured_data
        # 측정 값 변수 저장
        self.interior_volume = measured_data["interior_volume"]
        self.temperature = measured_data["temperature"]
        self.relative_humidity = measured_data["relative_humidity"]
        self.atmospheric_pressure = measured_data["atmospheric_pressure"]
        self.measured_values = measured_data["measured_value"]
        # 계산 결과 저장을 위한 변수
        self.val = dict()

    @classmethod
    def from_file(cls, file_path):
        # 측정 값 저장된 file 활용 시
        with open(file_path, 'r') as file:
            data = json.load(file)
        return cls(data)
        
    # 중간 값 계산
    def calculate_interim_values(self):
        self.val["measured values"] = self.measured_values
        # 𝑁
        self.val["N"] = len(self.measured_values)
        # 95% confidence, α = 0.025
        self.val["alpha"] = 0.025
        
        # 𝑥_𝑖 = ln⁡(∆𝑃_𝑖)
        self.val["x"] = [math.log(i) for i, j in self.measured_values]
        self.val["mean x"] = statistics.mean(self.val["x"])
        self.val["average of x"] = statistics.mean(self.val["x"])
        self.val["deviation of x"] = [x - self.val["average of x"] for x in self.val["x"]]
        self.val["average of deviation of x"] = statistics.mean(self.val["deviation of x"])
        self.val["variance of x"] = statistics.variance(self.val["x"])
        self.val["mean squared of x"] = statistics.mean([i**2 for i in self.val["x"]])
        
        # 𝑦_𝑖 = ln⁡(𝑉 ̇_𝑖)
        self.val["y"] = [math.log(j) for i, j in self.measured_values]
        self.val["mean y"] = statistics.mean(self.val["y"])
        self.val["average of y"] = statistics.mean(self.val["y"])
        self.val["deviation of y"] = [x - self.val["average of y"] for x in self.val["y"]]
        self.val["average of deviation of y"] = statistics.mean(self.val["deviation of y"])
        self.val["variance of y"] = statistics.variance(self.val["y"])
        
        # covariance (𝑥_𝑖−¯𝑥)(𝑦_𝑖−¯𝑦)/(𝑁-1)
        self.val["covariance"] = sum([i * j for (i, j) in zip(self.val["deviation of x"], 
                                                              self.val["deviation of y"])]) / (self.val["N"] - 1)
        
        # 𝑛 for 𝑦 = ln⁡(𝐶) + 𝑛𝑥
        self.val["n"] = self.val["covariance"] / self.val["variance of x"]
        # 𝐶 for 𝑦 = ln⁡(𝐶) + 𝑛𝑥
        self.val["C"] = math.exp(self.val["mean y"] - self.val["mean x"] * self.val["n"])
    
    # calibration for 𝜇, 𝜌 using 𝑇, ∅, 𝑃
    def calculate_calibration_values(self):
        self.val["T"] = 273.15 + self.temperature
        self.val["P"] = self.atmospheric_pressure
        self.val["H"] = self.relative_humidity/100

        # density(㎥/kg), 𝜌_𝑆𝑇𝑃 
        self.val["density at STP"] = 1.191887378
        # Partial Pressure(Pa), 𝑃_𝑣𝑠=e^(59.484085−6790.4985/T−5.02802 ln⁡(𝑇))
        self.val["partial pressure"] = self.val["H"] * math.exp(59.484085 - (6790.4985 / self.val["T"])\
                                                                - 5.02802 * math.log(self.val["T"]))
        # density(㎥/kg), 𝜌_𝑎𝑖𝑟 = (𝑃_𝑏𝑎𝑟−0.37802∅𝑃_𝑣𝑠)/287.055𝑇 
        self.val["density of air"] = (self.val["P"] - 0.37802 * self.val["partial pressure"]) / (287.055 * self.val["T"])
        # viscousity(Pa·s), 𝜇_𝑆𝑇𝑃 (not sure)
        self.val["viscousity at STP"] = 0.0000183
        # viscousity(Pa·s) of air, 𝜇_𝑎𝑖𝑟=(𝑏𝑇^0.5)/(1+𝑠/𝑇)
        self.val["viscousity of air"] = (0.000001458 * math.sqrt(self.val["T"]) ) / (1 + 110.4/self.val["T"])
        
        # 𝐶_𝑆𝑇𝑃 = 𝐶_0 from 𝐶_0/𝐶=(𝜇/𝜇_𝑆𝑇𝑃)^(2𝑛−1)×(𝜌/𝜌_𝑆𝑇𝑃)^(1−𝑛)
        self.val["C at STP"] = self.val["C"] * math.pow(self.val["viscousity of air"]/self.val["viscousity at STP"], 2*self.val["n"] - 1)\
                                * math.pow(self.val["density of air"]/self.val["density at STP"], 1- self.val["n"])

    def calculate_variance_and_confidence_values(self):
        # variance of 𝑛, 𝑠_𝑛
        self.val["variance of n"] = 1 / math.sqrt(self.val["variance of x"]) \
                                    * math.sqrt((self.val["variance of y"] \
                                                - self.val["n"] * self.val["covariance"]) / (self.val["N"] - 2))
        # variance of ln⁡(𝐶), 𝑠_ln⁡(𝐶)
        self.val["variance of ln(C)"] = self.val["variance of n"] * math.sqrt(self.val["mean squared of x"])
        # t table value for N-2 and alpha
        self.val["t"] = t.ppf(1 - self.val["alpha"], self.val["N"] - 2)
        # 95% confidence value of n, 𝐼_𝑛
        self.val["margin of error of n"] = self.val["variance of n"] * self.val["t"]
        # 95% confidence value of ln⁡(𝐶), 𝐼_ln⁡(𝐶)
        self.val["margin of error of ln(C)"] = self.val["variance of ln(C)"] * self.val["t"]

    # volumetric flow rate(㎥/s) for certain pressure
    def volumetric_flow_rate(self, dp=50):
        # vfra = volumetric_flow_rate_air
        vfra = self.val["C at STP"] * math.pow(dp, self.val["n"])
        # moey = margin_of_error_of_y 
        moey = self.val["t"] * self.val["variance of n"] \
                            * math.sqrt(self.val["variance of x"] * (self.val["N"] - 1) / \
                                        self.val["N"] + math.pow(math.log(dp) - self.val["mean x"], 2)) 
        self.val["margin of error of y"] = moey
        return [vfra, vfra * math.exp(-moey), vfra * math.exp(moey)]

    def calculate_results(self):
        self.calculate_interim_values()
        self.calculate_calibration_values()
        self.calculate_variance_and_confidence_values()
        
        self.val["volumetric flow rate of Air at 50Pa"] = self.volumetric_flow_rate()
        self.val["ACH50"] = self.val["volumetric flow rate of Air at 50Pa"][0] / self.interior_volume
        # save function to calculate air leakage/infiltration
        self.val["volumetric flow rate"] = self.volumetric_flow_rate

        # SST(Total Sum of Squares)
        self.val["SST"] = sum([(i - self.val["mean y"])**2 for [_, i] in self.val["measured values"]])
        # SSE(Explained Sum of Square)
        self.val["SSE"] = sum([(self.volumetric_flow_rate(i)[0] - self.val["mean y"])**2 for [i, _] in self.val["measured values"]])
        # R-squared
        self.val["R^2"] = self.val["SSE"] / self.val["SST"]

        return self.val
    
# BlowerDoorTestCalculator 클래스의 인스턴스를 json 파일로부터 생성
calculator = BlowerDoorTestCalculator.from_file('data_20230515_142310.json')

# 기밀시험 결과 계산
results = calculator.calculate_results()

# 결과 출력
pprint(results)

from graph_plotter import plot_graph

# 그래프 그리기
plot_graph(results)