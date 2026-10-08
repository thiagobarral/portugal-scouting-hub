from curl_cffi import requests
import json
import time
from pathlib import Path


# --------------------------------------------------
# CONFIGURAÇÕES
# --------------------------------------------------

TOURNAMENT_ID = 238
SEASON_ID = 77806

INPUT_FILE = Path("data/raw/players_2025_26.json")
OUTPUT_FILE = Path(
    "data/raw/player_statistics_2025_26.json"
)

session = requests.Session(
    impersonate="chrome"
)


# --------------------------------------------------
# 1. CARREGAR JOGADORES DA TEMPORADA
# --------------------------------------------------

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:
    players = json.load(file)


print("Jogadores encontrados:", len(players))


# --------------------------------------------------
# 2. RECUPERAR UMA COLETA ANTERIOR
# --------------------------------------------------

if OUTPUT_FILE.exists():

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        statistics_data = json.load(file)

    print(
        "Registros já coletados:",
        len(statistics_data)
    )

else:

    statistics_data = []


# --------------------------------------------------
# 3. IDENTIFICAR JOGADORES JÁ PROCESSADOS
# --------------------------------------------------

processed_ids = {
    item["player_id"]
    for item in statistics_data
}


# --------------------------------------------------
# 4. COLETAR ESTATÍSTICAS
# --------------------------------------------------

total = len(players)


for index, item in enumerate(
    players,
    start=1
):

    player = item["player"]

    player_id = player["id"]
    player_name = player["name"]


    # ----------------------------------------------
    # Não baixar novamente jogadores já processados
    # ----------------------------------------------

    if player_id in processed_ids:

        print(
            f"[{index}/{total}] "
            f"{player_name} - já processado"
        )

        continue


    # ----------------------------------------------
    # Endpoint das estatísticas
    # ----------------------------------------------

    url = (
        f"https://api.sofascore.com/api/v1/"
        f"player/{player_id}/"
        f"unique-tournament/{TOURNAMENT_ID}/"
        f"season/{SEASON_ID}/"
        f"statistics/overall"
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


        # Registro básico da consulta
        record = {
            "player_id": player_id,
            "player_name": player_name,
            "status_code": response.status_code
        }


        # ------------------------------------------
        # Requisição bem-sucedida
        # ------------------------------------------

        if response.status_code == 200:

            response_data = response.json()

            record["data"] = response_data


        # ------------------------------------------
        # Requisição sem sucesso
        # ------------------------------------------

        else:

            record["data"] = None


        # Adicionar resultado
        statistics_data.append(record)

        processed_ids.add(player_id)


        # ------------------------------------------
        # Salvar progressivamente
        # ------------------------------------------

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                statistics_data,
                file,
                indent=4,
                ensure_ascii=False
            )


    except Exception as error:

        print(
            f"Erro em {player_name}: {error}"
        )


    # Pequena pausa entre requisições
    time.sleep(0.5)


# --------------------------------------------------
# 5. RESUMO DA COLETA
# --------------------------------------------------

success = sum(
    1
    for item in statistics_data
    if item["status_code"] == 200
)


errors = len(statistics_data) - success


print("\nColeta finalizada.")

print(
    "Jogadores processados:",
    len(statistics_data)
)

print(
    "Sucesso (200):",
    success
)

print(
    "Outros status:",
    errors
)