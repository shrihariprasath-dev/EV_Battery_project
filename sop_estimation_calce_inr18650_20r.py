# ==============================================================================
# SOP Estimation for battery cell INR18650_20R
# Authors: Shrihariprasath Basuvaiyan, Vikash Ranjan Dhahia, Dinesh Vishnu
# ==============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import os
import pickle
from scipy.signal import savgol_filter


# =========================================================
# Load and merge all Channel sheets
# =========================================================
def load_all_sheets(path):
    print(f"[INFO] Loading workbook: {path}")
    xl = pd.ExcelFile(path, engine="openpyxl")
    channel_sheets = [s for s in xl.sheet_names if s.lower().startswith("channel")]
    all_rows = []

    for sh in channel_sheets:
        print(f"[INFO] Reading {sh}...")
        df = pd.read_excel(path, sheet_name=sh, engine="openpyxl")

        for col in ["Test_Time(s)", "Current(A)", "Voltage(V)",
                    "Charge_Capacity(Ah)", "Discharge_Capacity(Ah)"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna(subset=["Test_Time(s)", "Current(A)", "Voltage(V)"])
        df = df.sort_values("Test_Time(s)").reset_index(drop=True)
        df["Sheet"] = sh
        df["Sample_ID"] = df.index + 1
        all_rows.append(df)

    merged = pd.concat(all_rows, ignore_index=True)
    print(f"[INFO] Total merged rows: {len(merged)}")
    return merged


# =========================================================
# Fast Vectorized Coulomb Counting SOC
# =========================================================
def compute_soc(df, C_nominal=2.0, initial_soc=1.0, eta_chg=0.99, eta_dis=1.0):
    print("[INFO] Computing SOC using FAST vectorized Coulomb Counting...")

    df = df.sort_values("Test_Time(s)").reset_index(drop=True)
    dt = df["Test_Time(s)"].diff().fillna(0) / 3600.0

    # Flip sign → discharge must be negative
    I_raw = -df["Current(A)"]

    eta = np.where(I_raw > 0, eta_chg, eta_dis)
    eff_I = eta * I_raw

    dSOC = -(eff_I * dt) / C_nominal
    soc = initial_soc + np.cumsum(dSOC)

    df["SOC"] = np.clip(soc, 0, 1)
    print(f"[DEBUG] SOC range after CC: {df['SOC'].min()} → {df['SOC'].max()}")
    return df


# =========================================================
# Estimate resistance using HPPC pulses
# =========================================================
def estimate_resistance(df, I_rest_thr, I_pulse_thr, window):
    df["is_rest"] = df["Current(A)"].abs() <= I_rest_thr
    df["is_pulse"] = df["Current(A)"].abs() >= I_pulse_thr

    pulse_start = df["is_pulse"] & (~df["is_pulse"].shift(1, fill_value=False))
    rest_idx = df.index[df["is_rest"]].to_numpy()
    rest_time = df.loc[rest_idx, "Test_Time(s)"].to_numpy()

    records = []

    for idx, row in df.loc[pulse_start].iterrows():
        t = row["Test_Time(s)"]
        j = np.searchsorted(rest_time, t, side="right") - 1

        if j < 0 or rest_time[j] < t - window:
            continue

        rest_i = rest_idx[j]
        v_rest = df.loc[rest_i, "Voltage(V)"]
        v_pulse = row["Voltage(V)"]
        I_p = row["Current(A)"]

        if abs(I_p) < 1e-6:
            continue

        R = (v_pulse - v_rest) / I_p

        if 0 < R < 0.5:
            records.append([row["SOC"], v_rest, R])

    return pd.DataFrame(records, columns=["SOC", "OCV", "R"])


# =========================================================
# Build OCV and R maps (smoothed + monotonic)
# =========================================================
def build_maps(pulses, df, R_fallback):
    soc_grid = np.linspace(0, 1, 200)

    if len(pulses) > 0:
        bins = np.linspace(0, 1, 101)
        pulses["bin"] = np.digitize(pulses["SOC"], bins) - 1
        agg = pulses.groupby("bin")[["SOC", "OCV", "R"]].median().dropna()

        OCV_map = np.interp(soc_grid, agg["SOC"], agg["OCV"])
        R_map = np.interp(soc_grid, agg["SOC"], agg["R"])
    else:
        rest = df[df["is_rest"]]
        OCV_map = np.interp(soc_grid, rest["SOC"], rest["Voltage(V)"])
        R_map = np.ones_like(soc_grid) * R_fallback

    # Smooth curves heavily to remove SOP wiggles
    OCV_map = savgol_filter(OCV_map, window_length=101, polyorder=3)
    R_map   = savgol_filter(R_map,   window_length=101, polyorder=3)

    # Enforce physical monotonicity
    OCV_map = np.maximum.accumulate(OCV_map)

    # Clamp R to avoid divide-by-zero
    R_map = np.clip(R_map, 0.005, None)

    print("[DEBUG] OCV range:", OCV_map.min(), OCV_map.max())
    print("[DEBUG] R range:",  R_map.min(),  R_map.max())

    return soc_grid, OCV_map, R_map


# =========================================================
# HPPC Peak Power SOP Calculation
# =========================================================
def compute_sop(soc_grid, OCV, R, vmin, vmax, idismax, ichgmax, socmin, socmax):

    I_dis = np.maximum((OCV - vmin) / R, 0)
    I_dis = np.minimum(I_dis, idismax)
    I_dis[soc_grid <= socmin] = 0
    P_dis = vmin * I_dis

    I_chg = np.maximum((vmax - OCV) / R, 0)
    I_chg = np.minimum(I_chg, ichgmax)
    I_chg[soc_grid >= socmax] = 0
    P_chg = vmax * I_chg

    return P_dis, P_chg


# =========================================================
# MAIN PIPELINE
# =========================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", required=True)
    parser.add_argument("--vmin", type=float, required=True)
    parser.add_argument("--vmax", type=float, required=True)
    parser.add_argument("--idismax", type=float, required=True)
    parser.add_argument("--ichgmax", type=float, required=True)
    parser.add_argument("--socmin", type=float, required=True)
    parser.add_argument("--socmax", type=float, required=True)
    args = parser.parse_args()

    I_REST_THR = 0.02
    I_PULSE_THR = 0.5
    WINDOW = 30
    R_FALLBACK = 0.04

    df = load_all_sheets(Path(args.xlsx))
    df = compute_soc(df)

    pulses = estimate_resistance(df, I_REST_THR, I_PULSE_THR, WINDOW)
    soc_grid, OCV_map, R_map = build_maps(pulses, df, R_FALLBACK)

    P_dis, P_chg = compute_sop(
        soc_grid, OCV_map, R_map,
        args.vmin, args.vmax,
        args.idismax, args.ichgmax,
        args.socmin, args.socmax
    )

    df["SOP_Discharge(W)"] = np.interp(df["SOC"], soc_grid, P_dis)
    df["SOP_Charge(W)"]    = np.interp(df["SOC"], soc_grid, P_chg)

    # =====================================================
    # Final output excel export
    # =====================================================
    df["Data_ID"] = df["Sample_ID"]

    output_cols = [
        "Data_ID",
        "Sheet",
        "Voltage(V)",
        "Current(A)",
        "SOC",
        "SOP_Discharge(W)",
        "SOP_Charge(W)"
    ]

    final_out = df[output_cols]

    os.makedirs("outputs", exist_ok=True)
    final_out.to_excel("outputs/FINAL_SOP_OUTPUT.xlsx", index=False)

    print("Final clean SOP output saved → outputs/FINAL_SOP_OUTPUT.xlsx")

    # =====================================================
    # Save maps for debugging
    # =====================================================
    maps = {"soc": soc_grid, "ocv": OCV_map, "r": R_map}
    with open("outputs/sop_maps.pkl", "wb") as f:
        pickle.dump(maps, f)

    print("Maps saved → outputs/sop_maps.pkl")

    # =====================================================
    # PLOTS
    # =====================================================
    fig, axes = plt.subplots(3, 1, figsize=(10, 14))

    # SOP vs Voltage
    axes[0].plot(OCV_map, P_dis, label="Discharge")
    axes[0].plot(OCV_map, P_chg, label="Charge")
    axes[0].set_title("SOP vs Voltage")
    axes[0].set_xlabel("Voltage (V)")
    axes[0].set_ylabel("Power (W)")
    axes[0].grid(True)
    axes[0].legend()

    # SOP vs Current
    axes[1].plot((OCV_map - args.vmin) / R_map, P_dis, label="Discharge")
    axes[1].plot((args.vmax - OCV_map) / R_map, P_chg, label="Charge")
    axes[1].set_title("SOP vs Current")
    axes[1].set_xlabel("Current (A)")
    axes[1].set_ylabel("Power (W)")
    axes[1].grid(True)
    axes[1].legend()

    # SOP vs SOC
    axes[2].plot(soc_grid, P_dis, label="Discharge")
    axes[2].plot(soc_grid, P_chg, label="Charge")
    axes[2].set_title("SOP vs SOC")
    axes[2].set_xlabel("State of Charge (SOC, fraction)")
    axes[2].set_ylabel("Power (W)")
    axes[2].grid(True)
    axes[2].legend()

    plt.tight_layout()
    plt.savefig("outputs/FINAL_SOP_PLOT.png", dpi=300)
    print("SOP plot saved → outputs/FINAL_SOP_PLOT.png")

    # =====================================================
    # VALIDATION
    # =====================================================
    dfv = final_out.copy()

    OCV_i = np.interp(dfv["SOC"], soc_grid, OCV_map)
    R_i   = np.interp(dfv["SOC"], soc_grid, R_map)

    I_dis = np.clip((OCV_i - args.vmin) / R_i, 0, args.idismax)
    I_chg = np.clip((args.vmax - OCV_i) / R_i, 0, args.ichgmax)

    dfv["P_dis_val"] = args.vmin * I_dis
    dfv["P_chg_val"] = args.vmax * I_chg

    dfv["Err_Discharge"] = dfv["P_dis_val"] - dfv["SOP_Discharge(W)"]
    dfv["Err_Charge"]    = dfv["P_chg_val"] - dfv["SOP_Charge(W)"]

    dfv.to_excel("outputs/SOP_VALIDATION_OUTPUT.xlsx", index=False)

    with open("outputs/SOP_VALIDATION_REPORT.txt", "w") as log:
        log.write("========== SOP VALIDATION REPORT ==========\n\n")
        log.write(dfv[["Err_Discharge", "Err_Charge"]].describe().to_string())
        log.write("\n")

    print("Validation complete. All outputs saved in /outputs/")


if __name__ == "__main__":
    main()
