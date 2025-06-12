import math
import json
import statistics
from pprint import pprint
from scipy.stats import t
from datetime import datetime
import os

DEFAULT_COEFFICIENTS = {
    "none": {
        "forward": {"slope": 9.21069, "intercept": 935.46713},
        "reverse": {"slope": 9.21069, "intercept": 935.46713},
        "duty_range": [20, 100],
    },
    "low": {
        "forward": {"slope": 7.36855, "intercept": 748.3737},
        "reverse": {"slope": 7.36855, "intercept": 748.3737},
        "duty_range": [20, 100],
    },
    "high": {
        "forward": {"slope": 5.52641, "intercept": 561.2803},
        "reverse": {"slope": 5.52641, "intercept": 561.2803},
        "duty_range": [20, 100],
    },
}


def load_fan_coefficients(file_path="fan_coefficients.json"):
    """Load fan calibration coefficients from a JSON file."""
    coeffs = {k: v.copy() for k, v in DEFAULT_COEFFICIENTS.items()}
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
        for cover, values in data.items():
            coeffs.setdefault(cover, {}).update(values)
    return coeffs


'''
measured_data = {
                 "initial_zero_pressure": 0,        # (Pa)
                 "final_zero_pressure": 0,          # (Pa)
                 "temperature": float,              # (℃)
                 "relative_humidity": float,        # (%)
                 "atmospheric_pressure": float,     # (Pa)
                 "measured_value": [
                   [∆P_i: float,                    # (Pa)
                    V ̇_i: float], ...               # (㎥/h)
                   ]
                 }
'''

