"""Build docs/index.html from the stored results. Every number on the page is read from results/*.json, never typed in.

    python -m theorygraph site

The page is one self-contained file: no external fonts, scripts or images, so it can be archived and read offline.
"""
from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

import pandas as pd

from . import figures as fg
from .passes import load_example
from .util import DERIVED, EXAMPLES, LOGS, REPO, RESULTS, read_json

HERO_CASE = "pilot-591"
GALLERY = ["pilot-528", "pilot-1053"]
FICTIONAL = {"brinelog": "Brinelog (sensors for oyster farms)", "lathework": "Lathework (retired tradespeople as instructors)",
             "recallpost": "Recallpost (no-show reminders for dental clinics)"}
MODELS = ["gpt-4o-mini", "gpt-4.1"]
STATUS_LABEL = {"evidence_cited": "evidence cited", "expected": "expected", "speculative": "speculative", "asserted": "asserted"}
RESPONSE_LABEL = {"defends": "defends", "qualifies": "qualifies", "concedes": "concedes", "deflects": "deflects", "no_answer": "no answer"}


def pct(x, nd=0):
    return "n/a" if x is None else f"{x * 100:.{nd}f}%"


def f2(x):
    return f"{x:.2f}"


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def chip(kind: str, name: str, table: dict, colors: dict) -> str:
    return f'<span class="chip" style="--c:{colors[name]}">{escape(table[name])}</span>' if name in table else ""


def check_badge(outcome: str | None) -> str:
    if outcome is None:
        return ""
    text = {"verbatim": "quote found word for word", "near": "quote found, small differences", "none": "quote not found", "no_quote": "no quote given"}[outcome]
    cls = {"verbatim": "ok", "near": "ok", "none": "bad", "no_quote": "mute"}[outcome]
    return f'<span class="check {cls}">{text}</span>'


# ------------------------------------------------------------------------------------------------ the explorer
def graph_panel(g: dict, pitch: str, qa: str, key: str, active: bool) -> str:
    dom_of = {pid: d for d in g.get("domains") or [] for pid in d["premise_ids"]}
    tested: dict[str, list[dict]] = {}
    for x in (g.get("challenge") or {}).get("exchanges") or []:
        for t in x.get("targets") or []:
            tested.setdefault(t, []).append(x)
    out = [f'<div class="panel{" active" if active else ""}" data-key="{key}">']
    sc = g["meta"]["source_check"]
    dropped = len(g["meta"].get("dropped_links") or [])
    out.append(f'<p class="muted">Model: <b>{escape(g["meta"]["model"])}</b>. {len(g["premises"])} premises in {len(g.get("domains") or [])} domains, '
               f'{len(g.get("links") or [])} stated link{"" if len(g.get("links") or []) == 1 else "s"}{f" ({dropped} invalid link(s) dropped by the validator)" if dropped else ""}. '
               f'Quoted passages found in the transcript: {sc["verbatim"] + sc["near"]} of {sc["quoted"]}.</p>')
    name = key.split("|")[0]
    out.append(f'<figure>{fg.network(g, title=f"Theory graph of a fictional pitch ({name})")}</figure>')
    out.append('<details class="cards-detail"><summary>Every premise and link with its quoted passage</summary>')
    out.append('<div class="domains">')
    seen = []
    for d in g.get("domains") or []:
        seen.append(d["id"])
        out.append(f'<section class="domain"><h4>{escape(d["name"])}</h4>')
        for pid in d["premise_ids"]:
            p = next(x for x in g["premises"] if x["id"] == pid)
            st = p.get("status")
            out.append(f'<article class="premise" style="--c:{fg.STATUS_COLOR.get(st, fg.GREY)}"><div class="pid">{escape(pid)}</div><div class="pbody"><p>{escape(p["text"])}</p>'
                       f'<div class="meta">{chip("status", st, STATUS_LABEL, fg.STATUS_COLOR)}{check_badge(p["evidence_span_check"]["outcome"])}</div>')
            qs = tested.get(pid)
            if qs:
                out.append('<div class="meta">' + "".join(f'<span class="qtag">tested in {escape(x["id"])}: {chip("r", x["response"], RESPONSE_LABEL, fg.RESPONSE_COLOR)}</span>' for x in qs) + "</div>")
            cue = f'<p class="q"><b>Why this status:</b> {escape(p.get("status_reason", ""))}' + (f' “{escape(p["status_span"])}” {check_badge(p["status_span_check"]["outcome"])}' if p.get("status_span") else "") + "</p>"
            out.append(f'<details><summary>Passage in the transcript</summary><p class="q">“{escape(p["evidence_span"])}”</p>{cue}</details></div></article>')
        out.append("</section>")
    out.append("</div>")
    links = g.get("links") or []
    out.append('<h4>Dependences the speaker states</h4>')
    if links:
        out.append("<ul class='plain'>" + "".join(
            f'<li><b>{escape(l["from"])} → {escape(l["to"])}</b> (cue “{escape(l["cue"] or "withheld")}”) {check_badge(l["evidence_span_check"]["outcome"])}<br><span class="q">“{escape(l["evidence_span"])}”</span></li>' for l in links) + "</ul>")
    else:
        out.append('<p class="muted">None recorded. Zero is a valid answer: the codebook asks for a link only where the speaker states one.</p>')
    ex = (g.get("challenge") or {}).get("exchanges") or []
    out.append('<h4>Stage 2 pass, tried on this pitch: what the judges’ questions tested</h4><ul class="plain">')
    for x in ex:
        tgt = ", ".join(x["targets"]) if x["targets"] else f'a condition not in the premise list (<i>{escape((x.get("new_condition", "") or "").rstrip(".?")) or "description withheld"}</i>)'
        out.append(f'<li><b>{escape(x["id"])}</b> tests {tgt}. Response: {chip("r", x["response"], RESPONSE_LABEL, fg.RESPONSE_COLOR)}'
                   f'<br><span class="q">Q: “{escape(x["question_span"])}” {check_badge(x["question_span_check"]["outcome"])}</span>'
                   + (f'<br><span class="q">A: “{escape(x["answer_span"])}” {check_badge(x["answer_span_check"]["outcome"])}</span>' if x.get("answer_span") else "") + "</li>")
    out.append("</ul></details>")
    out.append(f'<details><summary>The fictional pitch and Q&amp;A text</summary><p class="q">{escape(pitch)}</p><p class="q"><i>Q&amp;A:</i> {escape(qa)}</p></details>')
    out.append("</div>")
    return "".join(out)


