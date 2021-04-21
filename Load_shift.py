import h5py
import numpy as np
from pathlib import Path
from Simple_plots import *
import pyomo.environ as pyo
from pyomo.opt import SolverStatus, TerminationCondition

import os

path2data = os.path.join(os.path.split(os.path.abspath(__file__))[0], "inputdata")

def read_h5(filename):
    print('reading hf file...')
    dict = {}
    hf = h5py.File(filename, "r")
    # save all arrays from hf to dict as np.array:
    for key in hf.keys():
        dict[key] = np.array(hf.get(key))
    hf.close()
    print('done')
    return dict


# load the data from h5 file:
filepath = Path('outputdata')
filename = 'Building_load_curve_Austria_2050.hdf5'
file = filepath / filename
dict_ = read_h5(file)


dict2 = {}
dict3 = {}
# erste februar woche wird für tests verwendet (stunde 744 bis 912)
# es wird das 1te Profil für die tests verwendet
cooling_load = dict_["Cooling_load"][1][743:911]
DHW_load = dict_["DHW_load"][1][743:911]
heating_load = dict_["Heating_load"][1][743:911]
T_set_heating = dict_["T_set_heating"][1][743:911]
T_set_cooling = dict_["T_set_cooling"][1][743:911]
T_outside = dict_["T_outside"][1][743:911]

dict2["Cooling_load"] = cooling_load
dict2["DHW_load"] = DHW_load
dict2["Heating_load"] = heating_load

dict3["T_set_heating"] = T_set_heating
dict3["T_set_cooling"] = T_set_cooling
dict3["T_outside"] = T_outside

# plot heating cooling and DHW loads as well as temperature settings and outside temp:
one_week(dict2, dict3)



def run_model(length, data):
    # model
    m = pyo.AbstractModel()

    # sets
    m.t = pyo.RangeSet(1, length)



    # parameters
    m.q_heating = pyo.Param(m.t)
    m.capacity = pyo.Param()
    m.price = pyo.Param(m.t)
    m.t_set_heating = pyo.Param(m.t)
    m.t_outside = pyo.Param(m.t)

    # variables
    m.t_inside = pyo.Var(m.t, within=pyo.NonNegativeReals)

    # objective
    def min_cost(m):
        rule = m.q_heating * m.price
        return rule

    # constraints
    # T_inside <= T_set_heating + 3
    def maximum_temperature_rule(m, t):
        return m.t_inside[t] <= m.t_set_heating[t] + 3
    m.t_inside_max = pyo.Constraint(m.t_inside, m.t, rule=maximum_temperature_rule)

    # T_inside >= T_set_heating - 2
    def minimum_temperature_rule(m, t):
        return m.t_inside[t] >= m.t_set_heating[t] - 2
    m.t_inside_min = pyo.Constraint(m.t_inside, m.t, rule=minimum_temperature_rule)









a = 1
