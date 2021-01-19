import numpy as np



def core_rc_model(sol_rad, data, DHW_need_day_m2_8760_up, DHW_loss_Circulation_040_day_m2_8760_up,
                  share_Circulation_DHW, T_e_HSKD_8760_clreg, Tset_heating_8760_up, Tset_cooling_8760_up):
    # umbenennung der variablen zum vergleich mit matlab und in shape (..., 8760)
    T_e_clreg = T_e_HSKD_8760_clreg

    sol_rad = sol_rad.drop(columns=["climate_region_index"]).to_numpy()
    climate_region_index = data.loc[:, "climate_region_index"].to_numpy().astype(int)
    UserProfile_idx = data.loc[:, "user_profile"].to_numpy().astype(int)
    unique_climate_region_index = np.unique(climate_region_index).astype(int)
    sol_rad_north = np.empty((1, 12), float)
    sol_rad_east_west = np.empty((1, 12))
    sol_rad_south = np.empty((1, 12))
    for climate_region in unique_climate_region_index:
        anzahl = len(np.where(climate_region_index == climate_region)[0])
        sol_rad_north = np.append(sol_rad_north,
                                  np.tile(sol_rad[int(climate_region - 1), np.arange(12)], (anzahl, 1)),
                                  axis=0)  # weil von 0 gezählt
        sol_rad_east_west = np.append(sol_rad_east_west,
                                      np.tile(sol_rad[int(climate_region - 1), np.arange(12, 24)], (anzahl, 1)), axis=0)
        sol_rad_south = np.append(sol_rad_south,
                                  np.tile(sol_rad[int(climate_region - 1), np.arange(24, 36)], (anzahl, 1)), axis=0)
    sol_rad_north = np.delete(sol_rad_north, 0, axis=0)
    sol_rad_east_west = np.delete(sol_rad_east_west, 0, axis=0)
    sol_rad_south = np.delete(sol_rad_south, 0, axis=0)

    Af = data.loc[:, "Af"].to_numpy()
    Atot = 4.5 * Af
    Hve = data.loc[:, "Hve"].to_numpy()
    Htr_w = data.loc[:, "Htr_w"].to_numpy()
    # opake Bauteile
    Hop = data.loc[:, "Hop"].to_numpy()
    # Speicherkapazität
    Cm = data.loc[:, "CM_factor"].to_numpy() * Af
    Am = data.loc[:, "Am_factor"].to_numpy() * Af
    # internal gains
    Qi = data.loc[:, "spec_int_gains_cool_watt"].to_numpy() * Af
    HWB_norm = data.loc[:, "hwb_norm"].to_numpy()

    # window areas in celestial directions
    Awindows_rad_east_west = data.loc[:, "average_effective_area_wind_west_east_red_cool"].to_numpy()
    Awindows_rad_south = data.loc[:, "average_effective_area_wind_south_red_cool"].to_numpy()
    Awindows_rad_north = data.loc[:, "average_effective_area_wind_north_red_cool"].to_numpy()

    DpM = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    h = np.arange(1, 25)
    # sol_hx = min(14, max(0, h + 0.5 - 6.5))
    sol_hx = []
    for i in h:
        if h[i - 1] + 0.5 - 6.5 < 0:
            sol_hx.append(0)
        elif h[i - 1] + 0.5 - 6.5 > 14:
            sol_hx.append(14)
        else:
            sol_hx.append(h[i - 1] + 0.5 - 6.5)

    # sol_rad_norm = max(0, np.sin(3.1415 * sol_hx / 13)) / 8.2360
    sol_rad_norm = []
    for i in sol_hx:
        if np.sin(3.1415 * i / 13) / 8.2360 < 0:
            sol_rad_norm.append(0)
        else:
            sol_rad_norm.append(np.sin(3.1415 * i / 13) / 8.2360)

    num_bc = len(Qi)
    print("Number if building classes: " + str(num_bc))

    # Kopplung Temp Luft mit Temp Surface Knoten s
    his = 3.45
    Htr_is = his * Atot
    Htr_1 = 1 / (1. / Hve + 1. / Htr_is)  # Equ. C.6
    Htr_2 = Htr_1 + Htr_w  # Equ. C.7

    # kopplung zwischen Masse und  zentralen Knoten s (surface)
    hms = 9.1  # W / m2K from Equ.C.3
    Htr_ms = hms * Am
    Htr_em = 1 / (1 / Hop - 1 / Htr_ms)
    Htr_3 = 1 / (1 / Htr_2 + 1 / Htr_ms)  # Equ.C.8
    subVar1 = Cm / 3600 - 0.5 * (Htr_3 + Htr_em)  # Part of Equ.C.4
    subVar2 = Cm / 3600 + 0.5 * (Htr_3 + Htr_em)  # Part of Equ.C.4

    # insert frames that will be needed later? matlab zeile 95-111

    # DHW Profile:
    DHW_losses_m2_8760_up = share_Circulation_DHW * DHW_loss_Circulation_040_day_m2_8760_up + 0.3 * \
                            DHW_need_day_m2_8760_up
    Q_DHW_losses = DHW_losses_m2_8760_up[UserProfile_idx, :] * np.tile(Af, (8760, 1)).T
    Q_DHW_LOAD_8760 = DHW_need_day_m2_8760_up[UserProfile_idx, :] * np.tile(Af, (8760, 1)).T + Q_DHW_losses

    cum_hours = 0
    for month in range(12):
        days_this_month = DpM[month]
        num_hours = 24 * days_this_month

        if month == 0:
            # Estimate starting value of first temperature sets
            Tm_prev_hour = (5 * T_e_clreg[climate_region_index, 0] + 1 * 20) / 6
            Q_HC_prev_hour = 10

        #  Heating and Cooling Heat flow rate (Thermal power) need
        PHIHC_nd = np.zeros((num_bc, num_hours))
        # Like PHIHC_nd but with 10 W/m2 internal load
        PHIHC_nd10 = PHIHC_nd + np.tile(Af * 10, (num_hours, 1)).T

        for day in range(days_this_month):
            # time_day_vector represents the index for the hours of one day (eg: 24-48 for second day in year)
            time_day_vector = np.arange(cum_hours + day * 24, cum_hours + (day+1) * 24)

            # outdoor temperature
            Te = T_e_clreg[np.ix_(climate_region_index, time_day_vector)]

            # TODO maybe iterate over the first day twice??
            # for the first day if the year the "prev_hour" has to be set manually:
            # if month == 0 and day == 0:


            # iterate through hours:
            for hour in range(24):
                if hour == 0:
                    prev_hour = 24
                else:
                    prev_hour = hour - 1

                # solar radiation
                sol_rad_n = sol_rad_norm[hour] * sol_rad_north[:, month] * 24
                sol_rad_ea = sol_rad_norm[hour] * sol_rad_east_west[:, month] * 24
                sol_rad_s = sol_rad_norm[hour] * sol_rad_south[:, month] * 24

                # calculate energy needs:
                # get desired Heating and Cooling Set Point Temperature
                Tset_h = Tset_heating_8760_up[UserProfile_idx, cum_hours + day * 24 + hour]

                # TODO vielleicht User Profile Einbauen??
                # estimate User behaviour: if outdoor temp drops, user will also reduce indoor temp slightly
                Tset_h = Tset_h + (Te[:, hour] - Tset_h + 12) / 8
                Tset_c = Tset_cooling_8760_up[UserProfile_idx, cum_hours + day * 24 + hour]



    a = 1