def explorer() -> str:
    m = MODELS[0]
    out = ['<div class="tabs" id="explorer"><div class="tabrow" role="tablist" aria-label="Pitch">']
    for i, (n, label) in enumerate(FICTIONAL.items()):
        out.append(f'<button type="button" class="tab{" on" if i == 0 else ""}" data-group="pitch" data-val="{n}">{escape(label)}</button>')
    out.append("</div>")
    for n in FICTIONAL:
        pitch, qa = load_example(n, EXAMPLES / "pitches")
        out.append(graph_panel(read_json(RESULTS / "graphs" / f"{n}__{m}.json"), pitch, qa or "", f"{n}|{m}", n == "brinelog"))
    out.append("</div>")
    return "".join(out)


def real_graph(cid: str) -> dict:
    """A real pitch as a GPT-4o-mini theory graph from the 375-pitch coding: the frozen premise list, its value statement
    and its domains from the same run. Quoted passages are not part of the shared data."""
    fz = pd.read_csv(DERIVED / "frozen_premises_gpt4omini.csv", keep_default_na=False)
    fz = fz[fz.case_id == cid]
    vs = pd.read_csv(DERIVED / "value_statements.csv", keep_default_na=False).set_index("case_id")
    g = {"premises": [{"id": r.premise_id, "text": r.text or "(statement withheld: repeats the transcript)"} for r in fz.itertuples()],
         "value": [{"id": "V1", "text": vs.loc[cid, "text"]}] if vs.loc[cid, "text"] else []}
    gr = pd.read_csv(DERIVED / "groupings_long.csv")
    gr = gr[(gr.grouper == "within_gpt4omini") & (gr.case_id == cid) & (gr.run == int(fz.consensus_run.iloc[0]))]
    g["domains"] = [{"id": f"D{i + 1}", "name": n, "premise_ids": list(gr[gr.group == n].premise_id)} for i, n in enumerate(dict.fromkeys(gr.group))]
    return g


def real_figure(cid: str, *, lead: str = "") -> str:
    cases = pd.read_csv(DERIVED / "cases.csv", dtype=str).set_index("case_id")
    vs = pd.read_csv(REPO / "data" / "video_sources.csv", dtype=str, keep_default_na=False)
    v = vs[(vs.case_id == cid) & (vs.segment == "PITCH")]
    name = f'{escape(cases.loc[cid, "company"])}, {escape(cases.loc[cid, "event"])}'
    link = f' (<a href="{escape(v.iloc[0].video_url)}">public recording</a>)' if len(v) and v.iloc[0].video_url else ""
    g = real_graph(cid)
    svg = fg.network(g, title="Theory graph of " + cases.loc[cid, "company"])
    return (f'<figure class="hero">{svg}'
            f'<figcaption>{lead}<b>{name}</b>{link}, read by GPT-4o-mini: {len(g["premises"])} premises in {len(g["domains"])} strategic domains. '
            'Hover a node for its full text. Quoted passages of real pitches are in the public recording, not in this repository.</figcaption></figure>')


