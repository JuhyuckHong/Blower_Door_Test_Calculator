import math
import json
import statistics
import os
from pprint import pprint
from scipy.stats import t


'''
measured_data = {"interior_volume": float,          # (㎥)
                 "initial_zero_pressure": 0,        # (Pa)
                 "final_zero_pressure": 0,          # (Pa)
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
        # 계산 결과 저장을 위한 변수
        self.val = dict()
        # PWM duty to Volumetric Flow rate calculation
        self.slope = 0.0801
        self.intercept = 3.59
        # 풍량 측정 값 저장
        self.measured_values = [[i, (self.slope * j + self.intercept)*60] for i, j in measured_data["measured_value"]]


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
        self.val["x"] = [math.log(i) for i, _ in self.measured_values]
        self.val["mean x"] = statistics.mean(self.val["x"])
        self.val["average of x"] = statistics.mean(self.val["x"])
        self.val["deviation of x"] = [x - self.val["average of x"] for x in self.val["x"]]
        self.val["average of deviation of x"] = statistics.mean(self.val["deviation of x"])
        self.val["variance of x"] = statistics.variance(self.val["x"])
        self.val["mean squared of x"] = statistics.mean([i**2 for i in self.val["x"]])
        
        # 𝑦_𝑖 = ln⁡(𝑉 ̇_𝑖)
        self.val["y"] = [math.log(j) for _, j in self.measured_values]
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
        self.val["n range"] = [self.val["n"] - self.val["margin of error of n"],
                               self.val["n"] + self.val["margin of error of n"]]
        # 95% confidence value of ln⁡(𝐶), 𝐼_ln⁡(𝐶)
        self.val["margin of error of ln(C)"] = self.val["variance of ln(C)"] * self.val["t"]
        self.val["C range"] = [self.val["C"]*math.exp(-self.val["margin of error of ln(C)"]),
                               self.val["C"]*math.exp(+self.val["margin of error of ln(C)"])]

    # volumetric flow rate(㎥/s) for certain pressure
    def volumetric_flow_rate(self, dp=50):
        # vfra = volumetric_flow_rate_air
        vfra = self.val["C at STP"] * math.pow(dp, self.val["n"])
        # 95% confidence
        vfra_min = self.val["C range"][0] * math.pow(dp, self.val["n range"][0])
        vfra_max = self.val["C range"][1] * math.pow(dp, self.val["n range"][1])
        # 95% prediction, moey = margin_of_error_of_y 
        moey = self.val["t"] * self.val["variance of n"] \
                            * math.sqrt(self.val["variance of x"] * (self.val["N"] - 1) / \
                                        self.val["N"] + math.pow(math.log(dp) - self.val["mean x"], 2)) 
        self.val["margin of error of y"] = moey
        return [vfra, vfra * math.exp(-moey), vfra * math.exp(moey), vfra_min, vfra_max]
    
    # reverse function of volumetric_flow_rate
    def reverse_vfra(self, vfra):
        # vfra = volumetric_flow_rate_air
        vfra_min = vfra / math.exp(-self.val["margin of error of y"])
        vfra_max = vfra / math.exp(+self.val["margin of error of y"])
        dp_min = math.pow(vfra_min / self.val["C at STP"], 1 / self.val["n"])
        dp_max = math.pow(vfra_max / self.val["C at STP"], 1 / self.val["n"])
        return [dp_min, dp_max]

    def calculate_results(self):
        self.calculate_interim_values()
        self.calculate_calibration_values()
        self.calculate_variance_and_confidence_values()
        
        self.val["volumetric flow rate of Air at 50Pa"] = self.volumetric_flow_rate()
        self.val["ACH50"] = self.val["volumetric flow rate of Air at 50Pa"][0] / self.interior_volume
        # save function to calculate air leakage/infiltration
        self.val["volumetric flow rate"] = self.volumetric_flow_rate
        # save function to calculate dp at certain vfra
        self.val["reverse vfra"] = self.reverse_vfra

        # SST(Total Sum of Squares)
        mean_of_vfra = statistics.mean([j for [_,j] in self.val["measured values"]])
        self.val["SST"] = sum([(j - mean_of_vfra)**2 for [_, j] in self.val["measured values"]])
        # SSE(Explained Sum of Square)
        self.val["SSR"] = sum([(j - self.volumetric_flow_rate(i)[0])**2 for [i, j] in self.val["measured values"]])
        # R-squared
        self.val["R^2"] = 1 - (self.val["SSR"] / self.val["SST"])

        return self.val
    
# BlowerDoorTestCalculator 클래스의 인스턴스를 json 파일로부터 생성
calculator = BlowerDoorTestCalculator.from_file('data_20230515_142310.json')

# 기밀시험 결과 계산
results = calculator.calculate_results()

# 결과 출력
for i in results.keys():
    if i in ["N", "ACH50", "R^2", "n","C at STP", "n range", "C range"]:
        print(f"{i}: {results[i]}")

pprint(results)

from graph_plotter import plot_graph, create_report

# 그래프 그리기
#plot_graph(results)
# 보고서 텍스트
text = """
여기에 보고서 텍스트를 작성하십시오. 
이 텍스트는 그림의 상단에 표시됩니다.
"""
create_report(results, text)