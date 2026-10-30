from theorygraph.sourcecheck import check_graph, check_span, normalize

T = normalize("We tested forty sensors on six farms in Maine and Nova Scotia, over the 2024 season. It worked!")


def test_verbatim_ignores_case_and_punctuation():
    assert check_span("we tested FORTY sensors on six farms", T)[0] == "verbatim"
    assert check_span("Maine and Nova Scotia over the 2024 season", T)[0] == "verbatim"


def test_near_match_catches_small_edits():
    assert check_span("we tested forty sensors on seven farms in Maine", T)[0] == "near"


def test_invented_quote_is_not_found():
    assert check_span("we tested ten thousand sensors in Texas", T)[0] == "none"


def test_empty_quote_is_reported_separately():
    assert check_span("", T)[0] == "no_quote"
    assert check_span(None, T)[0] == "no_quote"


def test_graph_summary_counts_by_kind():
    graph = {"premises": [{"id": "P1", "evidence_span": "forty sensors on six farms", "status": "asserted", "status_span": ""},
                          {"id": "P2", "evidence_span": "ten thousand sensors", "status": "expected", "status_span": "it worked"}],
             "links": [{"id": "L1", "evidence_span": "it worked"}]}
    s = check_graph(graph, "We tested forty sensors on six farms in Maine. It worked!")
    assert s["by_kind"]["premise"] == {"verbatim": 1, "near": 0, "none": 1, "no_quote": 0}
    assert s["by_kind"]["status_cue"]["verbatim"] == 1 and "status_cue" in s["by_kind"]
    assert s["quoted"] == 4 and s["none"] == 1