# ------------------------------------------------------------------------------------------------ page
CSS = """
:root{--ink:#1d2430;--mute:#55606e;--rule:#d5d9e0;--bg:#fff;--soft:#f5f7fa;--link:#0b5cad;--accent:#0072B2}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;color:var(--ink);background:var(--bg);font:17px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--link)}header,main,footer{max-width:960px;margin:0 auto;padding:0 20px}
header{padding-top:34px}h1{font-size:2.1rem;margin:.1em 0 .15em;letter-spacing:-.01em}
h2{font-size:1.45rem;margin:2.4em 0 .5em;padding-top:.6em;border-top:1px solid var(--rule)}h3{font-size:1.15rem;margin:1.8em 0 .4em}h4{margin:1.1em 0 .3em;font-size:1rem}h5{margin:.8em 0 .2em}
.sub{font-size:1.1rem;color:var(--mute);margin:.2em 0 1em;max-width:46em}.muted{color:var(--mute)}
nav{position:sticky;top:0;background:#fffffff2;border-bottom:1px solid var(--rule);padding:8px 20px;z-index:5;font-size:.9rem}
nav a{margin-right:16px;text-decoration:none;white-space:nowrap}nav .in{max-width:960px;margin:0 auto;overflow-x:auto}
.kicker{color:var(--mute);font-size:.9rem;margin:0 0 .4em}header .sub{font-size:1.2rem;color:var(--ink);max-width:44em}
.hero{border:1px solid var(--rule);border-radius:12px;padding:12px 14px;background:#fff}
.glance{background:var(--soft);border:1px solid var(--rule);border-radius:10px;padding:6px 18px;margin:18px 0}.glance p{margin:.6em 0 .2em}.glance ul{margin:.2em 0 .8em;padding-left:18px}.glance li{margin:4px 0}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:18px 0}
.card{background:var(--soft);border:1px solid var(--rule);border-radius:10px;padding:14px 16px}
.card .big{font-size:1.9rem;font-weight:700;line-height:1.1;color:var(--accent)}.card p{margin:.4em 0 0;font-size:.95rem}
.note{background:var(--soft);border-left:4px solid var(--accent);padding:10px 14px;margin:16px 0;border-radius:0 8px 8px 0}
.warn{border-left-color:#D55E00}
table.t{border-collapse:collapse;width:100%;font-size:.92rem;margin:14px 0}table.t th,table.t td{border-bottom:1px solid var(--rule);padding:6px 8px;text-align:left;vertical-align:top}
table.t th{background:var(--soft);font-weight:600}table.t caption{caption-side:top;text-align:left;color:var(--mute);padding:4px 0;font-size:.9rem}
table.compare tr.diff td{background:#fff6e6}
.chip{display:inline-block;border-radius:999px;padding:1px 9px;font-size:.78rem;font-weight:600;color:#fff;background:var(--c);white-space:nowrap}
.check{font-size:.78rem;border-radius:4px;padding:1px 6px;margin-left:4px;white-space:nowrap}.check.ok{background:#e3f4ec;color:#0a6b46}.check.bad{background:#fde7e1;color:#a23b0a}.check.mute{background:#eceff3;color:var(--mute)}
.tabrow{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0}.tab{font:inherit;font-size:.9rem;border:1px solid var(--rule);background:#fff;border-radius:999px;padding:5px 13px;cursor:pointer}.tab.on{background:var(--accent);border-color:var(--accent);color:#fff}
.js .panel{display:none}.js .panel.active{display:block}.panel{border-top:1px solid var(--rule);margin-top:10px;padding-top:6px}
.domains{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}.domain{border:1px solid var(--rule);border-radius:10px;padding:8px 12px;background:#fff}.domain h4{margin:.2em 0 .5em}
.premise{display:flex;gap:10px;border-left:5px solid var(--c);padding:6px 0 6px 10px;margin:8px 0;background:var(--soft);border-radius:0 8px 8px 0}.pid{font-weight:700;color:var(--mute);min-width:2.2em}
.pbody p{margin:0 0 4px;font-size:.95rem}.meta{display:flex;flex-wrap:wrap;gap:4px;align-items:center;margin:3px 0}.qtag{font-size:.8rem}
details{margin:4px 0;font-size:.9rem}summary{cursor:pointer;color:var(--link)}.q{color:#3b4656;font-size:.9rem;margin:.3em 0}
ul.plain{padding-left:18px}ul.plain li{margin:6px 0}.value{background:#eef6fb;padding:8px 12px;border-radius:8px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
figure{margin:18px 0}figcaption{color:var(--mute);font-size:.9rem;margin-top:4px}
code,pre{font-family:ui-monospace,Consolas,Menlo,monospace;font-size:.88rem}pre{background:#0f1720;color:#e8edf3;padding:12px 14px;border-radius:8px;overflow-x:auto}
.crit td:first-child{font-weight:600;white-space:nowrap}footer{padding:30px 20px 60px;color:var(--mute);font-size:.88rem}
@media print{nav{display:none}.js .panel{display:block!important}.tabrow{display:none}body{font-size:12pt}}
"""

JS = """
document.documentElement.classList.add('js');
(function(){var root=document.getElementById('explorer');if(!root)return;var sel={pitch:'brinelog',model:'gpt-4o-mini'};
function show(){root.querySelectorAll('.panel').forEach(function(p){p.classList.toggle('active',p.dataset.key===sel.pitch+'|'+sel.model)});
root.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('on',sel[t.dataset.group]===t.dataset.val)})}
root.querySelectorAll('.tab').forEach(function(t){t.addEventListener('click',function(){sel[t.dataset.group]=t.dataset.val;show()})});show()})();
"""


