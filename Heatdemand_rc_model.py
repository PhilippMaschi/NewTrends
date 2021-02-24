import numpy as np
import pandas as pd
import os
from pathlib import Path
from Create_out_temp_profile import Create_out_temp_profile
from Create_set_temp_profile import CREATE_SET_TEMP_PROFILE
from Create_dhw_energyneed_profile import CREATE_DHW_ENERGYDEMAND_PROFILE
from Core_rc_model import core_rc_model
import h5py
import timeit
from Simple_plots import *


def read_h5(filename):
    print('reading hf file...')
    dict_ = {}
    hf = h5py.File(filename, "r")
    # save all arrays from hf to dict as np.array:
    for key in hf.keys():
        dict_[key] = np.array(hf.get(key))
    hf.close()
    print('done')
    return dict_

def save_to_h5(outputpath, h5_name, Q_H_LOAD_8760, Q_C_LOAD_8760, Q_DHW_LOAD_8760, Af, bc_num_building_not_Zero_vctr,
               climate_region_index, share_Circulation_DHW, T_e_HSKD_8760_clreg, Tset_heating_8760_up,
               Tset_cooling_8760_up):
    print('hf file is being saved...')
    starttimeh5 = timeit.default_timer()
    # check if folder exists:
    try:
        os.makedirs(outputpath)
    except FileExistsError:
        pass
    # create file object, h5_name is path and name of file
    hf = h5py.File(outputpath + h5_name, "w")
    # files can be compressed with compression="lzf" and compression_opts=0-9 to save space, but then it reads slower
    # renaming the variables from here on!
    hf.create_dataset("Heating_load", data=Q_H_LOAD_8760)
    hf.create_dataset("Cooling_load", data=Q_C_LOAD_8760)
    hf.create_dataset("DHW_load", data=Q_DHW_LOAD_8760)

    hf.create_dataset("Af", data=Af)
    hf.create_dataset("bc_num_building_not_Zero_vctr", data=bc_num_building_not_Zero_vctr)
    hf.create_dataset("climate_region_index", data=climate_region_index)

    hf.create_dataset("share_Circulation_DHW", data=share_Circulation_DHW)
    hf.create_dataset("T_outside", data=T_e_HSKD_8760_clreg)
    hf.create_dataset("T_set_heating", data=Tset_heating_8760_up)
    hf.create_dataset("T_set_cooling", data=Tset_cooling_8760_up)
    # save data
    hf.close()
    print('saving hf completed')
    print("Time for saving to h5: ", timeit.default_timer() - starttimeh5)


