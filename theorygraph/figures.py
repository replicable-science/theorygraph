"""Small inline-SVG charts, written by hand so that the page needs no plotting library and no network.

Every chart carries <title> and <desc> for screen readers and prints its numbers as text, so the figure
can be read without colour. Colours are the Okabe-Ito palette (distinguishable with common colour-vision deficiency).
"""
from __future__ import annotations

import textwrap
from html import escape

BLUE, SKY, GREEN, ORANGE, VERM, GREY, INK, RULE = "#0072B2", "#56B4E9", "#009E73", "#E69F00", "#D55E00", "#8a8f98", "#1d2430", "#d5d9e0"
STATUS_COLOR = {"evidence_cited": BLUE, "expected": GREEN, "speculative": ORANGE, "asserted": GREY}
RESPONSE_COLOR = {"defends": BLUE, "qualifies": SKY, "concedes": VERM, "deflects": ORANGE, "no_answer": GREY}


def _svg(w: int, h: int, title: str, desc: str, body: str) -> str:
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-labelledby="t d" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="system-ui, -apple-system, Segoe UI, Roboto, sans-serif" font-size="13">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>{body}</svg>')


def dotplot(groups: list[tuple[str, list[dict]]], *, x_min: float, x_max: float, title: str, desc: str, x_label: str,
            label_w: int = 330, width: int = 760, row_h: int = 30) -> str:
    """Cleveland dot plot. groups = [(group title, [{label, value, lo, hi, color}])]."""
    plot_w = width - label_w - 70
    top = 28
    y = top
    parts = []

    def X(v: float) -> float:
        return label_w + (v - x_min) / (x_max - x_min) * plot_w

    ticks = [t / 10 for t in range(int(x_min * 10), int(x_max * 10) + 1, 2)]
    total_rows = sum(len(r) for _, r in groups) + len(groups) * 0.9
    height = int(top + total_rows * row_h + 52)
    for t in ticks:
        parts.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{top - 8}" y2="{height - 38}" stroke="{RULE}" stroke-width="1"/>')
        parts.append(f'<text x="{X(t):.1f}" y="{height - 20}" text-anchor="middle" fill="#55606e">{t:.1f}</text>')
    parts.append(f'<text x="{label_w + plot_w / 2:.0f}" y="{height - 4}" text-anchor="middle" fill="#55606e">{escape(x_label)}</text>')
    for gtitle, rows in groups:
        parts.append(f'<text x="0" y="{y + 14}" font-weight="600" fill="{INK}">{escape(gtitle)}</text>')
        y += int(row_h * 0.9)
        for r in rows:
            cy = y + row_h / 2 - 6
            parts.append(f'<text x="14" y="{cy + 4:.1f}" fill="{INK}">{escape(r["label"])}</text>')
            if r.get("lo") is not None:
                parts.append(f'<line x1="{X(r["lo"]):.1f}" x2="{X(r["hi"]):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="{r["color"]}" stroke-width="2.5"/>')
            parts.append(f'<circle cx="{X(r["value"]):.1f}" cy="{cy:.1f}" r="6" fill="{r["color"]}"/>')
            parts.append(f'<text x="{X(r["value"]) + 11:.1f}" y="{cy + 4:.1f}" fill="{INK}" font-weight="600">{r["value"]:.2f}</text>')
            y += row_h
    return _svg(width, height, title, desc, "".join(parts))


