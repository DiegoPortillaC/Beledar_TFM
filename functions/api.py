import time
import requests
from .config import CLIENT_ID, CLIENT_SECRET, REGION, LOCALE

_TOKEN = None
_TOKEN_EXP = 0

def get_token():
    global _TOKEN, _TOKEN_EXP
    now = int(time.time())
    if _TOKEN and now < _TOKEN_EXP - 60:
        return _TOKEN
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Faltan credenciales BLIZZARD_CLIENT_ID / BLIZZARD_CLIENT_SECRET")

    url = f"https://{REGION}.battle.net/oauth/token"
    data = {"grant_type": "client_credentials"}
    r = requests.post(url, data=data, auth=(CLIENT_ID, CLIENT_SECRET), timeout=20)
    r.raise_for_status()
    j = r.json()
    _TOKEN = j["access_token"]
    _TOKEN_EXP = now + int(j.get("expires_in", 3600))
    return _TOKEN

def auth_session():
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {get_token()}"})
    return s

def get_realm_auctions(sess, realm_id: int):
    url = f"https://{REGION}.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    params = {"namespace": f"dynamic-{REGION}", "locale": LOCALE}
    r = sess.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_commodities(sess):
    url = f"https://{REGION}.api.blizzard.com/data/wow/auctions/commodities"
    params = {"namespace": f"dynamic-{REGION}", "locale": LOCALE}
    r = sess.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def min_price_from(auctions_json, item_id: int):
    entries = [a for a in auctions_json.get("auctions", [])
               if a.get("item", {}).get("id") == item_id]
    if not entries:
        return None
    prices = []
    for a in entries:
        if "unit_price" in a:
            prices.append(a["unit_price"])
        elif "buyout" in a:
            prices.append(a["buyout"])
    return (min(prices) / 10000) if prices else None
