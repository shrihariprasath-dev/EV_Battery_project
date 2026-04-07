# =========================================================
# SOP Estimation for battery cell INR18650_20r 
# Author:Shrihariprasath Basuvaiyan
# =========================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
import os
import pickle

# =========================================================
# Load Data Sheet and merge it
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
# Calculate SOC first
# =========================================================
def compute_soc(df):
    net = df["Charge_Capacity(Ah)"].fillna(0) - df["Discharge_Capacity(Ah)"].fillna(0)
    soc = (net - net.min()) / (net.max() - net.min())
    df["SOC"] = soc.clip(0, 1)
    return df


# =========================================================
# Estimate resistance pulse
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
        i_p = row["Current(A)"]

        if abs(i_p) < 1e-6:
            continue

        R = (v_pulse - v_rest) / i_p
        if 0 < R < 0.5:
            records.append([row["SOC"], v_rest, R])

    return pd.DataFrame(records, columns=["SOC", "OCV", "R"])


# =========================================================
# Build map for validation
# =========================================================
def build_maps(pulses, df, R_fallback):
    soc_grid = np.linspace(0, 1, 200)

    if len(pulses) > 0:
        pulses["bin"] = pd.cut(pulses["SOC"], bins=np.linspace(0, 1, 101), labels=False)
        agg = pulses.groupby("bin").median()[["SOC", "OCV", "R"]].dropna()

        OCV_map = np.interp(soc_grid, agg["SOC"], agg["OCV"])
        R_map = np.interp(soc_grid, agg["SOC"], agg["R"])
    else:
        rest = df.loc[df["is_rest"]]
        OCV_map = np.interp(soc_grid, rest["SOC"], rest["Voltage(V)"])
        R_map = np.ones_like(soc_grid) * R_fallback

    return soc_grid, OCV_map, R_map


# =========================================================
# Calculate SOP
# ========================================================
def compute_sop(soc_grid, OCV, R, vmin, vmax, idismax, ichgmax, socmin, socmax):
    I_dis_allowed = (vmin - OCV) / R
    I_chg_allowed = (vmax - OCV) / R

    I_dis = -np.minimum(idismax, np.maximum(0, -I_dis_allowed))
    I_chg = np.minimum(ichgmax, np.maximum(0, I_chg_allowed))

    I_dis[soc_grid <= socmin] = 0
    I_chg[soc_grid >= socmax] = 0

    P_dis = vmin * (-I_dis)
    P_chg = vmax * I_chg

    return P_dis, P_chg


# =========================================================
#   Main function and validation
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

    # CONSTANTS
    I_REST_THR = 0.02
    I_PULSE_THR = 0.5
    WINDOW = 30
    R_FALLBACK = 0.04

    # =====================================================
    # SOP Estimation
    # =====================================================
    df = load_all_sheets(Path(args.xlsx))
    df = compute_soc(df)
    pulses = estimate_resistance(df, I_REST_THR, I_PULSE_THR, WINDOW)
    soc_grid, OCV_map, R_map = build_maps(pulses, df, R_FALLBACK)
    P_dis, P_chg = compute_sop(soc_grid, OCV_map, R_map,
                               args.vmin, args.vmax,
                               args.idismax, args.ichgmax,
                               args.socmin, args.socmax)

    df["SOP_Discharge(W)"] = np.interp(df["SOC"], soc_grid, P_dis)
    df["SOP_Charge(W)"] = np.interp(df["SOC"], soc_grid, P_chg)

    out = df[["Sample_ID", "Sheet", "Voltage(V)", "Current(A)", "SOC",
              "SOP_Discharge(W)", "SOP_Charge(W)"]]

    os.makedirs("outputs", exist_ok=True)
    out.to_excel("outputs/FINAL_SOP_OUTPUT.xlsx", index=False)
    print("Final consolidated SOP file saved → outputs/FINAL_SOP_OUTPUT.xlsx")

    # =====================================================
    # Save map for validation
    # =====================================================
    maps = {"soc": soc_grid, "ocv": OCV_map, "r": R_map}
    with open("outputs/sop_maps.pkl", "wb") as f:
        pickle.dump(maps, f)
    print("Saved SOP maps → outputs/sop_maps.pkl")

    # =====================================================
    # Plots for SOP VS VOLTAGE VS CURRENT VS SOC limits
    # =====================================================
    fig, axes = plt.subplots(3, 1, figsize=(10, 14))

    axes[0].plot(OCV_map, P_dis, label="Discharge")
    axes[0].plot(OCV_map, P_chg, label="Charge")
    axes[0].set_title("SOP vs Voltage")
    axes[0].grid(True)
    axes[0].legend()

    I_axis_dis = (args.vmin - OCV_map) / R_map
    I_axis_chg = (args.vmax - OCV_map) / R_map

    I_axis_dis = np.clip(I_axis_dis, -args.idismax, 0)
    I_axis_chg = np.clip(I_axis_chg, 0, args.ichgmax)

    axes[1].plot(I_axis_dis, P_dis, label="Discharge")
    axes[1].plot(I_axis_chg, P_chg, label="Charge")
    axes[1].set_title("SOP vs Current")
    axes[1].grid(True)
    axes[1].legend()

    axes[2].plot(soc_grid, P_dis)
    axes[2].plot(soc_grid, P_chg)
    axes[2].set_title("SOP vs SOC")
    axes[2].grid(True)

    plt.tight_layout()
    plt.savefig("outputs/FINAL_SOP_PLOT.png", dpi=300)
    print("Plot saved → outputs/FINAL_SOP_PLOT.png")

    # =====================================================
    # validation
    # =====================================================
    print("\nStarting SOP Validation...")

    dfv = pd.read_excel("outputs/FINAL_SOP_OUTPUT.xlsx")

    OCV_i = np.interp(dfv["SOC"], soc_grid, OCV_map)
    R_i = np.interp(dfv["SOC"], soc_grid, R_map)

    I_dis = -(args.vmin - OCV_i) / R_i
    I_dis = np.clip(I_dis, 0, float(args.idismax))
    I_dis[dfv["SOC"] <= args.socmin] = 0

    I_chg = (args.vmax - OCV_i) / R_i
    I_chg = np.clip(I_chg, 0, float(args.ichgmax))
    I_chg[dfv["SOC"] >= args.socmax] = 0

    dfv["P_dis_val"] = args.vmin * I_dis
    dfv["P_chg_val"] = args.vmax * I_chg

    dfv["Err_Discharge"] = dfv["P_dis_val"] - dfv["SOP_Discharge(W)"]
    dfv["Err_Charge"] = dfv["P_chg_val"] - dfv["SOP_Charge(W)"]

    dfv.to_excel("outputs/SOP_VALIDATION_OUTPUT.xlsx", index=False)
    print("\nValidation result saved → outputs/SOP_VALIDATION_OUTPUT.xlsx")

    print("\nValidation Error Summary:")
    print(dfv[["Err_Discharge", "Err_Charge"]].describe())

if __name__ == "__main__":
    main()
