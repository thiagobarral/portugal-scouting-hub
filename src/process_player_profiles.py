import json
import pandas as pd


# ---------------------------------------------
# 1. Carregar o JSON
# ---------------------------------------------

with open(
    "data/raw/player_profiles.json",
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


print("Perfis carregados:", len(data))


# ---------------------------------------------
# 2. Ver estrutura do primeiro registro
# ---------------------------------------------

print("\nChaves do primeiro registro:")
print(data[0].keys())

print("\nChaves dentro de player:")
print(data[0]["player"].keys())


# ---------------------------------------------
# 3. Extrair campos que interessam
# ---------------------------------------------

players = []

for item in data:

    player = item["player"]

    country = player.get("country", {})

    detailed_positions = player.get(
        "positionsDetailed",
        []
    )

    players.append({
        "player_id": player.get("id"),
        "name": player.get("name"),

        "detailed_position": (
            detailed_positions[0]
            if detailed_positions
            else None
        ),

        "birth_date": player.get("dateOfBirth"),
        "height_cm": player.get("height"),
        "preferred_foot": player.get("preferredFoot"),
        "country": country.get("name"),
        "market_value_eur": player.get(
            "proposedMarketValue"
        )
    })


# ---------------------------------------------
# 4. Criar DataFrame
# ---------------------------------------------

df = pd.DataFrame(players)


print("\nDimensão:")
print(df.shape)

print("\nPrimeiras linhas:")
print(df.head())

print("\nTipos:")
print(df.dtypes)

# ---------------------------------------------
# 5. Data Quality
# ---------------------------------------------

print("\nValores nulos por coluna:")
print(df.isnull().sum())

print("\nPercentual de valores nulos:")
print(
    (df.isnull().mean() * 100)
    .round(2)
)

print("\nPlayer IDs duplicados:")
print(df["player_id"].duplicated().sum())

print("\nPosições detalhadas:")
print(df["detailed_position"].value_counts(dropna=False))

print("\nPés preferidos:")
print(df["preferred_foot"].value_counts(dropna=False))

# ---------------------------------------------
# 6. Converter data de nascimento
# ---------------------------------------------

df["birth_date"] = pd.to_datetime(
    df["birth_date"],
    errors="coerce",
    utc=True
)

print("\nTipo de birth_date após conversão:")
print(df["birth_date"].dtype)

print("\nExemplo das datas:")
print(
    df[
        ["name", "birth_date"]
    ].head()
)

# ---------------------------------------------
# 7. Calcular idade no início da temporada
# ---------------------------------------------

REFERENCE_DATE = pd.Timestamp(
    "2025-07-01",
    tz="UTC"
)


def calculate_age(birth_date, reference_date):

    if pd.isna(birth_date):
        return pd.NA

    age = reference_date.year - birth_date.year

    # Verifica se o aniversário já ocorreu
    # na data de referência
    birthday_passed = (
        (reference_date.month, reference_date.day)
        >=
        (birth_date.month, birth_date.day)
    )

    if not birthday_passed:
        age -= 1

    return age


df["age_2025_26"] = df["birth_date"].apply(
    lambda x: calculate_age(x, REFERENCE_DATE)
)


df["is_u23"] = pd.Series(pd.NA, index=df.index, dtype="boolean")

df.loc[
    df["age_2025_26"].notna(),
    "is_u23"
] = df.loc[
    df["age_2025_26"].notna(),
    "age_2025_26"
] < 23


print("\nDistribuição das idades:")
print(
    df["age_2025_26"]
    .value_counts()
    .sort_index()
)


print("\nQuantidade de jogadores U23:")
print(
    df["is_u23"]
    .value_counts(dropna=False)
)

print("\nJogadores mais jovens:")

print(
    df[
        [
            "name",
            "birth_date",
            "age_2025_26",
            "detailed_position",
            "market_value_eur"
        ]
    ]
    .sort_values("birth_date", ascending=False)
    .head(20)
    .to_string(index=False)
)

# ---------------------------------------------
# 8. Carregar jogadores da temporada
# ---------------------------------------------

with open(
    "data/raw/players_2025_26.json",
    "r",
    encoding="utf-8"
) as file:
    season_data = json.load(file)


season_players = []

for item in season_data:

    player = item.get("player", {})
    team = item.get("team", {})

    season_players.append({
        "player_id": player.get("id"),
        "team_id": team.get("id"),
        "team_name": team.get("name")
    })


df_season = pd.DataFrame(season_players)


print("\nDados da temporada:")
print(df_season.head())

print("\nDimensão:")
print(df_season.shape)

# ---------------------------------------------
# 9. Merge perfil + temporada
# ---------------------------------------------

df_final = df.merge(
    df_season,
    on="player_id",
    how="left",
    validate="one_to_one"
)

df_final = df_final[
    [
        "player_id",
        "name",
        "team_id",
        "team_name",
        "birth_date",
        "age_2025_26",
        "is_u23",
        "detailed_position",
        "height_cm",
        "preferred_foot",
        "country",
        "market_value_eur"
    ]
]

print("\nDimensão após merge:")
print(df_final.shape)

print("\nPrimeiras linhas após merge:")
print(df_final.head())

print("\nJogadores sem clube:")
print(df_final["team_name"].isna().sum())

# ---------------------------------------------
# 10. Salvar dataset processado
# ---------------------------------------------

OUTPUT_FILE = "data/processed/players_2025_26.csv"

df_final.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(
    f"\nDataset processado salvo em: {OUTPUT_FILE}"
)

print("Jogadores salvos:", len(df_final))