def build_site() -> Path:
    A = read_json(RESULTS / "audit.json")
    pcn, grp, scx = A["premise_counts"], A["grouping"], A["source_check"]
    like = pcn["single_run_like_for_like"]
    sc_ari = grp["self_consistency"]
    bt = grp["between_groupers"]
    fgv = bt["fu_grok47__fu_gemini"]
    gp, gk, cl = scx["gpt4omini"], scx["grok47"], scx["claude_catalogue"]
    n_calls = len(list((EXAMPLES / "cache").glob("*.json")))
    validity = read_json(DERIVED / "schema_validity.json")

    # figure 1: same coder again versus a different coder
    fig1 = fg.dotplot([
        ("Premise count per pitch: rank correlation (Spearman)", [
            {"label": "Same model, run again (GPT-4o-mini, Grok 4.7)", "value": like["same_model_runs_mean_spearman"], "color": fg.GREEN},
            {"label": "Different model, same pitches", "value": like["different_models_mean_spearman"], "color": fg.VERM}]),
        ("Grouping of the same premises: adjusted Rand index per pitch (0 = chance)", [
            {"label": "GPT-4o-mini, free-form domains, run again", "value": sc_ari["within_gpt4omini"]["mean_ari"], "lo": sc_ari["within_gpt4omini"]["ci95"][0], "hi": sc_ari["within_gpt4omini"]["ci95"][1], "color": fg.GREEN},
            {"label": "Grok 4.7, ten fixed labels, run again", "value": sc_ari["fu_grok47"]["mean_ari"], "lo": sc_ari["fu_grok47"]["ci95"][0], "hi": sc_ari["fu_grok47"]["ci95"][1], "color": fg.GREEN},
            {"label": "Grok vs Gemini, same ten labels", "value": fgv["mean_ari"], "lo": fgv["ci95"][0], "hi": fgv["ci95"][1], "color": fg.VERM},
            {"label": "GPT free-form vs Grok ten labels", "value": bt["within_gpt4omini__fu_grok47"]["mean_ari"], "lo": bt["within_gpt4omini__fu_grok47"]["ci95"][0], "hi": bt["within_gpt4omini__fu_grok47"]["ci95"][1], "color": fg.VERM},
            {"label": "GPT free-form vs GPT three tags", "value": bt["within_gpt4omini__dfv_gpt4omini"]["mean_ari"], "lo": bt["within_gpt4omini__dfv_gpt4omini"]["ci95"][0], "hi": bt["within_gpt4omini__dfv_gpt4omini"]["ci95"][1], "color": fg.VERM}])],
        x_min=0.0, x_max=1.0, x_label="agreement (higher is better; bars are 95% bootstrap intervals over pitches)",
        title="Agreement of a model with itself and with another model",
        desc="Dot plot. Run again, the same model agrees closely with itself on premise counts and on grouping. Different models agree little on either.")
    # standalone copies of the two figures used in the proposal
    figdir = REPO / "docs" / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    hero_g = real_graph(HERO_CASE)
    (figdir / "figure1_theory_graph.svg").write_text(fg.standalone(fg.network(hero_g, title="A founder's value theory as a theory graph (GPT-4o-mini)"), width=960), encoding="utf-8", newline="\n")
    (figdir / "figure2_audit.svg").write_text(fg.standalone(fig1, width=760), encoding="utf-8", newline="\n")
    (figdir / "figure2_architecture.svg").write_text(fg.standalone(fg.architecture(), width=960), encoding="utf-8", newline="\n")
    vals = list(grp["fu_grok_vs_gemini_per_pitch"].values())
    fig2 = fg.histogram(vals, lo=-0.4, hi=1.0, bins=14, x_label="adjusted Rand index between Grok and Gemini, one value per pitch", marks={"median %.2f" % fgv["median_ari"]: fgv["median_ari"]},
                        title="Distribution of grouping agreement between two models", desc=f"Histogram over {len(vals)} pitches. Most values are near zero.")

    def row(m, d):
        return (f"<tr><td>{m}</td><td>{d['premises']:,}</td><td>{d['with_quote']:,}</td><td>{d['verbatim']:,}</td><td>{d['near']:,}</td><td>{d['not_found']:,}</td><td>{d['no_quote']:,}</td></tr>")

    srows = row("GPT-4o-mini (3 runs)", gp) + row("Grok 4.7 (3 runs)", gk) + row("Claude, 71-type catalogue (1 run)", cl)
    n_pit = A["headline"]["pitches"]
    flagged, dropped_total = [], 0
    for n in FICTIONAL:
        for m in MODELS:
            g = read_json(RESULTS / "graphs" / f"{n}__{m}.json")
            dropped_total += len(g["meta"].get("dropped_links") or [])
            for kind, items, keys in (("premise passage", g["premises"], ["evidence_span"]), ("status cue", g["premises"], ["status_span"]),
                                      ("link passage", g.get("links") or [], ["evidence_span"])):
                for it in items:
                    for k in keys:
                        if (it.get(f"{k}_check") or {}).get("outcome") == "none":
                            flagged.append(f"{m} on {n}, {kind}: “{escape(it[k])}”")
    flagged_html = (f"{len(flagged)} quoted passages in the six graphs are not in the transcript and are flagged: " + "; ".join(flagged[:3]) + ("; and others." if len(flagged) > 3 else ".")
                    + " The check does not tell us whether other passages were misread.") if flagged else "No quoted passage in the six graphs failed the check."
    ari_self = sc_ari["within_gpt4omini"]
    alpha1 = pcn["self_consistency"]["gpt4omini"]["alpha_single_run"]
    alpha3 = pcn["self_consistency"]["gpt4omini"]["alpha_median_of_3_spearman_brown"]
    gallery = "".join(real_figure(c) for c in GALLERY)
    arch = fg.architecture()
    st, oc = A["structure"], A["outcomes"]
    ND = read_json(RESULTS / "decomposability.json")
    sv, sims, bd = ND["survival"], ND["similarity"], ND["breadth"]
    sm = sv["models"]["main"]
    surv_rows = "".join(
        f"<tr><td>{escape(r['label'])}</td><td>β = {r['b']:+.2f} (odds ratio {r['odds_ratio_per_sd']:.2f})</td><td>p = {r['p']:.3f}, n = {r['n']}</td></tr>"
        for k, r in sv["models"].items())
    dom_mean = st["domains_per_pitch"]["mean"]

    def desc_row(label, d, share=False):
        v = (lambda x: pct(x)) if share else (lambda x: f"{x:.1f}" if x != int(x) else f"{x:.0f}")
        return f"<tr><td>{label}</td><td>{v(d['mean'])} ({v(d['sd'])})</td><td>{v(d['median'])} [{v(d['min'])}–{v(d['max'])}]</td></tr>"

    dist_txt = " / ".join(pct(st["domains_distribution"].get(k, 0)) for k in ("1", "2", "3", "4", "5+"))
    multi = 1 - st["domains_distribution"].get("1", 0)

    html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Theory Graph: making entrepreneurs’ value theories observable with AI</title>
