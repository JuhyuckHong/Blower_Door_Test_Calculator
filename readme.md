# Blower_Door_Test_Calculator

The Blower Door Test Calculator is a project aimed at calculating the air leakage of a building using the Blower Door Test method. This repository contains the necessary files and scripts to perform the calculations and generate useful visualizations.

## License

이 프로젝트는 MIT 라이선스로 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 확인하세요.

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
