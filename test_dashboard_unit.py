"""Fast check of the dashboard route without a browser (runs everywhere)."""
import pandas as pd
from dashboard_app import create_app

def test_inventory_route_shows_count(tmp_path):
    csv = tmp_path / "c.csv"
    pd.DataFrame({"part_code": ["A", "B", "C"]}).to_csv(csv, index=False)
    r = create_app(str(csv)).test_client().get("/inventory")
    assert b'id="part-count">3<' in r.data
