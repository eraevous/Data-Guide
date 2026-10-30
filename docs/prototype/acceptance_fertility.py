"""Kate's prototype acceptance loop on an unfamiliar dataset (World Bank fertility rates, bundled with statsmodels).

1. Profile the raw table.  2. Pick a concern.  3. Apply one recorded transformation and annotation.
4. Re-profile and compare.  5. Say what changed, what is still unknown, what to look at next.

Run from the repo root:  python docs/prototype/acceptance_fertility.py OUT_DIR
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import statsmodels.datasets as sd  # noqa: E402

from understanding.workflow import compare, render_compare, understand  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else "acceptance-out")
raw = sd.fertility.load_pandas().data
understand(raw, source="fertility (raw, statsmodels)", out_dir=out / "1-raw")

# Step 3: the transformation answers the raw guide's suggested action (reshape) and drops the two
# constant columns it flagged. Missing values are kept as missing: nothing is imputed.
long = raw.drop(columns=["Indicator Name", "Indicator Code"]).melt(
    id_vars=["Country Name", "Country Code"], var_name="year", value_name="fertility_rate")
long["year"] = long["year"].astype(int)
(out / "annotations.yml").parent.mkdir(parents=True, exist_ok=True)
(out / "annotations.yml").write_text("""\
dataset:
  row_unit: one row per country-or-group and year
  description: World Bank total fertility rate (births per woman), 1960-2013, reshaped from wide to long
  question: How has fertility changed, and where is the record incomplete?
columns:
  fertility_rate:
    meaning: Total fertility rate, births per woman (World Bank SP.DYN.TFRT.IN)
  year:
    meaning: Calendar year of the estimate
    semantic_type: numeric_count
  Country Name:
    meaning: Country, or a World Bank grouping of countries
    semantic_type: categorical
interpretations:
  - kind: interpretation
    statement: Rows such as 'OECD members' and 'Sub-Saharan Africa' are groupings of other rows, not countries; exclude them before averaging across countries.
    columns: [Country Name]
""", encoding="utf-8")
understand(long, source="fertility (long, reshaped)", out_dir=out / "2-long", annotations_path=out / "annotations.yml")
print(render_compare(compare(out / "1-raw" / "guide-profile.json", out / "2-long" / "guide-profile.json")))
