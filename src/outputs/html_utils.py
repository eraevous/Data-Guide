from __future__ import annotations

import base64
import html as _html
import io

import matplotlib.pyplot as plt


def fig_to_base64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return f'<img src="data:image/png;base64,{encoded}" style="max-width:100%;">'


def wrap_html(body: str, title: str = "Data Guide Report") -> str:
    safe_title = _html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title}</title>
  <style>
    body {{ font-family: sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; color: #222; }}
    h1 {{ border-bottom: 2px solid #444; padding-bottom: .5rem; }}
    h2 {{ margin-top: 2rem; color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ccc; padding: .4rem .7rem; text-align: left; }}
    th {{ background: #f4f4f4; }}
    .section {{ margin-bottom: 2rem; }}
    img {{ display: block; margin: 1rem 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""
