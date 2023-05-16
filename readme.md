# Blower_Door_Test_Calculator

The Blower Door Test Calculator is a project aimed at calculating the air leakage of a building using the Blower Door Test method. This repository contains the necessary files and scripts to perform the calculations and generate useful visualizations.

## Table of Contents

-   [Project Structure](#project-structure)
-   [Dependencies](#dependencies)
-   [Usage](#usage)
-   [Contributing](#contributing)
-   [License](#license)

## Project Structure

The project directory structure is as follows:

```
Blower_Door_Test_Calculator
├─ .gitignore
├─ ACH_calculator.py
├─ data_20230515_142310.json
├─ graph_plotter.py
├─ readme.md
└─ requirements.txt

```

-   `ACH_calculator.py`: Python script that calculates the Air Changes per Hour (ACH) of a building based on the Blower Door Test data.
-   `data_20230515_142310.json`: Sample data file containing the measurements obtained from the Blower Door Test.
-   `graph_plotter.py`: Python script that generates visualizations based on the Blower Door Test data.
-   `requirements.txt`: Specifies the required Python packages and their versions for running the project.

## Dependencies

The project has the following dependencies:

-   contourpy==1.0.7
-   cycler==0.11.0
-   fonttools==4.39.4
-   kiwisolver==1.4.4
-   matplotlib==3.7.1
-   numpy==1.24.3
-   packaging==23.1
-   Pillow==9.5.0
-   pyparsing==3.0.9
-   python-dateutil==2.8.2
-   scipy==1.10.1
-   six==1.16.0

## Usage

To use the Blower Door Test Calculator project, follow these steps:

1. Clone the repository: `git clone https://github.com/JuhyuckHong/Blower_Door_Test_Calculator.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the main script: `python ACH_calculator.py`

Before using, you need to measure data from the blower door tester and save the data into a JSON file with the following format:

```json
{
    "interior_volume": 500.00,
    "temperature": 25.5,
    "relative_humidity": 50,
    "atmospheric_pressure": 101300.00,
    "measured_value": [[50.00, 200.00], [60.00, 250.00]]
}
```

And then, either modify the file path of 'from_file' in 'ACH_calculator' or input the data in dictionary form.

## Contributing

Contributions to the PWM PID Control project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. We appreciate your feedback.

## License

The Blower Door Test Calculator project is licensed under the [MIT License](LICENSE).
