"""The stored replies must reproduce the stored graphs exactly, offline."""
import json

import pytest

from theorygraph import schema
from theorygraph.llm import Chat, ReplayMiss, request_key
from theorygraph.passes import load_example, run_case
from theorygraph.util import EXAMPLES, RESULTS

MODELS = ["gpt-4o-mini", "gpt-4.1"]
NAMES = ["brinelog", "lathework", "recallpost"]


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("name", NAMES)
def test_replay_reproduces_stored_graph(name, model):
    pitch, qa = load_example(name, EXAMPLES / "pitches")
    graph = run_case(Chat(mode="replay", model=model, log_path=None), name, pitch, qa)
    stored = json.loads((RESULTS / "graphs" / f"{name}__{model}.json").read_text(encoding="utf-8"))
    graph["meta"]["mode"] = stored["meta"]["mode"]  # replay vs the live run that created the reply
    assert graph == stored


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("name", NAMES)
def test_stored_graphs_are_structurally_sound(name, model):
    g = json.loads((RESULTS / "graphs" / f"{name}__{model}.json").read_text(encoding="utf-8"))
    assert schema.validate_graph(g) == []  # invalid links were dropped by the pipeline and are listed in meta


def test_replay_miss_is_an_error_not_a_fallback():
    pitch, qa = load_example("brinelog", EXAMPLES / "pitches")
    with pytest.raises(ReplayMiss):
        run_case(Chat(mode="replay", model="some-model-nobody-ran", log_path=None), "brinelog", pitch, qa)


def test_request_key_depends_on_every_input():
    m = [{"role": "user", "content": "x"}]
    k = request_key("a", 0.0, m)
    assert k != request_key("b", 0.0, m) and k != request_key("a", 0.2, m) and k != request_key("a", 0.0, [{"role": "user", "content": "y"}])
