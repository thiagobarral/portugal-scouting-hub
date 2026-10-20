import numpy as np
import pandas as pd
import pytest
from src import scouting


def test_duplicate_names_require_id():
    df = pd.DataFrame({"player_id": [1, 2], "name": ["Alex", "Alex"], "position_group": ["Striker", "Striker"]})
    with pytest.raises(ValueError, match="ambígua"):
        scouting.get_player_profile("Alex", df)
    assert scouting.get_player_profile("Alex", df, player_id=2)["player_id"] == 2
    assert scouting.get_player_info("Alex", df, player_id=1)["player_id"] == 1


def test_duplicate_names_in_kpis():
    candidates = pd.DataFrame({"player_id": [1, 2], "name": ["Alex", "Alex"], "position_group": ["Striker", "Striker"], "goals_per90": [1.0, 2.0]})
    benchmark = pd.DataFrame({"position_group": ["Striker", "Striker"], "goals_per90": [1.0, 2.0]})
    with pytest.raises(ValueError, match="ambígua"):
        scouting.get_player_kpis("Alex", candidates, benchmark)
    assert scouting.get_player_kpis("Alex", candidates, benchmark, player_id=2)["goals_per90"]["value"] == 2


@pytest.mark.parametrize("bad", [-1, float("nan"), float("inf"), -float("inf")])
def test_invalid_weights_rejected(bad):
    candidates = pd.DataFrame({"name": ["A"], "position_group": ["Striker"], "minutesPlayed": [900], "goals_per90": [1.0], "assists_per90": [1.0]})
    benchmark = candidates.copy()
    with pytest.raises(ValueError, match="pesos"):
        scouting.calculate_talent_ranking(candidates, benchmark, "Striker", {"goals_per90": 1, "assists_per90": bad})


def test_coverage_only_counts_positive_weight_metrics():
    candidates = pd.DataFrame({"name": ["A", "B"], "position_group": ["Striker", "Striker"], "minutesPlayed": [900, 900], "goals_per90": [1.0, np.nan], "assists_per90": [1.0, 1.0]})
    benchmark = pd.DataFrame({"position_group": ["Striker", "Striker"], "goals_per90": [0.5, 1.0], "assists_per90": [0.5, 1.0]})
    result = scouting.calculate_talent_ranking(candidates, benchmark, "Striker", {"goals_per90": 1, "assists_per90": 0}).set_index("name")
    assert result.loc["A", "metrics_used"] == 1
    assert result.loc["B", "metrics_used"] == 0
    assert result.loc["A", "metrics_total"] == 1
    assert np.isnan(result.loc["B", "talent_score"])
