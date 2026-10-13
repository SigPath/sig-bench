"""Generator samodzielnego raportu HTML (bez zależności, inline CSS)."""
import html
from datetime import datetime
from typing import List

from .models import ModelResult

_CSS = """
:root { color-scheme: dark; }
body { background:#101418; color:#e8ebef; font-family: system-ui, sans-serif; margin:0; padding:40px 20px; }
main { max-width: 860px; margin: 0 auto; }
h1 { font-size: 26px; } h1 span { color:#ffb000; }
.meta { color:#9aa4b0; font-size: 13px; margin: 6px 0 26px; font-family: ui-monospace, monospace; }
table { width:100%; border-collapse: collapse; margin-bottom: 28px; }
th, td { text-align:left; padding:10px 12px; border-bottom:1px solid #2a333e; font-size:14px; }
thead th { font-family: ui-monospace, monospace; font-size:11px; text-transform:uppercase; letter-spacing:.1em; color:#9aa4b0; }
td.num { font-variant-numeric: tabular-nums; font-family: ui-monospace, monospace; }
.score-bar { height:8px; background:#2a333e; border-radius:4px; overflow:hidden; min-width:90px; }
.score-bar i { display:block; height:100%; background:#3ecf8e; }
.good { color:#3ecf8e; } .bad { color:#ff6b6b; }
.foot { color:#9aa4b0; font-size:12px; margin-top:30px; }
a { color:#ffb000; }
"""


def _esc(text: str, limit: int = 160) -> str:
    one_line = " ".join(text.split())
    return html.escape(one_line[:limit] + ("…" if len(one_line) > limit else ""))


def render_report(results: List[ModelResult], title: str = "SIG·BENCH") -> str:
    rows = []
    for r in results:
        bar = f'<span class="score-bar"><i style="width:{round(r.mean_score * 100)}%"></i></span>'
        rows.append(
            f"<tr><th>{html.escape(r.model)}</th>"
            f"<td class='num'>{r.mean_score * 100:.0f}%</td><td>{bar}</td>"
            f"<td class='num'>{r.mean_latency_s:.2f} s</td>"
            f"<td class='num'>{r.mean_tok_s:.1f}</td>"
            f"<td class='num'>{len(r.results)}</td></tr>"
        )

    details = []
    for r in results:
        items = "".join(
            f"<li><b>{html.escape(res.task)}</b> — "
            f"<span class='{'good' if res.score >= 0.5 else 'bad'}'>{res.score * 100:.0f}%</span> "
            f"({res.latency_s:.2f} s): <i>{_esc(res.output)}</i></li>"
            for res in r.results
        )
        details.append(f"<h2>{html.escape(r.model)}</h2><ul>{items}</ul>")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — raport</title><style>{_CSS}</style></head>
<body><main>
<h1><span>SIG·BENCH</span> — raport benchmarku lokalnych LLM</h1>
<p class="meta">wygenerowano {stamp} · {len(results)} modeli · 5 zadań PL (logika, tłumaczenie, wiedza, streszczenie, formatowanie)</p>
<table>
<thead><tr><th>Model</th><th>Wynik</th><th></th><th>Latencja</th><th>Tok/s</th><th>Próbki</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
{''.join(details)}
<p class="foot">Wygenerowane przez <a href="https://github.com/SigPath/sig-bench">SIG·BENCH</a> · Marcin Burda · burda.eu.org</p>
</main></body></html>"""
