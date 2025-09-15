import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import Image, ImageTk
import csv, os


def calcular(precio_carnes, num_carnes, precio_venta):
    carnes_estimadas = num_carnes * 1.35
    posibles_beledar = ((carnes_estimadas / 15) * 1.05) * 3
    precio_total_carnes = precio_carnes * num_carnes
    pimientos = (carnes_estimadas / 15) * 5
    polvos = (carnes_estimadas / 15) * 40
    gastos_pimientos = pimientos * 0.098
    gastos_polvos = polvos * 0.0688
    beneficio = (precio_venta * posibles_beledar) - (
        gastos_pimientos + gastos_polvos + precio_total_carnes
    )

    return {
        "beneficio": beneficio,
        "precio_total_carnes": precio_total_carnes,
        "gastos_pimientos": gastos_pimientos,
        "gastos_polvos": gastos_polvos,
        "pimientos": pimientos,
        "polvos": polvos,
        "posibles_beledar": posibles_beledar,
    }


def leer_beneficios():
    archivo = "beneficio.csv"
    if not os.path.isfile(archivo):
        return [], []

    fechas, beneficios = [], []
    with open(archivo, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            try:
                fechas.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                beneficios.append(float(row[1]))
            except ValueError:
                continue

    acumulado, total = [], 0
    for b in beneficios:
        total += b
        acumulado.append(total)

    return fechas, acumulado


def crear_interfaz():
    ventana = tk.Tk()
    ventana.title("Cálculo de Beledar")
    ventana.geometry("1200x900")
    ventana.resizable(True, True)

    def on_closing():
        ventana.destroy()
        ventana.quit()

    ventana.protocol("WM_DELETE_WINDOW", on_closing)

    # ---- Fondo con imagen ----
    try:
        imagen_fondo = Image.open("fondo.png")
        imagen_fondo = imagen_fondo.resize((1200, 900), Image.LANCZOS)
        fondo_tk = ImageTk.PhotoImage(imagen_fondo)

        label_fondo = tk.Label(ventana, image=fondo_tk)
        label_fondo.place(x=0, y=0, relwidth=1, relheight=1)
        label_fondo.image = fondo_tk
    except Exception as e:
        print("No se pudo cargar la imagen de fondo:", e)

    font_big = ("Arial", 14, "bold")

    tk.Label(ventana, text="Precio de las carnes:", font=font_big).pack(pady=5)
    entry_precio_carnes = tk.Entry(ventana, font=font_big)
    entry_precio_carnes.pack(pady=5)

    tk.Label(ventana, text="Número de carnes:", font=font_big).pack(pady=5)
    entry_num_carnes = tk.Entry(ventana, font=font_big)
    entry_num_carnes.pack(pady=5)

    tk.Label(ventana, text="Precio de venta del Beledar:", font=font_big).pack(pady=5)
    entry_precio_venta = tk.Entry(ventana, font=font_big)
    entry_precio_venta.pack(pady=5)

    # ---- Subventanas ----
    def mostrar_beneficio(resultados):
        win = tk.Toplevel(ventana)
        win.title("Beneficio")
        win.geometry("300x150")
        color = "green" if resultados["beneficio"] >= 0 else "red"
        tk.Label(
            win,
            text=f"Beneficio estimado: {resultados['beneficio']:.2f}",
            font=("Arial", 18, "bold"),
            fg=color,
        ).pack(pady=30)

    def mostrar_gastos(resultados):
        win = tk.Toplevel(ventana)
        win.title("Gastos")
        win.geometry("350x200")
        font = ("Arial", 16)
        tk.Label(win, text=f"Precio total carnes: {resultados['precio_total_carnes']:.2f}", font=font).pack(pady=5)
        tk.Label(win, text=f"Precio total pimientos: {resultados['gastos_pimientos']:.2f}", font=font).pack(pady=5)
        tk.Label(win, text=f"Precio total polvos: {resultados['gastos_polvos']:.2f}", font=font).pack(pady=5)

    def mostrar_lista_compra(resultados):
        win = tk.Toplevel(ventana)
        win.title("Lista de la compra")
        win.geometry("350x200")
        font = ("Arial", 16)
        tk.Label(win, text=f"Pimientos necesarios: {resultados['pimientos']:.2f}", font=font).pack(pady=10)
        tk.Label(win, text=f"Polvos necesarios: {resultados['polvos']:.2f}", font=font).pack(pady=10)

    def guardar_beneficio_csv(beneficio):
        archivo = "beneficio.csv"
        existe = os.path.isfile(archivo)

        with open(archivo, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not existe:
                writer.writerow(["FechaHora", "Beneficio"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{beneficio:.2f}"])

        messagebox.showinfo("Guardado", "Beneficio guardado en beneficio.csv")
        actualizar_grafica()

    # ---- Frame para gráfica ----
    frame_grafica = tk.Frame(ventana, bd=2, relief="sunken")
    frame_grafica.pack(fill="both", expand=False, padx=10, pady=10)

    fig, ax = plt.subplots(figsize=(8, 4))
    line, = ax.plot([], [], marker="o", linestyle="-", color="green")
    ax.set_title("Evolución acumulada de Beneficios")
    ax.set_xlabel("Fecha y Hora")
    ax.set_ylabel("Beneficio Acumulado")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=frame_grafica)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---- Hover ----
    annot = ax.annotate("", xy=(0, 0), xytext=(15, 15), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind, xdata, ydata):
        idx = ind["ind"][0]
        annot.xy = (xdata[idx], ydata[idx])
        text = f"{xdata[idx].strftime('%Y-%m-%d %H:%M')}\nBeneficio: {ydata[idx]:.2f}"
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                xdata, ydata = line.get_data()
                update_annot(ind, xdata, ydata)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if annot.get_visible():
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    def actualizar_grafica():
        fechas, acumulado = leer_beneficios()
        line.set_data(fechas, acumulado)
        if fechas:
            margen = (max(fechas) - min(fechas)) * 0.1
            ax.set_xlim(min(fechas), max(fechas) + margen)
            ax.set_ylim(0, max(acumulado) * 1.1)
        canvas.draw()

    actualizar_grafica()

    # ---- Botón calcular ----
    def ejecutar_calculo():
        try:
            precio_carnes = float(entry_precio_carnes.get())
            num_carnes = int(entry_num_carnes.get())
            precio_venta = float(entry_precio_venta.get())

            resultados = calcular(precio_carnes, num_carnes, precio_venta)

            btn_beneficio.config(state="normal", command=lambda: mostrar_beneficio(resultados))
            btn_gastos.config(state="normal", command=lambda: mostrar_gastos(resultados))
            btn_lista.config(state="normal", command=lambda: mostrar_lista_compra(resultados))
            btn_guardar.config(state="normal", command=lambda: guardar_beneficio_csv(resultados["beneficio"]))
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese números válidos.")

    tk.Button(ventana, text="Calcular", command=ejecutar_calculo, font=("Arial", 14, "bold")).pack(pady=15)

    btn_beneficio = tk.Button(ventana, text="Mostrar Beneficio", font=("Arial", 14, "bold"), state="disabled")
    btn_beneficio.pack(pady=5)

    btn_gastos = tk.Button(ventana, text="Mostrar Gastos", font=("Arial", 14, "bold"), state="disabled")
    btn_gastos.pack(pady=5)

    btn_lista = tk.Button(ventana, text="Lista de la compra", font=("Arial", 14, "bold"), state="disabled")
    btn_lista.pack(pady=5)

    btn_guardar = tk.Button(ventana, text="Guardar Beneficio", font=("Arial", 14, "bold"), state="disabled")
    btn_guardar.pack(pady=5)

    ventana.mainloop()