def Heatdemand_rc_model(OUTPUT_PATH, OUTPUT_PATH_NUM_BUILD, OUTPUT_PATH_TEMP, RN, YEAR, climdata_file_name, load_data):
    # TODO für testen:
    YEAR = 2050

    input_dir_constant = 'inputdata/'
    BCAT_1_3 = np.ones((6, 3))
    BCAT_4_8 = np.ones((1, 5))
    NUM_GFA_BEFORE_BCAT_1_3 = np.ones((6, 3))
    NUM_GFA_BEFORE_BCAT_4_8 = np.ones((1, 5))
    NUM_GFA_AFTER_BCAT_1_3 = np.ones((6, 3))
    NUM_GFA_AFTER_BCAT_4_8 = np.ones((1, 5))

    for k in range(1, 7):
        # TODO diese if abfragen in funktion ändern weil blöd für andere länder
        if k == 1:
            # Weichstätten:
            nominal_gridloss_factor = 0.16
            region_obs_data_file_name = "Weichstaetten"
            t_movavg_DHW = 2
            t_movavg_SH = 3
            share_Circulation_DHW = 0
            GE_IDX = 1061

            # Wohngebäude mit je 6 Bauperioden (4 historisch, 5 Leer, 6 Neubau)
            # BCAT_1_3 = [1.0,0.5, 0.2, 0.2, 0.0, 1] *[1, 0.5, 0.3]
            # TODO Andi fragen was es mit den BCAT matrizen auf sich hat ud was share_Circulation_DHW bedeuted!
            BCAT_4_8[0, -2:] = 0

            TGridmom = 75
            TGridmin = 75
            scale_DHW = 1

        # obs_data_file_name combines region and climate data file names
        obs_data_file_name = region_obs_data_file_name + '-' + climdata_file_name

        # load building stock data exportet by invert run:
        datei = str(RN) + "__dynamic_calc_data_bc_" + str(YEAR) + ".npz"
        data_np = np.load(OUTPUT_PATH / datei)
        data = pd.DataFrame(data=data_np["arr_0"], columns=data_np["arr_1"][0])
        data.columns = data.columns.str.decode("utf-8")
        data.columns = data.columns.str.replace(" ", "")

        datei_num_build = "_BC_BUI_GE_" + str(YEAR) + ".npz"
        data_num_build_per_GE_np = np.load(OUTPUT_PATH_NUM_BUILD / datei_num_build)
        data_num_build_per_GE = pd.DataFrame(data=data_num_build_per_GE_np["arr_0"],
                                             columns=data_num_build_per_GE_np["arr_1"][0])
        data_num_build_per_GE.columns = data_num_build_per_GE.columns.str.decode("utf-8")
        data_num_build_per_GE.columns = data_num_build_per_GE.columns.str.replace(" ", "")

        datei_num_gfa_per_GE = "_BC_GFA_GE_" + str(YEAR) + ".npz"
        data_num_gfa_per_GE_np = np.load(OUTPUT_PATH_NUM_BUILD / datei_num_gfa_per_GE)
        data_num_gfa_per_GE = pd.DataFrame(data=data_num_gfa_per_GE_np["arr_0"],
                                           columns=data_num_gfa_per_GE_np["arr_1"][0])
        data_num_gfa_per_GE.columns = data_num_gfa_per_GE.columns.str.decode("utf-8")

        datei_num_gfa_per_GE = "_BC_BUILD_CAT_" + str(YEAR) + ".npz"
        data_Bcat_per_BC_np = np.load(OUTPUT_PATH_NUM_BUILD / datei_num_gfa_per_GE)
        data_Bcat_per_BC = pd.DataFrame(data=data_Bcat_per_BC_np["arr_0"], columns=data_Bcat_per_BC_np["arr_1"][0])
        data_Bcat_per_BC.columns = data_Bcat_per_BC.columns.str.decode("utf-8")

        if str(GE_IDX) in data_num_build_per_GE.columns:
            col = data_num_build_per_GE.columns.get_loc(str(GE_IDX))
        else:
            print("Gemeinde nicht gefunden!")

        if region_obs_data_file_name == "Wien":
            print("da musst du noch irgendeinen Shit machen")
        else:
            data_num_build_per_GE = data_num_build_per_GE.iloc[:, [0, col]]
            data_num_gfa_per_GE = data_num_gfa_per_GE.iloc[:, [0, col]]

        # time loops:
        starttime = timeit.default_timer()

        # Wohngebäude 1 bis 3
        # Bauperioden 1 bis 6
        if load_data == False:
            for i in range(1, 4):
                for j in range(1, 7):
                    idx = data_Bcat_per_BC.loc[(data_Bcat_per_BC["bcat_map"] == i) &
                                               (data_Bcat_per_BC["constrp_map"] == j), :].index
                    data_num_build_per_GE.iloc[idx, 1] = data_num_build_per_GE.iloc[idx, 1] * BCAT_1_3[
                        j - 1, i - 1]  # weil python bei 0 anfängt zu zählen
                    data_num_gfa_per_GE.iloc[idx, 1] = data_num_gfa_per_GE.iloc[idx, 1] * BCAT_1_3[j - 1, i - 1]

                    NUM_GFA_BEFORE_BCAT_1_3[j - 1, i - 1] = data_num_gfa_per_GE.iloc[idx, 1].sum()

            # für kategorien 4 bis 8:
            for i in range(1, 6):
                idx = data_Bcat_per_BC.loc[data_Bcat_per_BC["bcat_map"] == (i + 3)].index
                data_num_build_per_GE.iloc[idx, 1] = data_num_build_per_GE.iloc[idx, 1] * BCAT_4_8[0, i - 1]
                data_num_gfa_per_GE.iloc[idx, 1] = data_num_gfa_per_GE.iloc[idx, 1] * BCAT_4_8[0, i - 1]

                NUM_GFA_BEFORE_BCAT_4_8[0, i - 1] = data_num_gfa_per_GE.iloc[idx, 1].sum()

            # TODO Wieso dieses Limit?
            limit = 0.000002

            bc_num_building_not_Zero_vctr = (data_num_gfa_per_GE.iloc[:, 1] / data_num_gfa_per_GE.iloc[:,
                                                                              1].sum() > limit) & \
                                            (data_num_gfa_per_GE.iloc[:, 0] < data.iloc[:, 0].size)
            bc_idx_not_Zero = data_num_build_per_GE[bc_num_building_not_Zero_vctr].iloc[:, 0]
            bc_num_build = data_num_build_per_GE[bc_num_building_not_Zero_vctr].iloc[:, 1]
            print("Number of BC classes: " + str(bc_num_build.size))
            bc_gfa = data_num_gfa_per_GE[bc_num_building_not_Zero_vctr].iloc[:, 1]
            Bcat_per_BC = data_Bcat_per_BC[bc_num_building_not_Zero_vctr]
            print("WG")
            for i in range(1, 4):
                print("WG type " + str(i))
                for j in range(1, 7):  # Baukategorien
                    idx = Bcat_per_BC.loc[(Bcat_per_BC["bcat_map"] == i) &
                                          (Bcat_per_BC["constrp_map"] == j), :].index
                    NUM_GFA_AFTER_BCAT_1_3[j - 1, i - 1] = bc_gfa[idx].sum()
                    ratio = NUM_GFA_BEFORE_BCAT_1_3[j - 1, i - 1] / max(0.000001, NUM_GFA_AFTER_BCAT_1_3[j - 1, i - 1])
                    # TODO wieso 8? Ist das das maximale mögliche ratio oder einfach so?
                    ratio = min(8, max(1, ratio))
                    bc_gfa[idx] = bc_gfa[idx] * ratio
                    bc_num_build[idx] = bc_num_build[idx] * ratio

            print("NWG")
            for i in range(1, 6):
                idx = Bcat_per_BC.loc[Bcat_per_BC["bcat_map"] == (i + 3)].index
                NUM_GFA_AFTER_BCAT_4_8[0, i - 1] = bc_gfa[idx].sum()
                ratio = NUM_GFA_BEFORE_BCAT_4_8[0, i - 1] / max(0.000001, NUM_GFA_AFTER_BCAT_4_8[0, i - 1])
                ratio = min(8, max(1, ratio))
                bc_gfa[idx] = bc_gfa[idx] * ratio
                bc_num_build[idx] = bc_num_build[idx] * ratio

            # reducing the data:
            data = data.set_index("bc_index")
            data_red = data.loc[bc_idx_not_Zero.values, :]

            # load observed Grid Data:
            obs_data = pd.read_csv(input_dir_constant + climdata_file_name + ".csv", header=None)

            HoursPerYear = len(obs_data)
            # observed hourly temperature and load profile:
            ds_hourly = pd.DataFrame({"te_obs": obs_data[1].values,
                                      "load_obs": obs_data[2].values})

            # Consider only relative Values for load profile:
            ds_hourly.loc[:, "load_obs"] = ds_hourly.loc[:, "load_obs"] / ds_hourly.loc[:, "load_obs"].mean()

            # TODO fragen ob bei te_obs in matlab nicht ein fehler passiert ist (Zeile 288)
            # data reshaped daily:
            ds_daily = pd.DataFrame({"te_obs":
                                         ds_hourly["te_obs"].values.reshape((24, int(len(ds_hourly) / 24))).mean(axis=0),
                                     "load_obs":
                                         ds_hourly["load_obs"].values.reshape((24, int(len(ds_hourly) / 24))).sum(axis=0)})

            # data annually:
            ds_annually = pd.DataFrame({"load_obs": obs_data.loc[:, 2].sum(),
                                        "te_obs": ds_hourly.loc[:, "te_obs"].mean()}, index=[0])

            # call create temp profile skript: Ergebnisse sind numpy frames!
            T_e_8760_clreg, T_e_HSKD_8760_clreg = \
                Create_out_temp_profile(input_dir_constant, OUTPUT_PATH_TEMP, RN, OUTPUT_PATH, YEAR, ds_hourly)

            #  CREATE SET TEMPERATURE PROFILE
            Tset_heating_8760_up, Tset_cooling_8760_up = CREATE_SET_TEMP_PROFILE(RN, YEAR, OUTPUT_PATH)

            # TODO das macht überhaupt keinen Sinn (T_e_HSKD_8760_clreg) (komm später zurück warum das gebraucht wird.
            # TODO eventuell auch auf numpy array umstellen (nur mit welchen column names??)
            # ds_hourly = pd.concat([ds_hourly, pd.DataFrame(T_e_HSKD_8760_clreg), pd.DataFrame(Tset_heating_8760_up),
            #                        pd.DataFrame(Tset_cooling_8760_up)], axis=1,
            #                       keys=["orig", "T_e_clreg", "Tset_heating_8760_up", "Tset_cooling_8760_up"])

            # CREATE DHW PROFILE
            DHW_need_day_m2_8760_up, DHW_loss_Circulation_040_day_m2_8760_up = \
                CREATE_DHW_ENERGYDEMAND_PROFILE(RN, YEAR, OUTPUT_PATH)

            # TODO implement data of building segments!
            # data of building segments (number of buildings)
            # data_bssh = load([OUTPUT_PATH, RN '_dynamic_calc_data_bssh_' num2str(YEAR) '.mat'])

            # solar radiation
            datei = RN + '__climate_data_solar_rad_' + str(YEAR) + ".csv"
            sol_rad = pd.read_csv(OUTPUT_PATH / datei)

            # core rc model nach DIN EN ISO 13790:
            Q_H_LOAD_8760, Q_C_LOAD_8760, Q_DHW_LOAD_8760, Af, bc_num_building_not_Zero_vctr, climate_region_index =\
                core_rc_model(sol_rad, data_red, DHW_need_day_m2_8760_up, DHW_loss_Circulation_040_day_m2_8760_up,
                          share_Circulation_DHW, T_e_HSKD_8760_clreg, Tset_heating_8760_up, Tset_cooling_8760_up,
                          bc_num_building_not_Zero_vctr, obs_data_file_name)


            # save data to h5 file for fast accessability later:
            save_to_h5('outputdata/', 'Building_load_curve_' + obs_data_file_name + '.h5', Q_H_LOAD_8760, Q_C_LOAD_8760,
                       Q_DHW_LOAD_8760, Af, bc_num_building_not_Zero_vctr, climate_region_index, share_Circulation_DHW,
                       T_e_HSKD_8760_clreg, Tset_heating_8760_up, Tset_cooling_8760_up)

        # load the data from h5 file:
        filename = 'outputdata/' + 'Building_load_curve_' + obs_data_file_name + '.h5'
        dict_ = read_h5(filename)

        # print time
        print("Time for execution: ", timeit.default_timer() - starttime)

        if load_data == True:
            # create a dict for a simple plot if the data is loaded as dict:
            dict2 = dict.fromkeys(["Cooling_load", "DHW_load", "Heating_load"], [])
            for key in dict2:
                dict2[key] = dict_[key]
            # create dict for subplot with outside and set temperatures
            dict3 = dict.fromkeys(["T_set_heating", "T_set_cooling", "T_outside"], [])
            for key in dict3:
                dict3[key] = dict_[key]

            # plot only the Heating cooling and dhw loads
            lineplot_plt(dict2)

            # plot heating cooling and DHW loads as well as temperature settings and outside temp:
            overview_core(dict2, dict3)


        a = 1

    a = 1
