"""Tests for the understanding layer.

They follow requirement F: metric accuracy, type routing, degradation, reproducibility, and
preservation of the declared purpose (findings stay typed and sourced).
"""
from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
import pytest
from typer.testing import CliRunner

from cli import app
from understanding import annotations as ann
from understanding.artifact import build_artifact, dumps
from understanding.compare import compare_artifacts
from understanding.demo import ANNOTATIONS_YAML, encounters
from understanding.relations import correlation_ratio, cramers_v, spearman
from understanding.semantics import infer

runner = CliRunner()


@pytest.fixture(scope="module")
def demo_artifact(tmp_path_factory):
    d = tmp_path_factory.mktemp("ann")
    (d / "guide.yml").write_text(ANNOTATIONS_YAML)
    df = encounters()
    return build_artifact(df, source="demo", annotations=ann.load(d / "guide.yml", list(df.columns)))


def rules_fired(art, rule, column=None):
    return [f for f in art["findings"] if f["rule"] == rule and (column is None or column in f["subjects"])]


# ---------------------------------------------------------------- metric accuracy
def test_numeric_stats_match_numpy(demo_artifact):
    df = encounters()
    num = demo_artifact["columns"]["total_cost"]["stats"]["numeric"]
    assert num["median"] == pytest.approx(float(np.median(df.total_cost)), rel=1e-4)
    assert num["mean"] == pytest.approx(float(df.total_cost.mean()), rel=1e-4)
    assert num["p25"] == pytest.approx(float(df.total_cost.quantile(0.25)), rel=1e-4)
    assert sum(num["histogram"]["counts"]) == len(df)


def test_cramers_v_on_independent_and_identical():
    rng = np.random.default_rng(0)
    a = pd.Series(rng.choice(list("abc"), 3000))
    b = pd.Series(rng.choice(list("xyz"), 3000))
    v_indep, _ = cramers_v(a, b)
    v_same, _ = cramers_v(a, a.map({"a": "x", "b": "y", "c": "z"}))
    assert v_indep < 0.05
    assert v_same == pytest.approx(1.0, abs=1e-3)


def test_correlation_ratio_and_spearman_known_values():
    cat = pd.Series(["a"] * 50 + ["b"] * 50)
    num = pd.Series([0.0] * 50 + [1.0] * 50)
    eta, _ = correlation_ratio(cat, num)
    assert eta == pytest.approx(1.0)
    x = pd.Series(range(100), dtype=float)
    rho, _ = spearman(x, x ** 3)
    assert rho == pytest.approx(1.0)


# ---------------------------------------------------------------- type routing
@pytest.mark.parametrize("name,values,expected", [
    ("flag", [True, False] * 20, "boolean"),
    ("status", ["open", "closed"] * 20, "binary"),
    ("visit_date", pd.date_range("2025-01-01", periods=40).strftime("%Y-%m-%d"), "temporal"),
    ("email", [f"user{i}@example.com" for i in range(40)], "email"),
    ("amount_text", [f"{i}.50" for i in range(40)], "numeric_as_text"),
    ("price", np.linspace(-3.2, 9.7, 40), "numeric_continuous"),
    ("country", ["US", "CA", "MX", "BR"] * 10, "categorical"),
    ("same", ["x"] * 40, "constant"),
    ("customer_id", list(range(1000, 1040)), "identifier"),
])
def test_semantic_routing(name, values, expected):
    s = pd.Series(values)
    assert infer(name, s, len(s))["type"] == expected


def test_inferred_type_is_labelled_inferred_and_override_is_human(demo_artifact):
    cols = demo_artifact["columns"]
    assert cols["age"]["semantic"]["source"] == "inferred"
    assert cols["encounter_id"]["semantic"]["source"] == "human"
    assert cols["encounter_id"]["semantic"]["inferred"]["type"]  # the inference is kept


