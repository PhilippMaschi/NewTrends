import scipy.io
import pandas as pd
import numpy as np


def Create_out_temp_profile(input_dir_constant, OUTPUT_PATH_TEMP, RN, OUTPUT_PATH, YEAR, ds_hourly):
    # TODO soll die importdatei auf csv umgestellt werden??
    # mat["x"] und mat["y"] liefern die zwei numpy arrays aus dem file:
    #mat = scipy.io.loadmat(input_dir_constant + "dstr_hskd.mat")

    # monthly temperature per climate zone
    temp_file = str(RN) + '___mean_temperatur_' + str(YEAR) + '.csv'
    TEMP = pd.read_csv(OUTPUT_PATH_TEMP / temp_file)
    sol_rad_file = str(RN) + '__climate_data_solar_rad_' + str(YEAR) + '.csv'
    SOL_RAD = pd.read_csv(OUTPUT_PATH / sol_rad_file)
    num_clreg = len(SOL_RAD)

    sol_rad_north_clreg = SOL_RAD.iloc[:, 1: 13]
    sol_rad_east_west_clreg = SOL_RAD.iloc[:, 13: 25]
    sol_rad_south_clreg = SOL_RAD.iloc[:, 25: 37]

    # Days per month
    DpM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    h = np.arange(1, 25)

    # sol_hx = min(14, max(0, h + 0.5 - 6.5))
    sol_hx = []
    for i in h:
        if h[i-1] + 0.5 - 6.5 < 0:
            sol_hx.append(0)
        elif h[i-1] + 0.5 - 6.5 > 14:
            sol_hx.append(14)
        else:
            sol_hx.append(h[i-1] + 0.5 - 6.5)

    # sol_rad_norm = max(0, np.sin(3.1415 * sol_hx / 13)) / 8.2360
    sol_rad_norm = []
    for i in sol_hx:
        if np.sin(3.1415 * i / 13) / 8.2360 < 0:
            sol_rad_norm.append(0)
        else:
            sol_rad_norm.append(np.sin(3.1415 * i / 13) / 8.2360)

    T_e_HSKD_8760 = ds_hourly.loc[:, "te_obs"]
    T_e_8760_clreg = np.zeros((num_clreg, 8760))
    T_e_HSKD_8760_clreg = np.ones((num_clreg, 1)) * T_e_HSKD_8760


    a = 1
