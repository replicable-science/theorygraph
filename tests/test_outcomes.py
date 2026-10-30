from theorygraph.outcomes import load


def test_outcomes_file_holds_only_the_techcrunch_status():
    d = load()
    assert len(d) == 375
    assert list(d.columns) == ["case_id", "pitch_month", "techcrunch_status"]
    assert set(d.techcrunch_status) <= {"open", "closed", "acquired", "ipo"}
