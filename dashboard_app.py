"""Minimal inventory dashboard (Flask) so the Selenium UI test has something to validate."""
import pandas as pd
from flask import Flask

def create_app(csv_path="clean_inventory.csv"):
    app = Flask(__name__)
    app.config["CSV"] = csv_path

    @app.route("/")
    def home():
        return '<h1>HERP Inventory Dashboard</h1><a id="inv-link" href="/inventory">Inventory</a>'

    @app.route("/inventory")
    def inventory():
        df = pd.read_csv(app.config["CSV"])
        return (f'<h1>Inventory KPIs</h1><p>Total parts: '
                f'<span id="part-count">{df["part_code"].nunique()}</span></p>')
    return app

if __name__ == "__main__":
    create_app().run(port=5000)
