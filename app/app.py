import sys
import html as html_lib
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


# ============================================================
# SCOUTING ENGINE
# ============================================================

from src.scouting import (
    load_data,
    prepare_analysis,
    create_pools,
    get_player_info,
    get_player_kpis,
    calculate_talent_ranking,
    get_talent_metrics,
    MIN_MINUTES,
    LOWER_IS_BETTER,
)

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="Portugal Scouting Hub",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "PT"

if "page" not in st.session_state:
    st.session_state.page = "PLAYER PROFILE"

if "talent_position_menu_open" not in st.session_state:
    st.session_state.talent_position_menu_open = False


# ============================================================
# TEXT / TRANSLATIONS
# ============================================================

TEXT = {
    "EN": {
        "subtitle": "Data Driven Talent",
        "player_profile": "PLAYER PROFILE",
        "compare": "COMPARE",
        "talent_finder": "TALENT FINDER",
        "player": "Player",
        "player_a": "Player A",
        "player_b": "Player B",
        "market_value": "MARKET VALUE",
        "minutes": "MINUTES",
        "matches": "MATCHES",
        "starts": "STARTS",
        "performance": "PERFORMANCE",
        "performance_percentile_explanation":
            "P = Percentile among players in the same position with at least 450 minutes played.",
        "performance_profile": "PERFORMANCE PROFILE",
        "performance_profile_subtitle":
            "0–100 percentile scale vs. same-position players with at least 450 minutes",
        "comparison": "PLAYER COMPARISON",
        "comparison_subtitle":
            "Percentile comparison between players from the same positional group",
        "comparison_table": "METRIC COMPARISON",
        "years": "years",
        "goalkeeper_message":
            "Goalkeeper performance analysis will use a separate position-specific model.",
        "talent_message":
            "Talent Finder will be implemented in the next step.",
        "no_comparable":
            "No comparable players available.",
    },

    "PT": {
        "subtitle": "Talento Orientado por Dados",
        "player_profile": "PERFIL DO JOGADOR",
        "compare": "COMPARAR",
        "talent_finder": "BUSCAR TALENTOS",
        "player": "Jogador",
        "player_a": "Jogador A",
        "player_b": "Jogador B",
        "market_value": "VALOR DE MERCADO",
        "minutes": "MINUTOS",
        "matches": "JOGOS",
        "starts": "TITULARIDADES",
        "performance": "DESEMPENHO",
        "performance_percentile_explanation":
            "P = Percentil entre jogadores da mesma posição com no mínimo 450 minutos jogados.",
        "performance_profile": "RADAR DE DESEMPENHO",
        "performance_profile_subtitle":
            "Escala de percentil 0–100 comparada a jogadores da mesma posição com no mínimo 450 minutos",
        "comparison": "COMPARAÇÃO DE JOGADORES",
        "comparison_subtitle":
            "Comparação de percentis entre jogadores do mesmo grupo posicional",
        "comparison_table": "COMPARAÇÃO DE MÉTRICAS",
        "years": "anos",
        "goalkeeper_message":
            "A análise de desempenho de goleiros utilizará um modelo específico para a posição.",
        "talent_message":
            "O Talent Finder será implementado na próxima etapa.",
        "no_comparable":
            "Não há jogadores comparáveis disponíveis.",
    },
}


# ============================================================
# METRIC LABELS
# ============================================================

METRIC_LABELS = {
    "EN": {
        "goals_per90": "Goals / 90",
        "expectedGoals_per90": "xG / 90",
        "totalShots_per90": "Shots / 90",
        "shotsOnTarget_per90": "Shots on Target / 90",
        "assists_per90": "Assists / 90",
        "expectedAssists_per90": "xA / 90",
        "keyPasses_per90": "Key Passes / 90",
        "successfulDribbles_per90": "Successful Dribbles / 90",
        "accurateFinalThirdPasses_per90": "Final Third Passes / 90",
        "ballRecovery_per90": "Ball Recoveries / 90",
        "interceptions_per90": "Interceptions / 90",
        "tackles_per90": "Tackles / 90",
        "clearances_per90": "Clearances / 90",
        "aerialDuelsWonPercentage": "Aerial Duels Won %",
        "accuratePassesPercentage": "Pass Accuracy %",
        "saves_per90": "Saves / 90",
        "goalsPrevented_per90": "Goals Prevented / 90",
        "goalsConceded_per90": "Goals Conceded / 90",
        "highClaims_per90": "High Claims / 90",
        "successfulRunsOut_per90": "Successful Runs Out / 90",
    },

    "PT": {
        "goals_per90": "Gols / 90",
        "expectedGoals_per90": "xG / 90",
        "totalShots_per90": "Finalizações / 90",
        "shotsOnTarget_per90": "Finalizações no Alvo / 90",
        "assists_per90": "Assistências / 90",
        "expectedAssists_per90": "xA / 90",
        "keyPasses_per90": "Passes-Chave / 90",
        "successfulDribbles_per90": "Dribles Certos / 90",
        "accurateFinalThirdPasses_per90": "Passes no Terço Final / 90",
        "ballRecovery_per90": "Recuperações / 90",
        "interceptions_per90": "Interceptações / 90",
        "tackles_per90": "Desarmes / 90",
        "clearances_per90": "Cortes / 90",
        "aerialDuelsWonPercentage": "Duelos Aéreos Vencidos %",
        "accuratePassesPercentage": "Precisão de Passe %",
        "saves_per90": "Defesas / 90",
        "goalsPrevented_per90": "Gols Evitados / 90",
        "goalsConceded_per90": "Gols Sofridos / 90",
        "highClaims_per90": "Bolas Aéreas Dominadas / 90",
        "successfulRunsOut_per90": "Saídas Bem-Sucedidas / 90",
    },
}


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>

:root {
    --bg: #07111d;
    --sidebar: #07121f;
    --panel: #0b1b2a;
    --border: #18384d;
    --accent: #29a9e0;
    --pt-green: #168447;
    --pt-red: #D92D3A;
    --pt-gold: #F2C94C;
    --text: #f4f8fb;
    --muted: #8298aa;
    --green: #4bd39b;
    --yellow: #e6bb63;
    --red: #df7b7b;
}

.stApp {
    background:
        radial-gradient(
            circle at 85% 0%,
            rgba(19, 91, 130, 0.12),
            transparent 28%
        ),
        var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 1720px;
    width: calc(100% - 2rem);
    margin-left: 0;
    margin-right: auto;
    padding-top: 4.5rem;
    padding-left: 1.5rem;
    padding-right: 2.25rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    background: var(--sidebar);
    border-right: 1px solid #162c3c;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.4rem;
}

.sidebar-brand-top {
    color: #ffffff;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
}

.sidebar-brand-main {
    color: #ffffff;
    font-size: 1rem;
    font-weight: 850;
    letter-spacing: 0.06em;
    margin-top: 0.18rem;
}

.sidebar-subtitle {
    color: #55758c;
    font-size: 0.63rem;
    margin-top: 0.35rem;
    margin-bottom: 1.5rem;
}

.sidebar-brand-wrap {
    position: relative;
    overflow: hidden;
    min-height: 5.3rem;
}

.sidebar-language-label {
    color: #4f7188;
    font-size: 0.56rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    margin-top: 0.15rem;
    margin-bottom: 0.35rem;
}

.sidebar-language-separator {
    color: #35556a;
    text-align: center;
    font-size: 0.78rem;
    line-height: 2.55rem;
}

.sidebar-section {
    color: #4f7188;
    font-size: 0.59rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    margin-top: 1.5rem;
    margin-bottom: 0.65rem;
}

/* Professional sidebar navigation */
[data-testid="stSidebar"] .stButton {
    margin-bottom: 0.38rem;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    min-height: 2.65rem;
    justify-content: flex-start;
    padding: 0.62rem 0.78rem;
    border-radius: 9px;
    border: 1px solid transparent;
    background: transparent;
    color: #8fa5b6;
    font-size: 0.72rem;
    font-weight: 750;
    letter-spacing: 0.035em;
    text-align: left;
    box-shadow: none;
    transition: background 0.16s ease, border-color 0.16s ease, color 0.16s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(41, 169, 224, 0.07);
    border-color: rgba(41, 169, 224, 0.18);
    color: #f4f8fb;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(217,45,58,0.15), rgba(217,45,58,0.045));
    border-color: rgba(217,45,58,0.42);
    color: #ffffff;
    box-shadow: inset 3px 0 0 #D92D3A;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, rgba(217,45,58,0.20), rgba(217,45,58,0.065));
    border-color: rgba(217,45,58,0.52);
}

.hub-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        120deg,
        rgba(12, 36, 54, 0.98),
        rgba(8, 26, 41, 0.98)
    );
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.45rem 1.6rem;
    margin-bottom: 1.5rem;
}

.hub-header::after {
    content: "PT";
    position: absolute;
    right: 2.1rem;
    top: -0.6rem;
    color: #ffffff;
    font-size: 5.7rem;
    font-weight: 900;
    opacity: 0.035;
    transform: rotate(-6deg);
}

.hub-title {
    color: #ffffff;
    font-size: 1.65rem;
    font-weight: 850;
    letter-spacing: 0.055em;
}

.hub-subtitle {
    color: #7990a3;
    font-size: 0.76rem;
    margin-top: 0.35rem;
}

.page-title-plain {
    color: #ffffff;
    font-size: 1.65rem;
    font-weight: 850;
    letter-spacing: 0.055em;
    margin: 0 0 1.15rem 0;
    line-height: 1.15;
}

