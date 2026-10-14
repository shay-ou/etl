"""ETL pipeline for HERP production logs: Extract -> Transform -> Load.
Turns fragmented spreadsheet dumps into a hash-indexed dataset keyed on part code."""
import logging
import pandas as pd

log = logging.getLogger("herp_etl")

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")

def extract(path: str) -> pd.DataFrame:
    """Read a legacy log (CSV or Excel)."""
    if path.endswith((".xlsx", ".xls")):
        return pd.read_excel(path, dtype={"part_code": str})
    return pd.read_csv(path, dtype={"part_code": str})

def normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    """Key normalization: trim spaces, upper-case so 'p-1 ' and 'P-1' match."""
    df = df.copy()
    df["part_code"] = df["part_code"].str.strip().str.upper()
    return df

def parse_dates(series: pd.Series) -> pd.Series:
    """Try each known register format in turn; unparseable values become NaT."""
    out = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    for fmt in DATE_FORMATS:
        mask = out.isna()
        out[mask] = pd.to_datetime(series[mask], format=fmt, errors="coerce")
    return out

def handle_nulls(df: pd.DataFrame, fill_qty: int = 0) -> pd.DataFrame:
    """Null handling + type casting for quantity."""
    df = df.copy()
    df["qty"] = df["qty"].fillna(fill_qty).astype(int)
    return df

def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Keep one record per part code (dual data entry creates repeats)."""
    return df.drop_duplicates(subset="part_code", keep="first").reset_index(drop=True)

def transform(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_keys(df)
    df["date"] = parse_dates(df["date"].astype(str))
    df = handle_nulls(df)
    df = deduplicate(df)
    return df

def build_index(df: pd.DataFrame) -> pd.DataFrame:
    """Load stage: index on part code so lookups are O(1) hash lookups."""
    indexed = df.set_index("part_code")
    if not indexed.index.is_unique:
        raise ValueError("part_code index contains duplicates; run deduplicate() first")
    return indexed

def lookup(index: pd.DataFrame, part_code: str):
    """Constant-time retrieval of the full record for a part code."""
    key = part_code.strip().upper()
    return index.loc[key] if key in index.index else None

def run(path: str, out_csv: str = "clean_inventory.csv") -> pd.DataFrame:
    raw = extract(path)
    clean = transform(raw)
    log.info("rows in=%d out=%d duplicates removed=%d", len(raw), len(clean), len(raw) - len(clean))
    clean.to_csv(out_csv, index=False)   # central repository (CSV store)
    return build_index(clean)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    idx = run("inventory_log.csv")
    print(lookup(idx, "p-10042"))
