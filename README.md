# 🔋 SOP Estimation for INR18650‑20R Battery Cell
**State of Power (SOP) Estimation for Lithium‑Ion Battery Modeling**  
Author: **Shrihariprasath Basuvaiyan**

---

## 📘 Overview

This project performs comprehensive **State of Power (SOP) estimation** for the INR18650‑20R lithium‑ion cell using experimental test data.  
It extracts internal resistance using HPPC pulse tests, constructs OCV–SOC and R–SOC maps, and computes charge/discharge power limits based on physical constraints.

### ✅ Main Capabilities  
- SOC estimation using Coulomb counting  
- HPPC pulse resistance extraction  
- OCV–SOC curve generation with smoothing and monotonicity enforcement  
- SOP estimation (charge + discharge)  
- Validation metrics and plots  
- Excel + PNG + PKL output generation  

The tool is designed for EV battery research, BMS algorithm development, and academic analysis.

---

## 🚀 Features

- ✅ Automatic merging of multiple `Channel_*` sheets  
- ✅ Fast vectorized SOC computation  
- ✅ Pulse-based internal resistance estimation  
- ✅ OCV map & R map smoothing (Savitzky–Golay filter)  
- ✅ Physically valid monotonic OCV enforcement  
- ✅ SOP estimation for both charge and discharge  
- ✅ Detailed validation: RMSE, MAE, bias  
- ✅ Export of Excel summaries, pickle maps, and plots  

---

## 📂 Input Data Format

Your Excel workbook must include sheets named:
