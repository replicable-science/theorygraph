"""Command line: python -m theorygraph <command>.

  run NAME         build the theory graph for an example pitch (replays the stored replies; --live calls a model)
  sourcecheck F    check every quoted passage of a stored graph against its transcript
  audit            recompute stability, source check, robustness and near-decomposability
  site             rebuild docs/index.html from the stored results
  verify           check that shipped data and results are consistent (hashes, counts)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .util import EXAMPLES, RESULTS, REPO, read_json, write_json


def _run(args) -> int:
    from .llm import Chat, ReplayMiss
    from .passes import load_example, run_case

    root = EXAMPLES / "pitches"
    names = [args.name] if args.name != "all" else sorted(p.stem for p in root.glob("*.txt") if not p.stem.endswith(".qa"))
    chat = Chat(mode="live" if args.live else "replay", model=args.model, temperature=None if args.no_temperature else 0.0)
    for name in names:
        pitch, qa = load_example(name, root)
        try:
            graph = run_case(chat, name, pitch, qa)
        except ReplayMiss as e:
            print(f"[{name}] {e}", file=sys.stderr)
            return 2
        out = RESULTS / "graphs" / f"{name}__{args.model}.json"
        write_json(out, graph)
        sc = graph["meta"]["source_check"]
        print(f"[{name}] premises={len(graph['premises'])} domains={len(graph.get('domains') or [])} links={len(graph.get('links') or [])} "
              f"exchanges={len((graph.get('challenge') or {}).get('exchanges') or [])} quoted={sc['quoted']} supported={sc['share_supported']:.3f} "
              f"problems={len(graph['meta']['validation_problems'])} -> {out.relative_to(REPO)}")
    return 0


def _sourcecheck(args) -> int:
    from .sourcecheck import check_graph

    graph = read_json(args.graph)
    pitch = Path(args.pitch).read_text(encoding="utf-8")
    qa = Path(args.qa).read_text(encoding="utf-8") if args.qa else None
    print(json.dumps(check_graph(graph, pitch, qa), indent=2))
    return 0


def _audit(args) -> int:
    from .audit import run_audit

    res = run_audit()
    write_json(RESULTS / "audit.json", res)
    print(json.dumps(res["headline"], indent=2))
    from .decomposability import run_decomposability

    nd = run_decomposability()
    write_json(RESULTS / "decomposability.json", nd)
    m = nd["survival"]["models"]["main"]
    print(json.dumps({"separation_b": m["b"], "separation_p": m["p"]}, indent=2))
    return 0


def _site(args) -> int:
    from .site import build_site

    path = build_site()
    print(f"wrote {path.relative_to(REPO)}")
    return 0


def _verify(args) -> int:
    from .verify import verify_all

    problems = verify_all()
    for p in problems:
        print("PROBLEM:", p)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="theorygraph", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="build a theory graph for an example pitch")
    r.add_argument("name", help="example name (brinelog, lathework, recallpost) or 'all'")
    r.add_argument("--live", action="store_true", help="call a model instead of replaying stored replies")
    r.add_argument("--model", default="gpt-4o-mini")
    r.add_argument("--no-temperature", action="store_true", help="do not send a temperature (some models reject it)")
    r.set_defaults(fn=_run)
    s = sub.add_parser("sourcecheck", help="check the quoted passages of a graph")
    s.add_argument("graph")
    s.add_argument("pitch")
    s.add_argument("--qa")
    s.set_defaults(fn=_sourcecheck)
    a = sub.add_parser("audit", help="recompute the agreement audit from the shipped data")
    a.set_defaults(fn=_audit)
    w = sub.add_parser("site", help="rebuild docs/index.html")
    w.set_defaults(fn=_site)
    v = sub.add_parser("verify", help="check shipped data and results are consistent")
    v.set_defaults(fn=_verify)
    args = ap.parse_args(argv)
    return args.fn(args)
