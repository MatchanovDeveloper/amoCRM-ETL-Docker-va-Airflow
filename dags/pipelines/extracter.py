import time
import requests
import settings as s

BASE_URL = f"https://{s.AMO_SUBDOMAIN}.amocrm.ru/api/v4"
HEADERS = {"Authorization": f"Bearer {s.AMO_LONG_TOKEN}"}


def _get_all(endpoint, params=None):
    """Barcha sahifalarni aylanib, xom dict'lar ro'yxatini qaytaradi."""
    if not s.AMO_LONG_TOKEN:
        raise RuntimeError(".env da AMO_LONG_TOKEN yo'q")

    params = {"limit": 250, **(params or {})}
    result, page = [], 1

    while True:
        params["page"] = page
        r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS,
                         params=params, timeout=30)

        if r.status_code == 204:          # boshqa ma'lumot yo'q
            break
        if r.status_code == 429:          # so'rovlar limiti oshdi
            time.sleep(2)
            continue
        r.raise_for_status()

        data = r.json()
        result.extend(data["_embedded"][endpoint])

        if "next" not in data.get("_links", {}):
            break
        page += 1
        time.sleep(0.15)                  # amoCRM: ~7 so'rov/soniya

    return result


# ---------------------------------------------------------------------------------------------------------------------

# Barcha datalarni xom (raw) lug'at (dict) holida yig'ib olish

def get_contact():
    return _get_all("contacts")


def get_company():
    return _get_all("companies")


def get_transaction():
    return _get_all("leads")




# nested ichidan kerakli ustunga tegishli datani topib beradi
def get_field(row, name):
    fields = row['custom_fields_values']
    if fields is None:
        return None
    
    for f in fields:
        if f['field_name'] == name or f['field_code'] == name:
            return f['values'][0]['value']
        
    return None    




def get_tags(item):
    tags = item["_embedded"]["tags"]
    names = []
    for t in tags:
        name = t["name"]

        if name.lower().startswith("импорт_") or name.lower().startswith("import_"):
            continue
        names.append(name)

    return ", ".join(names)
