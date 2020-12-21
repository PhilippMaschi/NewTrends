import pandas as pd
from pathlib import Path

# Einlesen der Daten:
base_results_path = Path('V:/projects/2020_RES_H/invert/output_20201111/AUT')

# define scenarios:
scenariolist = [r"_scen_aut_cheetah_ref_install_iopt_dh_95"]

# start and end year:
start_year = 2017
end_year = 2050

for scn in scenariolist:
    results_path = base_results_path / scn
    run_number_str = "001"
    results_path_rcm = results_path / "ADD_RESULTS" / "Dynamic_Calc_Input_Data"
    results_path_temperatures = results_path / "ADD_RESULTS" / "Annual_Climate_Data"
    results_path_FWKWK_data = results_path / "ADD_RESULTS" / "FWKWK_REGIONAL_DATA"

    # check if paths exist:

    print("rcm path exists: " + str(results_path_rcm.exists()))
    print("temperatures path exists: " + str(results_path_rcm.exists()))
    print("FWKWK path exists: " + str(results_path_rcm.exists()))



    a=1




