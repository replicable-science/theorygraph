"""Export per-pitch structure measures from the authors' private working project.

PROVENANCE ONLY. Reads files that are not in this repository and writes `data/derived/structure_measures.csv`:
numbers only, one row per pitch.

  premises, domains           GPT-4o-mini premise count (median of three runs) and number of strategic domains
  *_tfidf                     cosine similarity of premise statements in TF-IDF space (toolkit/theory_graph/similarities.py):
                              mean over all premise pairs, within the same domain, between domains, and
                              domain_sep_tfidf = within minus between
  *_emb                       the same with Qwen3-Embedding-8B vectors of the premise statements
  hq_us                       1 if TechCrunch lists the company in the United States

The measures need the full premise statements, 5.9% of which are withheld from this repository, so they are shipped
as computed rather than recomputed here.

    TG_PRIVATE_ROOT=<private project> python provenance/export_structure_measures.py
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

ART = Path(__file__).resolve().parents[1]
ROOT = Path(os.environ["TG_PRIVATE_ROOT"])
RUN = ROOT / "reference/full_n375_k3_v211_gpt4o_mini"

cases = pd.read_csv(ART / "data" / "derived" / "cases.csv", dtype={"case_id": str})[["case_id"]]
ds = pd.read_csv(RUN / "aggregated" / "dataset.csv")[["case_id", "breadth", "n_domains", "premise_sim_mean", "within_domain_sim", "between_domain_sim", "domain_sep"]]
emb = pd.read_csv(RUN / "embeddings" / "embedding_measures.csv")[["case_id", "premise_sim_emb", "within_domain_emb", "between_domain_emb", "domain_sep_emb"]]
loc = pd.read_csv(ROOT / "data/corpora/startup_battlefield/survival_dv/survival_dv.csv")
loc = loc[loc.case_match_status == "matched"][["case_id", "location"]]
loc["hq_us"] = loc.location.fillna("").str.contains("United States", regex=False).astype(int)

out = (cases.merge(ds, on="case_id", how="left").merge(emb, on="case_id", how="left").merge(loc[["case_id", "hq_us"]], on="case_id", how="left")
       .rename(columns={"breadth": "premises", "n_domains": "domains", "premise_sim_mean": "premise_sim_tfidf", "within_domain_sim": "within_domain_sim_tfidf",
                        "between_domain_sim": "between_domain_sim_tfidf", "domain_sep": "domain_sep_tfidf", "within_domain_emb": "within_domain_sim_emb",
                        "between_domain_emb": "between_domain_sim_emb"}))
assert len(out) == 375
out.sort_values("case_id").to_csv(ART / "data" / "derived" / "structure_measures.csv", index=False, lineterminator="\n", float_format="%.6f")
print(f"wrote data/derived/structure_measures.csv: {len(out)} rows")
