"""Unit tests for Portugal Scouting Hub's statistical engine.

Run from the project root: python -m pytest tests/ -v
All fixtures are small, purpose-built test cases; no SofaScore dataset is needed.
"""

import numpy as np
import pandas as pd
import pytest

from src import scouting


def test_position_mapping_and_per90_without_mutating_input():
    raw = pd.DataFrame({
        'detailed_position': ['ST', 'DL', 'GK', 'UNKNOWN'],
        'minutesPlayed': [180, 90, 0, 90],
        'goals': [4, 1, 2, 0],
        'accuratePassesPercentage': [85, 75, 60, 90],
    })
    result = scouting.prepare_analysis(raw)
    assert result['position_group'].iloc[:3].tolist() == ['Striker', 'Full Back', 'Goalkeeper']
    assert pd.isna(result.loc[3, 'position_group'])
    assert result.loc[0, 'goals_per90'] == pytest.approx(2)
    assert result.loc[1, 'goals_per90'] == pytest.approx(1)
    assert pd.isna(result.loc[2, 'goals_per90'])
    assert 'accuratePassesPercentage_per90' not in result
    assert 'position_group' not in raw.columns


def test_create_pools_benchmark_cutoff_and_u23_independent():
    analysis = pd.DataFrame({
        'player_id': [1, 2, 3, 4, 5],
        'minutesPlayed': [449, 450, 900, 200, 900],
        'position_group': ['Striker', 'Striker', 'Striker', 'Winger', None],
        'is_u23': [True, True, False, True, True],
    })
    benchmark, scouting_pool = scouting.create_pools(analysis)
    assert benchmark['player_id'].tolist() == [2, 3]
    assert scouting_pool['player_id'].tolist() == [1, 2, 4]


@pytest.mark.parametrize('value,expected', [(1, 25), (2, 50), (3, 75), (4, 100)])
def test_percentile_higher_is_better(value, expected):
    assert scouting.calculate_percentile(value, [1, 2, 3, 4]) == pytest.approx(expected)


@pytest.mark.parametrize('value,expected', [(1, 100), (2, 75), (3, 50), (4, 25)])
def test_percentile_lower_is_better(value, expected):
    assert scouting.calculate_percentile(value, [1, 2, 3, 4], lower_is_better=True) == pytest.approx(expected)


def test_percentile_missing_values_and_ties():
    assert scouting.calculate_percentile(2, [1, 2, 2, np.nan]) == pytest.approx(100)
    assert scouting.calculate_percentile(2, [1, 2, 2, np.nan], True) == pytest.approx(200 / 3)
    assert np.isnan(scouting.calculate_percentile(np.nan, [1, 2]))
    assert np.isnan(scouting.calculate_percentile(2, [np.nan]))


def test_talent_metrics_invalid_position():
    assert 'goals_per90' in scouting.get_talent_metrics('Striker')
    with pytest.raises(ValueError, match='posição'):
        scouting.get_talent_metrics('Unknown')


def test_get_player_profile_and_info():
    analysis = pd.DataFrame([{
        'player_id': 10, 'name': 'Test Player', 'team_name': 'Team A',
        'detailed_position': 'ST', 'position_group': 'Striker',
        'age_2025_26': 21, 'minutesPlayed': 720,
    }])
    assert scouting.get_player_profile('Test Player', analysis)['player_id'] == 10
    info = scouting.get_player_info('Test Player', analysis)
    assert info['team'] == 'Team A'
    assert info['minutes'] == 720
    with pytest.raises(ValueError, match='não encontrado'):
        scouting.get_player_profile('Missing', analysis)


def test_player_kpis_use_only_same_position_and_invert_goalkeeper_metric():
    candidates = pd.DataFrame([{
        'name': 'Keeper A', 'position_group': 'Goalkeeper',
        'goalsConceded_per90': 1.0, 'saves_per90': 4.0,
    }])
    benchmark = pd.DataFrame({
        'position_group': ['Goalkeeper', 'Goalkeeper', 'Striker'],
        'goalsConceded_per90': [1.0, 2.0, 100.0],
        'saves_per90': [2.0, 4.0, 100.0],
    })
    kpis = scouting.get_player_kpis('Keeper A', candidates, benchmark)
    assert kpis['goalsConceded_per90']['percentile'] == pytest.approx(100)
    assert kpis['saves_per90']['percentile'] == pytest.approx(100)
    with pytest.raises(ValueError, match='não encontrado'):
        scouting.get_player_kpis('Missing', candidates, benchmark)


