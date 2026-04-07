flowchart TD

    A([Start]) --> B[Read CLI Arguments\n--xlsx, vmin, vmax, idismax, ichgmax, socmin, socmax]

    B --> C[Load Excel Sheets\nIdentify 'Channel*' sheets\nMerge & clean data]

    C --> D[Compute SOC\nUsing net Ah integration]

    D --> E[Estimate Resistance Pulses\nDetect rest & pulse regions\nCompute R = ΔV / ΔI]

    E --> F[Build OCV & R Maps\nBin pulses\nMedian filtering\n200‑point interpolation]

    F --> G[Compute SOP\nCharge & Discharge limits\nVoltage & current clipping]

    G --> H[Interpolate SOP Back\nMap SOP onto full dataset rows]

    H --> I[Export Excel Output\nFINAL_SOP_OUTPUT.xlsx]

    I --> J[Generate SOP Plots\nVoltage, Current, SOC curves\nSave FINAL_SOP_PLOT.png]

    J --> K([End])
