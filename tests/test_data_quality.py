"""Checks for the real scouting CSV. Run: python -m pytest tests/test_data_quality.py -v"""
from pathlib import Path
import warnings
import pandas as pd
import pytest
from src.scouting import MIN_MINUTES, POSITION_GROUP_MAP, prepare_analysis, create_pools, get_talent_metrics

PATH = Path(__file__).resolve().parents[1] / 'data/processed/scouting_dataset_2025_26.csv'
REQUIRED = {'player_id','name','team_id','team_name','birth_date','age_2025_26','is_u23','detailed_position','minutesPlayed','appearances','matchesStarted'}
NONNEGATIVE = ['minutesPlayed','appearances','matchesStarted','goals','assists','expectedGoals','expectedAssists','bigChancesCreated','bigChancesMissed','totalShots','shotsOnTarget','keyPasses','totalPasses','accuratePasses','accurateFinalThirdPasses','successfulDribbles','tackles','tacklesWon','interceptions','clearances','ballRecovery','outfielderBlocks','groundDuelsWon','aerialDuelsWon','totalDuelsWon','possessionLost','possessionWonAttThird','saves','goalsConceded','highClaims','successfulRunsOut','market_value_eur']

@pytest.fixture(scope='module')
def df():
    assert PATH.is_file(), f'CSV não encontrado: {PATH}. Copie o CSV real para data/processed/.'
    return pd.read_csv(PATH)

def test_nonempty_schema(df):
    assert not df.empty
    assert not (missing := REQUIRED - set(df.columns)), f'Colunas ausentes: {sorted(missing)}'

def test_unique_player_ids(df):
    assert df.player_id.notna().all()
    assert not df.player_id.duplicated().any(), 'IDs duplicados'

def test_identity(df):
    for col in ('name','team_name','team_id'):
        assert df[col].notna().all(), f'{col} ausente'
    for col in ('name','team_name'):
        assert df[col].astype(str).str.strip().ne('').all(), f'{col} vazio'
    assert df.groupby('team_id').team_name.nunique().le(1).all(), 'team_id associado a clubes diferentes'

@pytest.mark.parametrize('column', NONNEGATIVE)
def test_nonnegative(df,column):
    assert column in df, f'Coluna ausente: {column}'
    values=pd.to_numeric(df[column],errors='coerce')
    assert not (values<0).any(), f'{column} contém negativos'

@pytest.mark.parametrize('column', ['aerialDuelsWonPercentage','accuratePassesPercentage'])
def test_percentages(df,column):
    assert column in df
    assert pd.to_numeric(df[column],errors='coerce').dropna().between(0,100).all()

def test_match_consistency(df):
    assert (df.matchesStarted<=df.appearances).all()
    assert (df.loc[df.appearances.eq(0),'minutesPlayed']==0).all()

@pytest.mark.parametrize('subset,total',[('shotsOnTarget','totalShots'),('accuratePasses','totalPasses'),('tacklesWon','tackles')])
def test_subset_counts(df,subset,total):
    assert (df[subset]<=df[total]).all(), f'{subset} maior que {total}'

def test_age_and_dates(df):
    assert pd.to_numeric(df.age_2025_26,errors='coerce').dropna().between(14,55).all()
    dates=pd.to_datetime(df.birth_date,errors='coerce',utc=True)
    assert dates.notna().sum()==df.birth_date.notna().sum(), 'Datas preenchidas inválidas'

def test_u23_values(df):
    assert df.is_u23.dropna().astype(str).str.lower().isin(['true','false']).all()

def test_positions(df):
    invalid=set(df.detailed_position.dropna())-set(POSITION_GROUP_MAP)
    assert not invalid, f'Posições desconhecidas: {sorted(invalid)}'

def test_metrics_available(df):
    analysis=prepare_analysis(df)
    for group in set(POSITION_GROUP_MAP.values()):
        metrics=get_talent_metrics(group)
        assert metrics, f'Sem métricas para {group}'
        assert not (missing:=set(metrics)-set(analysis)), f'{group}: métricas ausentes {sorted(missing)}'

def test_pools(df):
    benchmark, young=create_pools(prepare_analysis(df))
    assert not benchmark.empty
    assert benchmark.minutesPlayed.ge(MIN_MINUTES).all()
    assert benchmark.position_group.notna().all()
    assert young.is_u23.eq(True).all()
    assert young.position_group.notna().all()

def test_missingness_monitor(df):
    columns=['detailed_position','expectedGoals','expectedAssists','goalsPrevented','birth_date','is_u23']
    gaps={c:int(df[c].isna().sum()) for c in columns if c in df}
    if any(gaps.values()):
        warnings.warn('Nulos (monitoramento, não falha): '+', '.join(f'{k}={v}' for k,v in gaps.items()),UserWarning,stacklevel=2)

def test_signed_goals_prevented(df):
    assert 'goalsPrevented' not in NONNEGATIVE, 'goalsPrevented pode ser negativo'
