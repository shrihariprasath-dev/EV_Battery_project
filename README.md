# 🔋 SOP Estimation for INR18650‑20R Battery Cell
**A Complete State of Power (SOP) Estimation Framework Using HPPC Pulse Resistance, OCV Mapping & Coulomb Counting**  
**Author:** *Shrihariprasath Basuvaiyan*

---

# 📘 Introduction

This project provides a full **State of Power (SOP)** estimation pipeline for the **INR18650‑20R** lithium‑ion battery cell using experimental test data.  

It is designed for research, BMS modeling, HPPC analysis, and algorithm development.

The system computes:

- ✅ **State of Charge (SOC)** using vectorized Coulomb counting  
- ✅ **OCV–SOC map** reconstruction  
- ✅ **Internal resistance (R–SOC map)** using HPPC pulses  
- ✅ **Charge & Discharge SOP** using physical constraints  
- ✅ **Validation and plotting** for analysis  
- ✅ **Excel and PKL exports** for BMS integration  

This README contains:

✅ Full methodology  
✅ Full workflow diagram  
✅ Complete explanation of Python implementation  
✅ Output descriptions  
✅ Folder structure  

All in **one single file**.

---

# ✅ Key Features

- Auto-detection of all `Channel_*` Excel sheets  
- Fast vectorized SOC estimation  
- Robust HPPC pulse resistance extraction  
- Savitzky–Golay smoothing for clean OCV/R curves  
- Physically constrained OCV monotonicity  
- Charge & Discharge SOP estimation  
- Complete export package (Excel, PNG, PKL)  
- Validation and error report  

---

# 📂 Input Excel Format

---

# ▶️ Running the Script

```bash
python sop_estimation.py \
    --xlsx data.xlsx \
    --vmin 2.5 --vmax 4.2 \
    --idismax 10 --ichgmax 5 \
    --socmin 0.1 --socmax 0.9

Your Excel workbook must contain sheets like:

CLI Arguments
🧠 Detailed Methodology
(Fully aligned with the Python code)
✅ 1. Loading & Merging Input Sheets
Function: load_all_sheets()

Reads all "Channel*" sheets from an Excel file
Converts numeric columns
Removes invalid rows
Sorts by time
Adds metadata (Sheet, Sample_ID)
Produces a complete merged dataset


✅ 2. SOC Estimation (Coulomb Counting)
Function: compute_soc()
Uses:
SOC=SOC0−∫I(t)⋅ηCnominaldtSOC = SOC_0 - \int \frac{I(t) \cdot \eta}{C_{nominal}} dtSOC=SOC0​−∫Cnominal​I(t)⋅η​dt
Where:

Charge efficiency = 0.99
Discharge efficiency = 1.00
dt computed from timestamp difference
SOC clipped to [0, 1]

This produces a continuous and stable SOC trace.

✅ 3. HPPC Resistance Extraction
Function: estimate_resistance()
Steps:

Identify rest regions (|I| < 0.02 A)
Identify pulse events (|I| > 0.5 A)
Match each pulse with nearest preceding rest point
Compute resistance:

R=Vpulse−VrestIpulseR = \frac{V_{pulse} - V_{rest}}{I_{pulse}}R=Ipulse​Vpulse​−Vrest​​

Reject unrealistic values (0 < R < 0.5 Ω)

Output columns:
SOC
OCV
R


✅ 4. Building OCV–SOC and R–SOC Maps
Function: build_maps()
Processing includes:

Binning pulses into 100 SOC bands
Median filtering to remove outliers
200‑point interpolation
Savitzky–Golay smoothing
Enforcing monotonic OCV:

OCV[i]=max⁡(OCV[0:i])OCV[i] = \max(OCV[0:i])OCV[i]=max(OCV[0:i])

Clamping R to prevent division-by-zero

Outputs:

soc_grid (200 points)
OCV_map
R_map


✅ 5. SOP Calculation
Function: compute_sop()
Discharge SOP:
Idis=OCV−VminRI_{dis} = \frac{OCV - V_{min}}{R}Idis​=ROCV−Vmin​​
Pdis=Vmin⋅IdisP_{dis} = V_{min} \cdot I_{dis}Pdis​=Vmin​⋅Idis​
Charge SOP:
Ichg=Vmax−OCVRI_{chg} = \frac{V_{max} - OCV}{R}Ichg​=RVmax​−OCV​
Pchg=Vmax⋅IchgP_{chg} = V_{max} \cdot I_{chg}Pchg​=Vmax​⋅Ichg​
Constraints applied:

Voltage limits
Current limits
SOC window
Non-negative currents


✅ 6. Interpolating SOP Back to Dataset
Linear interpolation maps the computed SOP curves:
SOP_Discharge(W)
SOP_Charge(W)

onto each time-indexed dataset row.

✅ 7. Output File Generation
Outputs stored under:
outputs/

✅ FINAL_SOP_OUTPUT.xlsx
Contains:

Voltage
Current
SOC
SOP_Discharge
SOP_Charge


✅ sop_maps.pkl
Serialized dictionary:
Python{  "soc": soc_grid,  "ocv": OCV_map,  "r": R_map}Show more lines

✅ FINAL_SOP_PLOT.png
Includes:

SOP vs Voltage
SOP vs Current
SOP vs SOC


✅ SOP_VALIDATION_OUTPUT.xlsx
Computed vs expected SOP values.

✅ SOP_VALIDATION_REPORT.txt
Contains:

RMSE
MAE
Bias
Summary statistics


📁 Folder Structure
project/
│── sop_estimation.py
│── data.xlsx
│── outputs/
│   │── FINAL_SOP_OUTPUT.xlsx
│   │── FINAL_SOP_PLOT.png
│   │── SOP_VALIDATION_OUTPUT.xlsx
│   │── SOP_VALIDATION_REPORT.txt
│   │── sop_maps.pkl
│── README.md


✅ Future Enhancements

Temperature‑dependent OCV/R maps
Full ECM (1RC/2RC) modeling
EKF/UKF‑based SOC estimation
BMS firmware integration
HPPC automatic classification
