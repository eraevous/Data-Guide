"""A synthetic encounters table with planted problems, for tests and for trying the tool.

Synthetic data, not real patients. The problems planted in it (each one should be found):
- ``age`` uses 999 for 'unknown';
- the three ``lab_*`` columns are missing together;
- ``payer`` contains 'TEST' rows and 'N/A';
- ``discharge_date`` has an empty month;
- ``total_cost`` is right-skewed, with extreme values;
- ``cost_usd_copy`` duplicates ``total_cost``;
- ``facility`` is almost constant;
- ``dx_group`` includes 'Surgery', which is a service, not a diagnosis;
- ``readmitted_30d`` depends on length of stay and diagnosis group;
- ``followup_call`` is recorded after the outcome (leakage).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

ANNOTATIONS_YAML = """\
dataset:
  row_unit: one row per hospital encounter
  question: Which discharges are at risk of 30-day readmission?
  decision: Who receives a follow-up call after discharge
  target: readmitted_30d
columns:
  encounter_id:
    meaning: Encounter identifier
    semantic_type: identifier
  dx_group:
    meaning: Primary diagnosis group
    note: '"Surgery" is a service line, not a diagnosis; it mixes several diagnostic processes.'
  readmitted_30d:
    meaning: Readmitted within 30 days of discharge (1 = yes)
interpretations:
  - kind: hypothesis
    statement: Diagnosis groups may follow different readmission processes and may need separate models.
    columns: [dx_group, readmitted_30d]
"""


def encounters(n: int = 1200, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dx = rng.choice(["Cardiac", "Respiratory", "Surgery", "Renal", "Other"], n, p=[0.3, 0.25, 0.2, 0.1, 0.15])
    los = rng.poisson(lam=np.where(dx == "Surgery", 5, 3)) + 1
    age = rng.integers(18, 95, n).astype(float)
    age[rng.random(n) < 0.03] = 999
    base = {"Cardiac": 0.18, "Respiratory": 0.14, "Surgery": 0.08, "Renal": 0.22, "Other": 0.07}
    p = np.array([base[d] for d in dx]) + 0.02 * (los - 3)
    readmit = (rng.random(n) < np.clip(p, 0.01, 0.9)).astype(int)
    cost = np.round(rng.lognormal(mean=9, sigma=0.9, size=n) * (1 + 0.1 * los), 2)
    days = rng.integers(0, 365, n)
    dates = pd.Timestamp("2025-01-01") + pd.to_timedelta(days, unit="D")
    gap = (dates >= "2025-06-01") & (dates < "2025-07-01")
    dates = dates.where(~gap, dates + pd.Timedelta(days=30))
    labs = rng.random(n) < 0.35
    payer = rng.choice(["Medicare", "Medicaid", "Commercial", "Self-pay", "N/A"], n, p=[0.45, 0.2, 0.28, 0.05, 0.02]).astype(object)
    payer[:6] = "TEST"
    df = pd.DataFrame({
        "encounter_id": [f"E{100000 + i}" for i in range(n)],
        "facility": np.where(rng.random(n) < 0.96, "Main Campus", "North Clinic"),
        "discharge_date": dates.strftime("%Y-%m-%d"),
        "age": age, "dx_group": dx, "length_of_stay": los, "payer": payer,
        "total_cost": cost, "cost_usd_copy": cost,
        "lab_creatinine": np.where(labs, np.nan, np.round(rng.normal(1.1, 0.3, n), 2)),
        "lab_sodium": np.where(labs, np.nan, np.round(rng.normal(139, 3, n), 1)),
        "lab_potassium": np.where(labs, np.nan, np.round(rng.normal(4.2, 0.4, n), 2)),
        "readmitted_30d": readmit,
        "followup_call": np.where(rng.random(n) < 0.97, readmit, 1 - readmit),
    })
    return df