def histogram(values: list[float], *, lo: float, hi: float, bins: int, title: str, desc: str, x_label: str, marks: dict[str, float] | None = None,
              width: int = 760, height: int = 250, color: str = BLUE) -> str:
    left, right, top, bottom = 48, 16, 20, 52
    pw, ph = width - left - right, height - top - bottom
    step = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        i = min(max(int((v - lo) / step), 0), bins - 1)
        counts[i] += 1
    cmax = max(counts)
    parts = []
    for k in range(0, 5):
        yv = cmax * k / 4
        yy = top + ph - ph * k / 4
        parts.append(f'<line x1="{left}" x2="{left + pw}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="{RULE}"/>')
        parts.append(f'<text x="{left - 6}" y="{yy + 4:.1f}" text-anchor="end" fill="#55606e">{int(round(yv))}</text>')
    for i, c in enumerate(counts):
        x0 = left + i * pw / bins
        bh = ph * c / cmax if cmax else 0
        parts.append(f'<rect x="{x0 + 1:.1f}" y="{top + ph - bh:.1f}" width="{pw / bins - 2:.1f}" height="{bh:.1f}" fill="{color}"/>')
    for t in [lo + step * i for i in range(0, bins + 1, 2)]:
        xx = left + (t - lo) / (hi - lo) * pw
        parts.append(f'<text x="{xx:.1f}" y="{top + ph + 18}" text-anchor="middle" fill="#55606e">{(0.0 if abs(t) < 1e-9 else t):.1f}</text>')
    parts.append(f'<text x="{left + pw / 2:.0f}" y="{height - 6}" text-anchor="middle" fill="#55606e">{escape(x_label)}</text>')
    parts.append(f'<text x="14" y="{top + ph / 2:.0f}" transform="rotate(-90 14 {top + ph / 2:.0f})" text-anchor="middle" fill="#55606e">pitches</text>')
    for name, v in (marks or {}).items():
        xx = left + (v - lo) / (hi - lo) * pw
        parts.append(f'<line x1="{xx:.1f}" x2="{xx:.1f}" y1="{top - 4}" y2="{top + ph}" stroke="{VERM}" stroke-width="2" stroke-dasharray="5 4"/>')
        parts.append(f'<text x="{xx + 8:.1f}" y="{top - 6}" fill="{VERM}" font-weight="600">{escape(name)}</text>')
    return _svg(width, height, title, desc, "".join(parts))


def stacked_bars(bars: list[tuple[str, dict[str, float]]], *, colors: dict[str, str], labels: dict[str, str], title: str, desc: str,
                 width: int = 760, bar_h: int = 34, label_w: int = 130) -> str:
    """Horizontal 100 % stacked bars. bars = [(row label, {category: share})]; shares are printed inside the segments."""
    pw = width - label_w - 20
    height = 30 + len(bars) * (bar_h + 14) + 46
    parts = []
    y = 14
    for name, shares in bars:
        parts.append(f'<text x="0" y="{y + bar_h / 2 + 4:.1f}" fill="{INK}">{escape(name)}</text>')
        x = label_w
        for cat, s in shares.items():
            if not s:
                continue
            w = pw * s
            parts.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{bar_h}" fill="{colors[cat]}"/>')
            if w > 38:
                parts.append(f'<text x="{x + w / 2:.1f}" y="{y + bar_h / 2 + 4:.1f}" text-anchor="middle" fill="#fff" font-weight="600">{s * 100:.0f}%</text>')
            x += w
        y += bar_h + 14
    lx = label_w
    for cat in labels:
        parts.append(f'<rect x="{lx}" y="{y + 8}" width="12" height="12" fill="{colors[cat]}"/>')
        parts.append(f'<text x="{lx + 17}" y="{y + 19}" fill="{INK}">{escape(labels[cat])}</text>')
        lx += 22 + 8 * len(labels[cat])
    return _svg(width, height, title, desc, "".join(parts))


STATUS_NAME = {"evidence_cited": "evidence cited", "expected": "expected", "speculative": "speculative", "asserted": "asserted"}


def _wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(text, width=width) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" ,.;") + "\u2026"
    return lines


def theory_graph(graph: dict, *, title: str, width: int = 980, cols: int = 3) -> str:
    """One theory graph: a box per domain, a card per premise (colour and word give the evidential status), arrows for stated links.

    Premises are shown as written by the model. Nothing here is a transcript passage.
    """
    prem = {p["id"]: p for p in graph["premises"]}
    domains = [dict(d) for d in (graph.get("domains") or [])]
    seen = {pid for d in domains for pid in d["premise_ids"]}
    loose = [pid for pid in prem if pid not in seen]
    if loose:
        domains.append({"id": "D?", "name": "Not grouped", "premise_ids": loose})
    gap, pad = 16, 12
    box_w = (width - (cols + 1) * gap) / cols
    wrap_chars = int((box_w - pad * 2 - 30) / 6.1)
    value = (graph.get("value") or [{}])[0].get("text", "")
    top = 20
    parts = []
    if value:
        vl = _wrap("Value the pitch promises: " + value, int((width - 2 * gap) / 6.4), 2)
        parts.append(f'<rect x="{gap}" y="{top}" width="{width - 2 * gap}" height="{16 + 17 * len(vl)}" rx="6" fill="#f5f7fa" stroke="{RULE}"/>')
        for i, ln in enumerate(vl):
            parts.append(f'<text x="{gap + 10}" y="{top + 22 + 17 * i}" fill="{INK}" font-weight="{600 if i == 0 else 400}">{escape(ln)}</text>')
        top += 16 + 17 * len(vl) + 16
    # card geometry
    cards = {}
    boxes = []
    for d in domains:
        h = 34
        rows = []
        for pid in d["premise_ids"]:
            if pid not in prem:
                continue
            lines = _wrap(prem[pid]["text"], wrap_chars, 3)
            rh = 24 + 15 * len(lines) + 6
            rows.append((pid, lines, rh))
            h += rh + 6
        boxes.append((d, rows, h + 4))
    col_y = [top] * cols
    placed = []
    for d, rows, h in boxes:
        c = min(range(cols), key=lambda k: col_y[k])
        x = gap + c * (box_w + gap)
        placed.append((d, rows, h, x, col_y[c]))
        col_y[c] += h + gap
    for d, rows, h, x, y in placed:
        parts.append(f'<rect x="{x:.1f}" y="{y}" width="{box_w:.1f}" height="{h}" rx="8" fill="#fff" stroke="{RULE}" stroke-width="1.5"/>')
        parts.append(f'<text x="{x + pad:.1f}" y="{y + 22}" font-weight="600" fill="{INK}">{escape(_wrap(d["name"], int((box_w - 2 * pad) / 6.6), 1)[0])}</text>')
        yy = y + 34
        for pid, lines, rh in rows:
            st = prem[pid].get("status") or "asserted"
            col = STATUS_COLOR.get(st, GREY)
            parts.append(f'<rect x="{x + pad:.1f}" y="{yy}" width="{box_w - 2 * pad - 20:.1f}" height="{rh}" rx="4" fill="#fafbfc" stroke="{RULE}"/>')
            parts.append(f'<rect x="{x + pad:.1f}" y="{yy}" width="5" height="{rh}" rx="2" fill="{col}"/>')
            parts.append(f'<text x="{x + pad + 12:.1f}" y="{yy + 16}" font-size="11.5" font-weight="600" fill="{col}">{escape(pid)} \u00b7 {STATUS_NAME.get(st, st)}</text>')
            for i, ln in enumerate(lines):
                parts.append(f'<text x="{x + pad + 12:.1f}" y="{yy + 32 + 15 * i}" font-size="12" fill="{INK}">{escape(ln)}</text>')
            cards[pid] = (x + box_w - pad - 20, yy + rh / 2, x + pad, d["id"])
            yy += rh + 6
    # links
    defs = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
    for l in graph.get("links") or []:
        a, b = cards.get(l["from"]), cards.get(l["to"])
        if a and b:
            if a[3] == b[3]:
                parts.append(f'<path d="M{a[0]:.1f},{a[1]:.1f} h14 V{b[1]:.1f} h-14" fill="none" stroke="{INK}" stroke-width="1.6" marker-end="url(#ah)"/>')
            else:
                parts.append(f'<path d="M{a[0] + 0:.1f},{a[1]:.1f} C{a[0] + 40:.1f},{a[1]:.1f} {b[0] + 40:.1f},{b[1]:.1f} {b[0] + 2:.1f},{b[1]:.1f}" fill="none" stroke="{INK}" stroke-width="1.6" marker-end="url(#ah)"/>')
        elif a:
            parts.append(f'<text x="{a[0] + 4:.1f}" y="{a[1] + 4:.1f}" font-size="11" fill="{INK}">\u2192 value</text>')
    height = max(col_y) + 44
    lx = gap
    ly = max(col_y) + 6
    for st in ("evidence_cited", "expected", "speculative", "asserted"):
        parts.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{STATUS_COLOR[st]}"/>')
        parts.append(f'<text x="{lx + 17}" y="{ly + 11}" font-size="12" fill="{INK}">{STATUS_NAME[st]}</text>')
        lx += 22 + int(len(STATUS_NAME[st]) * 6.6) + 22
    parts.append(f'<text x="{lx + 10}" y="{ly + 11}" font-size="12" fill="#55606e">arrow: a dependence the speaker states</text>')
    desc = (f"{len(prem)} premises in {len(domains)} domains, each shaded by evidential status; "
            f"{len(graph.get('links') or [])} stated dependence(s) drawn as arrows.")
    return _svg(width, height, title, desc, defs + "".join(parts))


RESPONSE_NAME = {"defends": "defends", "qualifies": "qualifies", "concedes": "concedes", "deflects": "deflects", "no_answer": "no answer"}


def network(graph: dict, *, title: str, width: int = 960, questions: bool = False) -> str:
    """A theory graph drawn as a network, read left to right: premises feed the strategic domains they belong to,
    and domains feed the value the pitch promises. Arrows on the left are dependences the founder states between premises.
    With questions=True, the experts' questions are drawn as a further column pointing at the premises they test.
    Hover a node for its full text."""
    prem = {p["id"]: p for p in graph["premises"]}
    has_status = any(p.get("status") for p in graph["premises"])
    domains = [dict(d) for d in (graph.get("domains") or [])]
    seen = {pid for d in domains for pid in d["premise_ids"]}
    loose = [pid for pid in prem if pid not in seen]
    if loose:
        domains.append({"id": "D?", "name": "Not grouped", "premise_ids": loose})
    value = (graph.get("value") or [{}])[0].get("text", "")
    exchanges = ((graph.get("challenge") or {}).get("exchanges") or []) if questions else []
    QX, CX, CW, DX, DW, VX = (46, 150, 320, 560, 172, 792) if questions else (0, 70, 370, 530, 182, 782)
    VW = width - VX - 8
    wrap = int((CW - 28) / 6.4)
    top = 44
    nodes, edges, over = [], [], []
    card = {}
    y = top
    for di, d in enumerate(domains):
        ys = []
        for pid in d["premise_ids"]:
            if pid not in prem:
                continue
            p = prem[pid]
            st = p.get("status") if has_status else None
            col = STATUS_COLOR.get(st, GREY) if has_status else "#5b7896"
            tag = f"{escape(pid)} \u00b7 {STATUS_NAME.get(st, st).upper()}" if has_status else escape(pid)
            lines = _wrap(p["text"], wrap, 3)
            h = 24 + 15 * len(lines)
            nodes.append(f'<g><title>{escape(pid)}' + (f' ({STATUS_NAME.get(st, st)})' if has_status else "") + f': {escape(p["text"])}</title>'
                         f'<rect x="{CX}" y="{y}" width="{CW}" height="{h}" rx="7" fill="#fff" stroke="{col}" stroke-width="1.6"/>'
                         f'<rect x="{CX}" y="{y}" width="6" height="{h}" rx="3" fill="{col}"/>'
                         f'<text x="{CX + 14}" y="{y + 15}" font-size="11" font-weight="700" fill="{col}">{tag}</text>'
                         + "".join(f'<text x="{CX + 14}" y="{y + 31 + 15 * i}" font-size="12.5" fill="{INK}">{escape(ln)}</text>' for i, ln in enumerate(lines)) + "</g>")
            card[pid] = (y + h / 2, col)
            ys.append(y + h / 2)
            y += h + 8
        d["_cy"] = sum(ys) / len(ys) if ys else y
        d["_lines"] = _wrap(d["name"], 22, 3)
        y += 14
    ghosts = []
    for x in exchanges:
        if not x.get("targets"):
            cond = (x.get("new_condition") or "").strip().rstrip(".?")
            lines = _wrap(f"Not in the pitch: {cond}" if cond else "A condition the pitch did not state", 46, 2)
            h = 14 + 15 * len(lines)
            nodes.append(f'<g><rect x="{CX}" y="{y}" width="{CW}" height="{h}" rx="7" fill="#fbfbfc" stroke="{GREY}" stroke-dasharray="5 4"/>'
                         + "".join(f'<text x="{CX + 14}" y="{y + 19 + 15 * i}" font-size="12" font-style="italic" fill="#55606e">{escape(ln)}</text>' for i, ln in enumerate(lines)) + "</g>")
            ghosts.append((x["id"], y + h / 2))
            y += h + 8
    bottom = y
    # domains: centred on their premises, pushed apart if they would overlap
    prev = top - 10
    for d in domains:
        h = 14 + 16 * len(d["_lines"])
        cy = max(d["_cy"], prev + h / 2 + 10)
        d["_cy"], d["_h"] = cy, h
        prev = cy + h / 2
    vlines = _wrap(value or "(no value statement)", 21, 7)
    vh = 40 + 16 * len(vlines)
    vy = sum(d["_cy"] for d in domains) / len(domains) if domains else top + vh / 2
    vy = max(vy, top + vh / 2)
    for d in domains:
        for pid in d["premise_ids"]:
            if pid in card:
                cy = card[pid][0]
                edges.append(f'<path d="M{CX + CW},{cy:.1f} C{CX + CW + 50},{cy:.1f} {DX - 50},{d["_cy"]:.1f} {DX},{d["_cy"]:.1f}" fill="none" stroke="#b9c1cc" stroke-width="1.6"/>')
        sw = 1.6 + 0.9 * sum(1 for pid in d["premise_ids"] if pid in card)
        edges.append(f'<path d="M{DX + DW},{d["_cy"]:.1f} C{DX + DW + 35},{d["_cy"]:.1f} {VX - 35},{vy:.1f} {VX},{vy:.1f}" fill="none" stroke="{BLUE}" stroke-opacity=".5" stroke-width="{sw:.1f}"/>')
        nodes.append(f'<g><title>Domain: {escape(d["name"])}</title><rect x="{DX}" y="{d["_cy"] - d["_h"] / 2:.1f}" width="{DW}" height="{d["_h"]}" rx="{min(18, d["_h"] / 2):.0f}" fill="#eaf3fa" stroke="{BLUE}" stroke-width="1.6"/>'
                     + "".join(f'<text x="{DX + DW / 2}" y="{d["_cy"] - d["_h"] / 2 + 22 + 16 * i:.1f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{INK}">{escape(ln)}</text>' for i, ln in enumerate(d["_lines"])) + "</g>")
    nodes.append(f'<g><title>Value: {escape(value)}</title><rect x="{VX}" y="{vy - vh / 2:.1f}" width="{VW}" height="{vh}" rx="12" fill="#0b3d63"/>'
                 f'<text x="{VX + VW / 2}" y="{vy - vh / 2 + 20:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" letter-spacing="1.5" fill="#9fc6e6">VALUE</text>'
                 + "".join(f'<text x="{VX + VW / 2}" y="{vy - vh / 2 + 40 + 16 * i:.1f}" text-anchor="middle" font-size="12.5" fill="#fff">{escape(ln)}</text>' for i, ln in enumerate(vlines)) + "</g>")
    # stated links
    for l in graph.get("links") or []:
        a = card.get(l["from"])
        if not a:
            continue
        if l["to"] in card:
            b = card[l["to"]][0]
            bulge = min(60, 26 + 0.12 * abs(b - a[0]))
            over.append(f'<path d="M{CX},{a[0]:.1f} C{CX - bulge:.1f},{a[0]:.1f} {CX - bulge:.1f},{b:.1f} {CX - 2},{b:.1f}" fill="none" stroke="{INK}" stroke-width="2" marker-end="url(#ah)"/>')
        else:
            edges.append(f'<path d="M{CX + CW},{a[0]:.1f} C{DX},{a[0] - 30:.1f} {VX - 120},{vy:.1f} {VX - 2},{vy:.1f}" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ah)"/>')
    # questions
    qs = []
    gh = dict(ghosts)
    for x in exchanges:
        ty = [card[t][0] for t in x.get("targets") or [] if t in card] or ([gh[x["id"]]] if x["id"] in gh else [])
        if ty:
            qs.append([sum(ty) / len(ty), x, ty])
    qs.sort(key=lambda q: q[0])
    prev = top - 20
    for q in qs:
        q[0] = max(q[0], prev + 34)
        prev = q[0]
    for qy, x, ty in qs:
        col = RESPONSE_COLOR.get(x.get("response"), GREY)
        for t in ty:
            edges.append(f'<path d="M{QX + 14},{qy:.1f} C{QX + 55},{qy:.1f} {CX - 45},{t:.1f} {CX},{t:.1f}" fill="none" stroke="{col}" stroke-width="1.8" stroke-opacity=".85"/>')
        nodes.append(f'<g><title>{escape(x["id"])}: the founders {escape(RESPONSE_NAME.get(x.get("response"), str(x.get("response"))))}</title>'
                     f'<rect x="{QX - 12}" y="{qy - 12:.1f}" width="24" height="24" rx="4" transform="rotate(45 {QX} {qy:.1f})" fill="{col}"/>'
                     f'<text x="{QX}" y="{qy + 4:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#fff">{escape(x["id"])}</text></g>')
        bottom = max(bottom, qy + 20)
    bottom = max(bottom, vy + vh / 2 + 8, max((d["_cy"] + d["_h"] / 2 for d in domains), default=0) + 8)
    heads = ([(QX, "middle", "QUESTIONS")] if questions else []) + [(CX, "start", "PREMISES"), (DX + DW / 2, "middle", "STRATEGIC DOMAINS"), (VX + VW / 2, "middle", "VALUE")]
    head = "".join(f'<text x="{x}" y="22" text-anchor="{a}" font-size="11" font-weight="700" letter-spacing="1.2" fill="#55606e">{t}</text>' for x, a, t in heads)
    ly = bottom + 18
    leg, lx = [], 0
    if has_status:
        for st in ("evidence_cited", "expected", "speculative", "asserted"):
            leg.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" rx="2" fill="{STATUS_COLOR[st]}"/><text x="{lx + 17}" y="{ly + 11}" font-size="12" fill="{INK}">{STATUS_NAME[st]}</text>')
            lx += 30 + int(len(STATUS_NAME[st]) * 6.8)
    if graph.get("links"):
        leg.append(f'<path d="M{lx + 4},{ly + 6} h26" stroke="{INK}" stroke-width="2" marker-end="url(#ah)"/><text x="{lx + 38}" y="{ly + 11}" font-size="12" fill="{INK}">dependence the founder states</text>')
    if not leg:
        ly -= 18
    ly2 = ly
    if questions:
        ly2 = ly + 22
        leg.append(f'<text x="0" y="{ly2 + 11}" font-size="12" fill="{INK}">Question; the founders:</text>')
        lx = 150
        for r in ("defends", "qualifies", "concedes", "deflects", "no_answer"):
            leg.append(f'<rect x="{lx + 1}" y="{ly2 + 1}" width="10" height="10" transform="rotate(45 {lx + 6} {ly2 + 6})" fill="{RESPONSE_COLOR[r]}"/><text x="{lx + 17}" y="{ly2 + 11}" font-size="12" fill="{INK}">{RESPONSE_NAME[r]}</text>')
            lx += 34 + int(len(RESPONSE_NAME[r]) * 6.8)
    height = int(ly2 + 26)
    defs = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
    desc = (f"Network of {len(prem)} premises in {len(domains)} strategic domains feeding the value the pitch promises; "
            f"{len(graph.get('links') or [])} stated dependence(s)" + (f"; {len(exchanges)} expert question(s) linked to the premises they test." if questions else "."))
    return _svg(width, height, title, desc, defs + head + "".join(edges) + "".join(nodes) + "".join(over) + "".join(leg))


