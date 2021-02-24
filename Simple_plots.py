import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt


def lineplot(dict_):
    fig = go.Figure()
    for key, value in dict.items():
        fig.add_trace(go.Scatter(x=np.arange(len(value[0])), y=value, mode="lines", name=key))
    fig.show()


def lineplot_plt(dict_):
    fig = plt.figure()
    for key, value in dict_.items():
        plt.plot(np.arange(len(value[1])), value[1], label=str(key))
    plt.legend()
    fig.show()

def overview_core(dic1, dic2):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    for key, value in dic1.items():
        ax1.plot(np.arange(len(value[1])), value[1], label=str(key))
    ax1.legend()

    for key, value in dic2.items():
        ax2.plot(np.arange(len(value[1])), value[1], label=str(key))
    ax2.legend()

    fig.show()


