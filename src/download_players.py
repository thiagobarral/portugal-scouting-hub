from curl_cffi import requests
import json
import time


TOURNAMENT_ID = 238
SEASON_ID = 77806

LIMIT = 100

BASE_URL = (
    f"https://api.sofascore.com/api/v1/"
    f"unique-tournament/{TOURNAMENT_ID}/"
    f"season/{SEASON_ID}/statistics"
)

session = requests.Session(
    impersonate="chrome"
)

all_players = []

offset = 0

while True:

    params = {
        "limit": LIMIT,
        "order": "-rating",
        "offset": offset,
        "accumulation": "total"
    }

    response = session.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    print(
        f"Offset {offset} | "
        f"Status: {response.status_code}"
    )

    if response.status_code != 200:
        print("Erro:", response.text[:500])
        break

    data = response.json()

    results = data.get("results", [])

    print(
        f"Registros recebidos: {len(results)}"
    )

    if not results:
        break

    all_players.extend(results)

    print(
        f"Total acumulado: {len(all_players)}"
    )

    # Se vier menos que LIMIT,
    # chegamos à última página
    if len(results) < LIMIT:
        break

    offset += LIMIT

    time.sleep(0.5)


print("\nDownload concluído!")
print("Total de registros:", len(all_players))


with open(
    "data/raw/players_2025_26.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        all_players,
        file,
        indent=4,
        ensure_ascii=False
    )


print(
    "\nArquivo salvo em:"
    " data/raw/players_2025_26.json"
)