.section-title {
    color: #dce8f1;
    font-size: 0.9rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    margin-top: 1.5rem;
    margin-bottom: 0.7rem;
}

.section-subtitle {
    color: #6f8799;
    font-size: 0.9rem;
    line-height: 1.5;
    margin-top: -0.28rem;
    margin-bottom: 0.75rem;
}

.player-panel {
    background: linear-gradient(
        135deg,
        #0d2232,
        #091a28
    );
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.15rem 1.35rem;
    margin-bottom: 0;
    min-height: 220px;
    height: 220px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 1rem;
    overflow: hidden;
}

.player-panel-content {
    width: 100%;
    min-width: 0;
}

.player-profile-body {
    display: flex;
    align-items: center;
    gap: 1.35rem;
    margin-top: 0.65rem;
}

.player-details-block {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
}

.player-role-line {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-top: 0;
}

.club-badge {
    width: 92px;
    height: 92px;
    object-fit: contain;
    flex: 0 0 92px;
}

.player-photo-wrap {
    width: 154px;
    height: 154px;
    flex: 0 0 154px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    overflow: hidden;
    border-radius: 14px;
    background: transparent;
    isolation: isolate;
}

.player-photo {
    width: 154px;
    height: 154px;
    object-fit: contain;
    object-position: center bottom;
    filter: none;
    mix-blend-mode: normal;
    -webkit-mask-image: radial-gradient(
        ellipse 76% 88% at 50% 42%,
        #000 0%,
        #000 72%,
        rgba(0, 0, 0, 0.92) 82%,
        transparent 100%
    );
    mask-image: radial-gradient(
        ellipse 76% 88% at 50% 42%,
        #000 0%,
        #000 72%,
        rgba(0, 0, 0, 0.92) 82%,
        transparent 100%
    );
}

.player-photo-fallback {
    width: 142px;
    height: 142px;
    display: none;
    align-items: center;
    justify-content: center;
    color: #4f7188;
    font-size: 3rem;
    background: rgba(255,255,255,0.025);
}

.player-name {
    color: #ffffff;
    font-size: 1.7rem;
    font-weight: 850;
    line-height: 1.1;
}

.player-role {
    color: var(--accent);
    font-size: 0.78rem;
    font-weight: 700;
    margin-top: 0.45rem;
}

.player-meta {
    color: #9db0bf;
    font-size: 0.88rem;
    margin-top: 1rem;
    line-height: 1.8;
}

.player-meta strong {
    color: #edf5fa;
}

.player-meta-compact {
    margin-top: 0.45rem;
    line-height: 1.65;
}

/* Profile overview is rendered as ONE HTML grid.
   This avoids independent Streamlit column wrappers adding their own
   spacing and guarantees exact top/bottom alignment. */
.profile-overview-grid {
    display: grid;
    /* Use the same three equal columns as the Performance section.
       The player panel occupies column 1 and the summary area occupies
       columns 2-3. This makes every vertical boundary line up exactly. */
    grid-template-columns: repeat(3, minmax(0, 1fr));
    column-gap: 1rem;
    height: 220px;
    width: 100%;
    align-items: stretch;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.profile-overview-grid .player-panel,
.profile-overview-grid .profile-summary-grid {
    margin: 0 !important;
    width: 100%;
    height: 220px;
    min-height: 220px;
    box-sizing: border-box;
}

.profile-overview-grid .player-panel {
    grid-column: 1;
}

.profile-overview-grid .profile-summary-grid {
    grid-column: 2 / 4;
}

.profile-summary-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: repeat(2, minmax(0, 1fr));
    column-gap: 1rem;
    row-gap: 0.75rem;
    height: 220px;
    box-sizing: border-box;
}

.profile-summary-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 1rem 1.1rem;
    height: 100%;
    min-height: 0;
    box-sizing: border-box;
}

.info-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 11px;
    padding: 1rem 1.1rem;
    min-height: 103px;
    height: 103px;
    margin-top: 0;
}

.info-label {
    color: #6e899d;
    font-size: 0.61rem;
    font-weight: 800;
    letter-spacing: 0.11em;
}

.info-value {
    color: #ffffff;
    font-size: 1.55rem;
    font-weight: 850;
    margin-top: 0.45rem;
}

.performance-card {
    background: linear-gradient(
        145deg,
        #0d2232,
        #0a1926
    );
    border: 1px solid #1c3b50;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    min-height: 135px;
    margin-bottom: 0.75rem;
}

.performance-label {
    color: #91a6b7;
    font-size: 0.7rem;
    font-weight: 700;
    min-height: 34px;
}

.performance-value {
    color: #ffffff;
    font-size: 1.75rem;
    font-weight: 850;
    margin-top: 0.1rem;
}

.percentile {
    display: inline-block;
    margin-top: 0.65rem;
    border-radius: 999px;
    padding: 0.23rem 0.58rem;
    font-size: 0.68rem;
    font-weight: 800;
}

.percentile-high {
    background: rgba(41, 190, 125, 0.13);
    color: var(--green);
    border: 1px solid rgba(75, 211, 155, 0.22);
}

.percentile-medium {
    background: rgba(215, 170, 65, 0.13);
    color: var(--yellow);
    border: 1px solid rgba(230, 187, 99, 0.22);
}

.percentile-low {
    background: rgba(202, 82, 82, 0.13);
    color: var(--red);
    border: 1px solid rgba(223, 123, 123, 0.22);
}

.compare-player {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        145deg,
        #0d2232,
        #091a28
    );
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    margin-top: 0.5rem;
    margin-bottom: 0.8rem;
}

.compare-name {
    color: #ffffff;
    font-size: 1.25rem;
    font-weight: 850;
}

.compare-info {
    color: #829aad;
    font-size: 0.76rem;
    margin-top: 0.45rem;
    line-height: 1.7;
}

.compare-team {
    color: var(--accent);
    font-weight: 700;
}