<meta name="description" content="Prototype: a language model reads the value theory behind a startup pitch into a checkable graph of premises, strategic domains, stated dependences and evidence.">
<style>{CSS}</style></head><body>
<nav><div class="in"><a href="#top">The idea</a><a href="#why">1 What becomes observable</a><a href="#graph">2 Explore a theory graph</a><a href="#done">3 Results so far</a><a href="#audit">4 Can it be trusted?</a><a href="#next">5 Next steps and limits</a><a href="#repro">6 Reproduce</a><a href="#data">7 Data, ethics, AI use</a></div></nav>
<header id="top"><p class="kicker">Stage 1 prototype · <i>Organization Science</i> special issue “AI-Assisted Frontiers in Organizational Science”</p>
<h1>The Theory Graph</h1>
<p class="sub">What theories of value do founders actually hold, and are they built to be revised one part at a time? The theory-based view says entrepreneurs should hold and test such theories, but what founders hold has been out of view. The theory graph uses AI to read them from founders’ own words: {n_pit} pitches so far, every element traceable to the passage it comes from.</p></header>
<main>
{real_figure(HERO_CASE, lead="A real founder pitch as a theory graph. ")}
<p class="muted">Read it left to right. Each premise is something the founder treats as necessary for the venture to create value. Premises that would have to be revised together form a strategic domain, and the domains feed the value the pitch promises.</p>
<div class="glance"><p><b>In four lines.</b></p><ul>
<li><b>The question.</b> The theory-based view casts entrepreneurs as theorists, and training experiments show that testing a theory helps. But what theories do founders hold untrained? How broad are they, and are they near-decomposable (Simon, 1962): built so that one part can be revised without rebuilding the whole?</li>
<li><b>What AI makes possible.</b> Startup Battlefield is a rare record: {n_pit} founders (2009–2023) each state a whole value theory in the same six-minute format to expert judges, and what became of the venture is visible years later. A language model reads each pitch into a theory graph with a fixed codebook, three times. By hand this stops at a few cases.</li>
<li><b>First answers.</b> Theories are modular: {pct(multi)} span two or more strategic domains. Two features of their architecture go with survival: breadth, with survival highest at about {bd['turning_point']:.0f} premises, and clearer separation between domains. Both are exploratory: hypotheses for Stage 2.</li>
<li><b>Why trust it.</b> Every element quotes its source passage, which is checked against the transcript; every reading is repeated; a human benchmark follows in Stage 2. Code, prompts and derived data are open, and one command rebuilds every number on this page.</li></ul></div>
<div class="cards">
<div class="card"><div class="big">≈{bd['turning_point']:.0f}</div><p>premises is where survival peaks (the average theory has {st['premises_per_pitch']['mean']:.1f}): predicted {pct(bd['predicted_survival']['4'])} at 4 premises, {pct(bd['predicted_survival']['10'])} at 10, lower beyond (inverted U, p = {bd['lind_mehlum_p']:.2f}; exploratory).</p></div>
<div class="card"><div class="big">{st['domains_per_pitch']['mean']:.1f}</div><p>strategic domains in the theory read from an average pitch; {pct(multi)} of theories span two or more: they are modular.</p></div>
<div class="card"><div class="big">{sm['odds_ratio_per_sd']:.2f}×</div><p>odds of survival per standard deviation of domain separation: more near-decomposable theories survived more often (p = {sm['p']:.2f}; exploratory).</p></div>
<div class="card"><div class="big">{pct(gp['share_verbatim'], 1)}</div><p>of {gp['premises']:,} quoted passages occur word for word in the transcript; domain groupings reproduce across runs (adjusted Rand index {f2(ari_self['mean_ari'])}).</p></div>
</div>

