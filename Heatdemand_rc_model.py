
import numpy as np
import pandas as pd
from pathlib import Path

def remove_b(columns):
    columns = columns.str.strip("b'")

def Heatdemand_rc_model(OUTPUT_PATH, OUTPUT_PATH_NUM_BUILD, OUTPUT_PATH_TEMP, RN, YEAR):
    # TODO für testen:
    YEAR = 2050

    input_dir_constant = 'inputdata/'
    BCAT_1_3 = np.ones((6, 3))
    BCAT_4_8 = np.ones((1, 5))
    NUM_GFA_BEFORE_BCAT_1_3 = np.ones((6, 3))
    NUM_GFA_BEFORE_BCAT_4_8 = np.ones((1, 5))

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
            # TODO Andi frage was es mit den BCAT matrizen auf sich hat
            BCAT_4_8[0, -2:] = 0

            TGridmom = 75
            TGridmin = 75
            scale_DHW = 1


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


        # Wohngebäude 1 bis 3
        # Bauperioden 1 bis 6


        for i in range(1, 4):
            for j in range(1, 7):
                idx = data_Bcat_per_BC.loc[(data_Bcat_per_BC["bcat_map"] == i) &
                                           (data_Bcat_per_BC["constrp_map"] == j), :].index
                data_num_build_per_GE.iloc[idx, 1] = data_num_build_per_GE.iloc[idx, 1] * BCAT_1_3[j-1, i-1] #weil python bei 0 anfängt zu zählen
                data_num_gfa_per_GE.iloc[idx, 1] = data_num_gfa_per_GE.iloc[idx, 1] * BCAT_1_3[j-1, i-1]

                NUM_GFA_BEFORE_BCAT_1_3[j-1, i-1] = data_num_gfa_per_GE.iloc[idx, 1].sum()

        # für kategorien 4 bis 8:
        for i in range(1, 6):
            idx = data_Bcat_per_BC.loc[data_Bcat_per_BC["bcat_map"] == (i + 3)].index
            data_num_build_per_GE.iloc[idx, 1] = data_num_build_per_GE.iloc[idx, 1] * BCAT_4_8[0, i - 1]
            data_num_gfa_per_GE.iloc[idx, 1] = data_num_gfa_per_GE.iloc[idx, 1] * BCAT_4_8[0, i - 1]

            NUM_GFA_BEFORE_BCAT_4_8[0, i-1] = data_num_gfa_per_GE.iloc[idx, 1].sum()

        # TODO Wieso dieses Limit?
        limit = 0.000002

        bc_num_building_not_Zero_vctr = (data_num_gfa_per_GE.iloc[:, 1]/data_num_gfa_per_GE.iloc[:, 1].sum() > limit) &\
                                        (data_num_gfa_per_GE.iloc[:, 0] < data.iloc[:, 0].size)


        a=1


    a=1



