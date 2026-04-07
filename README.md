# SOP Estimation for INR18650-20R Battery Cell

## Overview

This project performs **State of Power (SOP) estimation** for the INR18650-20R battery cell lithium-ion battery using:

* Voltage limits
* Current limits
* SOC limits
* HPPC pulse resistance extraction
* OCV-R map generation
* Coulomb counting SOC estimation

The script processes experimental Excel data (multiple channel sheets), estimates internal resistance from pulse events, builds smooth OCV and resistance maps, and computes both:

* **Discharge SOP**
* **Charge SOP**

---

## Author

**Shrihariprasath Basuvaiyan**

---

## Features

* Merge multiple `Channel_*` sheets automatically
* Fast vectorized Coulomb counting SOC estimation
* HPPC pulse-based resistance extraction
* Smoothed OCV-SOC and R-SOC maps using Savitzky-Golay filtering
* Physical monotonicity enforcement on OCV curve
* SOP calculation for charge and discharge
* Validation report generation
* Export final Excel outputs and plots

---

## Input Data Format

Input Excel workbook must contain sheets named:

```text
Channel_1
Channel_2
Channel_3
...
```

Each sheet must include these columns:

```text
Test_Time(s)
Current(A)
Voltage(V)
Charge_Capacity(Ah)
Discharge_Capacity(Ah)
```

---

## Required Python Libraries

Install dependencies:

```bash
pip install numpy pandas matplotlib scipy openpyxl
```

---

## Script Usage

Run from terminal:

```bash
python sop_estimation.py --xlsx data.xlsx --vmin 2.5 --vmax 4.2 --idismax 10 --ichgmax 5 --socmin 0.1 --socmax 0.9
```

---

## Command Line Arguments

| Argument    | Description               |
| ----------- | ------------------------- |
| `--xlsx`    | Input Excel file          |
| `--vmin`    | Minimum discharge voltage |
| `--vmax`    | Maximum charge voltage    |
| `--idismax` | Maximum discharge current |
| `--ichgmax` | Maximum charge current    |
| `--socmin`  | Minimum SOC allowed       |
| `--socmax`  | Maximum SOC allowed       |

---

## Example

```bash
python sop_estimation.py --xlsx INR18650_data.xlsx --vmin 2.5 --vmax 4.2 --idismax 10 --ichgmax 5 --socmin 0.1 --socmax 0.9
```

---

## Output Files

Generated inside:

```text
outputs/
```

Files created:

### 1. Final SOP Output

```text
FINAL_SOP_OUTPUT.xlsx
```

Contains:

* Voltage
* Current
* SOC
* SOP Discharge
* SOP Charge

---

### 2. SOP Maps

```text
sop_maps.pkl
```

Contains:

* SOC grid
* OCV map
* Resistance map

---

### 3. SOP Plot

```text
FINAL_SOP_PLOT.png
```

Includes:

* SOP vs Voltage
* SOP vs Current
* SOP vs SOC

---

### 4. Validation Output

```text
SOP_VALIDATION_OUTPUT.xlsx
```

Includes validation error calculation.

---

### 5. Validation Report

```text
SOP_VALIDATION_REPORT.txt
```

Statistical error summary.

---

## Core Methodology

### SOC Estimation

Coulomb counting:

SOC = SOC_{initial} - \int \frac{I,dt}{C_{nominal}}

---

### Resistance Estimation

Pulse resistance:

R = \frac{V_{pulse}-V_{rest}}{I_{pulse}}

---

### SOP Estimation

Discharge power:

P_{dis}=V_{min}\cdot \frac{OCV-V_{min}}{R}

Charge power:

P_{chg}=V_{max}\cdot \frac{V_{max}-OCV}{R}

---

## Notes

* OCV curve is forced monotonic for physical consistency
* Resistance is clamped to avoid divide-by-zero
* Savitzky-Golay smoothing removes SOP oscillations

---

## Recommended Dataset

Use battery test data from CALCE Battery Research Group for best results.

---

## Future Improvements

* 1RC equivalent circuit model integration
* Temperature-dependent SOP
* Real-time BMS deployment
* EKF-based SOC correction

---

## Folder Structure

```text
project/
│── sop_estimation.py
│── data.xlsx
│── outputs/
│── README.md
```

---

## License

For research and educational use.

