from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCOUTING_DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "scouting_dataset_2025_26.csv"
)


# ============================================================
# CONFIGURATION
# ============================================================

MIN_MINUTES = 450


# ============================================================
# POSITION GROUPS
# ============================================================

POSITION_GROUP_MAP = {
    # Goalkeeper
    "GK": "Goalkeeper",

    # Centre Back
    "DC": "Centre Back",

    # Full Back
    "DL": "Full Back",
    "DR": "Full Back",

    # Midfielder
    "DM": "Midfielder",
    "MC": "Midfielder",
    "AM": "Midfielder",

    # Winger
    "ML": "Winger",
    "MR": "Winger",
    "LW": "Winger",
    "RW": "Winger",

    # Striker
    "ST": "Striker",
}


# ============================================================
# METRICS BY POSITION
# ============================================================

METRICS_BY_POSITION = {

    "Striker": [
        "goals_per90",
        "expectedGoals_per90",
        "totalShots_per90",
        "shotsOnTarget_per90",
        "assists_per90",
        "expectedAssists_per90",
    ],

    "Winger": [
        "goals_per90",
        "expectedGoals_per90",
        "assists_per90",
        "expectedAssists_per90",
        "keyPasses_per90",
        "successfulDribbles_per90",
    ],

    "Midfielder": [
        "assists_per90",
        "expectedAssists_per90",
        "keyPasses_per90",
        "accurateFinalThirdPasses_per90",
        "ballRecovery_per90",
        "interceptions_per90",
    ],

    "Full Back": [
        "assists_per90",
        "expectedAssists_per90",
        "keyPasses_per90",
        "accurateFinalThirdPasses_per90",
        "successfulDribbles_per90",
        "interceptions_per90",
    ],

    "Centre Back": [
        "tackles_per90",
        "interceptions_per90",
        "clearances_per90",
        "ballRecovery_per90",
        "aerialDuelsWonPercentage",
        "accuratePassesPercentage",
    ],

    "Goalkeeper": [
        "saves_per90",
        "goalsPrevented_per90",
        "goalsConceded_per90",
        "highClaims_per90",
        "successfulRunsOut_per90",
        "accuratePassesPercentage",
    ],
}


# ============================================================
# METRICS WHERE LOWER VALUES ARE BETTER
# ============================================================

LOWER_IS_BETTER = {
    "goalsConceded_per90",
}


# ============================================================
# VOLUME METRICS
# ============================================================

# Estas métricas serão normalizadas por 90 minutos.
#
# Métricas percentuais NÃO entram aqui.

