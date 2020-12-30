from pathlib import Path
from Heatdemand_rc_model import Heatdemand_rc_model

# Einlesen der Daten:
# base_results_path = Path('V:/projects/2020_RES_H/invert/output_20201111/AUT')
base_results_path = Path('L:/projekte/_abgeschlossen/2015_P2H-Pot/Invert_Szenarien/Invert_output_new')

# define scenarios:
# scenariolist = [r"_scen_aut_cheetah_ref_install_iopt_dh_95"]
scenariolist = [r'_scen_aut_a00_WAM_plus_v6_ren_mue']

# start and end year:
start_year = 2020
end_year = 2050

# Grid reference year:
grid_reference_year = 2010

for scn in scenariolist:
    results_path = base_results_path / scn
    run_number_str = "001"
    results_path_rcm = results_path / "ADD_RESULTS" / "Dynamic_Calc_Input_Data"
    results_path_temperatures = results_path / "ADD_RESULTS" / "Annual_Climate_Data"
    results_path_FWKWK_data = results_path / "ADD_RESULTS" / "FWKWK_REGIONAL_DATA"

    # check if paths exist:
    print("rcm path exists: " + str(results_path_rcm.exists()))
    print("temperatures path exists: " + str(results_path_temperatures.exists()))
    print("FWKWK path exists: " + str(results_path_FWKWK_data.exists()))

    year_vektor = [start_year, end_year]

    # Schleife über Kufstein Daten:         ??
    for kk in [1, 2, 3]:
        if kk == 1:
            climdata_file_name = 'Kufstein_EOBS_8110'
        elif kk == 2:
            climdata_file_name = 'Kufstein_REGCM3_1140'
        elif kk == 3:
            climdata_file_name = 'Kufstein_REGCM3_3665'

        for year in year_vektor:
            Heatdemand_rc_model(results_path_rcm, results_path_FWKWK_data, results_path_temperatures,
                                run_number_str, year, climdata_file_name)


