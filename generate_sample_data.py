"""Creates SYNTHETIC inventory data that mimics the quality issues seen in the
legacy HERP logs (duplicates, mixed date formats, null quantities).
No real plant data is used."""
import numpy as np
import pandas as pd

def make_sample(n_unique=10_000, n_dupes=200, seed=42):
    rng = np.random.default_rng(seed)
    codes = [f"p-{10000 + i}" for i in range(n_unique)]
    df = pd.DataFrame({
        "part_code": codes,
        "description": [f"Turbine spare {i}" for i in range(n_unique)],
        "qty": rng.integers(0, 500, n_unique).astype(float),
        "shift": rng.choice(["A", "B", "C"], n_unique),
        "date": pd.to_datetime("2026-06-01") + pd.to_timedelta(rng.integers(0, 40, n_unique), unit="D"),
    })
    # Issue 1: mixed date formats from different shop floor registers
    half = n_unique // 2
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    df.loc[:half, "date"] = pd.to_datetime(df.loc[:half, "date"]).dt.strftime("%d/%m/%Y")
    # Issue 2: null quantities from incomplete shift logging
    df.loc[rng.choice(n_unique, max(1, n_unique // 33), replace=False), "qty"] = np.nan
    # Issue 3: messy keys (case and spaces)
    df.loc[::7, "part_code"] = " " + df.loc[::7, "part_code"].str.upper() + " "
    # Issue 4: duplicates from dual data entry across departments
    dupes = df.sample(n_dupes, random_state=seed)
    return pd.concat([df, dupes], ignore_index=True).sample(frac=1, random_state=seed)

if __name__ == "__main__":
    data = make_sample()
    data.to_csv("inventory_log.csv", index=False)
    print(f"Wrote inventory_log.csv with {len(data)} rows")