# ---------------------------------------------------------------- planted problems are found
@pytest.mark.parametrize("rule,column", [
    ("sentinel-number", "age"), ("co-missing", "lab_sodium"), ("test-values", "payer"),
    ("missing-as-text", "payer"), ("temporal-gap", "discharge_date"), ("skew", "total_cost"),
    ("near-duplicate", "cost_usd_copy"), ("dominant-level", "facility"),
    ("possible-leakage", "followup_call"),
])
def test_planted_problem_is_found(demo_artifact, rule, column):
    assert rules_fired(demo_artifact, rule, column), f"{rule} on {column} not found"


def test_decoy_clean_columns_do_not_trigger(demo_artifact):
    assert not rules_fired(demo_artifact, "sentinel-number", "length_of_stay")
    assert not rules_fired(demo_artifact, "missing", "dx_group")
    assert not rules_fired(demo_artifact, "possible-leakage", "dx_group")


# ---------------------------------------------------------------- purpose preservation
def test_every_finding_is_typed_and_sourced(demo_artifact):
    for f in demo_artifact["findings"]:
        assert f["kind"] in ("observation", "interpretation", "hypothesis", "action", "question")
        assert f["generator"] in ("rule", "human")


def test_causes_are_never_reported_as_observations(demo_artifact):
    for f in demo_artifact["findings"]:
        if f["rule"] in ("sentinel-number", "co-missing", "possible-leakage") and "may" in f["statement"]:
            assert f["kind"] == "hypothesis"


def test_human_annotations_enter_as_human(demo_artifact):
    human = [f for f in demo_artifact["findings"] if f["generator"] == "human"]
    assert any("Surgery" in f["statement"] and f["kind"] == "interpretation" for f in human)
    assert any(f["kind"] == "hypothesis" for f in human)
    assert demo_artifact["register"]["row_unit"]["source"] == "human"


def test_usefulness_unassessed_without_declared_question():
    art = build_artifact(encounters(300), source="x")
    assert art["usefulness"]["status"] == "unassessed"
    assert any(f["rule"] == "row-unit-unstated" for f in art["findings"])
    assert art["register"]["generating_process"]["source"] == "unknown"


def test_bivariate_screening_reports_counts_not_every_pair(demo_artifact):
    rel = demo_artifact["relations"]
    k = rel["eligible_columns"]
    assert rel["considered"] == k * (k - 1) // 2 and rel["screened"] <= rel["budget"]
    assert len(rel["top"]) <= rel["top_k"]
    assert all(p["strength"] != "negligible" for p in rel["top"])


def test_identifier_and_continuous_columns_are_not_candidate_keys(demo_artifact):
    keys = demo_artifact["register"]["candidate_keys"]
    assert "encounter_id" in keys
    assert "total_cost" not in keys


# ---------------------------------------------------------------- reproducibility and compare
def test_artifact_is_deterministic():
    df = encounters(400)
    assert dumps(build_artifact(df, source="x")) == dumps(build_artifact(df, source="x"))


def test_compare_shows_sentinel_fix():
    before = build_artifact(encounters(), source="before")
    fixed = encounters()
    fixed.loc[fixed.age == 999, "age"] = np.nan
    after = build_artifact(fixed, source="after")
    d = compare_artifacts(before, after)
    assert not d["same_data"]
    assert any("999" in f["statement"] for f in d["findings_resolved"])
    age = next(c for c in d["columns_changed"] if c["column"] == "age")
    assert age["changes"]["max"]["after"] < 100


# ---------------------------------------------------------------- annotations validation
def test_annotation_errors(tmp_path):
    cols = ["a", "b"]
    p = tmp_path / "g.yml"
    p.write_text("dataset:\n  target: zzz\n")
    with pytest.raises(ann.AnnotationError):
        ann.load(p, cols)
    p.write_text("columns:\n  a:\n    semantic_type: banana\n")
    with pytest.raises(ann.AnnotationError):
        ann.load(p, cols)
    p.write_text("dataset:\n  rowunit: typo\n")
    with pytest.raises(ann.AnnotationError):
        ann.load(p, cols)