.compare-player.player-a { box-shadow: inset 4px 0 0 #29a9e0; }
.compare-player.player-b { box-shadow: inset 4px 0 0 #f0a04b; }
.compare-player.player-a .compare-name { color: #dff5ff; }
.compare-player.player-b .compare-name { color: #ffe8cf; }

/* Subtle product interaction polish */
.performance-card, .profile-summary-card, .info-card, .compare-player, .score-shell {
    transition: transform 0.18s ease, border-color 0.18s ease, background 0.18s ease;
}
.performance-card:hover, .profile-summary-card:hover, .info-card:hover, .compare-player:hover {
    transform: translateY(-1px);
    border-color: rgba(104, 170, 205, 0.48);
}

/* Talent Finder visual grouping */
.talent-group-label {
    color: #dce8f1; font-size: 0.72rem; font-weight: 800; letter-spacing: 0.12em;
    margin: 0.8rem 0 0.55rem 0; padding-left: 0.65rem; border-left: 3px solid #D92D3A;
}

/* Percentile explanation bars */
.analysis-metric { margin: 0.55rem 0 0.9rem 0; }
.analysis-metric-head { display:flex; justify-content:space-between; gap:1rem; color:#dbe7ef; font-size:0.78rem; }
.analysis-metric-meta { color:#8fa5b6; white-space:nowrap; }
.analysis-bar { height:6px; background:rgba(255,255,255,0.07); border-radius:999px; overflow:hidden; margin-top:0.35rem; }
.analysis-bar > span { display:block; height:100%; border-radius:999px; }
.analysis-bar.high > span { background:#4bd39b; }
.analysis-bar.medium > span { background:#e6bb63; }
.analysis-bar.low > span { background:#D92D3A; }

/* Tiny Portuguese identity accent */
.sidebar-brand-wrap::after {
    content:""; display:block; width:42px; height:3px; margin-top:0.55rem; border-radius:999px;
    background:linear-gradient(90deg,#168447 0 48%,#f2c94c 48% 52%,#D92D3A 52% 100%); opacity:0.85;
}

/* Main content kept clean: Portuguese accent rails removed. */
[data-testid="stMain"] {
    position: relative;
}

/* Profile card: subtle Portugal band, not decorative noise. */
.player-panel {
    position: relative;
}

.player-panel::before {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--pt-green) 0 58%, var(--pt-gold) 58% 61%, var(--pt-red) 61% 100%);
    opacity: 0.9;
}

/* Active navigation now reads as Portugal rather than generic red. */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(90deg, rgba(22,132,71,0.17), rgba(217,45,58,0.07));
    border-color: rgba(217,45,58,0.38);
    box-shadow: inset 3px 0 0 var(--pt-green);
}

[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: linear-gradient(90deg, rgba(22,132,71,0.22), rgba(217,45,58,0.09));
    border-color: rgba(242,201,76,0.34);
}

/* A faint national glow in the upper-left keeps the identity visible on wide screens. */
.stApp {
    background:
        radial-gradient(circle at 18% 2%, rgba(22,132,71,0.075), transparent 20%),
        radial-gradient(circle at 28% 4%, rgba(217,45,58,0.045), transparent 16%),
        radial-gradient(circle at 85% 0%, rgba(19,91,130,0.12), transparent 28%),
        var(--bg);
}

div[data-baseweb="select"] > div {
    background-color: #101d2a;
    border-color: #244156;
}

/* Talent Finder: rótulo e dropdown de posição sem busca */
.filter-field-label {
    color: #ffffff;
    font-size: 0.92rem;
    font-weight: 600;
    margin-bottom: 0.35rem;
}

/* Dropdown de posição customizado: compacto, não pesquisável e com menu overlay. */
.st-key-talent_position_dropdown {
    position: relative;
    width: 280px !important;
    min-width: 280px !important;
    overflow: visible !important;
    z-index: 1000;
}

.st-key-talent_position_dropdown > div {
    overflow: visible !important;
}

.st-key-talent_position_dropdown .stButton > button {
    width: auto !important;
    min-width: 0 !important;
    min-height: 2.35rem !important;
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
}

/* O menu fica fora do fluxo normal e sobrepõe os filtros abaixo. */
.st-key-talent_position_menu {
    position: absolute !important;
    top: 2.75rem;
    left: 0;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    box-sizing: border-box !important;
    z-index: 10000 !important;
    background: #0d1117;
    border: 1px solid #34404c;
    border-radius: 12px;
    padding: 0.75rem;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45);
}

.st-key-talent_position_menu [data-testid="stVerticalBlock"] {
    width: 100% !important;
    min-width: 0 !important;
    gap: 0.45rem !important;
}

.st-key-talent_position_menu .stButton > button {
    width: 100% !important;
    min-height: 2.35rem !important;
    justify-content: center !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
}

div[data-baseweb="select"] span {
    color: #eef5f9;
}

[data-testid="stAlert"] {
    background: var(--panel);
    border: 1px solid var(--border);
}

#MainMenu {
    visibility: hidden;
}


/* Product-level page hierarchy */
.page-header-clean {
    margin: 0 0 1.25rem 0;
    padding: 0;
}
.page-header-clean .page-kicker {
    color: #ffffff;
    font-size: 2.05rem;
    font-weight: 850;
    letter-spacing: 0.055em;
    line-height: 1.15;
}
.page-header-clean .page-description {
    color: #7f98aa;
    font-size: 1rem;
    line-height: 1.55;
    margin-top: 0.48rem;
}

/* Talent Finder step indicator */
.workflow-steps {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.55rem;
    margin: 0.35rem 0 1.25rem 0;
}
.workflow-step {
    border: 1px solid rgba(217,45,58,0.22);
    background: rgba(217,45,58,0.045);
    border-radius: 9px;
    padding: 0.58rem 0.7rem;
    color: #8fa5b6;
    font-size: 0.66rem;
    font-weight: 750;
    letter-spacing: 0.055em;
}
.workflow-step strong { color: #D92D3A; margin-right: 0.28rem; }

/* Profile Score: analytical indicator, not an objective player grade */
.score-shell {
    border: 1px solid var(--border);
    background: linear-gradient(135deg, #0d2232, #091a28);
    border-radius: 12px;
    padding: 0.95rem 1rem;
    min-height: 96px;
}
.score-head { display:flex; align-items:baseline; justify-content:space-between; gap:1rem; }
.score-label { color:#6f8799; font-size:0.62rem; font-weight:800; letter-spacing:0.12em; }
.score-number { color:#ffffff; font-size:1.45rem; font-weight:850; }
.score-track { height:7px; border-radius:999px; background:rgba(255,255,255,0.07); margin-top:0.72rem; overflow:hidden; }
.score-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#D92D3A,#e85a65); }
.score-note { color:#5f7b8f; font-size:0.62rem; margin-top:0.48rem; }

.empty-state {
    border: 1px dashed rgba(111,135,153,0.32);
    border-radius: 12px;
    background: rgba(255,255,255,0.018);
    padding: 1.2rem 1.25rem;
    margin-top: 0.25rem;
}
.empty-state-title { color:#e7eef4; font-weight:800; font-size:0.88rem; }
.empty-state-copy { color:#6f8799; font-size:0.72rem; margin-top:0.3rem; }

.product-footer {
    border-top: 1px solid rgba(104,140,162,0.15);
    margin-top: 2.5rem;
    padding-top: 0.9rem;
    color: #526f83;
    font-size: 0.62rem;
    display:flex;
    justify-content:space-between;
    gap:1rem;
}
@media (max-width: 1800px) {
    .block-container { max-width: 1500px; margin-left: 0; margin-right: auto; }
}
@media (max-width: 900px) {
    .block-container { width: 100%; padding-left: 1rem; padding-right: 1rem; }
    .workflow-steps { grid-template-columns: 1fr 1fr; }
    .product-footer { flex-direction:column; }
}

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def persist_widget_value(widget_key):
    """Copy a widget value to a non-widget session key.

    Streamlit can remove widget state when a widget is not rendered on the
    current page. The shadow key below survives page navigation.
    """
    st.session_state[f"persist_{widget_key}"] = st.session_state[widget_key]


def restore_widget_value(
    widget_key,
    default,
    valid_values=None,
    min_value=None,
    max_value=None,
):
    """Restore a page widget from its persistent shadow value."""
    persistent_key = f"persist_{widget_key}"

    if persistent_key not in st.session_state:
        st.session_state[persistent_key] = default

    saved_value = st.session_state[persistent_key]

    if valid_values is not None and saved_value not in valid_values:
        saved_value = default

    if min_value is not None and saved_value < min_value:
        saved_value = min_value

    if max_value is not None and saved_value > max_value:
        saved_value = max_value

    st.session_state[persistent_key] = saved_value

    # Only restore when Streamlit has removed the page widget key.
    # If the key already exists, keep the user's current interaction.
    if widget_key not in st.session_state:
        st.session_state[widget_key] = saved_value


def player_options(frame):
    """Unique player IDs, sorted for consistent selectors."""
    return (frame.dropna(subset=["player_id"])
            .sort_values(["name", "team_name", "player_id"], kind="stable")
            ["player_id"].drop_duplicates().tolist())


def player_option_label(player_id):
    row = analysis.loc[analysis["player_id"] == player_id].iloc[0]
    return f"{row['name']} · {row['team_name']}"


def safe_value(value):
    try:
        if value is None:
            return None

        if value != value:
            return None

    except (TypeError, ValueError):
        pass

    return value


def format_age(value, language):
    value = safe_value(value)

    if value is None:
        return "N/A"

    return f"{int(value)} {TEXT[language]['years']}"


def format_height(value):
    value = safe_value(value)

    if value is None:
        return "N/A"

    return f"{value / 100:.2f} m"


def format_market_value(value):
    value = safe_value(value)

    if value is None:
        return "N/A"

    if value >= 1_000_000:
        return f"€{value / 1_000_000:.1f}M"

    if value >= 1_000:
        return f"€{value / 1_000:.0f}K"

    return f"€{value:,.0f}"


def format_integer(value):
    value = safe_value(value)

    if value is None:
        return "N/A"

    return f"{int(value):,}"


POSITION_GROUP_LABELS = {
    "PT": {
        "Goalkeeper": "Goleiro",
        "Centre Back": "Zagueiro",
        "Full Back": "Lateral",
        "Midfielder": "Meio-Campo",
        "Winger": "Ponta",
        "Striker": "Atacante",
    },
    "EN": {},
}

FOOT_LABELS = {
    "PT": {
        "Left": "Esquerdo",
        "Right": "Direito",
        "Both": "Ambos",
    },
    "EN": {},
}


def translate_position_group(value, language):
    value = safe_value(value)
    if value is None:
        return "N/A"
    return POSITION_GROUP_LABELS.get(language, {}).get(value, value)


def translate_foot(value, language):
    value = safe_value(value)
    if value is None:
        return "N/A"
    return FOOT_LABELS.get(language, {}).get(value, value)


def get_percentile_class(percentile):
    percentile = safe_value(percentile)

    if percentile is None:
        return "percentile-low"

    if percentile >= 70:
        return "percentile-high"

    if percentile >= 40:
        return "percentile-medium"

    return "percentile-low"


def render_section_title(title, subtitle=None):
    html = (
        '<div class="section-title">'
        f'{title}'
        '</div>'
    )

    if subtitle:
        html += (
            '<div class="section-subtitle">'
            f'{subtitle}'
            '</div>'
        )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_page_header(title, subtitle):
    st.markdown(
        (
            '<div class="page-header-clean">'
            f'<div class="page-kicker">{html_lib.escape(str(title))}</div>'
            f'<div class="page-description">{html_lib.escape(str(subtitle))}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_profile_score(score, language):
    score = safe_value(score)
    if score is None:
        score_value = 0.0
        score_text = "N/A"
    else:
        score_value = max(0.0, min(100.0, float(score)))
        score_text = f"{score_value:.1f} / 100"

    note = (
        "Média ponderada dos percentis selecionados."
        if language == "PT"
        else "Weighted average of the selected percentiles."
    )
    st.markdown(
        (
            '<div class="score-shell">'
            '<div class="score-head">'
            '<div class="score-label">PROFILE SCORE</div>'
            f'<div class="score-number">{score_text}</div>'
            '</div>'
            '<div class="score-track">'
            f'<div class="score-fill" style="width:{score_value:.1f}%"></div>'
            '</div>'
            f'<div class="score-note">{note}</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_info_card(label, value):
    html = (
        '<div class="info-card">'
        f'<div class="info-label">{label}</div>'
        f'<div class="info-value">{value}</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_performance_card(
    label,
    value,
    percentile,
):
    value = safe_value(value)
    percentile = safe_value(percentile)

    if value is None:
        value_text = "N/A"
    else:
        value_text = f"{value:.2f}"

    if percentile is None:
        percentile_text = "N/A"
    else:
        percentile_text = f"P{percentile:.0f}"

    percentile_class = get_percentile_class(
        percentile
    )

    html = (
        '<div class="performance-card">'
        f'<div class="performance-label">{label}</div>'
        f'<div class="performance-value">{value_text}</div>'
        f'<div class="percentile {percentile_class}">'
        f'{percentile_text}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_player_panel(
    info,
    language,
    team_id=None,
):
    name = safe_value(info["name"]) or "N/A"
    team = safe_value(info["team"]) or "N/A"
    position = safe_value(info["position"]) or "N/A"
    position_group = translate_position_group(
        info["position_group"], language
    )
    foot = translate_foot(
        info["preferred_foot"], language
    )
    country = safe_value(info["country"]) or "N/A"
    player_id = safe_value(info.get("player_id"))

    age = format_age(info["age"], language)
    height = format_height(info["height_cm"])

    # Escape dataset text before inserting it into HTML.
    name_html = html_lib.escape(str(name))
    team_html = html_lib.escape(str(team))
    position_html = html_lib.escape(str(position))
    position_group_html = html_lib.escape(str(position_group))
    foot_html = html_lib.escape(str(foot))
    country_html = html_lib.escape(str(country))

    badge_html = ""
    if team_id is not None:
        badge_url = (
            f"https://img.sofascore.com/api/v1/team/{int(team_id)}/image"
        )
        badge_html = (
            f'<img class="club-badge" src="{badge_url}" '
            f'alt="{team_html}" loading="lazy">'
        )

    if player_id is not None:
        photo_url = (
            f"https://img.sofascore.com/api/v1/player/{int(player_id)}/image"
        )
        photo_html = (
            '<div class="player-photo-wrap">'
            f'<img class="player-photo" src="{photo_url}" '
            f'alt="{name_html}" loading="lazy" '
            "onerror=\"this.style.display='none';"
            "this.nextElementSibling.style.display='flex';\">"
            '<div class="player-photo-fallback">&#9823;</div>'
            '</div>'
        )
    else:
        photo_html = (
            '<div class="player-photo-wrap">'
            '<div class="player-photo-fallback" style="display:flex">&#9823;</div>'
            '</div>'
        )

    panel_html = (
        '<div class="player-panel">'
        '<div class="player-panel-content">'
        f'<div class="player-name">{name_html}</div>'
        '<div class="player-profile-body">'
        f'{photo_html}'
        '<div class="player-details-block">'
        '<div class="player-role-line">'
        f'{badge_html}'
        f'<div class="player-role" style="margin-top:0">{team_html}</div>'
        '</div>'
        '<div class="player-meta player-meta-compact">'
        f'<strong>{position_html}</strong>'
        f' &nbsp;•&nbsp; {position_group_html}'
        '<br>'
        f'{age} &nbsp;•&nbsp; {height}'
        '<br>'
        f'{foot_html} &nbsp;•&nbsp; {country_html}'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    return panel_html


def render_compare_player(
    info,
    language,
    side=None,
):
    name = safe_value(
        info["name"]
    ) or "N/A"

    team = safe_value(
        info["team"]
    ) or "N/A"

    position = safe_value(
        info["position"]
    ) or "N/A"

    position_group = translate_position_group(
        info["position_group"],
        language,
    )

    foot = translate_foot(
        info["preferred_foot"],
        language,
    )

    country = safe_value(
        info["country"]
    ) or "N/A"

    age = format_age(
        info["age"],
        language,
    )

    height = format_height(
        info["height_cm"]
    )

    market_value = format_market_value(
        info["market_value_eur"]
    )

    html = (
        f'<div class="compare-player {"player-a" if side == "a" else "player-b" if side == "b" else ""}">'
        f'<div class="compare-name">{name}</div>'
        '<div class="compare-info">'
        f'<span class="compare-team">{team}</span>'
        f' &nbsp;•&nbsp; {position_group}'
        '<br>'
        f'{position}'
        f' &nbsp;•&nbsp; {age}'
        f' &nbsp;•&nbsp; {height}'
        '<br>'
        f'{foot}'
        f' &nbsp;•&nbsp; {country}'
        f' &nbsp;•&nbsp; {market_value}'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# ============================================================
# RADAR STYLE
# ============================================================

def style_radar(fig):
    fig.update_layout(
        height=610,

        margin=dict(
            l=90,
            r=90,
            t=60,
            b=40,
        ),

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#9fb2c1",
            size=13,
        ),

        polar=dict(
            bgcolor="rgba(0,0,0,0)",

            radialaxis=dict(
                visible=True,
                range=[0, 100],

                tickmode="array",

                tickvals=[
                    20,
                    40,
                    60,
                    80,
                    100,
                ],

                ticktext=[
                    "20",
                    "40",
                    "60",
                    "80",
                    "100",
                ],

                tickfont=dict(
                    color="#58758a",
                    size=12,
                ),

                gridcolor=(
                    "rgba(104,140,162,0.20)"
                ),

                linecolor=(
                    "rgba(104,140,162,0.15)"
                ),
            ),

            angularaxis=dict(
                gridcolor=(
                    "rgba(104,140,162,0.20)"
                ),

                linecolor=(
                    "rgba(104,140,162,0.15)"
                ),

                tickfont=dict(
                    color="#b8c8d4",
                    size=11,
                ),
            ),
        ),
    )


# ============================================================
# SINGLE PLAYER RADAR
# ============================================================

def build_radar_chart(
    player_name,
    player_kpis,
    language,
):
    categories = []
    percentiles = []

    for metric, data in player_kpis.items():

        percentile = safe_value(
            data["percentile"]
        )

        if percentile is None:
            continue

        label = (
            METRIC_LABELS[language]
            .get(metric, metric)
        )

        categories.append(label)
        percentiles.append(
            float(percentile)
        )

    if not categories:
        return None

    radar_categories = (
        categories
        + [categories[0]]
    )

    radar_percentiles = (
        percentiles
        + [percentiles[0]]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_percentiles,
            theta=radar_categories,
            fill="toself",
            name=player_name,

            line=dict(
                color="#29a9e0",
                width=3,
            ),

            fillcolor=(
                "rgba(41,169,224,0.20)"
            ),

            marker=dict(
                size=7,
                color="#65c8f1",
            ),

            hovertemplate=(
                "<b>%{theta}</b><br>"
                "Percentile: %{r:.0f}"
                "<extra></extra>"
            ),
        )
    )

    style_radar(fig)

    fig.update_layout(
        showlegend=False
    )

    return fig


# ============================================================
# COMPARISON RADAR
# ============================================================

def build_comparison_radar(
    name_a,
    kpis_a,
    name_b,
    kpis_b,
    language,
):
    common_metrics = [
        metric
        for metric in kpis_a.keys()
        if metric in kpis_b
    ]

    categories = []
    values_a = []
    values_b = []

    for metric in common_metrics:

        percentile_a = safe_value(
            kpis_a[metric]["percentile"]
        )

        percentile_b = safe_value(
            kpis_b[metric]["percentile"]
        )

        if (
            percentile_a is None
            or percentile_b is None
        ):
            continue

        label = (
            METRIC_LABELS[language]
            .get(metric, metric)
        )

        categories.append(label)

        values_a.append(
            float(percentile_a)
        )

        values_b.append(
            float(percentile_b)
        )

    if not categories:
        return None

    radar_categories = (
        categories
        + [categories[0]]
    )

    radar_a = (
        values_a
        + [values_a[0]]
    )

    radar_b = (
        values_b
        + [values_b[0]]
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=radar_a,
            theta=radar_categories,
            fill="toself",
            name=name_a,

            line=dict(
                color="#29a9e0",
                width=3,
            ),

            fillcolor=(
                "rgba(41,169,224,0.15)"
            ),

            marker=dict(
                size=6,
                color="#65c8f1",
            ),

            hovertemplate=(
                f"<b>{name_a}</b><br>"
                "%{theta}<br>"
                "P%{r:.0f}"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=radar_b,
            theta=radar_categories,
            fill="toself",
            name=name_b,

            line=dict(
                color="#f0a04b",
                width=3,
            ),

            fillcolor=(
                "rgba(240,160,75,0.10)"
            ),

            marker=dict(
                size=6,
                color="#f0a04b",
            ),

            hovertemplate=(
                f"<b>{name_b}</b><br>"
                "%{theta}<br>"
                "P%{r:.0f}"
                "<extra></extra>"
            ),
        )
    )

    style_radar(fig)

    fig.update_layout(
        showlegend=True,

        legend=dict(
            orientation="h",

            yanchor="bottom",
            y=1.05,

            xanchor="center",
            x=0.5,

            font=dict(
                color="#b8c8d4"
            ),
        ),
    )

    return fig



# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_app_data():

    df = load_data()

    analysis = prepare_analysis(
        df
    )

    benchmark_pool, scouting_pool = (
        create_pools(
            analysis
        )
    )

    return (
        analysis,
        benchmark_pool,
        scouting_pool,
    )


analysis, benchmark_pool, scouting_pool = (
    load_app_data()
)



# ============================================================
# TRANSPARENCY / DATA COVERAGE
# ============================================================

def render_data_notice(player_id, language, *, prefix=None):
    """Contextual warnings only; do not change rankings or impute missing data."""
    rows = analysis.loc[analysis["player_id"] == player_id]
    if rows.empty:
        return
    player = rows.iloc[0]
    minutes = pd.to_numeric(pd.Series([player.get("minutesPlayed")]), errors="coerce").iloc[0]
    label = f"{prefix}: " if prefix else ""
    if pd.isna(minutes) or minutes < MIN_MINUTES:
        st.caption(
            label + (
                f"⚠ Amostra reduzida: {format_integer(minutes)} minutos. "
                f"O benchmark usa jogadores com pelo menos {MIN_MINUTES} minutos; "
                "percentis deste jogador devem ser interpretados com cautela."
                if language == "PT" else
                f"⚠ Small sample: {format_integer(minutes)} minutes. "
                f"The benchmark includes players with at least {MIN_MINUTES} minutes; "
                "interpret this player's percentiles with caution."
            )
        )
    position = player.get("position_group")
    if pd.isna(position):
        return
    metrics = get_talent_metrics(position)
    missing = [metric for metric in metrics if metric not in analysis.columns or pd.isna(player.get(metric))]
    if missing:
        labels = ", ".join(METRIC_LABELS[language].get(m, m) for m in missing)
        st.caption(label + (
            f"⚠ Métricas indisponíveis: {labels}. Valores ausentes não são tratados como zero."
            if language == "PT" else
            f"⚠ Missing metrics: {labels}. Missing values are not treated as zero."
        ))


def render_methodology(language):
    """Compact, bilingual explanation of the actual scouting-engine rules."""
    with st.expander("ⓘ Metodologia e dados" if language == "PT" else "ⓘ Methodology & data", expanded=False):
        if language == "PT":
            st.markdown(
                "**Fonte:** estatísticas de jogadores coletadas do SofaScore, "
                "organizadas no dataset processado da Liga Portugal 2025/26. "
                "Os dados refletem o momento da coleta e não são atualizados em tempo real.\n\n"
                f"**Benchmark:** jogadores do mesmo grupo posicional com pelo menos **{MIN_MINUTES} minutos**. "
                "O Talent Finder considera jogadores SUB-23 com posição identificada, "
                "sem impor automaticamente esse limite de minutos.\n\n"
                "**Métricas:** contagens são convertidas para valores por 90 minutos; "
                "percentuais originais permanecem percentuais. "
                "Os percentis (0–100) comparam o jogador aos valores disponíveis do benchmark "
                "da mesma posição, inclusive quando o próprio jogador tem menos de 450 minutos.\n\n"
                "**Profile Score:** média ponderada dos percentis das métricas ativas "
                "do perfil escolhido. Métricas sem dados ou com peso zero não entram no cálculo; "
                "os pesos restantes são renormalizados. O score não é uma avaliação objetiva "
                "de qualidade nem uma previsão de desempenho futuro.\n\n"
                "**Limitações:** amostras pequenas, métricas ausentes e diferenças de contexto "
                "entre clubes podem influenciar os resultados."
            )
            st.caption("Métricas em que menor é melhor: " + ", ".join(
                METRIC_LABELS[language].get(m, m) for m in sorted(LOWER_IS_BETTER)
            ) + ".")
        else:
            st.markdown(
                "**Source:** player statistics collected from SofaScore and organized "
                "in the processed Liga Portugal 2025/26 dataset. Data are a snapshot, not a live feed.\n\n"
                f"**Benchmark:** same-position players with at least **{MIN_MINUTES} minutes**. "
                "Talent Finder includes U23 players with a known position, "
                "without automatically enforcing this minutes threshold.\n\n"
                "**Metrics:** counts are converted to per-90 values; existing percentages "
                "remain percentages. Percentiles (0–100) compare each available value with "
                "the same-position benchmark, even for players below 450 minutes.\n\n"
                "**Profile Score:** weighted average of percentiles for active profile metrics. "
                "Missing or zero-weight metrics are excluded and remaining weights are "
                "renormalized. This is neither an objective player grade nor a prediction.\n\n"
                "**Limitations:** small samples, missing statistics and club context "
                "may affect comparisons."
            )
            st.caption("Lower is better for: " + ", ".join(
                METRIC_LABELS[language].get(m, m) for m in sorted(LOWER_IS_BETTER)
            ) + ".")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    sidebar_brand = (
        '<div class="sidebar-brand-wrap">'
        '<div class="sidebar-brand-top">'
        '⚽ PORTUGAL'
        '</div>'
        '<div class="sidebar-brand-main">'
        'SCOUTING HUB'
        '</div>'
        '</div>'
    )

    st.markdown(
        sidebar_brand,
        unsafe_allow_html=True,
    )

    # Compact PT | EN language switcher.
    # The active language is highlighted using the primary button style.
    lang_pt, lang_sep, lang_en = st.columns([1, 0.22, 1])

    with lang_pt:
        if st.button(
            "PT",
            key="language_pt",
            width="stretch",
            type=(
                "primary"
                if st.session_state.language == "PT"
                else "secondary"
            ),
        ):
            st.session_state.language = "PT"
            st.rerun()

    with lang_sep:
        st.markdown(
            '<div class="sidebar-language-separator">|</div>',
            unsafe_allow_html=True,
        )

    with lang_en:
        if st.button(
            "EN",
            key="language_en",
            width="stretch",
            type=(
                "primary"
                if st.session_state.language == "EN"
                else "secondary"
            ),
        ):
            st.session_state.language = "EN"
            st.rerun()

    lang = st.session_state.language

    sidebar_section = (
        '<div class="sidebar-section">'
        'SCOUTING'
        '</div>'
    )

    st.markdown(
        sidebar_section,
        unsafe_allow_html=True,
    )

    page_options = [
        (
            "🏃︎",
            TEXT[lang]["player_profile"],
            "PLAYER PROFILE",
        ),
        (
            "⇄",
            TEXT[lang]["compare"],
            "COMPARE",
        ),
        (
            "⌕",
            TEXT[lang]["talent_finder"],
            "TALENT FINDER",
        ),
    ]

    # Navigation uses full-width buttons instead of radio controls.
    # The current page is rendered as the primary/active item.
    for icon, label, page_value in page_options:

        is_active = (
            st.session_state.page == page_value
        )

        if st.button(
            f"{icon}   {label}",
            key=f"nav_{page_value}",
            width="stretch",
            type=(
                "primary"
                if is_active
                else "secondary"
            ),
        ):
            st.session_state.page = page_value
            st.rerun()


    st.markdown("---")
    render_methodology(lang)

# ============================================================
# CURRENT SETTINGS
# ============================================================

lang = st.session_state.language
t = TEXT[lang]

page = st.session_state.page


# ============================================================
# PAGE CONTENT
# ============================================================


# ============================================================
# PLAYER PROFILE PAGE
# ============================================================

if page == "PLAYER PROFILE":

    render_page_header(
        t["player_profile"],
        (
            "Análise individual de desempenho e contexto do jogador."
            if lang == "PT"
            else "Individual player performance and context analysis."
        ),
    )

    player_ids = player_options(scouting_pool)
    restore_widget_value("profile_player", player_ids[0], valid_values=player_ids)
    player_selector_col, _player_selector_spacer = st.columns([1, 3])
    with player_selector_col:
        selected_player_id = st.selectbox(
            t["player"], player_ids, format_func=player_option_label,
            key="profile_player", on_change=persist_widget_value,
            args=("profile_player",),
        )
    player_info = get_player_info(None, analysis, player_id=selected_player_id)
    player_name = player_info["name"]
    render_data_notice(selected_player_id, lang)

    player_id = safe_value(player_info.get("player_id"))
    team_id = None

    if player_id is not None:
        player_row = analysis.loc[
            analysis["player_id"] == player_id,
            ["team_id"],
        ]
        if not player_row.empty:
            team_id = safe_value(player_row.iloc[0]["team_id"])

    # Render the entire profile overview as ONE HTML grid.
    # This removes Streamlit column wrappers from this section, so the
    # player card and the 2x2 summary grid share the exact same 220px box.
    render_section_title("PERFIL" if lang == "PT" else "PROFILE")

    player_panel_html = render_player_panel(
        player_info,
        lang,
        team_id=team_id,
    )

    summary_items = [
        (t["market_value"], format_market_value(player_info["market_value_eur"])),
        (t["minutes"], format_integer(player_info["minutes"])),
        (t["matches"], format_integer(player_info["appearances"])),
        (t["starts"], format_integer(player_info["starts"])),
    ]

    summary_html = '<div class="profile-summary-grid">'
    for label, value in summary_items:
        summary_html += (
            '<div class="profile-summary-card">'
            f'<div class="info-label">{html_lib.escape(str(label))}</div>'
            f'<div class="info-value">{html_lib.escape(str(value))}</div>'
            '</div>'
        )
    summary_html += '</div>'

    overview_html = (
        '<div class="profile-overview-grid">'
        f'{player_panel_html}'
        f'{summary_html}'
        '</div>'
    )

    st.markdown(overview_html, unsafe_allow_html=True)


    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    render_section_title(
        t["performance"],
        t["performance_percentile_explanation"],
    )

    position_group = safe_value(
        player_info[
            "position_group"
        ]
    )

    try:

        player_kpis = get_player_kpis(
            player_name,
            scouting_pool,
            benchmark_pool,
            player_id=selected_player_id,
        )

        metric_items = list(
            player_kpis.items()
        )

        for row_start in range(
            0,
            len(metric_items),
            3,
        ):

            row_metrics = (
                metric_items[
                    row_start:
                    row_start + 3
                ]
            )

            columns = st.columns(3)

            for (
                column,
                metric_item
            ) in zip(
                columns,
                row_metrics,
            ):

                metric, data = (
                    metric_item
                )

                label = (
                    METRIC_LABELS[
                        lang
                    ].get(
                        metric,
                        metric,
                    )
                )

                with column:

                    render_performance_card(
                        label=label,
                        value=data["value"],
                        percentile=data[
                            "percentile"
                        ],
                    )


        # ------------------------------------------------
        # RADAR
        # ------------------------------------------------

        render_section_title(
            t["performance_profile"],
            t[
                "performance_profile_subtitle"
            ],
        )

        radar = build_radar_chart(
            player_name,
            player_kpis,
            lang,
        )

        if radar is not None:

            st.plotly_chart(
                radar,
                width="stretch",
                config={
                    "displayModeBar":
                        False,
                    "responsive":
                        True,
                },
            )

    except ValueError as error:

        st.warning(
            str(error)
        )

# ============================================================
# COMPARE PAGE
# ============================================================

elif page == "COMPARE":

    render_page_header(
        t["comparison"],
        t["comparison_subtitle"],
    )


    # --------------------------------------------------------
    # PLAYER A
    # --------------------------------------------------------

    selectable_players = player_options(scouting_pool)
    selector_a, selector_b = st.columns(2)
    restore_widget_value("compare_player_a", selectable_players[0], valid_values=selectable_players)
    with selector_a:
        player_a_id = st.selectbox(
            t["player_a"], selectable_players, format_func=player_option_label,
            key="compare_player_a", on_change=persist_widget_value,
            args=("compare_player_a",),
        )
    info_a = get_player_info(None, analysis, player_id=player_a_id)
    player_a = info_a["name"]

    position_group_a = safe_value(
        info_a[
            "position_group"
        ]
    )


    # --------------------------------------------------------
    # PLAYER B — SAME POSITION GROUP
    # --------------------------------------------------------

    players_b = player_options(scouting_pool.loc[
        (scouting_pool["position_group"] == position_group_a)
        & (scouting_pool["player_id"] != player_a_id)
    ])
    with selector_b:
        if players_b:
            restore_widget_value("compare_player_b", players_b[0], valid_values=players_b)
            player_b_id = st.selectbox(
                t["player_b"], players_b, format_func=player_option_label,
                key="compare_player_b", on_change=persist_widget_value,
                args=("compare_player_b",),
            )
        else:
            player_b_id = None
            st.warning(t["no_comparable"])

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    if player_b_id is not None:

        info_b = get_player_info(None, analysis, player_id=player_b_id)
        player_b = info_b["name"]
        render_data_notice(player_a_id, lang, prefix=t["player_a"])
        render_data_notice(player_b_id, lang, prefix=t["player_b"])


        # ----------------------------------------------------
        # PLAYER SUMMARIES
        # ----------------------------------------------------

        profile_a, profile_b = (
            st.columns(2)
        )

        with profile_a:

            render_compare_player(
                info_a,
                lang,
                side="a",
            )

        with profile_b:

            render_compare_player(
                info_b,
                lang,
                side="b",
            )


        # ----------------------------------------------------
        # BASIC INFORMATION
        # ----------------------------------------------------

        basic_a, basic_b = (
            st.columns(2)
        )

        with basic_a:

            card_a1, card_a2 = (
                st.columns(2)
            )

            with card_a1:

                render_info_card(
                    t["minutes"],
                    str(int(info_a["minutes"]))
                    if safe_value(info_a["minutes"]) is not None
                    else "N/A",
                )

            with card_a2:

                render_info_card(
                    t["matches"],
                    format_integer(
                        info_a[
                            "appearances"
                        ]
                    ),
                )

        with basic_b:

            card_b1, card_b2 = (
                st.columns(2)
            )

            with card_b1:

                render_info_card(
                    t["minutes"],
                    str(int(info_b["minutes"]))
                    if safe_value(info_b["minutes"]) is not None
                    else "N/A",
                )

            with card_b2:

                render_info_card(
                    t["matches"],
                    format_integer(
                        info_b[
                            "appearances"
                        ]
                    ),
                )


        # ----------------------------------------------------
        # KPI COMPARISON
        # ----------------------------------------------------

        try:

            kpis_a = get_player_kpis(
                player_a,
                scouting_pool,
                benchmark_pool,
                player_id=player_a_id,
            )

            kpis_b = get_player_kpis(
                player_b,
                scouting_pool,
                benchmark_pool,
                player_id=player_b_id,
            )


            # ------------------------------------------------
            # RADAR
            # ------------------------------------------------

            render_section_title(
                t[
                    "performance_profile"
                ],
                t[
                    "performance_profile_subtitle"
                ],
            )

            comparison_radar = (
                build_comparison_radar(
                    player_option_label(player_a_id),
                    kpis_a,
                    player_option_label(player_b_id),
                    kpis_b,
                    lang,
                )
            )

            if comparison_radar is not None:

                st.plotly_chart(
                    comparison_radar,
                    width="stretch",
                    config={
                        "displayModeBar":
                            False,
                        "responsive":
                            True,
                    },
                )


            # ------------------------------------------------
            # TABLE
            # ------------------------------------------------

            render_section_title(
                t["comparison_table"]
            )

            table_rows = []

            for metric in kpis_a.keys():
                if metric not in kpis_b:
                    continue

                value_a = safe_value(kpis_a[metric]["value"])
                percentile_a = safe_value(kpis_a[metric]["percentile"])
                value_b = safe_value(kpis_b[metric]["value"])
                percentile_b = safe_value(kpis_b[metric]["percentile"])
                metric_label = METRIC_LABELS[lang].get(metric, metric)

                display_a = "N/A"
                if value_a is not None:
                    display_a = f"{value_a:.2f}"
                    if percentile_a is not None:
                        display_a += f" · P{percentile_a:.0f}"

                display_b = "N/A"
                if value_b is not None:
                    display_b = f"{value_b:.2f}"
                    if percentile_b is not None:
                        display_b += f" · P{percentile_b:.0f}"

                table_rows.append({
                    ("Métrica" if lang == "PT" else "Metric"): metric_label,
                    player_option_label(player_a_id): display_a,
                    player_option_label(player_b_id): display_b,
                })

            comparison_df = pd.DataFrame(table_rows)

            st.dataframe(
                comparison_df,
                width="stretch",
                hide_index=True,
            )

        except ValueError as error:

            st.warning(
                str(error)
            )


# ============================================================
# TALENT FINDER PAGE
# ============================================================

elif page == "TALENT FINDER":

    # ========================================================
    # TITLE
    # ========================================================

    render_page_header(
        "BUSCAR TALENTOS" if lang == "PT" else "TALENT FINDER",
        (
            "Identificação de jogadores SUB-23 de acordo com filtros de recrutamento e o perfil definido."
            if lang == "PT"
            else "Identify U23 players using recruitment filters and a defined performance profile."
        ),
    )

    # ========================================================
    # BASIC FILTERS
    # ========================================================

    st.markdown(
        '<div class="talent-group-label">' +
        ("FILTROS DE RECRUTAMENTO" if lang == "PT" else "RECRUITMENT FILTERS") +
        '</div>',
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2 = st.columns(2)

    position_labels_pt = {
        "Todos": "Todos",
        "Goalkeeper": "Goleiro",
        "Centre Back": "Zagueiro",
        "Full Back": "Lateral",
        "Midfielder": "Meio-Campo",
        "Winger": "Ponta",
        "Striker": "Atacante",
    }

    position_options = [
        "Todos",
        "Goalkeeper",
        "Centre Back",
        "Full Back",
        "Midfielder",
        "Winger",
        "Striker",
    ]

    restore_widget_value(
        "talent_position",
        "Todos",
        valid_values=position_options,
    )

    with filter_col1:

        # Dropdown de posição sem campo pesquisável.
        # st.selectbox permite digitação para busca; o popover abaixo mantém
        # o comportamento de dropdown, mas aceita apenas clique nas opções.
        st.markdown(
            '<div class="filter-field-label">'
            + ("Posição" if lang == "PT" else "Position")
            + '</div>',
            unsafe_allow_html=True,
        )

        current_position = st.session_state.get(
            "talent_position",
            "Todos",
        )

        current_position_label = (
            position_labels_pt.get(
                current_position,
                current_position,
            )
            if lang == "PT"
            else (
                "All"
                if current_position == "Todos"
                else current_position
            )
        )

        # Dropdown customizado: não permite digitação e fecha imediatamente
        # após a escolha. O menu é posicionado via CSS como overlay, portanto
        # não empurra os filtros abaixo.
        def toggle_position_menu():
            st.session_state.talent_position_menu_open = (
                not st.session_state.talent_position_menu_open
            )

        def choose_position(position):
            st.session_state["talent_position"] = position
            st.session_state["persist_talent_position"] = position
            st.session_state.talent_position_menu_open = False

        with st.container(key="talent_position_dropdown"):
            arrow = "▴" if st.session_state.talent_position_menu_open else "▾"

            st.button(
                f"{current_position_label} {arrow}",
                key="talent_position_trigger",
                on_click=toggle_position_menu,
            )

            if st.session_state.talent_position_menu_open:
                with st.container(key="talent_position_menu"):
                    for position in position_options:
                        option_label = (
                            position_labels_pt.get(position, position)
                            if lang == "PT"
                            else (
                                "All"
                                if position == "Todos"
                                else position
                            )
                        )

                        st.button(
                            option_label,
                            key=f"talent_position_option_{position}",
                            width="stretch",
                            type=(
                                "primary"
                                if position == current_position
                                else "secondary"
                            ),
                            on_click=choose_position,
                            args=(position,),
                        )

        selected_position = st.session_state.get(
            "talent_position",
            "Todos",
        )

    max_age_available = int(
        scouting_pool["age_2025_26"]
        .dropna()
        .max()
    )

    restore_widget_value(
        "talent_age",
        23,
        min_value=16,
        max_value=max_age_available,
    )

    with filter_col2:

        max_age = st.slider(
            "Idade máxima"
            if lang == "PT"
            else "Maximum age",
            min_value=16,
            max_value=max_age_available,
            value=23,
            step=1,
            key="talent_age",
            on_change=persist_widget_value,
            args=("talent_age",),
        )

    filter_col3, filter_col4 = st.columns(2)

    max_minutes_available = int(
        scouting_pool["minutesPlayed"].max()
    )

    restore_widget_value(
        "talent_minutes",
        450,
        min_value=0,
        max_value=max_minutes_available,
    )

    with filter_col3:

        min_minutes = st.slider(
            "Minutos mínimos"
            if lang == "PT"
            else "Minimum minutes",
            min_value=0,
            max_value=max_minutes_available,
            value=450,
            step=90,
            key="talent_minutes",
            on_change=persist_widget_value,
            args=("talent_minutes",),
        )

    market_values = (
        scouting_pool["market_value_eur"]
        .dropna()
    )

    max_market_available = int(
        market_values.max()
    )

    restore_widget_value(
        "talent_market_value",
        max_market_available,
        min_value=0,
        max_value=max_market_available,
    )

    with filter_col4:

        max_market_value = st.slider(
            "Valor de mercado máximo (€)"
            if lang == "PT"
            else "Maximum market value (€)",
            min_value=0,
            max_value=max_market_available,
            value=max_market_available,
            step=500_000,
            format="€%d",
            key="talent_market_value",
            on_change=persist_widget_value,
            args=("talent_market_value",),
        )

    # ========================================================
    # APPLY BASIC FILTERS
    # ========================================================

    talent_results = scouting_pool.copy()

    if selected_position != "Todos":

        talent_results = talent_results[
            talent_results["position_group"]
            == selected_position
        ]

    talent_results = talent_results[
        (
            talent_results["age_2025_26"]
            <= max_age
        )
        &
        (
            talent_results["minutesPlayed"]
            >= min_minutes
        )
        &
        (
            talent_results["market_value_eur"]
            .fillna(float("inf"))
            <= max_market_value
        )
    ].copy()

    # ========================================================
    # PROFILE RANKING
    # ========================================================

    #
    # O Profile Score só pode ser calculado quando uma posição
    # específica é selecionada.
    #
    # Isso ocorre porque cada posição possui métricas próprias
    # e o benchmark é feito contra jogadores da mesma posição.
    #

    ranking_available = (
        selected_position != "Todos"
    )

    if ranking_available:

        st.markdown("")

        st.markdown(
            '<div class="talent-group-label">' +
            ("PERFIL DESEJADO" if lang == "PT" else "TARGET PROFILE") +
            '</div>',
            unsafe_allow_html=True,
        )

        render_section_title(
            "PERFIL DESEJADO"
            if lang == "PT"
            else "TARGET PROFILE",
            (
                "Defina o peso de cada métrica "
                "para o perfil procurado."
                if lang == "PT"
                else
                "Define the weight of each metric "
                "for the desired player profile."
            ),
        )

        # ----------------------------------------------------
        # METRICS
        # ----------------------------------------------------

        talent_metrics = get_talent_metrics(
            selected_position
        )

        metric_labels_pt = {
            "goals_per90": "Gols / 90",
            "expectedGoals_per90": "xG / 90",
            "totalShots_per90": "Finalizações / 90",
            "shotsOnTarget_per90": "Finalizações no alvo / 90",
            "assists_per90": "Assistências / 90",
            "expectedAssists_per90": "xA / 90",
            "keyPasses_per90": "Passes-chave / 90",
            "successfulDribbles_per90": "Dribles certos / 90",
            "accurateFinalThirdPasses_per90": "Passes no terço final / 90",
            "ballRecovery_per90": "Recuperações / 90",
            "interceptions_per90": "Interceptações / 90",
            "tackles_per90": "Desarmes / 90",
            "clearances_per90": "Cortes / 90",
            "aerialDuelsWonPercentage": "Duelos aéreos ganhos (%)",
            "accuratePassesPercentage": "Passes certos (%)",
            "saves_per90": "Defesas / 90",
            "goalsPrevented_per90": "Gols evitados / 90",
            "goalsConceded_per90": "Gols sofridos / 90",
            "highClaims_per90": "Bolas aéreas dominadas / 90",
            "successfulRunsOut_per90": "Saídas bem-sucedidas / 90",
        }

        metric_labels_en = {
            "goals_per90": "Goals / 90",
            "expectedGoals_per90": "xG / 90",
            "totalShots_per90": "Shots / 90",
            "shotsOnTarget_per90": "Shots on Target / 90",
            "assists_per90": "Assists / 90",
            "expectedAssists_per90": "xA / 90",
            "keyPasses_per90": "Key Passes / 90",
            "successfulDribbles_per90": "Successful Dribbles / 90",
            "accurateFinalThirdPasses_per90": "Final Third Passes / 90",
            "ballRecovery_per90": "Ball Recoveries / 90",
            "interceptions_per90": "Interceptions / 90",
            "tackles_per90": "Tackles / 90",
            "clearances_per90": "Clearances / 90",
            "aerialDuelsWonPercentage": "Aerial Duels Won (%)",
            "accuratePassesPercentage": "Pass Accuracy (%)",
            "saves_per90": "Saves / 90",
            "goalsPrevented_per90": "Goals Prevented / 90",
            "goalsConceded_per90": "Goals Conceded / 90",
            "highClaims_per90": "High Claims / 90",
            "successfulRunsOut_per90": "Successful Runs Out / 90",
        }

        metric_labels = (
            metric_labels_pt
            if lang == "PT"
            else metric_labels_en
        )

        # ----------------------------------------------------
        # WEIGHT SLIDERS
        # ----------------------------------------------------

        weights = {}

        weight_columns = st.columns(3)

        for index, metric in enumerate(
            talent_metrics
        ):

            column = weight_columns[
                index % 3
            ]

            with column:

                weight_key = f"weight_{selected_position}_{metric}"

                restore_widget_value(
                    weight_key,
                    50,
                    min_value=0,
                    max_value=100,
                )

                weights[metric] = st.slider(
                    metric_labels.get(
                        metric,
                        metric,
                    ),
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=5,
                    key=weight_key,
                    on_change=persist_widget_value,
                    args=(weight_key,),
                )

        # ----------------------------------------------------
        # WEIGHT INFORMATION
        # ----------------------------------------------------

        total_weight = sum(
            weights.values()
        )

        if total_weight == 0:

            st.warning(
                (
                    "Defina pelo menos um peso maior que zero."
                    if lang == "PT"
                    else
                    "Set at least one weight above zero."
                )
            )

            ranked_results = None

        else:

            st.caption(
                (
                    "Os pesos são normalizados automaticamente. "
                    "Eles representam importância relativa e "
                    "não precisam somar 100."
                    if lang == "PT"
                    else
                    "Weights are automatically normalized. "
                    "They represent relative importance and "
                    "do not need to add up to 100."
                )
            )

            # ------------------------------------------------
            # CALCULATE RANKING
            # ------------------------------------------------

            ranked_results = (
                calculate_talent_ranking(
                    candidates=talent_results,
                    benchmark_pool=benchmark_pool,
                    position_group=selected_position,
                    weights=weights,
                )
            )

    else:

        ranked_results = None

    # ========================================================
    # RESULTS
    # ========================================================

    st.markdown("")

    result_title = (
        f"{len(talent_results)} jogadores encontrados"
        if lang == "PT"
        else
        f"{len(talent_results)} players found"
    )

    render_section_title(
        result_title
    )

    # ========================================================
    # NO RESULTS
    # ========================================================

    if talent_results.empty:

        st.markdown(
            (
                '<div class="empty-state">'
                '<div class="empty-state-title">Nenhum jogador encontrado</div>'
                '<div class="empty-state-copy">Tente reduzir o mínimo de minutos, aumentar a idade máxima ou ampliar o valor máximo de mercado.</div>'
                '</div>'
                if lang == "PT"
                else
                '<div class="empty-state">'
                '<div class="empty-state-title">No players found</div>'
                '<div class="empty-state-copy">Try lowering the minimum minutes, increasing maximum age, or expanding the market-value limit.</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    # ========================================================
    # RANKED RESULTS
    # ========================================================

    elif (
        ranking_available
        and ranked_results is not None
    ):

        talent_table = ranked_results[
            [
                "talent_rank",
                "name",
                "team_name",
                "age_2025_26",
                "minutesPlayed",
                "market_value_eur",
                "talent_score",
                "metrics_used",
                "metrics_total",
            ]
        ].copy()

        talent_table["age_2025_26"] = (
            talent_table["age_2025_26"]
            .astype("Int64")
        )

        talent_table["talent_score"] = (
            talent_table["talent_score"]
            .round(1)
        )

        talent_table["coverage"] = (
            talent_table["metrics_used"]
            .astype(str)
            + "/"
            + talent_table["metrics_total"]
            .astype(str)
        )

        talent_table = talent_table.drop(
            columns=[
                "metrics_used",
                "metrics_total",
            ]
        )

        if lang == "PT":

            talent_table = talent_table.rename(
                columns={
                    "talent_rank": "Ranking",
                    "name": "Jogador",
                    "team_name": "Clube",
                    "age_2025_26": "Idade",
                    "minutesPlayed": "Minutos",
                    "market_value_eur":
                        "Valor de Mercado (€)",
                    "talent_score":
                        "Profile Score",
                    "coverage":
                        "Coverage",
                }
            )

        else:

            talent_table = talent_table.rename(
                columns={
                    "talent_rank": "Ranking",
                    "name": "Player",
                    "team_name": "Club",
                    "age_2025_26": "Age",
                    "minutesPlayed": "Minutes",
                    "market_value_eur":
                        "Market Value (€)",
                    "talent_score":
                        "Profile Score",
                    "coverage":
                        "Coverage",
                }
            )

        # Convert numeric values to display strings so Streamlit renders
        # every column left-aligned, matching the basic results table.
        ranking_col = "Ranking"
        age_col = "Idade" if lang == "PT" else "Age"
        minutes_col = "Minutos" if lang == "PT" else "Minutes"
        market_col = (
            "Valor de Mercado (€)"
            if lang == "PT"
            else "Market Value (€)"
        )

        talent_table[ranking_col] = talent_table[ranking_col].apply(
            lambda value: str(int(value)) if pd.notna(value) else "N/A"
        )

        talent_table[age_col] = talent_table[age_col].apply(
            lambda value: str(int(value)) if pd.notna(value) else "N/A"
        )

        talent_table[minutes_col] = talent_table[minutes_col].apply(
            lambda value: str(int(value)) if pd.notna(value) else "N/A"
        )

        talent_table[market_col] = talent_table[market_col].apply(
            lambda value: f"€ {int(value)}" if pd.notna(value) else "N/A"
        )

        talent_table["Profile Score"] = talent_table["Profile Score"].apply(
            lambda value: (
                f"{'━' * max(1, int(float(value) // 10))}  {float(value):.1f}"
                if pd.notna(value) else "N/A"
            )
        )

        st.dataframe(
            talent_table,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            (
                "Profile Score = média ponderada dos percentis "
                "das métricas selecionadas, comparadas com "
                "jogadores da mesma posição no benchmark."
                if lang == "PT"
                else
                "Profile Score = weighted average of the "
                "selected metric percentiles, compared with "
                "same-position players in the benchmark."
            )
        )

        # ====================================================
        # RESULT ANALYSIS
        # ====================================================

        st.markdown("")

        render_section_title(
            "ANÁLISE DO RESULTADO"
            if lang == "PT"
            else "RESULT ANALYSIS",
            (
                "Entenda quais métricas sustentam o Profile Score "
                "do jogador selecionado."
                if lang == "PT"
                else
                "See which metrics support the selected player's "
                "Profile Score."
            ),
        )

        analysis_player_options = player_options(ranked_results)
        if analysis_player_options:
            if (
                "talent_analysis_player" in st.session_state
                and st.session_state.talent_analysis_player not in analysis_player_options
            ):
                st.session_state.talent_analysis_player = analysis_player_options[0]
            selected_analysis_player_id = st.selectbox(
                "Jogador" if lang == "PT" else "Player",
                options=analysis_player_options,
                format_func=player_option_label,
                key="talent_analysis_player",
                width=230,
            )
            selected_rank_row = ranked_results.loc[
                ranked_results["player_id"] == selected_analysis_player_id
            ].iloc[0]
            selected_analysis_player = selected_rank_row["name"]
            render_data_notice(selected_analysis_player_id, lang)
            selected_kpis = get_player_kpis(
                selected_analysis_player, scouting_pool, benchmark_pool,
                player_id=selected_analysis_player_id,
            )

            score_value = safe_value(
                selected_rank_row["talent_score"]
            )
            metrics_used = int(
                selected_rank_row["metrics_used"]
            )
            metrics_total = int(
                selected_rank_row["metrics_total"]
            )

            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:
                render_profile_score(score_value, lang)

            with summary_col2:
                render_info_card(
                    "MÉTRICAS ANALISADAS"
                    if lang == "PT"
                    else "METRICS ANALYZED",
                    f"{metrics_used}/{metrics_total}",
                )

            metric_analysis = []

            for metric in talent_metrics:

                if metric not in selected_kpis:
                    continue

                percentile = safe_value(
                    selected_kpis[metric]["percentile"]
                )

                if percentile is None:
                    continue

                metric_analysis.append(
                    {
                        "metric": metric,
                        "label": metric_labels.get(
                            metric,
                            metric,
                        ),
                        "percentile": float(percentile),
                        "weight": int(weights.get(metric, 0)),
                    }
                )

            if metric_analysis:

                highest_metrics = sorted(
                    metric_analysis,
                    key=lambda item: item["percentile"],
                    reverse=True,
                )[:3]

                lowest_metrics = sorted(
                    metric_analysis,
                    key=lambda item: item["percentile"],
                )[:3]

                high_col, low_col = st.columns(2)

                with high_col:
                    st.markdown(
                        "**Características de Maior Destaque**"
                        if lang == "PT"
                        else "**Key Strengths**"
                    )

                    for item in highest_metrics:
                        bar_class = (
                            "high" if item["percentile"] >= 70
                            else "medium" if item["percentile"] >= 40
                            else "low"
                        )
                        weight_text = (f"Peso {item['weight']}" if lang == "PT" else f"Weight {item['weight']}")
                        st.markdown(
                            f'<div class="analysis-metric">'
                            f'<div class="analysis-metric-head"><span>{html_lib.escape(str(item["label"]))}</span>'
                            f'<span class="analysis-metric-meta">P{item["percentile"]:.0f} · {weight_text}</span></div>'
                            f'<div class="analysis-bar {bar_class}"><span style="width:{item["percentile"]:.1f}%"></span></div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                with low_col:
                    st.markdown(
                        "**Características de Menor Destaque**"
                        if lang == "PT"
                        else "**Lower-Ranked Attributes**"
                    )

                    for item in lowest_metrics:
                        bar_class = (
                            "high" if item["percentile"] >= 70
                            else "medium" if item["percentile"] >= 40
                            else "low"
                        )
                        weight_text = (f"Peso {item['weight']}" if lang == "PT" else f"Weight {item['weight']}")
                        st.markdown(
                            f'<div class="analysis-metric">'
                            f'<div class="analysis-metric-head"><span>{html_lib.escape(str(item["label"]))}</span>'
                            f'<span class="analysis-metric-meta">P{item["percentile"]:.0f} · {weight_text}</span></div>'
                            f'<div class="analysis-bar {bar_class}"><span style="width:{item["percentile"]:.1f}%"></span></div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

            if metrics_used < metrics_total:
                st.caption(
                    (
                        f"Profile Score calculado com {metrics_used} "
                        f"de {metrics_total} métricas disponíveis "
                        "para este perfil."
                        if lang == "PT"
                        else
                        f"Profile Score calculated with {metrics_used} "
                        f"of {metrics_total} metrics available "
                        "for this profile."
                    )
                )
            else:
                st.caption(
                    (
                        f"{metrics_used} de {metrics_total} métricas disponíveis foram utilizadas no cálculo do Profile Score."
                        if lang == "PT"
                        else
                        f"{metrics_used} of {metrics_total} available metrics were used to calculate the Profile Score."
                    )
                )

    # ========================================================
    # BASIC RESULTS — NO POSITION SELECTED
    # ========================================================

    else:

        talent_table = talent_results[
            [
                "name",
                "team_name",
                "age_2025_26",
                "position_group",
                "minutesPlayed",
                "market_value_eur",
            ]
        ].copy()

        talent_table["age_2025_26"] = (
            talent_table["age_2025_26"]
            .astype("Int64")
        )

        talent_table = (
            talent_table
            .sort_values(
                "minutesPlayed",
                ascending=False,
            )
        )

        if lang == "PT":

            talent_table = talent_table.rename(
                columns={
                    "name": "Jogador",
                    "team_name": "Clube",
                    "age_2025_26": "Idade",
                    "position_group": "Posição",
                    "minutesPlayed": "Minutos",
                    "market_value_eur":
                        "Valor de Mercado (€)",
                }
            )

        else:

            talent_table = talent_table.rename(
                columns={
                    "name": "Player",
                    "team_name": "Club",
                    "age_2025_26": "Age",
                    "position_group": "Position",
                    "minutesPlayed": "Minutes",
                    "market_value_eur":
                        "Market Value (€)",
                }
            )

        # Convert the displayed values to text so every column is
        # left-aligned consistently in the Talent Finder table.
        age_col = "Idade" if lang == "PT" else "Age"
        minutes_col = "Minutos" if lang == "PT" else "Minutes"
        market_col = (
            "Valor de Mercado (€)"
            if lang == "PT"
            else "Market Value (€)"
        )

        talent_table[age_col] = talent_table[age_col].apply(
            lambda value: (
                str(int(value))
                if pd.notna(value)
                else "N/A"
            )
        )

        talent_table[minutes_col] = talent_table[minutes_col].apply(
            lambda value: (
                str(int(value))
                if pd.notna(value)
                else "N/A"
            )
        )

        talent_table[market_col] = talent_table[market_col].apply(
            lambda value: (
                f"€ {int(value)}"
                if pd.notna(value)
                else "N/A"
            )
        )

        st.dataframe(
            talent_table,
            width="stretch",
            hide_index=True,
        )

        st.caption(
            (
                "Selecione um grupo posicional específico "
                "para ativar o Profile Score e o ranking."
                if lang == "PT"
                else
                "Select a specific position group to activate "
                "the Profile Score and ranking."
            )
        )

# ============================================================
# PRODUCT FOOTER
# ============================================================
st.markdown(

    (
        '<div class="product-footer">'
        '<span>Portugal Scouting Hub · Liga Portugal 2025/26</span>'
        '<span>Dados para fins analíticos e de portfólio.</span>'
        '</div>'
        if lang == "PT"
        else
        '<div class="product-footer">'
        '<span>Portugal Scouting Hub · Liga Portugal 2025/26</span>'
        '<span>Data presented for analytics and portfolio purposes.</span>'
        '</div>'
    ),
    unsafe_allow_html=True,
)