def architecture(*, width: int = 960) -> str:
    """Generic schematic of the layers of a theory graph: premises, strategic domains, one or more higher layers, value.
    Several domains can fall under one higher-level area, and a theory need not cover every area."""
    top, row = 70, 30
    px, pw, dx, dw, ax, aw, vx, vw = 20, 140, 225, 165, 480, 175, 790, 150
    dom_of = [0, 0, 1, 1, 2, 3, 3, 3, 4, 4]
    area_of = [0, 0, 1, 2, 2]
    n_area = 4
    covered = set(area_of)
    ys = [top + i * row for i in range(len(dom_of))]
    nd = max(dom_of) + 1
    dys = [sum(ys[i] for i in range(len(dom_of)) if dom_of[i] == k) / dom_of.count(k) for k in range(nd)]
    span = ys[-1] - ys[0]
    ay = [ys[0] + 10 + i * (span - 20) / (n_area - 1) for i in range(n_area)]
    vy = (ys[0] + ys[-1]) / 2
    faint = "#c3c9d1"
    parts = []
    for i, y in enumerate(ys):
        parts.append(f'<path d="M{px + pw},{y} C{px + pw + 40},{y} {dx - 40},{dys[dom_of[i]]:.1f} {dx},{dys[dom_of[i]]:.1f}" fill="none" stroke="#b9c1cc" stroke-width="1.5"/>')
    for k, y in enumerate(dys):
        a = ay[area_of[k]]
        parts.append(f'<path d="M{dx + dw},{y:.1f} C{dx + dw + 45},{y:.1f} {ax - 45},{a:.1f} {ax},{a:.1f}" fill="none" stroke="{BLUE}" stroke-opacity=".45" stroke-width="2.5" stroke-dasharray="6 4"/>')
    mx = ax + aw + 40
    for k, y in enumerate(ay):
        on = k in covered
        parts.append(f'<path d="M{ax + aw},{y:.1f} C{ax + aw + 50},{y:.1f} {vx - 50},{vy:.1f} {vx},{vy:.1f}" fill="none" stroke="{BLUE if on else faint}" '
                     f'stroke-opacity="{".45" if on else "1"}" stroke-width="{3 if on else 1.5}" stroke-dasharray="6 4"/>')
    parts.append(f'<rect x="{mx - 8}" y="{vy - 18:.1f}" width="62" height="40" rx="6" fill="#fff"/>'
                 f'<text x="{mx + 23}" y="{vy + 2:.1f}" text-anchor="middle" font-size="22" font-weight="700" fill="#55606e">· · ·</text>'
                 f'<text x="{mx + 23}" y="{vy + 17:.1f}" text-anchor="middle" font-size="10" fill="#55606e">more layers</text>')
    for i, y in enumerate(ys):
        c = "#5b7896"
        parts.append(f'<rect x="{px}" y="{y - 11}" width="{pw}" height="22" rx="6" fill="#fff" stroke="{c}" stroke-width="1.5"/><rect x="{px}" y="{y - 11}" width="5" height="22" rx="2" fill="{c}"/>'
                     f'<text x="{px + 14}" y="{y + 4}" font-size="11.5" fill="{INK}">Premise {i + 1}</text>')
    for k, y in enumerate(dys):
        parts.append(f'<rect x="{dx}" y="{y - 15:.1f}" width="{dw}" height="30" rx="15" fill="#eaf3fa" stroke="{BLUE}" stroke-width="1.5"/>'
                     f'<text x="{dx + dw / 2}" y="{y + 4:.1f}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK}">Strategic domain {k + 1}</text>')
    for k, y in enumerate(ay):
        on = k in covered
        parts.append(f'<rect x="{ax}" y="{y - 19:.1f}" width="{aw}" height="38" rx="8" fill="{"#fff" if on else "#f6f7f9"}" stroke="{BLUE if on else faint}" stroke-width="1.5" stroke-dasharray="5 3"/>'
                     f'<text x="{ax + aw / 2}" y="{y + (0 if on else -2):.1f}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{INK if on else "#8a94a3"}">Higher-level area {"ABCD"[k]}</text>'
                     + (f'<text x="{ax + aw / 2}" y="{y + 13:.1f}" text-anchor="middle" font-size="10.5" fill="#55606e">{sum(1 for a in area_of if a == k)} domain{"s" if sum(1 for a in area_of if a == k) > 1 else ""}</text>' if on else
                        f'<text x="{ax + aw / 2}" y="{y + 12:.1f}" text-anchor="middle" font-size="10.5" fill="#8a94a3">not addressed in this theory</text>'))
    parts.append(f'<rect x="{vx}" y="{vy - 30:.1f}" width="{vw}" height="60" rx="12" fill="#0b3d63"/>'
                 f'<text x="{vx + vw / 2}" y="{vy - 10:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" letter-spacing="1.5" fill="#9fc6e6">VALUE</text>'
                 f'<text x="{vx + vw / 2}" y="{vy + 7:.1f}" text-anchor="middle" font-size="12.5" fill="#fff">what the venture</text>'
                 f'<text x="{vx + vw / 2}" y="{vy + 22:.1f}" text-anchor="middle" font-size="12.5" fill="#fff">promises</text>')
    def bracket(x0, x1, label, sub, dashed=False):
        dash = ' stroke-dasharray="5 3"' if dashed else ""
        return (f'<path d="M{x0},38 V30 H{x1} V38" fill="none" stroke="#55606e" stroke-width="1.3"{dash}/>'
                f'<text x="{(x0 + x1) / 2}" y="16" text-anchor="middle" font-size="12" font-weight="700" fill="{INK}">{escape(label)}</text>'
                f'<text x="{(x0 + x1) / 2}" y="{ys[-1] + 42}" text-anchor="middle" font-size="11.5" fill="#55606e">{escape(sub)}</text>')
    parts.append(bracket(px, dx + dw, "Read from each pitch", "premises grouped into strategic domains"))
    parts.append(bracket(ax, mx + 38, "Higher layers (one or more)", "several domains can share an area; some areas stay empty", dashed=True))
    height = ys[-1] + 58
    return _svg(width, height, "The layers of a theory graph",
                "Premises feed strategic domains. Domains can be grouped into one or more higher layers of broader areas: several domains can "
                "share an area, and a theory may leave some areas unaddressed. The top layer feeds the value the venture promises.", "".join(parts))


def standalone(svg: str, *, width: int, font: str = "Arial, Helvetica, sans-serif") -> str:
    """The inline figure with absolute size and a plain font, for a paper or slide."""
    import re
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    w, h = int(m.group(1)), int(m.group(2))
    out = svg.replace('width="100%"', f'width="{w}" height="{h}"', 1)
    out = re.sub(r'font-family="[^"]*"', f'font-family="{font}"', out, count=1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + out
