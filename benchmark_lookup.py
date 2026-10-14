"""Demonstrates O(n) linear scan vs O(1) indexed lookup on the sample data."""
import time
import pandas as pd
from generate_sample_data import make_sample
from etl_pipeline import transform, build_index, lookup

def linear_search(df, code):
    for _, row in df.iterrows():          # legacy-style row-by-row scan
        if row["part_code"] == code:
            return row

if __name__ == "__main__":
    clean = transform(make_sample())
    index = build_index(clean)
    target = clean["part_code"].iloc[-1]   # worst case: last row
    t0 = time.perf_counter(); linear_search(clean, target); t_lin = time.perf_counter() - t0
    t0 = time.perf_counter(); lookup(index, target); t_idx = time.perf_counter() - t0
    mem_mb = index.memory_usage(deep=True).sum() / 1e6
    print(f"records: {len(clean)}")
    print(f"linear scan : {t_lin*1000:.3f} ms")
    print(f"indexed     : {t_idx*1000:.3f} ms")
    print(f"index memory: {mem_mb:.2f} MB")