# ---------------------------------------------------------------- renderers and degradation
def test_html_report_keeps_kinds_and_sources(demo_artifact):
    from outputs.understanding_report import to_html, to_markdown
    html = to_html(demo_artifact)
    for f in demo_artifact["findings"]:
        assert f["id"] in html
    assert "Nothing here is AI-written" in html
    md = to_markdown(demo_artifact)
    assert "What this data cannot tell us" in md and "`human`" in md


def test_report_degrades_without_matplotlib(demo_artifact, monkeypatch):
    import outputs.understanding_report as r
    monkeypatch.setattr(r, "_plt", lambda: None)
    html = r.to_html(demo_artifact)
    assert "Chart unavailable" in html
    assert "data:image/png" not in html


def test_empty_and_tiny_frames_do_not_crash():
    art = build_artifact(pd.DataFrame({"a": [None, None], "b": [1, 1]}), source="tiny")
    assert art["columns"]["a"]["semantic"]["type"] == "empty"
    assert art["columns"]["b"]["semantic"]["type"] == "constant"


# ---------------------------------------------------------------- CLI
def test_cli_demo_understand_compare(tmp_path):
    r = runner.invoke(app, ["demo", "--out", str(tmp_path / "d")])
    assert r.exit_code == 0, r.output
    art = json.loads((tmp_path / "d" / "guide-profile.json").read_text())
    assert art["schema"] == "data-guide/understanding@0.1"
    df = pd.read_csv(tmp_path / "d" / "encounters.csv")
    df.loc[df.age == 999, "age"] = None
    df.to_csv(tmp_path / "fixed.csv", index=False)
    r = runner.invoke(app, ["understand", str(tmp_path / "fixed.csv"), "--out", str(tmp_path / "f"),
                            "--annotations", str(tmp_path / "d" / "guide.yml")])
    assert r.exit_code == 0, r.output
    r = runner.invoke(app, ["compare", str(tmp_path / "d" / "guide-profile.json"), str(tmp_path / "f" / "guide-profile.json")])
    assert r.exit_code == 0, r.output
    assert "No longer found" in r.output


def test_cli_rejects_bad_annotations(tmp_path):
    runner.invoke(app, ["demo", "--out", str(tmp_path / "d")])
    (tmp_path / "bad.yml").write_text("dataset:\n  target: not_a_column\n")
    r = runner.invoke(app, ["understand", str(tmp_path / "d" / "encounters.csv"), "--out", str(tmp_path / "x"),
                            "--annotations", str(tmp_path / "bad.yml")])
    assert r.exit_code == 1
    assert "annotations" in r.output


# ---------------------------------------------------------------- Kate's purpose-review fixtures
def test_filled_missingness_is_flagged_in_compare():
    df = encounters()
    before = build_artifact(df, source="before")
    filled = df.copy()
    filled["lab_sodium"] = filled["lab_sodium"].fillna(0)
    d = compare_artifacts(before, build_artifact(filled, source="after"))
    w = [x for x in d["missingness_warnings"] if x["column"] == "lab_sodium"]
    assert w and w[0]["likely_fill"] == 0
    assert "missing-indicator" in w[0]["statement"]


def test_filled_missingness_decoy_no_warning_when_nothing_filled():
    df = encounters()
    d = compare_artifacts(build_artifact(df, source="a"), build_artifact(df, source="b"))
    assert d["missingness_warnings"] == []


def test_confidence_means_different_things_by_kind(demo_artifact):
    for f in demo_artifact["findings"]:
        if f["generator"] == "human":
            assert f["confidence"] == "stated"
        elif f["kind"] == "observation":
            assert f["confidence"] == "measured"
        elif f["kind"] == "hypothesis":
            assert f["confidence"] == "untested"


def test_annotation_that_disagrees_with_values_raises_a_question(tmp_path):
    df = encounters(300)
    p = tmp_path / "g.yml"
    p.write_text("columns:\n  total_cost:\n    semantic_type: categorical\n")
    art = build_artifact(df, source="x", annotations=ann.load(p, list(df.columns)))
    assert art["columns"]["total_cost"]["semantic"]["source"] == "human"
    assert rules_fired(art, "annotation-disagrees", "total_cost")