<h2 id="why">1. What becomes observable</h2>
<p>The theory-based view holds that entrepreneurs who form and test theories of value make better decisions, and field experiments that train founders to do so support it (Camuffo et al., 2020; Agarwal et al., 2023). What untrained founders’ theories look like has stayed out of view. They are implicit and surface mainly in how founders talk, and coding them by hand does not scale beyond a few ventures. A language model can read a founder’s words with a fixed codebook, quote the passage behind each element, and do so for thousands of ventures. A construct that has been theorised becomes one that can be measured.</p>
<table class="t crit"><thead><tr><th>What we measure</th><th>Why it matters for theory</th></tr></thead><tbody>
<tr><td>Premises and breadth</td><td>What a founder treats as necessary for value creation, and how many: narrow theories leave blind spots, broad ones are hard to test.</td></tr>
<tr><td>Strategic domains</td><td>Which premises would be revised together if one failed. Near-decomposable theories (Simon) allow modular, targeted learning.</td></tr>
<tr><td>Stated links (Stage 2)</td><td>Which premise the founder says depends on which: the causal structure as the founder asserts it, not as we estimate it.</td></tr>
<tr><td>Evidential status (Stage 2)</td><td>Whether a premise is backed by evidence, planned, marked as uncertain, or only asserted: where the theory has been tested and where it is a bet.</td></tr>
<tr><td>Change (Stage 2)</td><td>Which premises are kept, qualified or dropped as evidence arrives, read from a venture’s dated updates: learning, observed.</td></tr>
<tr><td>Challenge (Stage 2)</td><td>Which premises the judges question in the Q&amp;A, and how founders respond: how a theory holds up under scrutiny.</td></tr>
</tbody></table>
<h3>The architecture of a value theory</h3>
<p>A theory graph is hierarchical: premises come first, strategic domains group them, and the structure ends in the value the venture promises. A six-minute pitch yields one layer of domains, because there is little room to say more. In a separate analysis of the same pitches, the domains fall into four broader areas: the customer problem or pain point, the product mechanism, the money module, and the route to market. Longer texts, such as a venture’s dated updates, can support further layers, so the same instrument can show how deep a founder’s theory goes.</p>
<figure>{arch}<figcaption>The layers of a theory graph. Solid: what each pitch graph on this page shows, premises grouped into strategic domains. Dashed: higher layers of broader areas. Several domains can fall under one area, a theory may leave an area unaddressed, and longer texts can add further layers. In the pitches, one such layer has four areas (customer problem, product mechanism, money, route to market).</figcaption></figure>
<p><b>The questions we start with.</b> How broad is a founder’s theory, and how broad should it be? A narrow theory leaves conditions for value unexamined; a sprawling one is hard to test. And is it near-decomposable, in Simon’s sense: do premises depend on each other mainly within strategic domains, so that a failed premise forces a local revision rather than a new theory? And are ventures with more decomposable theories more likely to survive, as a theory of learning would predict? Section 3 gives first answers from the premises and domains; Stage 2 adds the dependencies founders state and the evidence they cite for each premise.</p>

<h2 id="graph">2. Explore a theory graph</h2>
<p>For real pitches we share the graph but not the founders’ words. To show every quoted passage, we wrote three <b>fictional</b> pitches and ran them through the same pipeline. Hover a node for its text; open the list below the graph to see each premise and link beside the passage it rests on and the result of the source check.</p>
{explorer()}
<details><summary>Two more real pitches as theory graphs</summary>{gallery}</details>

