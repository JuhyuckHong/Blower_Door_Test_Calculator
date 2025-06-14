# Blower_Door_Test_Calculator

The Blower Door Test Calculator is a project aimed at calculating the air leakage of a building using the Blower Door Test method. This repository contains the necessary files and scripts to perform the calculations and generate useful visualizations.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Installation

1. Clone the repository
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Hardware Requirements
- Differential pressure sensor capable of Modbus/serial communication
- Temperature and humidity sensor
- PWM controllable fan(s) with a control board (tested with pigpio on Raspberry Pi)

## Usage
Execute the graphical interface which guides you through the complete workflow:
```bash
python user_interface.py
```
The program proceeds in the following order:
1. **Measurement** – collect pressure data
2. **Calculation** – compute flow rates and ACH
3. **Graph** – plot the pressure–flow relationship
4. **Report** – generate an Excel/PDF report

For headless environments or additional options refer to the source code.

## Running on Raspberry Pi
To control the fan using `pigpio` on a Raspberry Pi:

1. Clone this repository and enter the project directory:
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   ```
2. Install the `pigpio` daemon and enable it to start automatically:
   ```bash
   sudo apt update
   sudo apt install pigpio
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```
3. Install the Python dependencies listed in `requirements.txt`.
4. Run the GUI with root privileges so the program can access GPIO and serial ports:
   ```bash
   sudo python3 user_interface.py
   ```

## Offline Installation via USB
If the Raspberry Pi cannot connect to the internet, prepare the software on a PC and transfer it with a USB drive.

1. On a computer with internet access clone the repository and download the dependencies:
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   pip download -r requirements.txt -d packages
   ```
2. Copy the project directory and the `packages` folder to a USB drive.
3. Attach the USB to the Raspberry Pi and copy the files:
   ```bash
   sudo mount /dev/sda1 /mnt  # adjust device path as needed
   cp -r /mnt/Blower_Door_Test_Calculator ~/
   cp -r /mnt/packages ~/
   ```
4. Install the dependencies offline:
   ```bash
   pip install --no-index --find-links ~/packages -r ~/Blower_Door_Test_Calculator/requirements.txt
   ```
5. Any additional `.deb` packages such as `pigpio` must also be copied beforehand and installed using `sudo dpkg -i package.deb`.

After installation run the GUI normally:
```bash
sudo python3 ~/Blower_Door_Test_Calculator/user_interface.py
```

## GUI Launch Shortcut on Raspberry Pi
To start the GUI by double-clicking on the desktop:

1. Ensure `user_interface.py` is executable:
   ```bash
   chmod +x /home/pi/Blower_Door_Test_Calculator/user_interface.py
   ```
2. Create `~/Desktop/user_interface.desktop` with the following content (update paths as needed):
   ```ini
   [Desktop Entry]
   Type=Application
   Name=BlowerDoorTest
   Comment=Run blower door test GUI
   Exec=sudo /usr/bin/python3 /home/pi/Blower_Door_Test_Calculator/user_interface.py
   Icon=/home/pi/Blower_Door_Test_Calculator/icon.png
   Terminal=true
   ```
3. Make it executable:
   ```bash
   chmod +x ~/Desktop/user_interface.desktop
   ```
Double-click the icon to run the GUI with root privileges.


## Calculation and Execution Flow
The program automates a full blower door test using several helper modules:

1. `user_interface.py` gathers initial parameters and guides the measurement.
2. `sensor_and_controller.py` communicates with the sensors and fan controller to record pressure differences.
3. `pwm_pid_control.py` maintains target pressures using PID control of the fan.
4. `ACH_calculator.py` computes flow coefficients from the collected data and derives values such as Q50, ACH50 and leakage area.
5. `graph_plotter.py` plots pressure versus flow on a log–log scale and saves an image.
6. `reporting.py` fills an Excel template with the results and embeds the graph.

Running `python user_interface.py` executes these steps sequentially. Measurement data are stored as JSON, then processed to produce a final Excel/PDF report along with graphs for documentation.