def _ranking_frames():
    candidates = pd.DataFrame({
        'name': ['Alpha', 'Beta', 'Other'],
        'position_group': ['Striker', 'Striker', 'Winger'],
        'minutesPlayed': [900, 800, 900],
        'goals_per90': [3.0, 1.0, 9.0],
        'assists_per90': [1.0, 3.0, 9.0],
    })
    benchmark = pd.DataFrame({
        'position_group': ['Striker', 'Striker', 'Striker', 'Winger'],
        'goals_per90': [1.0, 2.0, 3.0, 100.0],
        'assists_per90': [1.0, 2.0, 3.0, 100.0],
    })
    return candidates, benchmark


def test_ranking_weighted_scores_and_position_filter():
    candidates, benchmark = _ranking_frames()
    result = scouting.calculate_talent_ranking(
        candidates, benchmark, 'Striker',
        weights={'goals_per90': 3, 'assists_per90': 1},
    )
    assert result['name'].tolist() == ['Alpha', 'Beta']
    assert result['talent_score'].tolist() == pytest.approx([83.3333333333, 50])
    assert result['talent_rank'].tolist() == [1, 2]
    assert result['metrics_used'].tolist() == [2, 2]
    assert result['metrics_total'].tolist() == [2, 2]
    assert 'talent_score' not in candidates.columns


def test_ranking_missing_metric_excluded_and_all_missing_is_nan():
    candidates, benchmark = _ranking_frames()
    candidates.loc[0, 'assists_per90'] = np.nan
    candidates.loc[1, ['goals_per90', 'assists_per90']] = np.nan
    result = scouting.calculate_talent_ranking(candidates, benchmark, 'Striker')
    alpha = result.set_index('name').loc['Alpha']
    beta = result.set_index('name').loc['Beta']
    assert alpha['talent_score'] == pytest.approx(100)
    assert alpha['metrics_used'] == 1
    assert pd.isna(beta['talent_score'])
    assert beta['metrics_used'] == 0
    assert pd.isna(beta['talent_rank'])


def test_ranking_zero_weights_rejected():
    candidates, benchmark = _ranking_frames()
    with pytest.raises(ValueError, match='soma dos pesos'):
        scouting.calculate_talent_ranking(candidates, benchmark, 'Striker', weights={})


def test_ranking_empty_candidates_and_missing_benchmark():
    candidates, benchmark = _ranking_frames()
    empty = scouting.calculate_talent_ranking(candidates.iloc[:0], benchmark, 'Striker')
    assert empty.empty
    with pytest.raises(ValueError, match='benchmark'):
        scouting.calculate_talent_ranking(candidates, benchmark.iloc[:0], 'Striker')


def test_ranking_equal_scores_tie_breaker_minutes():
    candidates, benchmark = _ranking_frames()
    candidates.loc[0, ['goals_per90', 'assists_per90']] = [2.0, 2.0]
    candidates.loc[1, ['goals_per90', 'assists_per90']] = [2.0, 2.0]
    result = scouting.calculate_talent_ranking(candidates, benchmark, 'Striker')
    assert result['name'].tolist() == ['Alpha', 'Beta']
    assert result['talent_rank'].tolist() == [1, 1]


def test_load_data_parses_dates_and_rejects_duplicate_ids(tmp_path, monkeypatch):
    file = tmp_path / 'data.csv'
    pd.DataFrame({
        'player_id': [1, 2], 'birth_date': ['2004-01-01', 'invalid'],
        'is_u23': [True, False],
    }).to_csv(file, index=False)
    monkeypatch.setattr(scouting, 'SCOUTING_DATA_FILE', file)
    df = scouting.load_data()
    assert isinstance(df['birth_date'].dtype, pd.DatetimeTZDtype)
    assert str(df['birth_date'].dt.tz) == 'UTC'
    assert pd.isna(df.loc[1, 'birth_date'])
    assert str(df['is_u23'].dtype) == 'boolean'
    pd.DataFrame({
        'player_id': [1, 1], 'birth_date': ['2004-01-01', '2005-01-01'],
        'is_u23': [True, False],
    }).to_csv(file, index=False)
    with pytest.raises(ValueError, match='duplicados'):
        scouting.load_data()
