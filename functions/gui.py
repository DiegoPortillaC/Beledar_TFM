import sys, os
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import timedelta

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from .api import auth_session, get_realm_auctions, get_commodities, min_price_from
from .calculations import calcular
from .csv_utils import (
    leer_beneficios, guardar_beneficio_csv,
    guardar_precios_csv, leer_precios_csv
)
from .plotting import make_beneficio_figure, theme_axes, autoscale_time_axis, make_precios_figure
from .config import REALM_ID, ITEM_ID_CARNE, ITEM_ID_BELEDAR, ICON_PATH

BG = "#101418"

def crear_interfaz():
    ventana = tk.Tk()
    ventana.title("Cálculo de Beledar con WoW API")
    ventana.geometry("1300x1080")
    ventana.resizable(True, True)
    try:
        if ICON_PATH.is_file():
            ventana.iconbitmap(False, str(ICON_PATH))
    except Exception:
        pass

    # Tema oscuro por defecto
    ventana.configure(bg=BG)
    ventana.option_add("*Background", BG)
    ventana.option_add("*Foreground", "white")
    ventana.option_add("*Button.Background", "#2b2b2b")
    ventana.option_add("*Button.Foreground", "white")
    ventana.option_add("*Entry.Background", "#1e1e1e")
    ventana.option_add("*Entry.Foreground", "white")
    ventana.option_add("*Entry.InsertForeground", "white")
    ventana.option_add("*Entry.HighlightThickness", 0)

    bg_label = tk.Label(ventana)
    bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    bg_label.lower()
    bg_image_orig = {"img": None}
    bg_image_tk = {"img": None}

    image_mode_flag = {"value": False}

    def _resize_bg(event=None):
        if not bg_image_orig["img"]:
            return
        w = max(1, ventana.winfo_width())
        h = max(1, ventana.winfo_height())
        try:
            from PIL import Image, ImageTk
        except Exception:
            return
        img_resized = bg_image_orig["img"].resize((w, h), Image.LANCZOS)
        bg_image_tk["img"] = ImageTk.PhotoImage(img_resized)
        bg_label.configure(image=bg_image_tk["img"])

    def set_background_image(path: str):
        try:
            from PIL import Image, ImageTk
            img = Image.open(path).convert("RGB")
            bg_image_orig["img"] = img
            _resize_bg()
            image_mode_flag["value"] = True
            theme_axes(ax, True)
            canvas.draw_idle()
        except Exception as e:
            messagebox.showerror("Fondo", f"No se pudo cargar la imagen:\n{e}")

    def clear_background_image():
        bg_image_orig["img"] = None
        bg_image_tk["img"] = None
        bg_label.configure(image="")
        image_mode_flag["value"] = False
        theme_axes(ax, False)
        canvas.draw_idle()

    ventana.bind("<Configure>", _resize_bg)

    big = ("Arial", 16)

    tk.Label(ventana, text="Precio de las carnes (oro):", font=big).pack(pady=4)
    entry_precio_carnes = tk.Entry(ventana, font=big, width=18)
    entry_precio_carnes.pack(pady=2)

    tk.Label(ventana, text="Número de carnes:", font=big).pack(pady=4)
    entry_num_carnes = tk.Entry(ventana, font=big, width=18)
    entry_num_carnes.pack(pady=2)

    tk.Label(ventana, text="Precio de venta del Beledar (oro):", font=big).pack(pady=4)
    entry_precio_venta = tk.Entry(ventana, font=big, width=18)
    entry_precio_venta.pack(pady=2)

    frame_graf = tk.Frame(ventana, bd=2, relief="sunken", width=1100, height=350)
    frame_graf.pack(padx=10, pady=12)
    frame_graf.pack_propagate(False)

    fig, ax, linea = make_beneficio_figure()
    theme_axes(ax, False)

    canvas = FigureCanvasTkAgg(fig, master=frame_graf)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    def actualizar_grafica():
        fechas, acum = leer_beneficios()
        linea.set_data(fechas, acum)
        if fechas:
            autoscale_time_axis(ax, fechas)
            ymin = min(0.0, min(acum)) * 1.1 if acum else 0.0
            ymax = max(0.0, max(acum)) * 1.1 if acum else 1.0
            ax.set_ylim(ymin, ymax)
        canvas.draw_idle()

    # Tooltip
    anot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(15, 15),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    anot.set_visible(False)

    def _update_annot(ind, xs, ys):
        i = ind["ind"][0]
        anot.xy = (xs[i], ys[i])
        anot.set_text(f"{xs[i].strftime('%Y-%m-%d %H:%M')}\n{ys[i]:.2f}g")
        anot.get_bbox_patch().set_alpha(0.95)

    def _on_move(event):
        xs = list(linea.get_xdata())
        ys = list(linea.get_ydata())
        if not xs or not ys:
            return
        vis = anot.get_visible()
        if event.inaxes != ax:
            if vis:
                anot.set_visible(False)
                fig.canvas.draw_idle()
            return
        contains, ind = linea.contains(event)
        if contains and ind and "ind" in ind and len(ind["ind"]) > 0:
            _update_annot(ind, xs, ys)
            anot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if vis:
                anot.set_visible(False)
                fig.canvas.draw_idle()

    hover_cid = fig.canvas.mpl_connect("motion_notify_event", _on_move)
    actualizar_grafica()

    # Ventanas de resultados
    def mostrar_beneficio(res):
        win = tk.Toplevel(ventana)
        win.title("Beneficio")
        win.geometry("360x160")
        color = "green" if res["beneficio"] >= 0 else "red"
        tk.Label(win, text=f"Beneficio estimado: {res['beneficio']:.2f} g",
                 font=("Arial", 20, "bold"), fg=color).pack(pady=30)

    def mostrar_gastos(res):
        win = tk.Toplevel(ventana)
        win.title("Gastos")
        win.geometry("420x220")
        f = ("Arial", 16)
        tk.Label(win, text=f"Carnes: {res['precio_total_carnes']:.2f} g", font=f).pack(pady=6)
        tk.Label(win, text=f"Pimientos: {res['gastos_pimientos']:.2f} g", font=f).pack(pady=6)
        tk.Label(win, text=f"Polvos: {res['gastos_polvos']:.2f} g", font=f).pack(pady=6)

    def mostrar_lista(res):
        win = tk.Toplevel(ventana)
        win.title("Lista de la compra")
        win.geometry("420x220")
        f = ("Arial", 16)
        tk.Label(win, text=f"Pimientos necesarios: {res['pimientos']:.2f}", font=f).pack(pady=10)
        tk.Label(win, text=f"Polvos necesarios: {res['polvos']:.2f}", font=f).pack(pady=10)

    # 1) Obtener precios
    def actualizar_precios_wow():
        try:
            sess = auth_session()
            realm_json = get_realm_auctions(sess, REALM_ID)
            p_carne = min_price_from(realm_json, ITEM_ID_CARNE)
            p_beledar = min_price_from(realm_json, ITEM_ID_BELEDAR)
            if p_carne is None or p_beledar is None:
                comm_json = get_commodities(sess)
                if p_carne is None:
                    p_carne = min_price_from(comm_json, ITEM_ID_CARNE)
                if p_beledar is None:
                    p_beledar = min_price_from(comm_json, ITEM_ID_BELEDAR)

            if p_carne is not None:
                entry_precio_carnes.delete(0, tk.END)
                entry_precio_carnes.insert(0, f"{p_carne:.2f}")
            if p_beledar is not None:
                entry_precio_venta.delete(0, tk.END)
                entry_precio_venta.insert(0, f"{p_beledar:.2f}")

            if p_carne is not None or p_beledar is not None:
                ok = guardar_precios_csv(p_carne, p_beledar)
                if not ok:
                    messagebox.showwarning("CSV precios", "No se pudo escribir data/precios.csv.")
            else:
                messagebox.showwarning("WoW API", "No se encontraron precios (ni en realm ni en commodities).")
                return
            messagebox.showinfo("WoW API", "Precios actualizados y guardados.")
        except Exception as e:
            messagebox.showerror("Error API", str(e))

    btn_obtener = tk.Button(ventana, text="Obtener precios", font=("Arial", 16, "bold"),
                            command=actualizar_precios_wow)
    btn_obtener.pack(pady=10)

    # 2) Calcular
    def ejecutar_calculo():
        try:
            precio_carnes = float(entry_precio_carnes.get())
            num_carnes = int(entry_num_carnes.get())
            precio_venta = float(entry_precio_venta.get())
            res = calcular(precio_carnes, num_carnes, precio_venta)
            btn_beneficio.config(state="normal", command=lambda: mostrar_beneficio(res))
            btn_gastos.config(state="normal", command=lambda: mostrar_gastos(res))
            btn_lista.config(state="normal", command=lambda: mostrar_lista(res))
            btn_guardar.config(state="normal", command=lambda: _guardar_beneficio(res))
        except ValueError:
            messagebox.showerror("Error", "Introduce números válidos.")

    btn_calcular = tk.Button(ventana, text="Calcular", font=("Arial", 16, "bold"),
                             command=ejecutar_calculo)
    btn_calcular.pack(pady=10)

    btn_beneficio = tk.Button(ventana, text="Mostrar beneficio", font=("Arial", 16, "bold"),
                              state="disabled")
    btn_beneficio.pack(pady=6)

    btn_gastos = tk.Button(ventana, text="Mostrar gasto", font=("Arial", 16, "bold"),
                           state="disabled")
    btn_gastos.pack(pady=6)

    btn_lista = tk.Button(ventana, text="Lista de la compra", font=("Arial", 16, "bold"),
                          state="disabled")
    btn_lista.pack(pady=6)

    def _guardar_beneficio(res):
        if guardar_beneficio_csv(res["beneficio"]):
            messagebox.showinfo("Guardado", f"Beneficio ({res['beneficio']:.2f} g) guardado.")
            actualizar_grafica()
        else:
            messagebox.showerror("Error", "No se pudo guardar el beneficio.")

    btn_guardar = tk.Button(ventana, text="Guardar beneficio", font=("Arial", 16, "bold"),
                            state="disabled")
    btn_guardar.pack(pady=6)

    # 7) Gráfica precios
    def mostrar_grafica_precios():
        fechas, carnes, beledar = leer_precios_csv()
        if not fechas:
            messagebox.showinfo("Precios", "Aún no hay datos en data/precios.csv.")
            return
        top = tk.Toplevel(ventana)
        top.title("Evolución de precios")
        top.geometry("900x500")
        fig2, ax2 = make_precios_figure(fechas, carnes, beledar, image_mode_flag["value"])
        canvas2 = FigureCanvasTkAgg(fig2, master=top)
        canvas2.get_tk_widget().pack(fill="both", expand=True)

        anot2 = ax2.annotate(
            "",
            xy=(0, 0),
            xytext=(15, 15),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        anot2.set_visible(False)
        lines = ax2.get_lines()

        def _upd(ind, line):
            xdata = list(line.get_xdata()); ydata = list(line.get_ydata())
            i = ind["ind"][0]
            if ydata[i] is None:
                return
            anot2.xy = (xdata[i], ydata[i])
            anot2.set_text(f"{xdata[i].strftime('%Y-%m-%d %H:%M')}\n{line.get_label()}: {ydata[i]:.2f} g")
            anot2.get_bbox_patch().set_alpha(0.95)

        def _on_move_prices(event):
            vis = anot2.get_visible()
            if event.inaxes != ax2:
                if vis:
                    anot2.set_visible(False); fig2.canvas.draw_idle()
                return
            shown = False
            for line in lines:
                contains, ind = line.contains(event)
                if contains and ind and "ind" in ind and len(ind["ind"]) > 0:
                    _upd(ind, line)
                    anot2.set_visible(True)
                    fig2.canvas.draw_idle()
                    shown = True
                    break
            if not shown and vis:
                anot2.set_visible(False)
                fig2.canvas.draw_idle()

        fig2.canvas.mpl_connect("motion_notify_event", _on_move_prices)

        def cerrar_top():
            try: plt.close(fig2)
            except Exception: pass
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", cerrar_top)

    btn_graf_precios = tk.Button(ventana, text="Gráfica precios", font=("Arial", 16, "bold"),
                                 command=mostrar_grafica_precios)
    btn_graf_precios.pack(pady=10)

    # Opciones (fondo)
    def abrir_opciones():
        top = tk.Toplevel(ventana)
        top.title("Opciones")
        top.geometry("320x160")
        tk.Button(top, text="Elegir fondo…", font=("Arial", 12, "bold"),
                  command=lambda: _elegir_fondo_y_cerrar(top)).pack(pady=8)
        tk.Button(top, text="Quitar fondo", font=("Arial", 12, "bold"),
                  command=lambda: (clear_background_image(), top.destroy())).pack(pady=8)

    def _elegir_fondo_y_cerrar(win):
        ruta = filedialog.askopenfilename(
            title="Elegir imagen de fondo",
            filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if ruta:
            set_background_image(ruta)
        win.destroy()

    btn_opciones = tk.Button(ventana, text="Opciones", font=("Arial", 16, "bold"),
                             command=abrir_opciones)
    btn_opciones.pack(pady=12)

    def cerrar_app():
        try:
            try: fig.canvas.mpl_disconnect(hover_cid)
            except Exception: pass
            try:
                plt.close(fig); plt.close('all')
            except Exception: pass
            try: ventana.quit()
            except Exception: pass
            try: ventana.destroy()
            except Exception: pass
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    ventana.protocol("WM_DELETE_WINDOW", cerrar_app)
    ventana.mainloop()
