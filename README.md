⚡ State of Power (SOP) Estimation for INR18650‑20R Battery Cell
Author: Shrihariprasath Basuvaiyan
Updated: April 2026

📘 Overview
This repository contains a complete end‑to‑end State of Power (SOP) estimation pipeline for the Samsung INR18650‑20R lithium‑ion cell.
The pipeline processes raw multi‑sheet battery test data, extracts HPPC characteristics, builds OCV/R maps, computes SOC using Coulomb Counting, and generates charge & discharge peak‑power limits.
✅ Supports multi‑sheet Excel input
✅ Fast vectorized SOC calculation
✅ Automatic resistance pulse extraction
✅ Smoothed + monotonic OCV/R maps
✅ HPPC‑based SOP model
✅ Clean Excel outputs
✅ Plots & validation reports

🚀 How to Run
✅ 1. Install required Python packages
Shellpip install numpy pandas matplotlib scipy openpyxlShow more lines

✅ 2. Execute the SOP Estimation Script
Shellpython sop_estimation_calce_inr18650_20r.py \  --xlsx test_data/your_input.xlsx \  --vmin 3.2 \  --vmax 4.2 \  --idismax 8 \  --ichgmax 4 \  --socmin 0.05 \  --socmax 0.95Show more lines
✅ 3. Run using bat script

ArgumentDescription--xlsxInput Excel file containing channel-based battery data--vminMinimum voltage limit for discharge--vmaxMaximum voltage limit for charge--idismaxMaximum discharge current--ichgmaxMaximum charge current--socminMinimum usable SOC limit--socmaxMaximum usable SOC limit

⚙️ Pipeline Summary
A full SOP estimation workflow consists of:

1️⃣ Load Multi‑sheet Raw Data
All sheet names beginning with "Channel" are automatically merged.

2️⃣ SOC Estimation (Coulomb Counting – Vectorized)

Automatic current sign correction
Efficiency‑adjusted
No loops → ultra-fast
Output: Smooth SOC curve in range [0,1]


3️⃣ HPPC Pulse Analysis

Detect rest segments
Identify current pulses
Compute instantaneous resistance:
R=Vpulse−VrestIpulseR = \frac{V_{\text{pulse}} - V_{\text{rest}}}{I_{\text{pulse}}}R=Ipulse​Vpulse​−Vrest​​



4️⃣ OCV & R Maps

Binned median smoothing
Savitzky–Golay filter applied (window 101, polyorder 3)
OCV forced monotonic increasing
R clamped to avoid instability


5️⃣ SOP Estimation (Peak Power)
Using HPPC equations:
✅ Discharge:
Idis=OCV−Vmin⁡R,Pdis=Vmin⁡⋅IdisI_{\text{dis}} = \frac{OCV - V_{\min}}{R}, \quad P_{\text{dis}} = V_{\min} \cdot I_{\text{dis}}Idis​=ROCV−Vmin​​,Pdis​=Vmin​⋅Idis​
✅ Charge:
Ichg=Vmax⁡−OCVR,Pchg=Vmax⁡⋅IchgI_{\text{chg}} = \frac{V_{\max} - OCV}{R}, \quad P_{\text{chg}} = V_{\max} \cdot I_{\text{chg}}Ichg​=RVmax​−OCV​,Pchg​=Vmax​⋅Ichg​
SOC windowing is applied:

If SOC ≤ SOCmin → discharge power = 0
If SOC ≥ SOCmax → charge power = 0


✅ 6️⃣ Clean Excel Output: FINAL_SOP_OUTPUT.xlsx
Contains only the required fields:
Data id
sheet
voltage
current
SOC
SOP


✅ 7️⃣ SOP Plots (Saved as PNG)
The code generates 3 diagnostic plots:

SOP vs Voltage
SOP vs Current
SOP vs SOC

These plots visually confirm:

Smooth OCV map
Stable R map
Physically valid SOP curves


✅ 8️⃣ Validation Outputs
📄 SOP_VALIDATION_OUTPUT.xlsx
Contains:

Calculated discharge/charge power
Difference from interpolated SOP maps

📄 SOP_VALIDATION_REPORT.txt
Summaries include:

Mean error
Standard deviation
Min/Max error

Used to verify that:

SOP interpolation is correct
OCV and R maps are behaving properly


📊 Example SOP Plot
Your project will produce a plot similar to the one below:
FINAL_SOP_PLOT.png
(Your actual image will be available in the outputs/ folder.)

✅ Key Advantages of This Implementation
✅ Extremely high accuracy
✅ Smooth and physical SOP curves
✅ Stable under noise
✅ Works with any multi-sheet CALCE/Arbin dataset
✅ Easy to integrate into a Battery Management System (BMS)
✅ Clean logs, maps, and validation
