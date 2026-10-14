"""Selenium UI test: log in to the dashboard, open Inventory and check the
displayed part count matches the cleaned dataset. Set DASHBOARD_URL to run it."""
import os
import pandas as pd
import pytest

pytest.importorskip("selenium")
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

URL = os.environ.get("DASHBOARD_URL")
pytestmark = pytest.mark.skipif(not URL, reason="DASHBOARD_URL not set")

@pytest.fixture
def driver():
    opts = Options(); opts.add_argument("--headless=new"); opts.add_argument("--no-sandbox")
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()

def test_inventory_part_count_matches_data(driver):
    expected = pd.read_csv("clean_inventory.csv")["part_code"].nunique()
    driver.get(URL)
    driver.find_element(By.ID, "inv-link").click()
    shown = int(driver.find_element(By.ID, "part-count").text)
    assert shown == expected
