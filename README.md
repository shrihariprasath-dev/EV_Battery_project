# ⚡ State of Power (SOP) Estimation for INR18650‑20R Battery Cell

[![Python](https://img.shields.io/badge/Python-3.9+-blue)]()
[![License](https://img.shields.io/badge/License-Open--Use-green)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

**Author:** *Shrihariprasath Basuvaiyan*  
**Last Updated:** April 2026  

---

## 📘 Overview
This repository provides a complete **State of Power (SOP)** estimation pipeline for the Samsung **INR18650‑20R** lithium-ion cell.

The pipeline includes:
- Fast vectorized **Coulomb Counting SOC**
- HPPC‑based **Resistance Extraction**
- Smoothed, monotonic **OCV–SOC** & **R–SOC** maps
- **Peak‑power SOP** for charge & discharge
- Clean Excel outputs & SOP diagnostic plots
- Automatic validation reporting

The implementation is suitable for **EV/HEV BMS**, modeling & research.

---

## 📂 Project Structure
EV_Battery_Project/
│── sop_estimation_calce_inr18650_20r.py
│── README.md
│── input.xlsx
│── outputs/
├── FINAL_SOP_OUTPUT.xlsx
├── FINAL_SOP_PLOT.png
├── SOP_VALIDATION_OUTPUT.xlsx
├── SOP_VALIDATION_REPORT.txt
└── sop_maps.pkl

---

## 🚀 How to Run

### ✅ Install dependencies
pip install numpy pandas matplotlib scipy openpyxl
####
Run the SOP script
python sop_estimation_calce_inr18650_20r.py \
  --xlsx test_data/input.xlsx \
  --vmin 3.2 \
  --vmax 4.2 \
  --idismax 8 \
  --ichgmax 4 \
  --socmin 0.05 \
  --socmax 0.95