## ACH_calculator Derivation
`ACH_calculator.py` fits the measured data to the power-law model:

$$
\dot{V} = C_0\,\Delta P^n
$$

The steps are:
1. Convert each pressure difference $\Delta P$ and flow rate $\dot{V}$ to natural-log form. Least-squares regression of $\ln\Delta P$ versus $\ln\dot{V}$ yields the exponent $n$ and intercept $\ln C$.
2. Compute air density and viscosity from temperature, humidity and barometric pressure. These correct $C$ to $C_0$ via
   $\displaystyle \frac{C_0}{C} = \left( \frac{\mu}{\mu_{\text{STP}}} \right)^{2n-1} \left( \frac{\rho}{\rho_{\text{STP}}} \right)^{1-n}$.

3. Estimate the standard errors of `n` and `ln(C)` and apply the Student t-distribution to provide 95% confidence limits.
4. Use the resulting coefficients to compute
   * `Q50` – the volumetric flow rate at 50 Pa,
   * `ACH50` – air changes per hour based on the interior volume, and
   * `AL50` – effective leakage area at 50 Pa.

The module also returns prediction bounds and `R^2` so the report includes uncertainty metrics.

## 한국어 안내

Blower Door Test Calculator는 블로어 도어 테스트를 통해 건물의 공기 누설량을 계산하기 위한 프로젝트입니다. 이 저장소에는 계산 수행과 시각화에 필요한 파일과 스크립트가 들어 있습니다.

### 라이선스
이 프로젝트는 MIT 라이선스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 확인하세요.

### 설치
1. 저장소를 클론합니다.
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   ```
2. 의존성을 설치합니다.
   ```bash
   pip install -r requirements.txt
   ```

### 하드웨어 요구 사항
- Modbus/직렬 통신이 가능한 차압 센서
- 온도 및 습도 센서
- PWM 제어가 가능한 팬(테스트는 Raspberry Pi의 pigpio 기반)

### 사용 방법
그래픽 인터페이스를 실행하여 전체 워크플로우를 진행합니다.
```bash
python user_interface.py
```
프로그램은 다음 순서로 진행됩니다.
1. **측정** – 압력 데이터를 수집합니다.
2. **계산** – 유량과 ACH를 계산합니다.
3. **그래프** – 압력과 유량 관계를 플로팅합니다.
4. **보고서** – Excel/PDF 보고서를 생성합니다.

GUI 없이 사용하거나 추가 옵션이 필요한 경우 소스 코드를 참고하세요.

### 라즈베리 파이에서 실행
Raspberry Pi에서 `pigpio`를 사용해 팬을 제어하려면 다음 단계를 따르세요.

1. 저장소를 클론한 후 디렉터리로 이동합니다.
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   ```
2. `pigpio` 데몬을 설치하고 자동 시작되도록 설정합니다.
   ```bash
   sudo apt update
   sudo apt install pigpio
   sudo systemctl enable pigpiod
   sudo systemctl start pigpiod
   ```
3. `requirements.txt`에 명시된 파이썬 의존성을 설치합니다.
4. GPIO와 시리얼 포트 접근을 위해 루트 권한으로 GUI를 실행합니다.
   ```bash
   sudo python3 user_interface.py
   ```

### USB를 이용한 오프라인 설치
라즈베리 파이가 인터넷에 연결될 수 없다면 PC에서 소프트웨어를 준비해 USB로 옮길 수 있습니다.

1. 인터넷이 되는 PC에서 저장소를 클론하고 의존성을 다운로드합니다.
   ```bash
   git clone <repo-url>
   cd Blower_Door_Test_Calculator
   pip download -r requirements.txt -d packages
   ```
2. 프로젝트 디렉터리와 `packages` 폴더를 USB 드라이브에 복사합니다.
3. 라즈베리 파이에 USB를 연결해 파일을 복사합니다.
   ```bash
   sudo mount /dev/sda1 /mnt  # 필요에 따라 경로 수정
   cp -r /mnt/Blower_Door_Test_Calculator ~/
   cp -r /mnt/packages ~/
   ```
4. 오프라인으로 의존성을 설치합니다.
   ```bash
   pip install --no-index --find-links ~/packages -r ~/Blower_Door_Test_Calculator/requirements.txt
   ```
5. `pigpio` 같은 추가 `.deb` 패키지도 미리 복사해 `sudo dpkg -i package.deb`로 설치해야 합니다.

설치 후 GUI를 다음과 같이 실행합니다.
```bash
sudo python3 ~/Blower_Door_Test_Calculator/user_interface.py
```

### 라즈베리 파이 바탕화면에서 GUI 실행
바탕화면에서 두 번 클릭해 GUI를 시작하려면:

1. `user_interface.py`를 실행 가능하게 만듭니다.
   ```bash
   chmod +x /home/pi/Blower_Door_Test_Calculator/user_interface.py
   ```
2. 다음 내용을 담은 `~/Desktop/user_interface.desktop` 파일을 만듭니다.(경로는 상황에 맞게 수정)
   ```ini
   [Desktop Entry]
   Type=Application
   Name=BlowerDoorTest
   Comment=Run blower door test GUI
   Exec=sudo /usr/bin/python3 /home/pi/Blower_Door_Test_Calculator/user_interface.py
   Icon=/home/pi/Blower_Door_Test_Calculator/icon.png
   Terminal=true
   ```
3. 파일에 실행 권한을 부여합니다.
   ```bash
   chmod +x ~/Desktop/user_interface.desktop
   ```
아이콘을 더블 클릭하면 루트 권한으로 GUI가 실행됩니다.

### 계산 및 실행 흐름
이 프로그램은 여러 보조 모듈을 통해 블로어 도어 테스트의 전 과정을 자동화합니다.

1. `user_interface.py` – 초기 파라미터를 받고 측정을 안내합니다.
2. `sensor_and_controller.py` – 센서와 팬 컨트롤러와 통신하여 압력 차이를 기록합니다.
3. `pwm_pid_control.py` – PID 제어를 통해 목표 압력을 유지합니다.
4. `ACH_calculator.py` – 수집된 데이터를 바탕으로 Q50, ACH50, 누설 면적 등을 계산합니다.
5. `graph_plotter.py` – 압력과 유량의 관계를 로그–로그 그래프로 저장합니다.
6. `reporting.py` – 결과를 엑셀 템플릿에 채우고 그래프를 삽입합니다.

`python user_interface.py`를 실행하면 이 단계들이 순차적으로 진행되며, 측정된 데이터는 JSON으로 저장되고 최종 Excel/PDF 보고서와 그래프가 생성됩니다.

### ACH_calculator 계산식
`ACH_calculator.py`는 측정 데이터를 다음의 거듭제곱 법칙 모델에 맞춥니다.

$$
\dot{V} = C_0\,\Delta P^n
$$

절차는 다음과 같습니다.
1. 각 압력 차이 $\Delta P$와 유량 $\dot{V}$를 자연로그로 변환하여 회귀 분석을 수행해 지수 $n$과 절편 $\ln C$를 구합니다.
2. 온도, 습도, 기압으로부터 공기 밀도와 점도를 계산하여 다음 식을 이용해 $C$를 $C_0$로 보정합니다.
   $\displaystyle \frac{C_0}{C} = \left( \frac{\mu}{\mu_{\text{STP}}} \right)^{2n-1} \left( \frac{\rho}{\rho_{\text{STP}}} \right)^{1-n}.$
3. `n`과 `ln(C)`의 표준 오차를 추정하고 t-분포를 사용해 95% 신뢰 구간을 제공합니다.
4. 얻어진 계수를 활용해
   * `Q50` – 50 Pa에서의 유량,
   * `ACH50` – 실내 부피를 기준으로 한 시간당 공기 교환 횟수,
   * `AL50` – 50 Pa에서의 등가 누설 면적
   을 계산합니다.

이 모듈은 예측 구간과 결정 계수 `R^2`도 반환하여 보고서에 불확실성을 표시합니다.
