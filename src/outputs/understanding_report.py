"""Derived views of the understanding artifact: Markdown and self-contained HTML.

Renderers read only the artifact (requirement E). They add no claims, and they keep each finding's
kind and generator visible. Charts degrade gracefully: without matplotlib the report is still
complete, with a note in place of each chart (requirement F).
"""
from __future__ import annotations

import base64
import html as _h
import io
from typing import Any

PLURAL = {"observation": "observations", "interpretation": "interpretations", "hypothesis": "hypotheses",
          "action": "suggested actions", "question": "open questions"}
KIND_LABEL = {"observation": "Observation", "interpretation": "Interpretation", "hypothesis": "Hypothesis",
              "action": "Suggested action", "question": "Open question"}


def _label(text: str, n: int = 28) -> str:
    """Chart label: truncated, with $ escaped so matplotlib does not read it as maths notation."""
    return str(text)[:n].replace("$", r"\$")


def _md(text: Any) -> str:
    """Escape user-controlled text for Markdown (tables, HTML passthrough, code spans)."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace("|", "\\|").replace("`", "\\`"))


def _fmt(v: Any) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.4g}" if abs(v) < 1e6 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


# ---------------------------------------------------------------- charts
def _plt():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except Exception:  # pragma: no cover - exercised by the degradation test via monkeypatch
        return None


INK, MUTED, ACCENT = "#2b2f36", "#8a9099", "#3b6fb6"


def _img(fig, plt) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=INK, labelsize=8)


def column_chart(col: dict, plt) -> str | None:
    st = col.get("stats", {})
    t = col["semantic"]["type"]
    if plt is None:
        return None
    if "numeric" in st and st["numeric"].get("histogram") and t not in ("binary", "boolean"):
        h = st["numeric"]["histogram"]
        fig, ax = plt.subplots(figsize=(4.2, 1.9))
        e = h["edges"]
        ax.bar(e[:-1], h["counts"], width=[e[i + 1] - e[i] for i in range(len(e) - 1)], align="edge", color=ACCENT, edgecolor="white", linewidth=0.4)
        ax.set_ylabel("rows", fontsize=8, color=MUTED)
        _style(ax)
        return _img(fig, plt)
    if "categorical" in st and st["categorical"].get("top"):
        top = st["categorical"]["top"]
        levels = st["categorical"]["levels"]
        top = top if levels <= 8 else top[:10]
        fig, ax = plt.subplots(figsize=(4.2, 0.28 * len(top) + 0.5))
        labels = [_label(x["value"]) for x in top][::-1]
        ax.barh(labels, [x["count"] for x in top][::-1], color=ACCENT)
        if levels > 8:
            ax.set_title(f"top 10 of {levels} levels", fontsize=8, color=MUTED, loc="left")
        _style(ax)
        return _img(fig, plt)
    if "temporal" in st and st["temporal"].get("monthly_counts"):
        mc = st["temporal"]["monthly_counts"]
        fig, ax = plt.subplots(figsize=(4.2, 1.9))
        ax.plot(list(range(len(mc))), list(mc.values()), color=ACCENT, marker="o", markersize=2.5, linewidth=1.2)
        ticks = list(range(0, len(mc), max(1, len(mc) // 6)))
        ax.set_xticks(ticks, [_label(list(mc)[i]) for i in ticks], rotation=0)
        ax.set_ylabel("rows / month", fontsize=8, color=MUTED)
        _style(ax)
        return _img(fig, plt)
    return None


def relation_chart(pair: dict, plt) -> str | None:
    g = pair.get("groups")
    if plt is None or not g or not g["rows"]:
        return None
    rows = g["rows"][::-1]
    fig, ax = plt.subplots(figsize=(4.2, 0.28 * len(rows) + 0.6))
    ax.barh([_label(r["group"]) for r in rows], [r["value"] for r in rows], color=ACCENT)
    ax.set_xlabel(_label(g["measure"], 80), fontsize=8, color=MUTED)
    _style(ax)
    return _img(fig, plt)


# ---------------------------------------------------------------- markdown
def to_markdown(a: dict) -> str:
    L: list[str] = []
    ds = a["dataset"]
    L += [f"# Data Guide: {_md(ds['source'])}", "",
          f"{ds['rows']:,} rows × {ds['columns']} columns · fingerprint `{ds['fingerprint'][:12]}` · schema `{a['schema']}`", "",
          "Every finding names its kind and who produced it. **rule** means deterministic rules; **human** means the annotations file. "
          "There is no AI-generated text.", ""]
    L += ["## What this data cannot tell us", ""]
    reg = a["register"]
    ru = reg["row_unit"]
    L.append(f"- **Row unit:** {_md(ru['value']) + ' (human)' if ru.get('value') else 'not stated'}")
    gp = reg["generating_process"]
    L.append(f"- **How rows were produced:** {_md(gp['value']) + ' (human)' if gp.get('value') else 'not stated'}")
    L.append(f"- **Why values are missing:** {reg['missingness_mechanism']}")
    if reg.get("candidate_keys"):
        L.append(f"- **Candidate keys (measured):** {', '.join(reg['candidate_keys'][:5])}")
    L.append("")
    u = a["usefulness"]
    L += ["## Usefulness", ""]
    if u["status"] == "unassessed":
        L += [f"**Unassessed.** {u['reason']}", ""]
    else:
        for k in ("question", "decision", "target"):
            if u.get(k):
                L.append(f"- **{k.title()} (human):** {_md(u[k])}")
        L += ["", u["note"], ""]
    byk: dict[str, list] = {}
    for f in a["findings"]:
        byk.setdefault(f["kind"], []).append(f)
    L += ["## Findings", ""]
    for k in ("observation", "interpretation", "hypothesis", "action", "question"):
        fs = byk.get(k, [])
        if not fs:
            continue
        L += [f"### {PLURAL[k].capitalize()} ({len(fs)}): {a['kind_meaning'][k]}", ""]
        for f in fs:
            tag = f"`{f['generator']}`" + (" · `target`" if f.get("relevance") == "target" else "")
            L.append(f"- {_md(f['statement'])} {tag} <sub>{f['id']}</sub>")
        L.append("")
    rel = a["relations"]
    L += ["## Relations", "",
          f"{rel['considered']} candidate pairs among {rel['eligible_columns']} columns; {rel['screened']} computed (budget {rel['budget']}); "
          + (f"left out: {'; '.join(x['column'] + ' (' + x['reason'] + ')' for x in rel['excluded_columns'][:8])}; " if rel['excluded_columns'] else "") + f"showing the strongest {len(rel['top'])} (negligible effects omitted). {rel['caution']}", "",
          "| columns | measure | effect | strength | n |", "|---|---|---|---|---|"]
    for p in rel["top"]:
        L.append(f"| {_md(' × '.join(p['columns']))} | {p['method']} | {p['effect']} | {p['strength']} | {p['n']} |")
    L += ["", "## Data dictionary", ""]
    for name, c in a["columns"].items():
        sem = c["semantic"]
        meaning = c["meaning"] or "_not stated_"
        L += [f"### {_md(name)}", "",
              f"- **Meaning:** {_md(meaning)}" + (" (human)" if c["meaning"] else ""),
              f"- **Type:** {sem['type']} ({sem['source']}, confidence {sem['confidence']}): {'; '.join(sem['reasons'])}",
              f"- **Non-null:** {c['count'] - c['nulls']:,} of {c['count']:,} · distinct {c['distinct']:,}",
              f"- **Examples:** {_md(', '.join(c['examples'][:5]))}"]
        num = c.get("stats", {}).get("numeric")
        if num:
            L.append(f"- **Distribution:** median {_fmt(num['median'])}, IQR {_fmt(num['p25'])}–{_fmt(num['p75'])}, "
                     f"range {_fmt(num['min'])}–{_fmt(num['max'])}, skew {_fmt(num['skew'])}")
        L.append("")
    pv = a["provenance"]
    L += ["## Provenance", "", f"- {pv['tool']} {pv['tool_version']} · annotations: {pv['annotations']['file'] or 'none'}"
          + (f" (`{pv['annotations']['sha256'][:12]}`)" if pv['annotations']['sha256'] else ""), f"- {pv['generators']}", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- html
CSS = """
:root{--bg:#fbfaf7;--panel:#ffffff;--ink:#22262c;--muted:#6b7280;--line:#e6e2da;--accent:#3b6fb6;
--obs:#3b6fb6;--int:#7a5cad;--hyp:#b7791f;--act:#2f855a;--que:#c0392b;--human:#0f766e}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15171a;--panel:#1d2024;--ink:#e8e6e1;--muted:#9aa1ab;--line:#2c3036;
--accent:#7aa7e8;--obs:#7aa7e8;--int:#b39ddb;--hyp:#e0b25a;--act:#68c08f;--que:#ef7f72;--human:#4fd1c5}}
:root[data-theme="dark"]{--bg:#15171a;--panel:#1d2024;--ink:#e8e6e1;--muted:#9aa1ab;--line:#2c3036;--accent:#7aa7e8;--obs:#7aa7e8;
--int:#b39ddb;--hyp:#e0b25a;--act:#68c08f;--que:#ef7f72;--human:#4fd1c5}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 "Iowan Old Style","Charter",Georgia,serif}
main{max-width:1060px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:28px;margin:0 0 4px;letter-spacing:-.01em}h2{font:600 13px/1.2 ui-sans-serif,system-ui,sans-serif;text-transform:uppercase;
letter-spacing:.12em;color:var(--muted);margin:40px 0 12px;border-top:1px solid var(--line);padding-top:16px}
.meta,.small,table,code,.tag,nav{font-family:ui-sans-serif,system-ui,sans-serif}.meta{color:var(--muted);font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:16px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
.stat b{display:block;font:600 22px ui-sans-serif,system-ui,sans-serif}.stat span{font:12px ui-sans-serif,system-ui,sans-serif;color:var(--muted)}
.unknown{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--que);border-radius:8px;padding:12px 16px}
.unknown li{margin:4px 0}.finding{display:flex;gap:10px;align-items:baseline;padding:8px 0;border-bottom:1px solid var(--line)}
.tag{font-size:11px;font-weight:600;border-radius:999px;padding:1px 8px;border:1px solid currentColor;white-space:nowrap}
.observation{color:var(--obs)}.interpretation{color:var(--int)}.hypothesis{color:var(--hyp)}.action{color:var(--act)}.question{color:var(--que)}
.gen-human{color:var(--human)}.gen-rule{color:var(--muted)}.target{color:var(--accent)}
.fid{font:11px ui-monospace,monospace;color:var(--muted);margin-left:auto;white-space:nowrap}
details{background:var(--panel);border:1px solid var(--line);border-radius:8px;margin:10px 0;padding:0 14px}
summary{cursor:pointer;padding:10px 0;font-family:ui-sans-serif,system-ui,sans-serif}summary code{font-weight:600}
.cols{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;padding-bottom:12px}
@media (max-width:720px){.cols{grid-template-columns:1fr}.finding{flex-wrap:wrap}.fid{margin-left:0}}
table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid var(--line);padding:5px 6px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600}img{max-width:100%;height:auto;border-radius:4px;background:#fff}
.scroll{overflow-x:auto}.legend{font-size:13px;color:var(--muted);font-family:ui-sans-serif,system-ui,sans-serif}
nav{font-size:13px;margin-top:10px}nav a{color:var(--accent);margin-right:12px;text-decoration:none}
"""


def _finding_html(f: dict) -> str:
    tags = f'<span class="tag {f["kind"]}">{KIND_LABEL[f["kind"]]}</span>'
    gen = f'<span class="tag gen-{f["generator"]}">{f["generator"]}</span>'
    tgt = '<span class="tag target">target</span>' if f.get("relevance") == "target" else ""
    return f'<div class="finding">{tags}<div>{_h.escape(f["statement"])}</div>{gen}{tgt}<span class="fid">{f["id"]}</span></div>'


def to_html(a: dict) -> str:
    plt = _plt()
    e = _h.escape
    ds, reg, u = a["dataset"], a["register"], a["usefulness"]
    counts = a["summary"]["findings_by_kind"]
    out = [f"<main><h1>Data Guide: {e(ds['source'])}</h1>",
           f"<div class='meta'>{ds['rows']:,} rows × {ds['columns']} columns · fingerprint <code>{ds['fingerprint'][:12]}</code> · "
           f"schema <code>{e(a['schema'])}</code></div>",
           "<nav><a href='#unknown'>Unknowns</a><a href='#findings'>Findings</a><a href='#relations'>Relations</a><a href='#dictionary'>Dictionary</a></nav>",
           "<div class='grid'>" + "".join(f"<div class='stat'><b class='{k}'>{counts[k]}</b><span>{PLURAL[k]}</span></div>" for k in counts) + "</div>",
           "<p class='legend'>Each finding shows its kind and its source: <b>rule</b> (deterministic rules) or <b>human</b> (the annotations file). "
           "Nothing here is AI-written. Observations are measured; interpretations and hypotheses may be wrong; questions need a person.</p>"]
    ru, gp = reg["row_unit"], reg["generating_process"]
    items = [f"<li><b>Row unit:</b> {e(ru['value']) + ' <span class=tag gen-human>human</span>' if ru.get('value') else 'not stated'}</li>",
             f"<li><b>How rows were produced:</b> {e(gp['value']) + ' <span class=tag gen-human>human</span>' if gp.get('value') else 'not stated'}</li>",
             f"<li><b>Why values are missing:</b> {e(reg['missingness_mechanism'])}</li>"]
    if reg.get("candidate_keys"):
        items.append(f"<li><b>Candidate keys (measured):</b> {e(', '.join(reg['candidate_keys'][:5]))}</li>")
    out.append("<h2 id='unknown'>What this data cannot tell us</h2><div class='unknown'><ul>" + "".join(items) + "</ul></div>")
    out.append("<h2>Usefulness</h2>")
    if u["status"] == "unassessed":
        out.append(f"<p><b>Unassessed.</b> {e(u['reason'])}</p>")
    else:
        out.append("<ul>" + "".join(f"<li><b>{k.title()}</b> <span class='tag gen-human'>human</span> {e(u[k])}</li>"
                                    for k in ("question", "decision", "target") if u.get(k)) + f"</ul><p class='legend'>{e(u['note'])}</p>")
    out.append("<h2 id='findings'>Findings</h2>")
    for k in ("question", "hypothesis", "interpretation", "action", "observation"):
        fs = [f for f in a["findings"] if f["kind"] == k]
        if fs:
            out.append(f"<h3 class='{k}' style='font:600 15px ui-sans-serif,system-ui,sans-serif;margin:20px 0 4px'>{PLURAL[k].capitalize()} "
                       f"<span class='meta'>· {e(a['kind_meaning'][k])}</span></h3>" + "".join(_finding_html(f) for f in fs))
    rel = a["relations"]
    out.append(f"<h2 id='relations'>Relations</h2><p class='legend'>{rel['considered']} candidate pairs among {rel['eligible_columns']} columns; "
               f"{rel['screened']} computed (target pairs first, budget {rel['budget']}), {rel['not_computed_budget']} left for a larger budget. "
               + (f"Left out: {e('; '.join(x['column'] + ' (' + x['reason'] + ')' for x in rel['excluded_columns'][:8]))}. " if rel['excluded_columns'] else "") +
               f"showing the strongest {len(rel['top'])} (pairs with a negligible effect are omitted). {e(rel['caution'])}</p><div class='scroll'><table><tr><th>columns</th><th>measure</th>"
               "<th>effect</th><th>strength</th><th>n</th></tr>"
               + "".join(f"<tr><td>{e(' × '.join(p['columns']))}</td><td>{p['method']}</td><td>{p['effect']}</td><td>{p['strength']}</td><td>{p['n']}</td></tr>"
                         for p in rel["top"]) + "</table></div>")
    shown = {tuple(p["columns"]): p for p in (rel.get("target_pairs") or []) + rel["top"]}
    charts = [(p, relation_chart(p, plt)) for p in list(shown.values())[:4]]
    charts = [(p, c) for p, c in charts if c]
    if charts:
        out.append("<div class='cols'>" + "".join(f"<figure style='margin:0'><img alt='{e(p['groups']['measure'])} by {e(p['groups']['by'])}' src='{c}'>"
                                                 f"<figcaption class='legend'>{e(p['groups']['measure'])} by {e(p['groups']['by'])} ({p['method']} {p['effect']})</figcaption></figure>"
                                                 for p, c in charts) + "</div>")
    out.append("<h2 id='dictionary'>Data dictionary</h2>")
    fid = {f["id"]: f for f in a["findings"]}
    for name, c in a["columns"].items():
        sem = c["semantic"]
        chart = column_chart(c, plt)
        rows = [("Meaning", (e(c["meaning"]) + " <span class='tag gen-human'>human</span>") if c["meaning"] else "<i>not stated</i>"),
                ("Type", f"{e(sem['type'])} <span class='tag gen-{'human' if sem['source'] == 'human' else 'rule'}'>{sem['source']}</span> "
                         f"confidence {e(str(sem['confidence']))}<br><span class='legend'>{e('; '.join(sem['reasons']))}"
                         + (f" · alternatives: {e(', '.join(sem['alternatives']))}" if sem.get("alternatives") else "") + "</span>"),
                ("Non-null", f"{c['count'] - c['nulls']:,} of {c['count']:,} ({1 - (c['null_rate'] or 0):.0%})"),
                ("Distinct", f"{c['distinct']:,}"), ("Examples", e(", ".join(c["examples"][:5])))]
        num = c.get("stats", {}).get("numeric")
        if num:
            rows.append(("Distribution", f"median {_fmt(num['median'])} · IQR {_fmt(num['p25'])}–{_fmt(num['p75'])} · range {_fmt(num['min'])}–"
                                         f"{_fmt(num['max'])} · skew {_fmt(num['skew'])}"))
        tem = c.get("stats", {}).get("temporal")
        if tem:
            rows.append(("Coverage", f"{e(tem['min'][:10])} to {e(tem['max'][:10])} · {tem['months_covered']} months"))
        table = "<table>" + "".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows) + "</table>"
        fl = "".join(_finding_html(fid[i]) for i in c["findings"] if i in fid)
        img = f"<img alt='distribution of {e(name)}' src='{chart}'>" if chart else ("<p class='legend'>Chart unavailable (matplotlib not installed).</p>" if plt is None else "")
        badge = f" <span class='tag question'>{sum(1 for i in c['findings'] if fid.get(i, {}).get('kind') == 'question')} open</span>" \
            if any(fid.get(i, {}).get("kind") == "question" for i in c["findings"]) else ""
        out.append(f"<details><summary><code>{e(name)}</code> · {e(sem['type'])} · {len(c['findings'])} findings{badge}</summary>"
                   f"<div class='cols'><div>{table}</div><div>{img}</div></div>{fl}</details>")
    pv = a["provenance"]
    out.append(f"<h2>Provenance</h2><p class='legend'>{e(pv['tool'])} {e(pv['tool_version'])} · annotations: {e(str(pv['annotations']['file'] or 'none'))}"
               + (f" (<code>{pv['annotations']['sha256'][:12]}</code>)" if pv["annotations"]["sha256"] else "") + f"<br>{e(pv['generators'])}</p></main>")
    title = e(f"Data Guide · {ds['source']}")
    return (f"<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{CSS}</style></head><body>" + "\n".join(out) + "</body></html>\n")
