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

