import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

def make_beneficio_figure():
    fig, ax = plt.subplots(figsize=(10, 3.5), constrained_layout=True)
    (linea,) = ax.plot([], [], "-", marker="o")
    ax.set_title("Beneficio acumulado en el tiempo", fontsize=12)
    ax.set_xlabel("Fecha")
    ax.set_ylabel("oro acumulado")
    ax.grid(True, alpha=0.25)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
    fig.autofmt_xdate()
    return fig, ax, linea

def theme_axes(ax, image_mode: bool):
    fig = ax.get_figure()
    if image_mode:
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.tick_params(colors="black")
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")
        ax.title.set_color("black")
        ax.grid(True, alpha=0.25)
    else:
        BG = "#101418"
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        ax.grid(True, alpha=0.25)

def autoscale_time_axis(ax, fechas):
    from datetime import timedelta
    if not fechas:
        return
    if len(fechas) == 1:
        xmin = fechas[0] - timedelta(hours=12)
        xmax = fechas[0] + timedelta(hours=12)
    else:
        rng = fechas[-1] - fechas[0]
        xmin = fechas[0]
        xmax = fechas[-1] + rng * 0.10
    ax.set_xlim(xmin, xmax)

def make_precios_figure(fechas, carnes, beledar, image_mode: bool):
    fig2, ax2 = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    ax2.plot(fechas, carnes, marker="o", linestyle="-", label="Carne")
    ax2.plot(fechas, beledar, marker="o", linestyle="-", label="Beledar")
    ax2.set_title("Evolución de precios (oro)")
    ax2.set_xlabel("Fecha")
    ax2.set_ylabel("Precio (g)")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
    if image_mode:
        theme_axes(ax2, True)
    else:
        theme_axes(ax2, False)

    if fechas:
        if len(fechas) == 1:
            from datetime import timedelta
            xmin = fechas[0] - timedelta(hours=6)
            xmax = fechas[0] + timedelta(hours=18)
        else:
            rng = fechas[-1] - fechas[0]
            xmin = fechas[0]
            xmax = fechas[-1] + rng * 0.10
        ax2.set_xlim(xmin, xmax)
    return fig2, ax2
