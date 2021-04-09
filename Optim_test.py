import pyomo.environ as pyo
import numpy as np
from pyomo.opt import SolverStatus,TerminationCondition
import matplotlib.pyplot as plt
from pyomo.util.infeasible import log_infeasible_constraints

# testing pyomo very simple example for 5 hours: (5 steps)
# Hot water tank with input, output, losses depending on inside temperature
# surrounding temperature T_a = 20°C constant
# losses Q_loss = 0.003 * (T_inside - T_a) kWh
# water mass in the tank m = 1000kg, c_p water = 4.2 kJ/kgK
# Useful energy in the Tank Q = m * cp * (T_inside - T_a)
# heat demand supplied by the tank Q_a = [2, 4, 5, 5, 3] kWh
# input into the tank Q_e = ??? (variable to be determined)
# price for buying energy every hour p = [1, 6, 8, 8, 2] [price units / kWh]
# Goal: Minimize operation cost of hot water tank!
# Q = Q_(-1) + Q_e - Q_v - Q_a   Q_(-1) is the energy of the timestep before in the tank (T_0 = 50°C)
# initial condition: Q_0 = m*cp*(80-20) = 70 kWh
# max Temperature in the tank T_max = 100°C --> Q_max = 93.3 kWh

def create_dict(liste):
    dictionary = {}
    for index, value in enumerate(liste, start=1):
         dictionary[index] = value
    return dictionary

#var = {1: 20, 2: 25, 3: 15, 4: 12, 5: 25, 6: 20}  # Q_a
var2 = create_dict([1, 6, 8, 8, 2, 1])  # price
ta = create_dict([20, 20, 20, 20, 20, 20])  # constant surrounding temp
tout = create_dict([5, 4, 0, -1, -2, -2])  # outside temperature

# U-Value
U = 0.2  # W/m2K
# heat capacity room
C_h = 2000  # J/K
# useful area
Am = 425  # m2

# model
m = pyo.AbstractModel()

# parameters
m.t = pyo.RangeSet(1, 6)
m.p = pyo.Param(m.t, initialize=var2)
m.T_a = pyo.Param(m.t, initialize=ta)
m.T_out = pyo.Param(m.t, initialize=tout)


# variables
m.Q_e = pyo.Var(m.t, within=pyo.NonNegativeReals)
m.T_tank = pyo.Var(m.t, within=pyo.NonNegativeReals)
m.Q_a = pyo.Var(m.t, within=pyo.NonNegativeReals)
m.T_room = pyo.Var(m.t, within=pyo.NonNegativeReals)

# objective
def minimize_cost(m):
    rule = sum(m.Q_e[t] * m.p[t] for t in m.t)
    return rule
m.OBJ = pyo.Objective(rule=minimize_cost)


# constraints
def maximum_temperature_tank(m, t):
    return m.T_tank[t] <= 100
m.maximum_temperature_tank = pyo.Constraint(m.t, rule=maximum_temperature_tank)


def minimum_temperature_tank(m, t):
    return m.T_tank[t] >= 20
m.minimum_temperature_tank = pyo.Constraint(m.t, rule=minimum_temperature_tank)

def maximum_temperature_room(m, t):
    return m.T_room[t] <= 28
m.maximum_temperature_raum = pyo.Constraint(m.t, rule=maximum_temperature_room)

def minimum_temperature_room(m, t):
    return m.T_room[t] >= 20
m.minimum_temperature_raum = pyo.Constraint(m.t, rule=minimum_temperature_room)

def room_temperature(m, t):
    if t == 1:
        return m.T_room[t] == 21 - U * Am / C_h * (m.T_room[t] - m.T_out[t]) + m.Q_a[t] / C_h
    else:
        return m.T_room[t] == m.T_room[t - 1] - U * Am / C_h * (m.T_room[t] - m.T_out[t]) + m.Q_a[t] / C_h
m.room_temperature = pyo.Constraint(m.t, rule=room_temperature)

def tank_temperatur(m, t):
    if t == 1:
        return m.T_tank[t] == 50 - m.Q_a[t] / 1000 / 4.2 * 3600 + m.Q_e[t] / 1000 / 4.2 * 3600 - 0.003 * (50 - m.T_a[t])
    else:
        return m.T_tank[t] == m.T_tank[t - 1] - m.Q_a[t] / 1000 / 4.2 * 3600 + m.Q_e[t] / 1000 / 4.2 * 3600 - 0.003 * (m.T_tank[t] - m.T_a[t])
m.tank_temperatur = pyo.Constraint(m.t, rule=tank_temperatur)


def max_power_tank(m, t):
    return m.Q_e[t] <= 100  # kWh
m.max_power = pyo.Constraint(m.t, rule=max_power_tank)

def min_power_tank(m, t):
    return m.Q_e[t] >= 0
m.min_power = pyo.Constraint(m.t, rule=min_power_tank)

def max_power_heating(m,t):
    return m.Q_a[t] <= 30
m.max_power_heating = pyo.Constraint(m.t, rule=max_power_heating)

def min_power_heating(m, t):
    return m.Q_a[t] >= 0
m.min_power_heating = pyo.Constraint(m.t, rule=min_power_heating)



instance = m.create_instance(report_timing=True)
opt = pyo.SolverFactory("gurobi")
results = opt.solve(instance, tee=True)
print(results)




# create plots to visualize results

Q_e = [instance.Q_e[t]() for t in m.t]
price = [var2[i] for i in range(1, 7)]
Q_a = [instance.Q_a[t]() for t in m.t]
# indoor temperature is constant 20°C
# Q = [4.2 * 1000 / 3600 * (instance.T_innen[t]()-20) for t in m.t]
# cost = [list(price)[i] * Q_e[i] for i in range(6)]
# total_cost = sum(cost)

# fig = plt.figure()
# ax = plt.gca()
# ax2 = ax.twinx()
#
# x_achse = [0, 1, 2, 3, 4, 5]
#
# lns1 = ax.bar(x_achse, Q_e, label="heating power")
# lns2 = ax.plot(x_achse, Q_a, label="output energy", color="green")
# # lns3 = ax.plot(x_achse, Q, label="energy in tank", color="red")
# lns4 = ax2.plot(x_achse, price, color="orange", label="price")
#
# ax.set_ylabel("energy kWh")
# ax2.set_ylabel("price per kWh")
#
# lines, labels = ax.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax2.legend(lines + lines2, labels + labels2, loc=0)
#
# # plt.title("minimal cost = " + str(round(total_cost)))
# plt.show()





