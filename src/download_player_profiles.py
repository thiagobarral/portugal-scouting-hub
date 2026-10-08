from curl_cffi import requests
import json
import time
from pathlib import Path


INPUT_FILE = Path("data/raw/players_2025_26.json")
OUTPUT_FILE = Path("data/raw/player_profiles.json")

session = requests.Session(
    impersonate="chrome"
)


# --------------------------------------------------
# Carregar jogadores da temporada
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    players_season = json.load(file)


print("Jogadores encontrados:", len(players_season))


# --------------------------------------------------
# Recuperar coleta anterior, caso exista
# --------------------------------------------------

if OUTPUT_FILE.exists():

    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        profiles = json.load(file)

    print("Perfis já baixados:", len(profiles))

else:
    profiles = []


# IDs que já foram baixados
downloaded_ids = {
    item["player"]["id"]
    for item in profiles
    if "player" in item
}


# --------------------------------------------------
# Download
# --------------------------------------------------

total = len(players_season)

for index, item in enumerate(players_season, start=1):

    player = item["player"]

    player_id = player["id"]
    player_name = player["name"]

    # Evita baixar novamente
    if player_id in downloaded_ids:

        print(
            f"[{index}/{total}] "
            f"{player_name} - já baixado"
        )

        continue


    url = (
        f"https://api.sofascore.com/api/v1/"
        f"player/{player_id}"
    )


    try:

        response = session.get(
            url,
            timeout=30
        )

        print(
            f"[{index}/{total}] "
            f"{player_name} | "
            f"Status: {response.status_code}"
        )


        if response.status_code == 200:

            profile = response.json()

            profiles.append(profile)

            downloaded_ids.add(player_id)


            # Salva progressivamente
            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    profiles,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        else:

            print(
                f"Erro ao baixar {player_name}"
            )


    except Exception as error:

        print(
            f"Erro em {player_name}: {error}"
        )


    # Evitar muitas requisições seguidas
    time.sleep(0.5)


print("\nColeta finalizada.")
print("Perfis salvos:", len(profiles))