PER90_METRICS = [
    # Offensive production
    "goals",
    "assists",
    "expectedGoals",
    "expectedAssists",
    "bigChancesCreated",
    "bigChancesMissed",

    # Shooting
    "totalShots",
    "shotsOnTarget",

    # Creation / passing
    "keyPasses",
    "totalPasses",
    "accuratePasses",
    "accurateFinalThirdPasses",

    # Dribbling
    "successfulDribbles",

    # Defensive
    "tackles",
    "tacklesWon",
    "interceptions",
    "clearances",
    "ballRecovery",
    "outfielderBlocks",

    # Duels
    "groundDuelsWon",
    "aerialDuelsWon",
    "totalDuelsWon",

    # Possession
    "possessionLost",
    "possessionWonAttThird",

    # Goalkeeper
    "saves",
    "goalsPrevented",
    "goalsConceded",
    "highClaims",
    "successfulRunsOut",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_data():
    """
    Carrega o dataset processado utilizado pela aplicação.

    O arquivo já reúne informações dos jogadores e estatísticas
    da temporada, portanto a aplicação não depende dos dados
    brutos nem de nova coleta para ser executada.
    """

    df = pd.read_csv(
        SCOUTING_DATA_FILE
    )

    df["birth_date"] = pd.to_datetime(
        df["birth_date"],
        errors="coerce",
        utc=True,
    )

    df["is_u23"] = (
        df["is_u23"]
        .astype("boolean")
    )

    if df["player_id"].duplicated().any():
        raise ValueError(
            "Existem player_id duplicados "
            "no dataset processado."
        )

    return df


# ============================================================
# PREPARE ANALYSIS
# ============================================================

def prepare_analysis(df):
    """
    Prepara a base utilizada pelo motor de scouting.

    Cria:
    - grupos posicionais;
    - métricas por 90 minutos.
    """

    analysis = df.copy()

    # --------------------------------------------------------
    # POSITION GROUP
    # --------------------------------------------------------

    analysis["position_group"] = (
        analysis[
            "detailed_position"
        ]
        .map(
            POSITION_GROUP_MAP
        )
    )

    # --------------------------------------------------------
    # PER 90 METRICS
    # --------------------------------------------------------

    for metric in PER90_METRICS:

        if metric not in analysis.columns:
            continue

        analysis[
            f"{metric}_per90"
        ] = np.where(
            analysis["minutesPlayed"] > 0,
            (
                analysis[metric]
                / analysis["minutesPlayed"]
                * 90
            ),
            np.nan,
        )

    return analysis


# ============================================================
# CREATE POOLS
# ============================================================

def create_pools(analysis):
    """
    Cria duas populações diferentes.

    benchmark_pool:
        Jogadores da liga com minutos suficientes para
        formar a população estatística de referência.

    scouting_pool:
        Jogadores U23 utilizados pelo Talent Finder.

    Importante:
    o scouting_pool NÃO aplica automaticamente o corte de
    450 minutos, pois o usuário pode controlar esse filtro
    no dashboard.

    Já o benchmark usa MIN_MINUTES para evitar percentis
    baseados em amostras extremamente pequenas.
    """

    # --------------------------------------------------------
    # BENCHMARK
    # --------------------------------------------------------

    benchmark_pool = analysis[
        (
            analysis[
                "minutesPlayed"
            ] >= MIN_MINUTES
        )
        &
        (
            analysis[
                "position_group"
            ].notna()
        )
    ].copy()

    # --------------------------------------------------------
    # SCOUTING POOL
    # --------------------------------------------------------

    scouting_pool = analysis[
        (
            analysis[
                "is_u23"
            ] == True
        )
        &
        (
            analysis[
                "position_group"
            ].notna()
        )
    ].copy()

    return (
        benchmark_pool,
        scouting_pool,
    )


# ============================================================
# GET PLAYER PROFILE
# ============================================================

def get_player_profile(
    player_name,
    analysis,
):
    """
    Retorna a linha completa de um jogador.
    """

    player = analysis[
        analysis["name"]
        == player_name
    ]

    if player.empty:

        raise ValueError(
            f"Jogador não encontrado: "
            f"{player_name}"
        )

    return player.iloc[0]


# ============================================================
# GET PLAYER INFO
# ============================================================

def get_player_info(
    player_name,
    analysis,
):
    """
    Retorna as principais informações utilizadas
    pelo dashboard.
    """

    player = get_player_profile(
        player_name,
        analysis,
    )

    return {
        "player_id":
            player.get(
                "player_id"
            ),

        "name":
            player.get(
                "name"
            ),

        "team":
            player.get(
                "team_name"
            ),

        "position":
            player.get(
                "detailed_position"
            ),

        "position_group":
            player.get(
                "position_group"
            ),

        "age":
            player.get(
                "age_2025_26"
            ),

        "height_cm":
            player.get(
                "height_cm"
            ),

        "preferred_foot":
            player.get(
                "preferred_foot"
            ),

        "country":
            player.get(
                "country"
            ),

        "market_value_eur":
            player.get(
                "market_value_eur"
            ),

        "minutes":
            player.get(
                "minutesPlayed"
            ),

        "appearances":
            player.get(
                "appearances"
            ),

        "starts":
            player.get(
                "matchesStarted"
            ),
    }


# ============================================================
# GET POSITION METRICS
# ============================================================

def get_talent_metrics(
    position_group,
):
    """
    Retorna as métricas utilizadas para determinada posição.
    """

    if (
        position_group
        not in METRICS_BY_POSITION
    ):

        raise ValueError(
            "Não existem métricas configuradas "
            f"para a posição: {position_group}"
        )

    return METRICS_BY_POSITION[
        position_group
    ]


# ============================================================
# PERCENTILE
# ============================================================

def calculate_percentile(
    value,
    reference_values,
    lower_is_better=False,
):
    """
    Calcula o percentil de um valor em relação
    à população de referência.

    Para métricas normais:
        maior = melhor

    Para métricas inversas:
        menor = melhor
    """

    if pd.isna(value):
        return np.nan

    reference_values = (
        pd.Series(
            reference_values
        )
        .dropna()
    )

    if reference_values.empty:
        return np.nan

    if lower_is_better:

        percentile = (
            (
                reference_values
                >= value
            )
            .mean()
            * 100
        )

    else:

        percentile = (
            (
                reference_values
                <= value
            )
            .mean()
            * 100
        )

    return float(
        percentile
    )


# ============================================================
# GET PLAYER KPIS
# ============================================================

def get_player_kpis(
    player_name,
    scouting_pool,
    benchmark_pool,
):
    """
    Retorna valores e percentis das métricas específicas
    da posição de um jogador.

    Os percentis são calculados contra jogadores da mesma
    posição no benchmark.
    """

    player_rows = scouting_pool[
        scouting_pool["name"]
        == player_name
    ]

    if player_rows.empty:

        raise ValueError(
            f"Jogador não encontrado "
            f"no scouting pool: "
            f"{player_name}"
        )

    player = (
        player_rows.iloc[0]
    )

    position_group = player[
        "position_group"
    ]

    metrics = get_talent_metrics(
        position_group
    )

    reference_pool = benchmark_pool[
        benchmark_pool[
            "position_group"
        ] == position_group
    ]

    if reference_pool.empty:

        raise ValueError(
            "Não existem jogadores no benchmark "
            "para esta posição."
        )

    kpis = {}

    for metric in metrics:

        if (
            metric not in
            scouting_pool.columns
            or metric not in
            benchmark_pool.columns
        ):
            continue

        value = player.get(
            metric
        )

        reference_values = (
            reference_pool[
                metric
            ]
            .dropna()
        )

        percentile = (
            calculate_percentile(
                value=value,
                reference_values=reference_values,
                lower_is_better=(
                    metric
                    in LOWER_IS_BETTER
                ),
            )
        )

        kpis[metric] = {
            "value": value,
            "percentile": percentile,
        }

    return kpis


# ============================================================
# TALENT FINDER — EXPLAINABLE RANKING
# ============================================================

def calculate_talent_ranking(
    candidates,
    benchmark_pool,
    position_group,
    weights=None,
):
    """
    Calcula um ranking explicável de jogadores.

    O Profile Score é uma média ponderada dos percentis
    das métricas específicas da posição.

    Parameters
    ----------
    candidates : pandas.DataFrame
        Jogadores que passaram pelos filtros
        do Talent Finder.

    benchmark_pool : pandas.DataFrame
        População utilizada como referência estatística.

    position_group : str
        Grupo posicional.

    weights : dict, optional
        Pesos definidos pelo usuário.

        Exemplo:

        {
            "goals_per90": 100,
            "expectedGoals_per90": 100,
            "assists_per90": 50
        }

        Os pesos representam importância relativa.
        Eles não precisam somar 100.

    Returns
    -------
    pandas.DataFrame
        Jogadores ordenados pelo Profile Score.
    """

    metrics = get_talent_metrics(
        position_group
    )

    # --------------------------------------------------------
    # FILTER POSITION
    # --------------------------------------------------------

    candidate_pool = candidates[
        candidates[
            "position_group"
        ] == position_group
    ].copy()

    reference_pool = benchmark_pool[
        benchmark_pool[
            "position_group"
        ] == position_group
    ].copy()

    if candidate_pool.empty:
        return candidate_pool

    if reference_pool.empty:

        raise ValueError(
            "Não existem jogadores suficientes "
            "no benchmark para esta posição."
        )

    # --------------------------------------------------------
    # CHECK AVAILABLE METRICS
    # --------------------------------------------------------

    available_metrics = [
        metric
        for metric in metrics
        if (
            metric
            in candidate_pool.columns
            and metric
            in reference_pool.columns
        )
    ]

    if not available_metrics:

        raise ValueError(
            "Nenhuma métrica disponível "
            "para calcular o ranking."
        )

    # --------------------------------------------------------
    # WEIGHTS
    # --------------------------------------------------------

    if weights is None:

        weights = {
            metric: 1.0
            for metric
            in available_metrics
        }

    else:

        weights = {
            metric: float(
                weights.get(
                    metric,
                    0,
                )
            )
            for metric
            in available_metrics
        }

    if (
        sum(
            weights.values()
        )
        <= 0
    ):

        raise ValueError(
            "A soma dos pesos deve "
            "ser maior que zero."
        )

    # --------------------------------------------------------
    # CALCULATE PERCENTILES
    # --------------------------------------------------------

    percentile_columns = []

    for metric in available_metrics:

        percentile_column = (
            f"{metric}_percentile"
        )

        percentile_columns.append(
            percentile_column
        )

        reference_values = (
            reference_pool[
                metric
            ]
            .dropna()
        )

        if reference_values.empty:

            candidate_pool[
                percentile_column
            ] = np.nan

            continue

        lower_is_better = (
            metric
            in LOWER_IS_BETTER
        )

        candidate_pool[
            percentile_column
        ] = candidate_pool[
            metric
        ].apply(
            lambda value:
                calculate_percentile(
                    value=value,
                    reference_values=(
                        reference_values
                    ),
                    lower_is_better=(
                        lower_is_better
                    ),
                )
        )

    # --------------------------------------------------------
    # WEIGHTED PROFILE SCORE
    # --------------------------------------------------------

    def calculate_player_score(
        row
    ):

        weighted_sum = 0.0
        valid_weight_sum = 0.0

        for metric in available_metrics:

            percentile_column = (
                f"{metric}_percentile"
            )

            percentile = row[
                percentile_column
            ]

            weight = weights[
                metric
            ]

            # Métrica ausente não vira zero.
            # Ela simplesmente não participa do score.
            if (
                pd.notna(
                    percentile
                )
                and weight > 0
            ):

                weighted_sum += (
                    percentile
                    * weight
                )

                valid_weight_sum += (
                    weight
                )

        if valid_weight_sum == 0:
            return np.nan

        return (
            weighted_sum
            / valid_weight_sum
        )

    candidate_pool[
        "talent_score"
    ] = candidate_pool.apply(
        calculate_player_score,
        axis=1,
    )

    # --------------------------------------------------------
    # METRIC COVERAGE
    # --------------------------------------------------------

    candidate_pool[
        "metrics_used"
    ] = (
        candidate_pool[
            percentile_columns
        ]
        .notna()
        .sum(
            axis=1
        )
    )

    candidate_pool[
        "metrics_total"
    ] = len(
        available_metrics
    )

    # --------------------------------------------------------
    # RANKING
    # --------------------------------------------------------

    candidate_pool = (
        candidate_pool
        .sort_values(
            [
                "talent_score",
                "minutesPlayed",
            ],
            ascending=[
                False,
                False,
            ],
            na_position="last",
        )
        .reset_index(
            drop=True
        )
    )

    candidate_pool[
        "talent_rank"
    ] = (
        candidate_pool[
            "talent_score"
        ]
        .rank(
            method="min",
            ascending=False,
        )
        .astype(
            "Int64"
        )
    )

    return candidate_pool