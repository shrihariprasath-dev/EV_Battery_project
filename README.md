# State of Power (SOP) Estimation — INR 18650-20R (CALCE), Incremental Current OCV, Sample 1, 25 °C

## 1.  Project Goal:
The objective of this project is to **estimate the State of Power (SOP)** of a lithium‑ion cell using only signals that a Battery Management System (BMS) typically has access to:

- **Voltage** (terminal or near‑OCV),
- **Current**, and
- **SOC limits** (minimum/maximum SOC constraints).

The dataset is the CALCE “Incremental Current OCV” test for an **INR 18650‑20R** cell at **25 °C**, Sample 1.

---

## 2. What SOP means (and why it matters)
**SOP** is the maximum power that can be safely delivered (discharge) or absorbed (charge) **at the current state** of the battery.

In practice, a BMS must guarantee that a requested power does not violate:

1. **Voltage limits** (avoid undervoltage/overvoltage),
2. **Current limits** (hardware/safety limits), and
3. **SOC limits** (avoid operation too close to empty/full).

SOP therefore acts like an *instantaneous power envelope* for the cell.

---

## 3. Dataset characteristics and Scrip Explaination
### Raw signals
The Arbin export provides time series columns including:

- `Current(A)`
- `Voltage(V)`
- `Charge_Capacity(Ah)` and `Discharge_Capacity(Ah)`

There is **no dedicated SOC column** in this file, so SOC must be inferred.

### SOC estimation used in this project

# SOP Estimation & Validation Script — Full Line‑by‑Line Explanation

This ReadME file explains how the SOP (State of Power) estimation and validation script works. It covers:
- Loading multi‑sheet battery test data
- Computing SOC (State of Charge)
- Extracting resistance via pulse method
- Building OCV–R maps
- Computing SOP curves
- Mapping SOP back to every data sample
- Saving outputs
- Creating plots
- Running automatic validation

---

# 3.1. IMPORT LIBRARIES
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import os
import pickle
```
These import essential modules:
- `numpy` → fast numerical arrays
- `pandas` → Excel & dataframe handling
- `matplotlib` → plotting
- `argparse` → command line input
- `pickle` → storing calibration maps
- `pathlib` → handle file paths

---

# 3.2. LOAD & MERGE ALL CHANNEL SHEETS
```python
def load_all_sheets(path):
```
Loads all sheets whose names start with `Channel`, merges them into a single dataframe.

Steps:
1. Read Excel file using `pd.ExcelFile`
2. Identify channel sheets: `startswith("channel")`
3. Convert numeric columns
4. Sort by time
5. Add **Sheet name** and **Sample_ID**
6. Append to list and concatenate

This gives one unified dataset for SOP modeling.

---

# 3.3. COMPUTE SOC
```python
def compute_soc(df):
```
SOC is computed using normalized net capacity:
- Net capacity = Charge_Capacity − Discharge_Capacity
- SOC = (net − min) / (max − min)

This produces SOC values in **0–1** range.

---

# 3.4. PULSE‑BASED RESISTANCE ESTIMATION
```python
def estimate_resistance(df, I_rest_thr, I_pulse_thr, window):
```
- Identifies rest segments (`|I| ≤ threshold`)
- Identifies pulse segments (`|I| ≥ threshold`)
- Detect **start of pulse**
- Finds nearest previous rest point
- Computes R using formula:
  
  → **R = (V_pulse − V_rest) / (I_pulse)**

Filters valid R values between 0 and 0.5 Ω.

This produces a resistance dataset as function of SOC.

---

# 3.5. BUILD OCV & R MAPS
```python
def build_maps(pulses, df, R_fallback):
```
If valid pulse data exist:
- Bin SOC into 100 bins
- Median‑aggregate OCV & R
- Interpolate onto SOC grid (0–1, 200 points)

Else:
- Use rest voltages for OCV
- Use fallback R for all SOC

Outputs:
- `soc_grid` (200 points)
- `OCV_map`
- `R_map`

These curves are the **core of the battery model**.

---

# 3.6. SOP COMPUTATION
```python
def compute_sop(...):
```
For every SOC grid point:

### Discharge current limit:
```
I_dis_allowed = (vmin - OCV) / R
```
### Charging current limit:
```
I_chg_allowed = (vmax - OCV) / R
```
Apply hardware limits:
- Clip using idismax and ichgmax
- Zero beyond SOC limits

Compute power:
```
P_dis = vmin * (-I_dis)
P_chg = vmax * I_chg
```

---

# 3.7. INTERPOLATE SOP BACK TO ALL DATA ROWS
```
df["SOP_Discharge(W)"] = np.interp(df["SOC"], soc_grid, P_dis)
df["SOP_Charge(W)"] = np.interp(df["SOC"], soc_grid, P_chg)
```
Every sample row gets its SOP value.

---

# 3.8. SAVE FINAL OUTPUT
Saves a clean Excel file:
```
outputs/FINAL_SOP_OUTPUT.xlsx
```

---

# 3.9. SAVE CALIBRATION MAPS FOR VALIDATION
These maps are required to recompute SOP later:
```
sop_maps.pkl
```

---

# 3.10. GENERATE PLOTS
Three subplots:
- SOP vs Voltage
- SOP vs Current
- SOP vs SOC

Saved as:
```
outputs/FINAL_SOP_PLOT.png
```

---

# 3.11. VALIDATION MODULE
After SOP is generated, the script automatically validates it.

Steps:
1. Reload FINAL_SOP_OUTPUT.xlsx
2. Recompute OCV and R via interpolation
3. Recompute allowed currents
4. Recompute SOP
5. Compute error vs original:
```
Err_Discharge = P_dis_val − SOP_Discharge
Err_Charge    = P_chg_val − SOP_Charge
```
6. Save:
```
outputs/SOP_VALIDATION_OUTPUT.xlsx
```
7. Print descriptive statistics

If the SOP model is correct: errors ≈ 0.

---

# HOW TO RUN THE SCRIPT

In CMD Python command:
```
python sop_estimation_calce_inr18650_20r.py ^
  --xlsx "12_2_2015_Incremental OCV test_SP20-1.xlsx" ^
  --vmin 2.50 --vmax 4.20 ^
  --idismax 20 --ichgmax 4 ^
  --socmin 0.05 --socmax 0.95
```
Usinmg BAT file
Double click Run_SOP.bat
---

# SUMMARY
This script:
- Reads multi‑sheet battery data
- Computes SOC
- Extracts resistance pulses
- Builds OCV–R model
- Computes SOP limits
- Maps SOP to individual samples
- Generates plots
- Saves all outputs
- Performs full automatic validation
