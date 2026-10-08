# Portugal Scouting Hub

[🇬🇧 English](README.md) | [🇧🇷 Português](README.pt-BR.md)

**Data-driven scouting analytics for identifying and evaluating U23 talent in Portuguese football.**

Portugal Scouting Hub is a portfolio project combining data collection, processing, football analytics and an interactive Streamlit product. It supports player profiling, same-position comparison and configurable talent discovery using position-specific performance metrics.

> **Important:** the Profile Score is a configurable profile-fit indicator based on selected metrics and weights. It is not an objective measure of overall player quality.

## Product Preview

> Screenshots will be added here before publication: Player Profile, Player Comparison and Talent Finder.

## Project Objective

The project addresses a practical recruitment question: **How can performance data help identify and contextualize U23 players in Portuguese football?**

The goal is not to automate scouting decisions. The application provides an analytical layer to explore player profiles, compare players within the same positional group, filter U23 candidates by recruitment constraints, contextualize performance through same-position percentiles and create custom scouting profiles by changing metric weights.

## Main Features

- **Player Profile:** player information, season participation, position-specific indicators and percentile radar.
- **Player Comparison:** comparison of two players from the same positional group using the same benchmark methodology.
- **Talent Finder:** filters candidates by position, age, minutes and market value, with configurable position-specific metric weights.
- **Result Analysis:** shows metric coverage and the highest- and lowest-ranked attributes of a selected candidate.
- **Bilingual interface:** Portuguese and English, with Portuguese as the default language.

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

The public application does **not** require a new data collection run. The repository includes the processed dataset required by the app:

```text
data/processed/scouting_dataset_2025_26.csv
```

Raw collection files are kept outside version control.

## Dataset

The application dataset contains **574 unique players** from the 2025/26 Portuguese league dataset used in this project. The final public dataset contains **46 fields**, selected from the larger collected dataset to include only information and statistics required by the application.

It includes player/team identifiers, name, birth date, calculated age, U23 flag, position, height, preferred foot, country, market value, minutes, appearances, starts and the attacking, passing, defensive and goalkeeper statistics required by the analytical engine.

Derived fields such as per-90 metrics, positional percentiles and Profile Score are calculated by the code rather than stored as source observations.

## Scouting Methodology

### U23 Definition

Age is calculated using **1 July 2025** as the reference date for the 2025/26 season. A player is classified as U23 when they had not yet turned 23 on that date.

### Minimum Minutes

A minimum threshold of **450 minutes** is used for the statistical benchmark, equivalent to five complete 90-minute matches. Players below this threshold are not deleted from the dataset; the threshold is used to build a more stable comparison benchmark.

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

Volume statistics are normalized to 90 minutes:

```text
metric_per90 = metric / minutes_played × 90
```

Percentage-based metrics are not converted to per 90.

### Positional Benchmark

Percentiles are calculated against **all eligible players in the same positional group with at least 450 minutes**, not only U23 players. This contextualizes U23 candidates against the broader league-level positional benchmark.

### Percentiles

For most metrics, higher values produce higher percentiles. For lower-is-better metrics the direction is inverted; in the current methodology, `goalsConceded_per90` is treated this way.

A percentile close to 100 means the player's value ranks near the top of the same-position benchmark for that metric.

### Position-Specific Metrics

| Position | Metrics |
|---|---|
| Striker | Goals/90, xG/90, Shots/90, Shots on Target/90, Assists/90, xA/90 |
| Winger | Goals/90, xG/90, Assists/90, xA/90, Key Passes/90, Successful Dribbles/90 |
| Midfielder | Assists/90, xA/90, Key Passes/90, Accurate Final Third Passes/90, Ball Recoveries/90, Interceptions/90 |
| Full Back | Assists/90, xA/90, Key Passes/90, Accurate Final Third Passes/90, Successful Dribbles/90, Interceptions/90 |
| Centre Back | Tackles/90, Interceptions/90, Clearances/90, Ball Recoveries/90, Aerial Duels Won %, Accurate Passes % |
| Goalkeeper | Saves/90, Goals Prevented/90, Goals Conceded/90, High Claims/90, Successful Runs Out/90, Accurate Passes % |

These metrics represent the analytical profiles selected for this project, not universal definitions of performance for each position.

### Profile Score

The Profile Score is a weighted average of the player's same-position metric percentiles:

```text
Profile Score = Σ(metric percentile × metric weight) / Σ(available metric weights)
```

Users can change the metric weights in Talent Finder. Missing metrics are excluded rather than treated as zero, and the application reports metric coverage.

The score answers: **How strongly does this player's statistical profile match the currently selected metrics and weights relative to players in the same position?** It is not an objective ranking of overall football ability or future potential.

## Project Structure

```text
football-analytics/
├── app/
│   └── app.py
├── data/
│   ├── processed/
│   │   └── scouting_dataset_2025_26.csv
│   └── raw/                       # ignored by Git
├── notebooks/
│   ├── 01_data_quality.ipynb
│   └── 02_player_analysis.ipynb
├── src/
│   ├── scouting.py
│   └── collection / processing scripts
├── .gitignore
├── requirements.txt
├── README.md
└── README.pt-BR.md
```

`src/scouting.py` contains the reusable analytical logic used by the Streamlit application, including data preparation, per-90 calculations, positional pools, percentiles and Talent Finder ranking.

## Technologies

Python · Pandas · NumPy · Streamlit · Plotly · Matplotlib · curl-cffi · Jupyter Notebook

## Installation

```bash
git clone <repository-url>
cd football-analytics
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

The processed dataset is already included, so running the app does not require collecting the raw data again.

## Data Collection

The project retains scripts used during collection and processing. The source data used in development was obtained from SofaScore-derived internal/undocumented endpoints, which may change or become unavailable over time.

For this reason, raw JSON files are not required by the public app, `data/raw/` is excluded from version control, and the processed dataset needed by the app is included in the repository. Collection scripts are retained to demonstrate the data-engineering workflow, but successful future collection is not guaranteed.

Player and team images displayed by the application may also depend on external image resources and can therefore become unavailable independently of the processed dataset.

## Limitations

This project is an analytical scouting aid and does not replace contextual football analysis, live scouting or video analysis. Statistical data cannot capture every tactical or qualitative aspect of performance; per-90 normalization does not remove differences in role, team strength, tactical context or sample size; market values are contextual estimates; the 450-minute threshold is a methodological choice; positional groups simplify more specific roles; and selected metrics and weights directly influence the Profile Score. Goalkeeper metrics can also be strongly affected by team and opposition context.

A high Profile Score therefore represents fit to the selected statistical profile, not guaranteed quality, potential or recruitment success.

## Future Improvements

Possible extensions include additional seasons and historical trends, league/season selectors, richer role-specific profiles, additional contextual metrics, exportable scouting reports and public deployment of the Streamlit application.

Machine-learning player similarity and predictive models are intentionally outside the current scope.

## Author

Portfolio project focused on **Data Analytics, Data Engineering and Football Analytics**.