def test_screening_is_selective_and_reports_exclusions():
    df = encounters()
    art = build_artifact(df, source="x", budget=5)
    rel = art["relations"]
    assert rel["screened"] == 5 and rel["not_computed_budget"] == rel["considered"] - 5
    assert any(x["column"] == "encounter_id" for x in rel["excluded_columns"])


def test_target_pairs_are_computed_first_under_budget(tmp_path):
    df = encounters()
    p = tmp_path / "g.yml"
    p.write_text("dataset:\n  target: readmitted_30d\n")
    art = build_artifact(df, source="x", annotations=ann.load(p, list(df.columns)), budget=3)
    assert all(pp["involves_target"] for pp in art["relations"]["target_pairs"])
    assert len(art["relations"]["target_pairs"]) >= 1


def test_usefulness_wording_does_not_deny_exploratory_value():
    art = build_artifact(encounters(300), source="x")
    assert "Exploratory findings are still reported" in art["usefulness"]["reason"]


# ---------------------------------------------------------------- shape and aggregate rules (found on the acceptance dataset)
def _wide(n_periods=8):
    rng = np.random.default_rng(1)
    df = pd.DataFrame({"country": [f"C{i}" for i in range(40)]})
    for k, y in enumerate(range(2000, 2000 + n_periods)):
        v = rng.normal(3, 1, 40) + 0.01 * k
        if k >= n_periods - 2:
            v[:30] = np.nan
        df[str(y)] = v
    return df


def test_wide_by_period_is_detected_and_per_column_noise_collapsed():
    art = build_artifact(_wide(), source="wide")
    assert art["register"]["shape"]["form"] == "wide-by-period"
    assert rules_fired(art, "wide-by-period")
    assert not rules_fired(art, "near-duplicate")
    assert not [f for f in art["findings"] if f["rule"] == "missing" and f["subjects"] == ["2007"]]
    assert all(x["column"] != "2001" or "period" in x["reason"] for x in art["relations"]["excluded_columns"])


def test_wide_by_period_decoy_ordinary_table():
    art = build_artifact(encounters(300), source="x")
    assert art["register"]["shape"]["form"] == "rows-as-records"


def test_aggregate_labels_hypothesis_and_decoy():
    df = pd.DataFrame({"region": ["North", "South", "East", "West", "All regions", "Grand total"] * 10,
                       "sales": range(60)})
    art = build_artifact(df, source="x")
    hyp = rules_fired(art, "aggregate-labels", "region")
    assert any(f["kind"] == "hypothesis" for f in hyp)
    clean = build_artifact(pd.DataFrame({"region": ["North", "South", "East", "West"] * 15, "sales": range(60)}), source="y")
    assert not rules_fired(clean, "aggregate-labels")


# ---------------------------------------------------------------- regressions from the independent technical review
def test_missing_by_group_does_not_fire_on_random_missingness():
    fired = 0
    for seed in range(20):
        rng = np.random.default_rng(seed)
        n = 600
        x = pd.Series(rng.normal(size=n))
        x[rng.random(n) < .15] = np.nan
        df = pd.DataFrame({"x": x, "store": rng.choice([f"s{i}" for i in range(50)], n), "y": rng.normal(size=n)})
        fired += bool(rules_fired(build_artifact(df, source="m"), "missing-by-group"))
    assert fired <= 1


def test_missing_by_group_fires_on_real_dependence():
    rng = np.random.default_rng(0)
    period = np.repeat(np.arange(2000, 2010), 100)
    x = pd.Series(rng.normal(size=1000))
    x[(period >= 2008) & (rng.random(1000) < 0.9)] = np.nan
    art = build_artifact(pd.DataFrame({"x": x, "period": period}), source="d")
    obs = [f for f in rules_fired(art, "missing-by-group") if f["kind"] == "observation"]
    assert obs and "varies with" in obs[0]["statement"] and obs[0]["evidence"]["p_value"] < 1e-6


