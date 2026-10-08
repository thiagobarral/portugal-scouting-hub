from curl_cffi import requests
import json

PLAYER_ID = 1503836
TOURNAMENT_ID = 238
SEASON_ID = 77806

url = (
    f"https://api.sofascore.com/api/v1/"
    f"player/{PLAYER_ID}/"
    f"unique-tournament/{TOURNAMENT_ID}/"
    f"season/{SEASON_ID}/statistics/overall"
)

session = requests.Session(
    impersonate="chrome"
)

response = session.get(
    url,
    timeout=30
)

print("Status:", response.status_code)

if response.status_code == 200:

    data = response.json()

    print("\nChaves principais:")
    print(data.keys())

    print("\nJSON completo:\n")

    print(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )
    )

else:

    print("Erro ao acessar SofaScore")
    print(response.text[:500])