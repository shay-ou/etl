"""PyTest suite for the backend ETL logic."""
import pandas as pd
import pytest
from generate_sample_data import make_sample
from etl_pipeline import (normalize_keys, parse_dates, handle_nulls,
                          deduplicate, transform, build_index, lookup)

def test_deduplication_10200_to_10000():
    raw = make_sample(n_unique=10_000, n_dupes=200)
    assert len(raw) == 10_200
    clean = transform(raw)
    assert len(clean) == 10_000
    assert clean["part_code"].is_unique

@pytest.mark.parametrize("raw,expected", [
    (" p-1 ", "P-1"), ("p-2", "P-2"), ("P-3", "P-3"), ("  p-4", "P-4"),
])
def test_key_normalization(raw, expected):
    out = normalize_keys(pd.DataFrame({"part_code": [raw]}))
    assert out["part_code"].iloc[0] == expected

@pytest.mark.parametrize("raw,expected", [
    ("2026-06-15", "2026-06-15"), ("15/06/2026", "2026-06-15"), ("15-06-2026", "2026-06-15"),
])
def test_date_formats(raw, expected):
    out = parse_dates(pd.Series([raw]))
    assert out.iloc[0] == pd.Timestamp(expected)

def test_bad_date_becomes_nat():
    assert pd.isna(parse_dates(pd.Series(["not a date"])).iloc[0])

def test_null_quantity_filled_and_int():
    out = handle_nulls(pd.DataFrame({"qty": [5.0, None]}))
    assert out["qty"].tolist() == [5, 0]
    assert str(out["qty"].dtype).startswith("int")

def test_lookup_hit_and_miss():
    idx = build_index(transform(make_sample(100, 5)))
    code = idx.index[0]
    assert lookup(idx, code.lower() + " ")["description"].startswith("Turbine")
    assert lookup(idx, "NOPE-1") is None

def test_index_is_unique():
    with pytest.raises(ValueError):
        build_index(pd.DataFrame({"part_code": ["A", "A"], "qty": [1, 2]}))