<h2 id="done">3. Results so far</h2>
<p>All numbers are GPT-4o mini readings, computed by <code>python -m theorygraph audit</code> from the shipped data (<code>results/audit.json</code>, <code>results/decomposability.json</code>). Only Tables 2 and 3 use venture outcomes.</p>
<table class="t res"><caption>Table 1. The structure of founders’ value theories: {n_pit} pitches</caption>
<thead><tr><th></th><th>Mean (SD)</th><th>Median [range]</th></tr></thead><tbody>
{desc_row('Premises per pitch (breadth)', st['premises_per_pitch'])}
{desc_row('Strategic domains per pitch', st['domains_per_pitch'])}
{desc_row('Premises per domain', st['premises_per_domain'])}
{desc_row('Share of a pitch’s premises in its largest domain', st['share_in_largest_domain'], share=True)}
<tr><td>Pitches with 1 / 2 / 3 / 4 / 5 or more domains</td><td colspan="2">{dist_txt}</td></tr>
</tbody></table>
<p>Premise counts are the median of three runs; domain statistics are over the {st['pitch_runs']:,} pitch-runs. Domains are found with a co-revision test (“if this premise failed, which others would have to change?”), so no taxonomy is imposed on the founder.</p>
<p><b>What we read from it.</b> Founders’ theories are compact but not monolithic: the median pitch spreads {st['premises_per_pitch']['median']:.0f} premises over {st['domains_per_pitch']['median']:.0f} domains, and the largest domain holds about half of them; a single-domain theory is rare ({pct(st['domains_distribution'].get('1', 0), 1)} of pitch-runs).</p>
<h3>How broad should a theory be?</h3>
<p>A narrow theory leaves conditions for value unexamined; a sprawling one is hard to test and to revise. Breadth is the number of premises (median of three runs).</p>
<table class="t res"><caption>Table 2. Theory breadth and venture survival</caption>
<thead><tr><th></th><th>Estimate</th><th>Test</th></tr></thead><tbody>
<tr><td>Breadth (premises)</td><td>β = {bd['b_premises']:+.2f}</td><td>p = {bd['p_premises']:.3f}</td></tr>
<tr><td>Breadth squared</td><td>β = {bd['b_premises_sq']:+.3f}</td><td>p = {bd['p_premises_sq']:.3f}</td></tr>
<tr><td>Inverted U over the observed range ({bd['range'][0]}–{bd['range'][1]} premises)</td><td>peak at {bd['turning_point']:.1f} premises [{bd['turning_point_ci95'][0]:.1f}, {bd['turning_point_ci95'][1]:.1f}]</td><td>Lind–Mehlum p = {bd['lind_mehlum_p']:.3f}, n = {bd['n']}</td></tr>
<tr><td>Predicted survival at 4 / 7 / 10 / 14 premises</td><td colspan="2">{' / '.join(pct(bd['predicted_survival'][k]) for k in ('4', '7', '10', '14'))}</td></tr>
<tr><td>Pitches with 4–5 / 6–9 / 10–12 / 13 or more premises</td><td colspan="2">{' / '.join(str(bd['pitches_by_premises'][k]) for k in ('4-5', '6-9', '10-12', '13+'))}</td></tr>
</tbody></table>
<p>Survival models: logit of the venture not being listed as closed by TechCrunch (August 2026), {sv['sample']['pitches']} pitches with at least {sv['sample']['min_words']} words, {sv['sample']['closed_techcrunch']} closed, standard errors clustered by event ({sv['sample']['events']} events). Controls: pitch length, year, US headquarters, healthcare, mean premise similarity. Every specification run is shown, here and in Table 3.</p>
<p><b>What we read from it.</b> Survival rises with breadth up to about {bd['turning_point']:.0f} premises and falls beyond. The rise is well covered by the data; the fall rests on few theories ({bd['pitches_by_premises']['13+']} pitches have 13 or more premises). Premise counts are also the most model-dependent measure (section 4), so this is a reading by GPT-4o mini, to be checked against the human benchmark in Stage 2.</p>
<h3>Are founders’ theories near-decomposable?</h3>
<p>Simon (1962) argued that complex systems that can adapt are <i>near-decomposable</i>: strong interactions within parts, weak ones between them. For a value theory this means premises hang together mainly inside a strategic domain, so a failed premise forces revision of its domain, not of the whole theory. We measure how clearly a theory separates into domains: the mean similarity of premises within a domain minus between domains. Premises within a domain are more similar than premises across domains in {pct(sims['tfidf']['share_positive'])} of pitches. We then ask whether clearer separation goes with survival, with the same sample, outcome and controls as Table 2; separation is standardised.</p>
<table class="t res"><caption>Table 3. Domain separation and venture survival</caption>
<thead><tr><th></th><th>Estimate</th><th>Test</th></tr></thead><tbody>
{surv_rows}
</tbody></table>

<p><b>What we read from it.</b> Ventures whose theories separate more cleanly into domains were more likely to stay open (odds ratio {sm['odds_ratio_per_sd']:.2f} per standard deviation), and this does not change when breadth and breadth squared or the number of domains are added. The association is weaker with an embedding-based measure of separation and rests on {sv['sample']['closed_techcrunch']} closures. We treat it as a hypothesis for Stage 2, not a finding. The direct test of near-decomposability, whether the dependencies founders state stay inside domains, needs the dependency pass on all pitches (Stage 2).</p>
<p><b>Next: evidence and the judges’ questions.</b> Two further passes are built and tested on the fictional pitches in section 2: one codes how each premise is supported and which dependencies the founder states; one records which premise each of the judges’ questions tests and how the founders respond. Running them on all pitches is Stage 2 work.</p>

<h2 id="audit">4. Can the measurement be trusted?</h2>
<p>A language model always returns a theory graph. The call asks when AI-enabled research is valid science and when it builds “Potemkin villages”. We answer that for our own instrument with three checks.</p>
<h3>Check 1: is every element anchored in what the founder said?</h3>
<p>For every premise the model must copy a passage from the transcript, and we check that the passage is there (after lower-casing and removing punctuation). Of {gp['with_quote']:,} passages, {gp['verbatim']:,} are found word for word, {gp['near']} with small differences, and {gp['not_found']} are not found and flagged. The check catches invented quotes; it does not show that a real passage was read correctly, which is what Check 3 is for.</p>
<h3>Check 2: run again, does it give the same theory?</h3>
<p>Yes. Each pitch was read three times. The number of premises per pitch is reliable across runs (Krippendorff’s α = {f2(alpha1)} for one run, {f2(alpha3)} for the median of three), and the grouping of premises into domains reproduces closely (adjusted Rand index {f2(ari_self['mean_ari'])}, 95% interval {f2(ari_self['ci95'][0])} to {f2(ari_self['ci95'][1])}; 0 is chance, 1 is identical).</p>
<h3>Check 3: is it close to trained human coders? (Stage 2)</h3>
<p>Two trained coders will code about 40 random pitches independently, following a written protocol (<code>benchmark/PROTOCOL.md</code>). Their agreement sets the ceiling for the model, and the human sample corrects regressions that use model-coded variables.</p>
<details><summary>Robustness: other models read the same pitches differently</summary>
<p>We also read the {n_pit} pitches with Grok 4.7, Claude and Qwen3-32B. Each is stable with itself, but models differ from each other: premise counts correlate {f2(min(v['spearman'] for v in pcn['between_models'].values()))} to {f2(max(v['spearman'] for v in pcn['between_models'].values()))} across models, and two models assigning the same premises to the same ten labels agree at {f2(fgv['mean_ari'])} (adjusted Rand index; shuffled baseline {f2(fgv['null_mean'])}). A theory graph is therefore reported with the model that produced it, and the human benchmark decides which reading is closest to trained coders.</p>
<figure>{fig1}<figcaption>Green: a model compared with its own repeat. Red: one model compared with another on the same {n_pit} pitches. Bars are 95% bootstrap intervals over pitches.</figcaption></figure></details>

