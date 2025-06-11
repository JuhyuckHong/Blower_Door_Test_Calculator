# Blower_Door_Test_Calculator

The Blower Door Test Calculator helps evaluate building air leakage through automated measurement and reporting. The application collects pressure data, calculates ACH values, plots graphs and produces a final report.

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
