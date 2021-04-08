import pyomo.environ as pyo
from pyomo.opt import SolverStatus,TerminationCondition
import matplotlib.pyplot as plt

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

var = {1: 20, 2: 25, 3: 15, 4: 12, 5: 25, 6: 20}  # Q_a
var2 = {1: 1, 2: 6, 3: 8, 4: 8, 5: 2, 6: 1}  # price
ta = {1: 20, 2: 20, 3: 20, 4: 20, 5: 20, 6: 20}  # constant surrounding temp

# model
m = pyo.AbstractModel()

# parameters
m.t = pyo.RangeSet(1, 6)
m.Q_a = pyo.Param(m.t, initialize=var)
m.p = pyo.Param(m.t, initialize=var2)
m.T_a = pyo.Param(m.t, initialize=ta)



# variables
m.Q_e = pyo.Var(m.t, within=pyo.NonNegativeReals)
m.T_innen = pyo.Var(m.t, within=pyo.NonNegativeReals)


# objective
def minimize_cost(m):
    rule = sum(m.Q_e[t] * m.p[t] for t in m.t)
    return rule
m.OBJ = pyo.Objective(rule=minimize_cost)


# constraints
def maximum_temperature(m, t):
    return m.T_innen[t] <= 100
m.maximum_temperature_t = pyo.Constraint(m.t, rule=maximum_temperature)


def minimum_temperature(m,t):
    return m.T_innen[t] >= 20
m.minimum_temperature = pyo.Constraint(m.t, rule=minimum_temperature)


def Zusammenhang(m, t):
    if t == 1:
        return m.T_innen[t] == 50
    else:
        return m.T_innen[t] == m.T_innen[t-1] - m.Q_a[t]/1000/4.2*3600 + m.Q_e[t]/1000/4.2*3600 - 0.003*(m.T_innen[t]-m.T_a[t])
m.zusammenhang = pyo.Constraint(m.t, rule=Zusammenhang)


def max_power(m, t):
    return m.Q_e[t] <= 20  # kWh
m.max_power = pyo.Constraint(m.t, rule=max_power)

def min_power(m, t):
    return m.Q_e[t] >= 0
m.min_power = pyo.Constraint(m.t, rule=min_power)


instance = m.create_instance(report_timing=True)
opt = pyo.SolverFactory("gurobi")
results = opt.solve(instance, tee=True)
print(results)




# create plots to visualize results

Q_e = [instance.Q_e[t]() for t in m.t]
price = [var2[i] for i in range(1, 7)]
Q_a = [var[i] for i in range(1, 7)]
# indoor temperature is constant 20°C
Q = [4.2 * 1000 / 3600 * (instance.T_innen[t]()-20) for t in m.t]
cost = [list(price)[i] * Q_e[i] for i in range(6)]
total_cost = sum(cost)

fig = plt.figure()
ax = plt.gca()
ax2 = ax.twinx()

x_achse = [1, 2, 3, 4, 5]

lns1 = ax.bar(x_achse, Q_e[1:], label="heating power")
lns2 = ax.plot(x_achse, Q_a[1:], label="output energy", color="green")
lns3 = ax.plot(x_achse, Q[1:], label="energy in tank", color="red")
lns4 = ax2.plot(x_achse, price[1:], color="orange", label="price")

ax.set_ylabel("energy kWh")
ax2.set_ylabel("price per kWh")

lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc=0)

plt.title("minimal cost = " + str(round(total_cost)))
plt.show()

