import numpy as np


def core_rc_model(sol_rad, data):
    sol_rad = sol_rad.drop(columns=["climate_region_index"]).to_numpy()
    climate_region_index = data.loc[:, "climate_region_index"].to_numpy()
    UserProfile_idx = data.loc[:, "user_profile"].to_numpy()
    unique_climate_region_index = np.unique(climate_region_index)
    sol_rad_north = np.empty((1, 12), float)
    sol_rad_east_west = np.empty((1, 12))
    sol_rad_south = np.empty((1, 12))
    for climate_region in unique_climate_region_index:
        anzahl = len(np.where(climate_region_index == climate_region)[0])
        sol_rad_north = np.append(sol_rad_north,
                                  np.tile(sol_rad[int(climate_region-1), np.arange(12)], (anzahl, 1)), axis=0) # weil von 0 gezählt
        sol_rad_east_west = np.append(sol_rad_east_west,
                                  np.tile(sol_rad[int(climate_region-1), np.arange(12, 24)], (anzahl, 1)), axis=0)
        sol_rad_south = np.append(sol_rad_south,
                                  np.tile(sol_rad[int(climate_region-1), np.arange(24, 36)], (anzahl, 1)), axis=0)
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
    CM = data.loc[:, "CM_factor"].to_numpy() * Af
    Am = data.loc[:, "Am_factor"].to_numpy() * Af
    # internal gains
    Qi = data.loc[:, "spec_int_gains_cool_watt"].to_numpy() * Af
    HWB_norm = data.loc[:, "hbw_norm"].to_numpy()

    # window areas in celestial directions
    Awindows_rad_east_west = data.loc[:, "average_effective_area_wind_west_east_red_cool"].to_numpy()
    Awindows_rad_south = data.loc[:, "average_effective_area_wind_south_red_cool"].to_numpy()
    Awindows_rad_north = data.loc[:, "average_effective_area_wind_north_red_cool"].to_numpy()

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

    num_bc = len(Qi)
    print("Number if building classes: " + str(num_bc))

    # Kopplung Temp Luft mit Temp Surface Knoten s
    his = 3.45
    Htr_is = his * Atot
    Htr_1 = 1 / (1./Hve + 1./Htr_is) # Equ. C.6
    Htr_2 = Htr_1 + Htr_w  # Equ. C.7

    # kopplung zwischen Masse und  Zentralen Knoten s (surface)
    hms = 9.1 # W / m2K from Equ.C.3
    Htr_ms = hms * Am



    a = 1
