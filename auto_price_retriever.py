import time
from datetime import datetime, timedelta

from functions.api import auth_session, get_realm_auctions, get_commodities, min_price_from
from functions.csv_utils import guardar_precios_csv
from functions.config import REALM_ID, ITEM_ID_CARNE, ITEM_ID_BELEDAR

INTERVAL_MINUTES = 30  # cada 30 minutos

def run_once():
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

    ok = guardar_precios_csv(p_carne, p_beledar)
    if not ok:
        raise RuntimeError("No se pudo escribir data/precios.csv")
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Guardado: carne={p_carne}, beledar={p_beledar}")

def seconds_until_next_interval(minutes: int) -> float:
    """Espera hasta el próximo múltiplo del intervalo (alineado a :00 y :30)."""
    now = datetime.now()
    minute = (now.minute // minutes + 1) * minutes
    next_tick = now.replace(second=0, microsecond=0)
    if minute >= 60:
        next_tick = (next_tick + timedelta(hours=1)).replace(minute=0)
    else:
        next_tick = next_tick.replace(minute=minute)
    return max(1.0, (next_tick - now).total_seconds())

if __name__ == "__main__":
    # Ejecuta inmediatamente y luego cada 30 min alineado
    try:
        run_once()
    except Exception as e:
        print(f"ERROR inicial: {e}")

    while True:
        try:
            time.sleep(seconds_until_next_interval(INTERVAL_MINUTES))
            run_once()
        except KeyboardInterrupt:
            print("Detenido por el usuario.")
            break
        except Exception as e:
            # Si falla una ejecución, lo mostramos y reintentamos en 5 minutos
            print(f"ERROR en ejecución: {e}")
            time.sleep(300)