class BlowerDoorTestCalculator:
    def __init__(self, measured_data):
        # 측정 값
        self.measured_data = measured_data
        # 측정 값 변수 저장
        self.interior_volume = float(measured_data["interior volume"])
        self.temperature = float(measured_data["temperature"])
        self.relative_humidity = float(measured_data["relative_humidity"])
        self.atmospheric_pressure = float(measured_data["atmospheric_pressure"])
        # 계산 결과 저장을 위한 변수
        self.val = dict()
        # PWM duty to Volumetric Flow rate calculation
        # 9GV2048P0G201 fan only (formerly OF-OD172SAP-Reversible)
        self.cover = measured_data.get("fan_cover", "none").lower()
        self.num_fans = int(measured_data.get("fan_count", 2))

        fan_coeffs = load_fan_coefficients()
        coeff = fan_coeffs.get(self.cover, fan_coeffs.get("none", DEFAULT_COEFFICIENTS["none"]))
        # for Forward flow
        self.slope_fwd = coeff["forward"]["slope"]
        self.intercept_fwd = coeff["forward"]["intercept"]
        # for Reverse flow
        self.slope_rev = coeff["reverse"]["slope"]
        self.intercept_rev = coeff["reverse"]["intercept"]
        # 풍량 측정 값 저장
        self.measured_values = [[i, (self.slope_fwd * j + self.intercept_fwd) * self.num_fans]
                                if j < 50 else
                                [i, (self.slope_rev * j + self.intercept_rev) * self.num_fans]
                                for i, j in measured_data["measured_value"]]


    @classmethod
    def from_file(cls, file_path, conditions="conditions.json"):
        # 측정 값 저장된 file 활용 시
        with open(file_path, 'r') as file:
            data = json.load(file)
        with open(conditions, 'r') as file:
            data.update(json.load(file))
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

        # density(㎥/kg), 𝜌_𝑆𝑇𝑃 where STP: 23 degree celcius, 1atm
        self.val["density at STP"] = 1.1919
        # Partial Pressure(Pa), 𝑃_𝑣𝑠=e^(59.484085−6790.4985/T−5.02802 ln⁡(𝑇))
        self.val["partial pressure"] = self.val["H"] * math.exp(59.484085 - (6790.4985 / self.val["T"])\
                                                                - 5.02802 * math.log(self.val["T"]))
        # density(㎥/kg), 𝜌_𝑎𝑖𝑟 = (𝑃_𝑏𝑎𝑟−0.37802∅𝑃_𝑣𝑠)/287.055𝑇 
        self.val["density of air"] = (self.val["P"] - 0.37802 * self.val["partial pressure"]) / (287.055 * self.val["T"])
        # viscousity(Pa·s), 𝜇_𝑆𝑇𝑃 (not sure)
        self.val["viscousity at STP"] = 0.00001827
        # viscousity(Pa·s) of air, 𝜇_𝑎𝑖𝑟=(𝑏𝑇^0.5)/(1+𝑠/𝑇)
        self.val["viscousity of air"] = (0.000001458 * math.sqrt(self.val["T"]) ) / (1 + 110.4/self.val["T"])
        
        # 𝐶_0 from 𝐶_0/𝐶=(𝜇/𝜇_𝑆𝑇𝑃)^(2𝑛−1)×(𝜌/𝜌_𝑆𝑇𝑃)^(1−𝑛)
        self.val["C0"] = self.val["C"] * math.pow(self.val["viscousity of air"]/self.val["viscousity at STP"], 2*self.val["n"] - 1)\
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
        self.val["C0 range"] = [self.val["C range"][0] * math.pow(self.val["viscousity of air"]/self.val["viscousity at STP"], 2*self.val["n"] - 1)\
                                * math.pow(self.val["density of air"]/self.val["density at STP"], 1- self.val["n"]),
                                self.val["C range"][1] * math.pow(self.val["viscousity of air"]/self.val["viscousity at STP"], 2*self.val["n"] - 1)\
                                * math.pow(self.val["density of air"]/self.val["density at STP"], 1- self.val["n"])]

    # volumetric flow rate(㎥/h) for certain pressure
    def volumetric_flow_rate(self, dp=50):
        # vfra = volumetric_flow_rate_air
        vfra = self.val["C0"] * math.pow(dp, self.val["n"])
        # 95% confidence
        vfra_min = self.val["C0 range"][0] * math.pow(dp, self.val["n range"][0])
        vfra_max = self.val["C0 range"][1] * math.pow(dp, self.val["n range"][1])
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
        dp_min = math.pow(vfra_min / self.val["C0"], 1 / self.val["n"])
        dp_max = math.pow(vfra_max / self.val["C0"], 1 / self.val["n"])
        return [dp_min, dp_max]

    def calculate_results(self):
        self.calculate_interim_values()
        self.calculate_calibration_values()
        self.calculate_variance_and_confidence_values()
        
        # save interior volume to report
        self.val["interior_volume"] = self.interior_volume
        # volumetric flow rate of Air at 50Pa
        self.val["Q50"] = self.volumetric_flow_rate()[0]
        # Air change per hour at 50 pressure difference
        self.val["ACH50"] = self.val["Q50"] / self.interior_volume
        # leakage area at 50 Pa (㎡)
        self.val["AL50"] = self.val["C0"] * math.pow(self.val["density at STP"]/2,0.5)*math.pow(50, self.val["n"]-0.5) / 3_600
        
        # confidence intervals
        Q50s = self.volumetric_flow_rate()
        self.val["Q50+-"] = f"{(Q50s[3]-Q50s[0])/Q50s[0]*100:+.1f}%/{(Q50s[4]-Q50s[0])/Q50s[0]*100:+.1f}%"
        C0s = [self.val["C0"]] + self.val["C0 range"]
        self.val["C0+-"] = f"{(C0s[1]-C0s[0])/C0s[0]*100:+.1f}%/{(C0s[2]-C0s[0])/C0s[0]*100:+.1f}%"
        ns = [self.val["n"]] + self.val["n range"]
        self.val["n+-"] = f"{(ns[1]-ns[0])/ns[0]*100:+.1f}%/{(ns[2]-ns[0])/ns[0]*100:+.1f}%"

        # SST(Total Sum of Squares)
        mean_of_vfra = statistics.mean([j for [_,j] in self.val["measured values"]])
        self.val["SST"] = sum([(j - mean_of_vfra)**2 for [_, j] in self.val["measured values"]])
        # SSE(Explained Sum of Square)
        self.val["SSR"] = sum([(j - self.volumetric_flow_rate(i)[0])**2 for [i, j] in self.val["measured values"]])
        # R-squared
        self.val["r^2"] = 1 - (self.val["SSR"] / self.val["SST"])

        return self.val


