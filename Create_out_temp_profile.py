import scipy.io
import pandas as pd
import numpy as np
from scipy import interpolate


def Create_out_temp_profile(input_dir_constant, OUTPUT_PATH_TEMP, RN, OUTPUT_PATH, YEAR, ds_hourly):
    # TODO soll die importdatei auf csv umgestellt werden??
    # M["x"] und M["Y"] liefern die zwei numpy arrays aus dem file:
    M = scipy.io.loadmat(input_dir_constant + "dstr_hskd.mat")

    # monthly temperature per climate zone
    temp_file = str(RN) + '___mean_temperatur_' + str(YEAR) + '.csv'
    TEMP = pd.read_csv(OUTPUT_PATH_TEMP / temp_file)
    TEMP = TEMP.set_index("month")
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
    T_e_HSKD_8760_clreg = pd.concat([T_e_HSKD_8760] * num_clreg, axis=1)

    # Temperature and Climate:
    Te_month_mean2 = np.zeros((num_clreg, 12))
    dT_nextday = np.zeros(num_clreg)
    dT_thisday = np.zeros(num_clreg)

    # Differenz between daily min temperature and daily avg. temperature per month:
    Te1 = np.array([1.90, 0.30, 5.40, 8.30, 14.00, 17.60, 19.10, 18.50, 15.00, 10.20, 4.40, 2.40])
    Te2 = np.array([3.1, 2.1, 8.1, 11.7, 18, 21.2, 23, 22.1, 18.6, 13, 6.4, 3.4])
    DeltaT05 = Te2 - Te1

    # TODO von pandas auf numpy umsteigen weil schneller in schleifen...
    for month in np.arange(1, 13):
        days_this_month = DpM[month-1]
        num_hours = 24 * days_this_month

        # Erstellen des DailyTfacotrs mit std=0.0172 und mean=1
        Daily_T_factor2 = np.random.normal(loc=1, scale=0.0172, size=days_this_month)
        #Daily_T_factor = interpolate.splrep(M["Y"], M["x"])

        # daily temperatures:
        Temin = TEMP.loc[month, :] - DeltaT05[month-1]
        Temax = TEMP.loc[month, :] + DeltaT05[month-1]
        angle_offset = -9  # TODO was ist das? ändert er sich für andere länder?
        sinus_fkt = np.sin((np.arange(0.5, 24) + angle_offset) / (24 / 2 / 3.1415))
        Te_month_konst = pd.concat([(Temax - Temin) / 2 + Temin] * 24, axis=1) + \
                         pd.concat([(Temax - Temin) / 2 * n for n in sinus_fkt], axis=1)

        if month == 1:
            Tm_0 = pd.concat([(Te_month_konst.iloc[:, 0] * 5 + 20) / 6] * 24, axis=1)
            Tm_10 = pd.concat([(Te_month_konst.iloc[:, 0] * 2 + 20) / 3] * 24, axis=1)

        if month > 1:
            delta_Tmonth_prev = TEMP.loc[month, :] - TEMP.loc[month-1, :]
        else:
            delta_Tmonth_prev = TEMP.loc[month, :] - TEMP.loc[12, :] # TODO -temp von Dez?

        if month < 12:
            delta_Tmonth_next = TEMP.loc[month + 1, :] - TEMP.loc[month, :]
        else:
            delta_Tmonth_next = TEMP.loc[1, :] - TEMP.loc[month, :]

        # describes the relative change of the month compared to next and last month times all days??
        days_prev_trend_prev_month = days_this_month * (delta_Tmonth_next / (delta_Tmonth_next + delta_Tmonth_prev))
        days_prev_trend_prev_month = days_prev_trend_prev_month.reset_index(drop=True)

        # convert TEMP to np array:
        Te_mean_month_clreg = TEMP.to_numpy()
        for day in np.arange(days_this_month): # achtung tage fangen bei 0 an!
            # Variation der Tagesmitteltemperaturen innerhalb eines Monats
            curr_Daily_T_factor = (TEMP.loc[month, :] + 273) * Daily_T_factor2[day] - 273 - TEMP.loc[month, :]
            Te = Te_month_konst + pd.concat([curr_Daily_T_factor] * 24, axis=1)
            Te.columns = [np.arange(0, Te.shape[1])]

            # Trend der Tagestemperatur zur durchschnittlichen Tagestemp des nächsten monats
            idx = days_prev_trend_prev_month.loc[days_prev_trend_prev_month > day].index
            dT_thisday[idx] = - ((days_prev_trend_prev_month.values[idx] - day) / (
                    days_prev_trend_prev_month.values[idx] - 1) * delta_Tmonth_prev.values[idx] / 2)
            idx = days_prev_trend_prev_month.loc[days_prev_trend_prev_month < day].index
            # TODO warum 30- und nicht monatstag?
            dT_thisday[idx] = ((day - days_prev_trend_prev_month.values[idx]) /
                                np.maximum(1, np.maximum(0, 30 - days_prev_trend_prev_month.values[idx])) *
                                delta_Tmonth_next.values[idx] / 2)
            Te = Te.reset_index(drop=True).values + np.tile(dT_thisday, (24, 1)).T
            # TODO Te ist jetzt numpy array.. fange an alles in numpy zu machen
            idx = days_prev_trend_prev_month.loc[days_prev_trend_prev_month > (day + 1)].index
            dT_nextday[idx] = - ((days_prev_trend_prev_month.values[idx] - day) / (
                    days_prev_trend_prev_month.values[idx] - 1) * delta_Tmonth_prev.values[idx] / 2)
            idx = days_prev_trend_prev_month.loc[days_prev_trend_prev_month < (day + 1)].index
            dT_nextday[idx] = ((day - days_prev_trend_prev_month.values[idx]) /
                                np.maximum(1, np.maximum(0, 30 - days_prev_trend_prev_month.values[idx])) *
                                delta_Tmonth_next.values[idx] / 2)

            # Trend innerhalb des Tages zur Tagestemperatur des nächsten Tages
            delta_Te = (Te_month_konst(:, 1) + 273) *Daily_T_factor2(min(day + 1, days_this_month)) - (Te_month_konst(:,1)+273) * Daily_T_factor2(day) + dT_nextday - dT_thisday

        a = 1