def test_mixed_utc_offsets_do_not_crash():
    df = pd.DataFrame({"ts": [f"2020-{m:02d}-15T08:00:00{'-05:00' if m in (1, 2, 3, 11, 12) else '-04:00'}" for m in range(1, 13)] * 4,
                       "v": range(48)})
    art = build_artifact(df, source="x")
    assert art["columns"]["ts"]["semantic"]["type"] == "temporal"


def test_infinite_values_are_excluded_and_reported():
    art = build_artifact(pd.DataFrame({"x": [1., 2, 3] * 13 + [np.inf], "y": range(40)}), source="x")
    assert art["columns"]["x"]["stats"]["numeric"]["inf_count"] == 1
    assert rules_fired(art, "infinite-values", "x")


def test_non_string_column_names_and_collisions():
    rng = np.random.default_rng(0)
    art = build_artifact(pd.DataFrame({"country": ["a", "b"] * 20, 1960: rng.normal(size=40), 1961: rng.normal(size=40)}), source="x")
    assert "1960" in art["columns"]
    with pytest.raises(ValueError):
        build_artifact(pd.DataFrame([[1, 2]] * 5, columns=[1, "1"]), source="x")


def test_zero_fill_detected_when_column_already_had_zeros():
    rng = np.random.default_rng(3)
    x = pd.Series(rng.normal(10, 2, 1000))
    x[rng.random(1000) < .2] = 0
    x[rng.random(1000) < .4] = np.nan
    d = compare_artifacts(build_artifact(pd.DataFrame({"x": x}), source="b"), build_artifact(pd.DataFrame({"x": x.fillna(0)}), source="a"))
    assert d["missingness_warnings"][0].get("likely_fill") == 0


def test_compare_keeps_generator(tmp_path):
    df = encounters(300)
    p = tmp_path / "g.yml"
    p.write_text("interpretations:\n  - statement: A human note\n    columns: [payer]\n")
    d = compare_artifacts(build_artifact(df, source="a"), build_artifact(df, source="b", annotations=ann.load(p, list(df.columns))))
    assert any(f["generator"] == "human" for f in d["findings_new"])


def test_small_scale_statistics_survive_rounding():
    from understanding.columns import numeric_stats
    st = numeric_stats(pd.Series(np.random.default_rng(0).normal(scale=1e-5, size=500)))
    assert st["std"] > 0 and len(set(st["histogram"]["edges"])) > 1


def test_left_skew_wording():
    art = build_artifact(pd.DataFrame({"score": 100 - np.random.default_rng(0).lognormal(size=500) * 5}), source="x")
    interp = [f for f in rules_fired(art, "skew", "score") if f["kind"] == "interpretation"]
    assert interp and "small values pull it down" in interp[0]["statement"]


def test_single_row_and_nested_and_two_date_values():
    art = build_artifact(pd.DataFrame({"a": [1], "b": ["x"]}), source="one")
    assert rules_fired(art, "too-few-rows") and not rules_fired(art, "constant")
    art = build_artifact(pd.DataFrame({"tags": [["a"], ["b", "c"]] * 20, "v": range(40)}), source="n")
    assert art["columns"]["tags"]["semantic"]["type"] == "nested"
    art = build_artifact(pd.DataFrame({"d": pd.to_datetime(["2020-01-01", "2020-02-01"] * 20)}), source="d")
    assert art["columns"]["d"]["semantic"]["type"] == "temporal"


def test_numeric_column_names_can_be_annotated(tmp_path):
    df = pd.DataFrame({"country": ["a", "b"] * 20, "1960": range(40)})
    p = tmp_path / "g.yml"
    p.write_text("dataset:\n  target: 1960\ncolumns:\n  1960:\n    meaning: year value\n")
    a = ann.load(p, list(df.columns))
    assert a["dataset"]["target"] == "1960" and "1960" in a["columns"]


def test_dollar_labels_and_markdown_escaping():
    from outputs.understanding_report import to_html, to_markdown
    df = pd.DataFrame({"band": ["$5 to $10", "$x^$", "<b>|"] * 20, "v": range(60)})
    art = build_artifact(df, source="x")
    to_html(art)  # must not raise
    md = to_markdown(art)
    assert "<b>" not in md and "\\|" in md
