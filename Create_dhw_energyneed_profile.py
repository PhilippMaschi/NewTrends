import pandas as pd
import numpy as np


def CREATE_DHW_ENERGYDEMAND_PROFILE(RN, YEAR, OUTPUT_PATH):
    datei = RN + '__dynamic_calc_data_up_' + str(YEAR) + '.csv'
    data_user_profiles = pd.read_csv(OUTPUT_PATH / datei, usecols=["DHW_per_day"])
    num_up = len(data_user_profiles)

    # to numpy:
    DHW_need_day_m2 = data_user_profiles.to_numpy()
    DHW_need_day_m2_8760_up = np.ones((num_up, 8760))

    DpM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    cum_hours = 0
    use_HoursPerYear

    a=1
