import pandas as pd
import pytest
from pathlib import Path

from core.models import GuideDataFrame, ProfilingResult, SchemaContract
from outputs.static_report import StaticReportRenderer


@pytest.fixture
def simple_gdf():
    df = pd.DataFrame({
        "metric": ["balance_due", "visit_count", "balance_due", "visit_count"],
        "value": [150.0, 3, 0.0, 1],
        "data_type": ["currency", "numeric", "currency", "numeric"],
    })
    sc = SchemaContract(metric_col="metric", value_col="value", type_col="data_type", mode="long")
    return GuideDataFrame(df=df, schema=sc, source_type="csv", origin="test.csv")


@pytest.fixture
def simple_result(simple_gdf):
    return ProfilingResult(
        source=simple_gdf,
        dataset_stats={"row_count": 4, "col_count": 3, "missing_pct": 0.0},
        column_stats={
            "value": {"mean": 38.5, "min": 0.0, "max": 150.0, "null_count": 0}
        },
    )


def test_renderer_produces_html(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "<html" in content
    assert "Data Guide" in content


def test_html_is_self_contained(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    content = out_path.read_text(encoding="utf-8")
    assert "<img src=" not in content or "base64" in content


def test_html_contains_dataset_stats(simple_result, tmp_path):
    out_path = tmp_path / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    content = out_path.read_text(encoding="utf-8")
    assert "row_count" in content or "4" in content


def test_renderer_creates_parent_dirs(simple_result, tmp_path):
    out_path = tmp_path / "nested" / "deep" / "report.html"
    renderer = StaticReportRenderer()
    renderer.render(simple_result, output_path=str(out_path))
    assert out_path.exists()
