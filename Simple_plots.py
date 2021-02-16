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
        plt.plot(np.arange(len(value[0])), value[0], label=str(key))
    plt.legend()
    fig.show()


