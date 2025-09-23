import csv
from datetime import datetime
from .config import CSV_FILE, PRECIOS_CSV

def leer_beneficios():
    if not CSV_FILE.is_file():
        return [], []
    fechas, beneficios = [], []
    with CSV_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if len(row) >= 2:
                try:
                    fechas.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                    beneficios.append(float(row[1]))
                except Exception:
                    continue
    acum, total = [], 0.0
    for b in beneficios:
        total += b
        acum.append(total)
    return fechas, acum

def guardar_beneficio_csv(beneficio: float):
    try:
        existe = CSV_FILE.is_file()
        with CSV_FILE.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(["FechaHora", "Beneficio"])
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{beneficio:.2f}"])
        return True
    except Exception:
        return False

def guardar_precios_csv(precio_carne, precio_beledar):
    try:
        existe = PRECIOS_CSV.is_file()
        with PRECIOS_CSV.open("a", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            if not existe:
                w.writerow(["FechaHora", "PrecioCarne", "PrecioBeledar"])
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            fila = [
                ts,
                f"{precio_carne:.2f}" if precio_carne is not None else "",
                f"{precio_beledar:.2f}" if precio_beledar is not None else ""
            ]
            w.writerow(fila)
        return True
    except Exception:
        return False

def leer_precios_csv():
    if not PRECIOS_CSV.is_file():
        return [], [], []
    fechas, carnes, beledar = [], [], []
    with PRECIOS_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        _ = next(reader, None)
        for row in reader:
            if len(row) < 3:
                continue
            try:
                fechas.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
            except Exception:
                continue
            try:
                carnes.append(float(row[1])) if row[1] != "" else carnes.append(None)
            except Exception:
                carnes.append(None)
            try:
                beledar.append(float(row[2])) if row[2] != "" else beledar.append(None)
            except Exception:
                beledar.append(None)
    return fechas, carnes, beledar
