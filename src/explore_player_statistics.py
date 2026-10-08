import json
from collections import Counter


INPUT_FILE = "data/raw/player_statistics_2025_26.json"


# --------------------------------------------------
# 1. Carregar estatísticas
# --------------------------------------------------

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


print("Registros carregados:", len(data))


# --------------------------------------------------
# 2. Ver estrutura geral
# --------------------------------------------------

print("\nChaves do primeiro registro:")
print(data[0].keys())

print("\nChaves dentro de data:")
print(data[0]["data"].keys())


# --------------------------------------------------
# 3. Estatísticas do primeiro jogador
# --------------------------------------------------

statistics = data[0]["data"].get(
    "statistics",
    {}
)

print("\nJogador:")
print(data[0]["player_name"])

print("\nQuantidade de métricas:")
print(len(statistics))

print("\nMétricas disponíveis:")

for key, value in statistics.items():
    print(
        f"{key}: {value}"
    )


# --------------------------------------------------
# 4. Contar frequência de cada métrica
# --------------------------------------------------

metric_counter = Counter()


for item in data:

    response_data = item.get(
        "data",
        {}
    )

    if not response_data:
        continue

    stats = response_data.get(
        "statistics",
        {}
    )

    metric_counter.update(
        stats.keys()
    )


# --------------------------------------------------
# 5. Mostrar cobertura das métricas
# --------------------------------------------------

print("\nCobertura das métricas:\n")

for metric, count in sorted(
    metric_counter.items(),
    key=lambda x: x[1],
    reverse=True
):

    percentage = (
        count / len(data)
    ) * 100

    print(
        f"{metric:35} "
        f"{count:3} "
        f"({percentage:6.2f}%)"
    )