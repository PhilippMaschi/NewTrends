
import numpy as np
import pandas as pd
from pathlib import Path

def Heatdemand_rc_model():

    input_dir_constant = 'inputdata/'
    BCAT_1_3 = np.ones((6, 3))
    BCAT_4_8 = np.ones((1, 5))
    NUM_GFA_BEFORE_BCAT_1_3 = np.ones((6, 3))
    NUM_GFA_BEFORE_BCAT_4_8 = np.ones((1, 5))

    for k in range(1, 7):
        if k == 1:
            # Weichstätten:
            nominal_gridloss_factor = 0.16
            region_obs_data_file_name = "Weichstaetten"
            t_movavg_DHW = 2
            t_movavg_SH = 3
            share_Circulation_DHW = 0
            GE_IDX = 1061

            # Wohngebäude mit je 6 Bauperioden (4 historisch, 5 Leer, 6 Neubau)
            #BCAT_1_3 = [1.0,0.5, 0.2, 0.2, 0.0, 1] *[1, 0.5, 0.3]
            BCAT_4_8[0, -2:] = 0

            TGridmom = 75
            TGridmin = 75
            scale_DHW = 1


    a=1

if __name__ == "__main__":
    Heatdemand_rc_model()