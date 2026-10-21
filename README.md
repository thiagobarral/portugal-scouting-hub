# Portugal Scouting Hub

[English](README.md) | [Português](README.pt-BR.md)

**[⚽ Launch the live app](https://portugal-scouting-u23.streamlit.app)** · [Source code on GitHub](https://github.com/thiagobarral/portugal-scouting-hub)

**Data-driven scouting analytics for identifying and evaluating U23 talent in Portuguese football.**

Portugal Scouting Hub is a portfolio project combining data collection, processing, football analytics, and an interactive Streamlit data product. The application enables users to explore player profiles, compare players in the same positional group, and discover talent using position-specific metrics.

> **Important:** Profile Score is a configurable measure of how closely a player's statistical profile matches the selected metrics and weights. It is **not** an objective measure of a player's overall quality.

## Project Objective

The project addresses a practical recruitment question: **How can performance data help identify and contextualize U23 players in Portuguese football?**

The goal is not to automate scouting decisions. Instead, the app provides an analytical layer for individual player exploration, same-position comparisons, U23 candidate filtering, positional percentiles, and customized scouting profiles through adjustable metric weights.

## Key Features

- **Player Profile:** player information, season participation, position-specific indicators, and a percentile radar chart.
- **Compare:** side-by-side comparison of two players in the same positional group using a shared benchmark.
- **Talent Finder:** filters for position, age, minutes, and market value, with customizable position-specific metric weights.
- **Result Analysis:** metric coverage and the selected candidate's strongest and weakest percentile indicators.
- **Bilingual interface:** Portuguese and English, with Portuguese as the default.
- **Methodology and transparency:** explanations of benchmarks, percentiles, and Profile Score, plus contextual notices for small samples and missing metrics.
- **Player photos and club badges:** external images loaded temporarily by the application, subject to source availability and usage terms.

## Data Pipeline

```text
Data source
    ↓
Collection scripts
    ↓
Raw JSON data
    ↓
Cleaning and processing
    ↓
Processed scouting dataset
    ↓
Per-90 metrics + positional benchmarks + percentiles
    ↓
Profile Score
    ↓
Streamlit + Plotly application
```

The processed file `data/processed/scouting_dataset_2025_26.csv` is version-controlled in this repository and powers the deployed application. Raw data under `data/raw/` remains excluded from version control. Publication does not replace the need to comply with the original source's usage and redistribution conditions.

## Dataset

The application uses **574 unique players** from the Liga Portugal 2025/26 dataset assembled for this project. The processed dataset contains **46 fields**, selected from the original data to retain information and statistics relevant to scouting.

Fields include identifiers, player name, club, date of birth, calculated age, U23 flag, position, height, preferred foot, country, market value, minutes, matches, starts, and attacking, passing, defensive, and goalkeeper statistics.

Derived metrics such as per-90 rates, positional percentiles, and Profile Score are calculated in code rather than stored as original observations from the source.

## Scouting Methodology

### U23 Definition

Age is calculated using **July 1, 2025** as the reference date for the 2025/26 season. A player is classified as U23 if they had not yet turned 23 on that date.

### Minimum Minutes

The statistical benchmark uses a **450-minute** threshold, equivalent to five full matches. Players below this threshold remain in the dataset; the threshold is used to construct a more stable reference group.

### Positional Groups

| Positional Group | Detailed Positions |
|---|---|
| Goalkeeper | GK |
| Centre Back | DC |
| Full Back | DL, DR |
| Midfielder | DM, MC, AM |
| Winger | ML, MR, LW, RW |
| Striker | ST |

### Per-90 Normalization

Counting statistics are normalized to 90 minutes:

```text
metric_per90 = metric / minutes_played × 90
```

Percentage metrics are not converted to per-90 rates.

### Positional Benchmark

Percentiles are calculated against **all eligible players in the same positional group with at least 450 minutes**, not only U23 players. This places young candidates in the context of the broader positional benchmark in the league.

### Percentiles

For most metrics, higher values correspond to higher percentiles. The direction is reversed for metrics where lower values are preferable; in the current methodology, `goalsConceded_per90` is treated this way.

A percentile near 100 indicates that a player's value is near the top of the same-position benchmark for that metric.

### Metrics by Position

| Position | Metrics |
|---|---|
| Striker | Goals/90, xG/90, Shots/90, Shots on Target/90, Assists/90, xA/90 |
| Winger | Goals/90, xG/90, Assists/90, xA/90, Key Passes/90, Successful Dribbles/90 |
| Midfielder | Assists/90, xA/90, Key Passes/90, Accurate Final Third Passes/90, Ball Recoveries/90, Interceptions/90 |
| Full Back | Assists/90, xA/90, Key Passes/90, Accurate Final Third Passes/90, Successful Dribbles/90, Interceptions/90 |
| Centre Back | Tackles/90, Interceptions/90, Clearances/90, Ball Recoveries/90, Aerial Duels Won %, Pass Accuracy % |
| Goalkeeper | Saves/90, Goals Prevented/90, Goals Conceded/90, High Claims/90, Successful Runs Out/90, Pass Accuracy % |

These metrics reflect the analytical profiles selected for this project; they are not universal definitions of performance for each position.

### Profile Score

Profile Score is the weighted average of a player's metric percentiles within their positional group:

```text
Profile Score = Σ(metric percentile × metric weight) / Σ(weights of available metrics)
```

Users can adjust weights in Talent Finder. Missing metrics are excluded from the calculation rather than assigned a value of zero, and the application reports metric coverage.

The score answers: **How closely does this player's statistical profile match the currently selected metrics and weights, compared with players in the same position?** It does not represent an objective ranking of overall quality or future potential.

## Project Structure

```text
football-analytics/
├── app/
│   └── app.py
├── data/
│   ├── processed/
│   │   └── scouting_dataset_2025_26.csv  # version-controlled
│   └── raw/                               # Git-ignored
├── notebooks/
│   ├── 01_data_quality.ipynb
│   └── 02_player_analysis.ipynb
├── src/
│   ├── scouting.py
│   └── collection / processing scripts
├── tests/                                  # unit and data-quality tests
├── .github/
│   └── workflows/
│       └── tests.yml                       # GitHub Actions tests
├── .gitignore
├── requirements.txt
├── README.md
└── README.pt-BR.md
```

`src/scouting.py` contains reusable analytical logic for data preparation, per-90 calculations, positional pools, percentiles, and Talent Finder rankings.

## Tech Stack

Python · Pandas · NumPy · Streamlit · Plotly · Matplotlib · curl-cffi · Jupyter Notebook

## Installation

```bash
git clone https://github.com/thiagobarral/portugal-scouting-hub.git
cd portugal-scouting-hub
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running the Application

From the project root:

```bash
python -m streamlit run app/app.py
```

**Prerequisite:** `data/processed/scouting_dataset_2025_26.csv` must be available at the specified path. It is included in the current repository. Alternatively, use the hosted application at **[portugal-scouting-u23.streamlit.app](https://portugal-scouting-u23.streamlit.app)** without installing anything locally.

## Data Source and Usage Conditions

**Source consulted during development:** [SofaScore](https://www.sofascore.com/). The project uses Liga Portugal 2025/26 player statistics obtained through internal/undocumented endpoints used by the website. The local dataset was cleaned, selected, and transformed for scouting analysis; these transformations do not change the attribution of the original source.

The processed dataset used by the application contains 574 players and 46 fields and is available in this repository. The application also publicly displays statistics derived from these data. The maintainer is responsible for ensuring that collection, redistribution, and display of data and images comply with applicable permissions and terms. Attribution does not imply affiliation with or endorsement by SofaScore.

Collection and processing scripts document the project's technical workflow; they do not represent an official API or permission to use it. Endpoints may change, and future collection must comply with applicable terms and permissions. Player photos and club badges depend on external resources; the application may temporarily cache them in memory for display without permanently storing them in the repository.

## Limitations

This project supports scouting analysis but does not replace contextual assessment, live observation, or video analysis. Statistics do not capture every tactical or qualitative aspect; per-90 normalization does not remove differences in role, team strength, tactical context, or sample size; market values are estimates; the 450-minute threshold is a methodological choice; positional groups simplify more specific roles; and selected metrics and weights directly influence Profile Score. Goalkeeper metrics are also strongly affected by team and opposition context.

A high Profile Score indicates alignment with the selected statistical profile, not a guarantee of player quality, potential, or recruitment success.

## Potential Improvements

Potential extensions include additional seasons and historical trends, league/season selectors, more role-specific profiles, additional contextual metrics, report exports, and improvements to monitoring and maintenance of the deployed application.

Predictive Machine Learning models and automatic player similarity are intentionally outside the current scope.

## Testing and Continuous Integration

The project includes automated tests for scouting logic and data quality. In the most recent reported validation, **75 tests passed**, with one informational warning about expected missing values in the dataset.

Run locally:

```bash
python -m pytest tests/ -v
```

The `.github/workflows/tests.yml` workflow runs tests in GitHub Actions after repository updates. To run the suite locally, install `pytest` if it is not already available in your environment.

## Live Application

**[Open Portugal Scouting Hub](https://portugal-scouting-u23.streamlit.app)**

The application is deployed on Streamlit Community Cloud from the GitHub repository, using `app/app.py` as its entry point. The interface provides Player Profile, Compare, and Talent Finder pages.

## Author

A portfolio project focused on **Data Analytics, Data Engineering, and Football Analytics**.
