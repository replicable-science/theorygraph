import json

import pytest

from theorygraph.audit import run_audit
from theorygraph.util import RESULTS
from theorygraph.verify import verify_all


def test_audit_reproduces_the_values_reported_from_the_private_project():
    h = run_audit()["headline"]
    assert h["pitches"] == 375
    assert h["premise_count_alpha_gpt_single_run"] == pytest.approx(0.805, abs=0.001)
    assert h["premise_count_alpha_gpt_median_of_3"] == pytest.approx(0.925, abs=0.001)
    assert 0.70 <= h["grouping_self_consistency_ari_grok_ten_labels"] <= 0.76
    assert h["grouping_ari_grok_vs_gemini_same_ten_labels"] == pytest.approx(0.11, abs=0.01)
    assert h["share_premises_with_quote_found_verbatim_gpt4omini"] == pytest.approx(0.967, abs=0.001)


def test_stored_audit_equals_fresh_audit():
    assert verify_all() == []  # includes a field-by-field comparison of results/audit.json with a fresh run


def test_same_model_agrees_more_with_itself_than_with_another_model():
    a = run_audit()
    like = a["premise_counts"]["single_run_like_for_like"]
    assert like["same_model_runs_mean_spearman"] > like["different_models_mean_spearman"] + 0.3
    g = a["grouping"]
    assert g["self_consistency"]["fu_grok47"]["mean_ari"] > g["between_groupers"]["fu_grok47__fu_gemini"]["mean_ari"] + 0.4
    assert g["between_groupers"]["fu_grok47__fu_gemini"]["null_p95"] < g["between_groupers"]["fu_grok47__fu_gemini"]["mean_ari"]