<h2 id="next">5. Next steps and limits</h2>
<p><b>Stage 2.</b> (0) Test near-decomposability properly: run the dependency pass on all {n_pit} pitches, pre-register the survival model, and check in a venture’s dated updates whether revisions stay within a domain. (1) Run the human benchmark and report the model against it. (2) Test stronger and open-weight models on the same protocol. (3) Code the judges’ questions for all {n_pit} pitches. (4) Attempt the full roster of about 1,700 Battlefield pitches, as far as recordings can be obtained. (5) Apply the pipeline to a long text series, Buffer’s public shareholder updates, to observe how a theory changes.</p>
<p><b>Limits we state up front.</b></p>
<ul>
<li><b>No human benchmark yet.</b> Until it exists we know the reading is anchored and stable, not that it matches trained coders; other models read pitches differently (section 4).</li>
<li><b>Pitches are persuasion.</b> They show espoused theories, not private beliefs; the judges’ questions show how those theories hold up.</li>
<li><b>The prompts for status, links and challenge are a first version</b>, written on three fictional pitches.</li>
<li><b>Pitches are short and flat</b> ({pcn['means']['gpt4omini']['mean_premises_per_pitch']:.1f} premises on average, one level of domains). Deeper structure needs longer sources.</li>
<li><b>Transcripts come from speech recognition</b> without speaker labels; transcription errors pass through to the coding.</li>
<li><b>The survival result is exploratory.</b> One association, {sv['sample']['closed_techcrunch']} closures on TechCrunch’s listing ({oc['techcrunch'].get('closed', 0)} of {n_pit} ventures), observational, and weaker with an embedding-based measure. The listing can miss closures.</li>
<li><b>Public prompts differ from the as-run prompts</b> only in leaving out three third-party transcripts used as worked examples; <code>prompts/README.md</code> gives the hash of each.</li>
</ul>

<h2 id="repro">6. Reproduce</h2>
<pre>pip install -r requirements.txt
python -m theorygraph verify            # shipped data, hashes and counts agree
python -m theorygraph audit             # sections 3 and 4, from data/derived/
python -m theorygraph run all --model gpt-4o-mini    # replays stored replies offline
python -m theorygraph site              # rebuilds this page

# your own model, any OpenAI-compatible server (a local one included)
export THEORYGRAPH_BASE_URL=http://localhost:11434/v1
python -m theorygraph run brinelog --live --model &lt;name&gt;</pre>
<p>Replay refuses to guess: if the request differs from a stored one by a single character, it stops and says so.</p>

<h2 id="data">7. Data, ethics and use of AI</h2>
<ul>
<li><b>Shared:</b> the codings of {n_pit} pitches (premise statements, groupings, quote checks, similarity measures), value statements, each venture’s TechCrunch status, the prompts and their hashes, the three fictional pitches with every model reply, code, and tests.</li>
<li><b>Not shared:</b> transcripts, quoted passages of real pitches, and Crunchbase fields (exact dates, funding), which are licensed. Public video links and cut times (<code>data/video_sources.csv</code>) plus <code>data/rebuild_transcripts.py</code> let anyone with the right to process the videos rebuild transcripts.</li>
<li><b>People.</b> Pitches are public performances at a startup competition. We do not code or release any characteristic of the presenters. Company names appear only to identify the public recording.</li>
<li><b>Risks we see.</b> Mislabeling a founder’s reasoning in a way that travels as fact; we therefore show every output beside its quote and its check, and <code>LIMITATIONS.md</code> separates what is measured from what is only planned.</li>
<li><b>Use of AI.</b> A language model does the reading under study, and that is what is checked. A language-model coding assistant (in Cursor) helped write the code and the text of this page. The numbers are generated from the stored results, not typed; the authors are responsible for the content (<code>AI_USE.md</code>).</li>
</ul>
</main>
<footer><p>Built from <code>results/audit.json</code> (SHA-256 {sha(RESULTS / 'audit.json')[:16]}…) and <code>results/decomposability.json</code> ({sha(RESULTS / 'decomposability.json')[:16]}…). Code under the MIT licence; derived data under CC BY 4.0. See <code>DATA_CARD.md</code>, <code>ETHICS.md</code>, <code>LIMITATIONS.md</code>.</p></footer>
<script>{JS}</script></body></html>"""
    out = REPO / "docs" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(html.encode("utf-8"))
    (REPO / "docs" / ".nojekyll").write_text("", encoding="utf-8")
    return out
