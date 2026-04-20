import pandas as pd
import pytest
from core.models import GuideDataFrame, Narrative, ProfilingResult, SchemaContract


def test_schema_contract_defaults():
    sc = SchemaContract()
    assert sc.metric_col == "metric"
    assert sc.value_col == "value"
    assert sc.type_col is None
    assert sc.mode == "unknown"
    assert sc.key_cols == []
    assert sc.context_cols == []


def test_schema_contract_long_mode():
    sc = SchemaContract(
        key_cols=["patient_id"],
        context_cols=["location"],
        metric_col="metric",
        value_col="value",
        type_col="data_type",
        mode="long",
    )
    assert sc.mode == "long"
    assert sc.type_col == "data_type"


def test_guide_dataframe_wraps_df():
    df = pd.DataFrame({"metric": ["balance"], "value": [100.0]})
    sc = SchemaContract(mode="long", metric_col="metric", value_col="value")
    gdf = GuideDataFrame(df=df, schema=sc, source_type="csv", origin="test.csv")
    assert len(gdf.df) == 1
    assert gdf.source_type == "csv"
    assert gdf.schema.mode == "long"


def test_profiling_result_annotations_none_by_default():
    gdf = GuideDataFrame(
        df=pd.DataFrame(),
        schema=SchemaContract(),
        source_type="csv",
        origin="test.csv",
    )
    result = ProfilingResult(source=gdf, dataset_stats={}, column_stats={})
    assert result.annotations is None


def test_narrative_fields():
    n = Narrative(element_id="col_age", text="Age is right-skewed.", framework="plain")
    assert n.element_id == "col_age"
    assert n.framework == "plain"
