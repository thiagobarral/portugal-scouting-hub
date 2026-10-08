import json
import pandas as pd


# --------------------------------------------------
# 1. Carregar JSON bruto
# --------------------------------------------------

with open(
    "data/raw/players_2025_26.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


print("Registros no JSON:", len(data))


# --------------------------------------------------
# 2. Extrair informações principais
# --------------------------------------------------

players = []

for item in data:

    player = item.get("player", {})
    team = item.get("team", {})

    players.append(
        {
            "player_id": player.get("id"),
            "player_name": player.get("name"),
            "team_id": team.get("id"),
            "team_name": team.get("name")
        }
    )


# --------------------------------------------------
# 3. Criar DataFrame
# --------------------------------------------------

df = pd.DataFrame(players)


# --------------------------------------------------
# 4. Inspecionar
# --------------------------------------------------

print("\nPrimeiras linhas:")
print(df.head())

print("\nDimensão:")
print(df.shape)

print("\nColunas:")
print(df.columns.tolist())

print("\nTipos:")
print(df.dtypes)


# --------------------------------------------------
# 5. Verificar jogadores únicos
# --------------------------------------------------

print("\nJogadores únicos:")
print(df["player_id"].nunique())

print("\nTimes únicos:")
print(df["team_id"].nunique())


# --------------------------------------------------
# 6. Procurar duplicidades
# --------------------------------------------------

duplicates = df[
    df.duplicated(
        subset=["player_id"],
        keep=False
    )
].sort_values("player_id")

print("\nRegistros com player_id duplicado:")
print(len(duplicates))

if not duplicates.empty:
    print(duplicates.head(20))


# --------------------------------------------------
# 7. Quantidade por clube
# --------------------------------------------------

players_per_team = (
    df.groupby("team_name")
      .size()
      .sort_values(ascending=False)
)

print("\nRegistros por clube:")
print(players_per_team)

print("\nChaves disponíveis no primeiro registro:")
print(data[0].keys())

print("\nFrequência de cada player_id:")

print(
    df["player_id"]
    .value_counts()
    .head(20)
)

print("\nObjeto PLAYER completo:")

import json

print(
    json.dumps(
        data[0]["player"],
        indent=4,
        ensure_ascii=False
    )
)