if __name__ == '__main__':

    # 시험 조건 불러오기
    conditions = 'conditions.json'
    with open(conditions, 'r') as file:
        data = json.load(file)
    
    # 아무 시험 결과 없는 경우, Just in case.
    if not data.get("depressurization") and not data.get("pressurization"):
        pass

    # 결과 저장 변수 선언
    calculation_raw = {}
    # 보고서 용 값 저장
    calculation_raw["report"] = {}

    # 저장 할 값 지정
    need_to_save = ["C0", 
                    "n", 
                    "C0 range", 
                    "n range", 
                    "t", 
                    "variance of n", 
                    "variance of x", 
                    "mean x",
                    "N", 
                    "measured values", 
                    "margin of error of y",
                    "Q50",
                    "ACH50",
                    "AL50",
                    "r^2",
                    "Q50+-",
                    "ACH50+-",
                    "n+-",
                    "C0+-",
                    "interior_volume"]
    
    need_to_report = ["Q50",
                      "ACH50", 
                      "AL50", 
                      "C0", 
                      "n", 
                      "Q50+-", 
                      "C0+-", 
                      "n+-", 
                      "r^2",
                      "interior_volume"]
    
    # 감압 시험을 수행 한 경우
    if data.get("depressurization"):
        # 파일 불러오기
        depressureization = BlowerDoorTestCalculator.from_file('depressurization_raw.json',
                                                               'conditions.json')
        # 결과 계산
        results_depr = depressureization.calculate_results()
        # Raw data 저장
        now = datetime.now().strftime("%d%m%Y-%H%M%S")
        with open(f"./calculations/depressurization_{now}.json", 'w') as file:
            json.dump(results_depr, file, indent=4)
        # 결과 값 변수 저장
        calculation_raw['depressurization'] = {}
        for i in results_depr.keys():
            if i in need_to_save:
                calculation_raw['depressurization'][i]=results_depr[i]
        
        for i in need_to_report:
            report_key = i + "-"
            calculation_raw["report"][report_key] = calculation_raw["depressurization"][i]

    # 가압 시험을 수행 한 경우
    if data.get("pressurization"):
        # 파일 불러오기
        pressureization = BlowerDoorTestCalculator.from_file('pressurization_raw.json',
                                                             'conditions.json')
        # 결과 계산
        results_pres = pressureization.calculate_results()
        # Raw data 저장
        now = datetime.now().strftime("%d%m%Y-%H%M%S")
        with open(f"./calculations/pressurization_{now}.json", 'w') as file:
            json.dump(results_pres, file, indent=4)
        # 결과 값 변수 저장
        calculation_raw['pressurization'] = {}
        for i in results_pres.keys():
            if i in need_to_save:
                calculation_raw['pressurization'][i]=results_pres[i]
        
        for i in need_to_report:
            report_key = i + "+"
            calculation_raw["report"][report_key] = calculation_raw["pressurization"][i]

    # 감/가압 시험 모두 수행 한 경우, 평균 값 계산
    if data.get("depressurization") and data.get("pressurization"):
        calculation_raw["average"] = {}
        for i in ["Q50", "ACH50", "AL50"]:
            calculation_raw["report"][i + "_avg"] = (
                calculation_raw["depressurization"][i]
                + calculation_raw["pressurization"][i]
            ) / 2

    with open(f"./calculation_raw.json", 'w') as file:
        json.dump(calculation_raw, file, indent=4)
