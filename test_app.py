"""
test_app.py — Basic automated tests for the Olympic Platform.

Run from the project root:
    /tmp/olympic_venv/bin/python test_app.py

Tests cover:
  - Data loading (all 4 CSVs readable)
  - KPI computation (no crashes, correct types)
  - Every chart helper (returns non-empty dict with 'data' key)
  - Flask routes (HTTP 200, JSON content-type)
  - Country API (valid country, invalid country, missing param)
  - Leaderboard API (returns list of dicts with expected keys)
"""

import sys
import os
import json
import unittest

# Make sure we can import the Flask app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import (
    app, DATA, compute_kpis, get_country_list,
    chart_medal_trends_over_time,
    chart_top_countries_medals,
    chart_gold_silver_bronze_breakdown,
    chart_efficiency_vs_investment,
    chart_gender_split_by_sport,
    chart_region_medal_share,
    chart_top_sports_by_medals,
    chart_host_advantage,
    chart_efficiency_ranking,
)


class TestDataLoading(unittest.TestCase):
    """Verify all four datasets load correctly."""

    def test_medals_not_empty(self):
        self.assertFalse(DATA["medals"].empty, "medal_results.csv is empty or missing")

    def test_athletes_not_empty(self):
        self.assertFalse(DATA["athletes"].empty, "athletes_cleaned.csv is empty or missing")

    def test_games_not_empty(self):
        self.assertFalse(DATA["games"].empty, "games_summary.csv is empty or missing")

    def test_investment_not_empty(self):
        self.assertFalse(DATA["investment"].empty, "alltime_investment.csv is empty or missing")

    def test_medals_columns(self):
        expected = {"year", "country", "gold", "silver", "bronze", "total_medals"}
        self.assertTrue(expected.issubset(set(DATA["medals"].columns)))

    def test_investment_columns(self):
        expected = {"country", "region", "alltime_total_medals", "avg_efficiency_pct", "sports_investment"}
        self.assertTrue(expected.issubset(set(DATA["investment"].columns)))


class TestKPIComputation(unittest.TestCase):
    """Verify KPI helper returns correct structure."""

    def setUp(self):
        self.kpis = compute_kpis()

    def test_keys_present(self):
        for key in ["total_countries", "total_games", "total_athletes", "total_sports",
                    "top_country", "top_country_medals", "most_efficient", "most_efficient_pct"]:
            self.assertIn(key, self.kpis, f"KPI key missing: {key}")

    def test_positive_counts(self):
        self.assertGreater(self.kpis["total_countries"], 0)
        self.assertGreater(self.kpis["total_games"], 0)

    def test_top_country_is_string(self):
        self.assertIsInstance(self.kpis["top_country"], str)

    def test_efficiency_is_float(self):
        self.assertIsInstance(self.kpis["most_efficient_pct"], float)


class TestChartHelpers(unittest.TestCase):
    """Verify each chart function returns a valid Plotly figure dict."""

    def _assert_valid_fig(self, fig, name):
        self.assertIsInstance(fig, dict, f"{name} did not return a dict")
        self.assertIn("data", fig, f"{name}: missing 'data' key")
        self.assertGreater(len(fig["data"]), 0, f"{name}: 'data' is empty")

    def test_medal_trends(self):
        self._assert_valid_fig(chart_medal_trends_over_time(), "medal_trends")

    def test_top_countries(self):
        self._assert_valid_fig(chart_top_countries_medals(), "top_countries")

    def test_global_medal_breakdown(self):
        self._assert_valid_fig(chart_gold_silver_bronze_breakdown(), "global_breakdown")

    def test_country_medal_breakdown(self):
        countries = get_country_list()
        if countries:
            fig = chart_gold_silva_bronze_breakdown = chart_gold_silver_bronze_breakdown(countries[0])
            self._assert_valid_fig(fig, f"breakdown for {countries[0]}")

    def test_efficiency_scatter(self):
        self._assert_valid_fig(chart_efficiency_vs_investment(), "efficiency_scatter")

    def test_gender_split(self):
        self._assert_valid_fig(chart_gender_split_by_sport(), "gender_split")

    def test_region_treemap(self):
        self._assert_valid_fig(chart_region_medal_share(), "region_treemap")

    def test_top_sports(self):
        self._assert_valid_fig(chart_top_sports_by_medals(), "top_sports")

    def test_host_advantage(self):
        self._assert_valid_fig(chart_host_advantage(), "host_advantage")

    def test_efficiency_ranking(self):
        self._assert_valid_fig(chart_efficiency_ranking(), "efficiency_ranking")


class TestFlaskRoutes(unittest.TestCase):
    """Integration tests for all Flask HTTP routes."""

    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage_200(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Olympic", resp.data)

    def test_overview_api_200(self):
        resp = self.client.get("/api/charts/overview")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, "application/json")

    def test_overview_api_has_expected_keys(self):
        resp = self.client.get("/api/charts/overview")
        data = json.loads(resp.data)
        for key in ["medal_trends", "top_countries", "region_share", "gender_split",
                    "top_sports", "efficiency_vs_inv", "host_advantage", "efficiency_rank"]:
            self.assertIn(key, data, f"API response missing key: {key}")

    def test_country_api_valid(self):
        resp = self.client.get("/api/charts/country?name=United+States")
        self.assertEqual(resp.status_code, 200)

    def test_country_api_no_param(self):
        resp = self.client.get("/api/charts/country")
        self.assertEqual(resp.status_code, 400)

    def test_country_api_invalid_country(self):
        resp = self.client.get("/api/charts/country?name=ZZZFakeCountry999")
        self.assertEqual(resp.status_code, 404)

    def test_leaderboard_api_200(self):
        resp = self.client.get("/api/leaderboard")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_leaderboard_has_expected_fields(self):
        resp = self.client.get("/api/leaderboard")
        data = json.loads(resp.data)
        first = data[0]
        for field in ["country", "Total Medals", "Efficiency (%)", "Investment (M$)"]:
            self.assertIn(field, first, f"Leaderboard missing field: {field}")

    def test_search_api(self):
        resp = self.client.get("/api/search?q=aus")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIsInstance(data, list)


# ---------- Run ----------
if __name__ == "__main__":
    print("=" * 60)
    print("  Olympic Platform — Automated Tests")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
