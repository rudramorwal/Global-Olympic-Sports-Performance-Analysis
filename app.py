"""
Olympic Performance Intelligence Platform
==========================================
A Flask web application that performs full data analysis in the backend
using Pandas, generates interactive Plotly charts, and serves them to a
rich, independently built frontend — replacing the Tableau-only approach.

Author : (your name)
Purpose: College submission — independently implemented version
"""

import os
import json
import math
from flask import Flask, render_template, jsonify, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

# ---------------------------------------------------------------------------
# App Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR,
    "DataSets - Global Olympic Sports Performance Analysis",
    "Cleaned Datasets")

# ---------------------------------------------------------------------------
# Data Loading  (loaded once at startup for performance)
# ---------------------------------------------------------------------------
def load_datasets():
    """Read all four CSVs and return a dict of DataFrames."""
    paths = {
        "medals":     os.path.join(DATA_DIR, "medal_results.csv"),
        "athletes":   os.path.join(DATA_DIR, "athletes_cleaned.csv"),
        "games":      os.path.join(DATA_DIR, "games_summary.csv"),
        "investment": os.path.join(DATA_DIR, "alltime_investment.csv"),
    }
    dfs = {}
    for key, path in paths.items():
        try:
            dfs[key] = pd.read_csv(path)
        except FileNotFoundError:
            # Fail gracefully — chart helpers will return empty figures
            dfs[key] = pd.DataFrame()
    return dfs

DATA = load_datasets()


# ---------------------------------------------------------------------------
# Chart Helper Functions
# Each function returns a JSON-serialisable Plotly figure dict.
# ---------------------------------------------------------------------------

def chart_medal_trends_over_time():
    """Line chart — total medals per year aggregated across all countries."""
    df = DATA["medals"]
    if df.empty:
        return {}
    agg = df.groupby("year")["total_medals"].sum().reset_index()
    fig = px.line(
        agg, x="year", y="total_medals",
        markers=True,
        title="Total Medals Distributed Per Olympic Games (1992–2026)",
        labels={"year": "Olympic Year", "total_medals": "Total Medals"},
        template="plotly_dark",
        color_discrete_sequence=["#f4c300"],
    )
    fig.update_traces(line_width=3, marker_size=8)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_top_countries_medals():
    """Horizontal bar chart — all-time total medals for top 15 countries."""
    df = DATA["investment"]
    if df.empty:
        return {}
    top = df.nlargest(15, "alltime_total_medals").sort_values("alltime_total_medals")
    fig = px.bar(
        top, x="alltime_total_medals", y="country",
        orientation="h",
        title="Top 15 Countries by All-Time Olympic Medals",
        labels={"alltime_total_medals": "Total Medals", "country": "Country"},
        template="plotly_dark",
        color="alltime_total_medals",
        color_continuous_scale=["#1a3a5c", "#f4c300"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
        coloraxis_showscale=False,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_gold_silver_bronze_breakdown(country=None):
    """Stacked bar — gold / silver / bronze per year for a selected country."""
    df = DATA["medals"]
    if df.empty:
        return {}
    if country:
        df = df[df["country"] == country]
    agg = df.groupby("year")[["gold", "silver", "bronze"]].sum().reset_index()
    fig = go.Figure()
    colours = {"gold": "#FFD700", "silver": "#C0C0C0", "bronze": "#CD7F32"}
    for medal in ["gold", "silver", "bronze"]:
        fig.add_trace(go.Bar(
            x=agg["year"], y=agg[medal],
            name=medal.capitalize(),
            marker_color=colours[medal],
        ))
    title = f"Medal Breakdown — {country}" if country else "Global Medal Breakdown by Type"
    fig.update_layout(
        barmode="stack",
        title=title,
        xaxis_title="Olympic Year",
        yaxis_title="Medals",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_efficiency_vs_investment():
    """Scatter — medal efficiency % vs sports investment, sized by total medals."""
    df = DATA["investment"]
    if df.empty:
        return {}
    fig = px.scatter(
        df,
        x="sports_investment",
        y="avg_efficiency_pct",
        size="alltime_total_medals",
        color="region",
        hover_name="country",
        title="Sports Investment vs Medal Efficiency by Country",
        labels={
            "sports_investment": "Sports Investment (Million USD)",
            "avg_efficiency_pct": "Avg Medal Efficiency (%)",
        },
        template="plotly_dark",
        size_max=50,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_gender_split_by_sport():
    """Pie/donut — male vs female athlete count across sports."""
    df = DATA["athletes"]
    if df.empty or "Sex" not in df.columns:
        return {}
    counts = df["Sex"].value_counts().reset_index()
    counts.columns = ["gender", "count"]
    counts["gender"] = counts["gender"].map({"M": "Male", "F": "Female"})
    fig = px.pie(
        counts, names="gender", values="count",
        title="Athlete Gender Distribution (1992–2026)",
        template="plotly_dark",
        color_discrete_map={"Male": "#2196F3", "Female": "#E91E63"},
        hole=0.45,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_region_medal_share():
    """Treemap — medal share by region."""
    df = DATA["investment"]
    if df.empty:
        return {}
    region_agg = df.groupby("region")["alltime_total_medals"].sum().reset_index()
    fig = px.treemap(
        region_agg,
        path=["region"],
        values="alltime_total_medals",
        title="Global Medal Share by Continental Region",
        template="plotly_dark",
        color="alltime_total_medals",
        color_continuous_scale=["#0d2137", "#f4c300"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_top_sports_by_medals():
    """Bar — which sport categories produce the most medals."""
    df = DATA["athletes"]
    if df.empty or "sport_category" not in df.columns:
        return {}
    agg = df.groupby("sport_category")["sport_medals"].sum().reset_index()
    agg = agg.nlargest(12, "sport_medals").sort_values("sport_medals")
    fig = px.bar(
        agg, x="sport_medals", y="sport_category",
        orientation="h",
        title="Top 12 Sport Categories by Medals Produced",
        labels={"sport_medals": "Total Medals", "sport_category": "Sport"},
        template="plotly_dark",
        color="sport_medals",
        color_continuous_scale=["#1a3a5c", "#df3e41"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
        coloraxis_showscale=False,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_host_advantage():
    """
    NEW FEATURE — Host Nation Advantage.
    Compares a host country's medals in the hosting year vs their average
    in the two Games before and after hosting.
    """
    df = DATA["medals"]
    gs = DATA["games"]
    if df.empty or gs.empty:
        return {}

    results = []
    for _, row in gs.iterrows():
        host = row["host_country"]
        year = row["year"]

        host_rows = df[df["country"] == host]
        if host_rows.empty:
            continue

        host_year_row = host_rows[host_rows["year"] == year]
        host_medals = host_year_row["total_medals"].sum() if not host_year_row.empty else None

        other_years = host_rows[host_rows["year"] != year]["total_medals"]
        avg_other = round(other_years.mean(), 1) if not other_years.empty else None

        if host_medals is not None and avg_other is not None:
            results.append({
                "year": year,
                "host": host,
                "host_year_medals": host_medals,
                "avg_other_years": avg_other,
                "advantage": round(host_medals - avg_other, 1),
            })

    if not results:
        return {}

    result_df = pd.DataFrame(results)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=result_df["year"].astype(str) + " – " + result_df["host"],
        y=result_df["host_year_medals"],
        name="As Host",
        marker_color="#f4c300",
    ))
    fig.add_trace(go.Bar(
        x=result_df["year"].astype(str) + " – " + result_df["host"],
        y=result_df["avg_other_years"],
        name="Avg (Other Years)",
        marker_color="#1a3a5c",
    ))
    fig.update_layout(
        barmode="group",
        title="Host Nation Advantage: Hosting Year vs Average",
        xaxis_title="Olympic Games — Host Country",
        yaxis_title="Total Medals",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
        xaxis_tickangle=-30,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_efficiency_ranking():
    """
    NEW FEATURE — Medal Efficiency Leaderboard.
    Ranks countries by avg_efficiency_pct with a color gradient.
    """
    df = DATA["investment"]
    if df.empty:
        return {}
    top = df.nlargest(20, "avg_efficiency_pct").sort_values("avg_efficiency_pct")
    fig = px.bar(
        top, x="avg_efficiency_pct", y="country",
        orientation="h",
        title="Top 20 Most Efficient Medal-Winning Nations",
        labels={"avg_efficiency_pct": "Medal Efficiency (%)", "country": "Country"},
        template="plotly_dark",
        color="avg_efficiency_pct",
        color_continuous_scale=["#1a3a5c", "#00c853"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e0e0e0",
        title_font_size=16,
        coloraxis_showscale=False,
    )
    return json.loads(json.dumps(fig, cls=PlotlyJSONEncoder))


def chart_country_over_time(country):
    """
    NEW FEATURE — Country Deep-Dive.
    Returns gold/silver/bronze trend for any queried country.
    """
    return chart_gold_silver_bronze_breakdown(country=country)


# ---------------------------------------------------------------------------
# KPI Summary Cards
# ---------------------------------------------------------------------------
def compute_kpis():
    """Return a dict of headline statistics shown on the dashboard."""
    medals_df = DATA["medals"]
    athletes_df = DATA["athletes"]
    invest_df = DATA["investment"]
    games_df = DATA["games"]

    kpis = {}
    kpis["total_countries"] = int(invest_df["country"].nunique()) if not invest_df.empty else 0
    kpis["total_games"] = int(games_df["year"].nunique()) if not games_df.empty else 0
    kpis["total_athletes"] = int(athletes_df["Name"].nunique()) if not athletes_df.empty else 0
    kpis["total_sports"] = int(athletes_df["sport_category"].nunique()) if not athletes_df.empty else 0

    if not invest_df.empty:
        top_country = invest_df.loc[invest_df["alltime_total_medals"].idxmax()]
        kpis["top_country"] = top_country["country"]
        kpis["top_country_medals"] = int(top_country["alltime_total_medals"])
        most_efficient = invest_df.loc[invest_df["avg_efficiency_pct"].idxmax()]
        kpis["most_efficient"] = most_efficient["country"]
        kpis["most_efficient_pct"] = round(float(most_efficient["avg_efficiency_pct"]), 1)
    else:
        kpis.update({"top_country": "N/A", "top_country_medals": 0,
                     "most_efficient": "N/A", "most_efficient_pct": 0})
    return kpis


def get_country_list():
    """Return sorted list of all countries for the search/filter UI."""
    df = DATA["investment"]
    if df.empty:
        return []
    return sorted(df["country"].dropna().unique().tolist())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    kpis = compute_kpis()
    countries = get_country_list()
    return render_template("index.html", kpis=kpis, countries=countries)


@app.route("/api/charts/overview")
def api_overview_charts():
    """Return all overview dashboard charts in one call."""
    return jsonify({
        "medal_trends":     chart_medal_trends_over_time(),
        "top_countries":    chart_top_countries_medals(),
        "region_share":     chart_region_medal_share(),
        "gender_split":     chart_gender_split_by_sport(),
        "top_sports":       chart_top_sports_by_medals(),
        "efficiency_vs_inv": chart_efficiency_vs_investment(),
        "host_advantage":   chart_host_advantage(),
        "efficiency_rank":  chart_efficiency_ranking(),
    })


@app.route("/api/charts/country")
def api_country_chart():
    """Return medal breakdown chart for a specific country."""
    country = request.args.get("name", "")
    if not country:
        return jsonify({"error": "No country specified"}), 400

    # Check whether the country actually exists in the dataset before charting
    df = DATA["medals"]
    if df.empty or country not in df["country"].values:
        return jsonify({"error": f"No data found for '{country}'"}), 404

    chart = chart_country_over_time(country)
    if not chart:
        return jsonify({"error": f"No data found for '{country}'"}), 404
    return jsonify(chart)


@app.route("/api/leaderboard")
def api_leaderboard():
    """Return top-N countries as JSON table data for the leaderboard tab."""
    df = DATA["investment"]
    if df.empty:
        return jsonify([])
    top = df.nlargest(20, "alltime_total_medals")[
        ["country", "region", "alltime_total_medals", "avg_efficiency_pct", "sports_investment"]
    ].round(2)
    top = top.rename(columns={
        "alltime_total_medals": "Total Medals",
        "avg_efficiency_pct":  "Efficiency (%)",
        "sports_investment":   "Investment (M$)",
    })
    return jsonify(top.to_dict(orient="records"))


@app.route("/api/search")
def api_search():
    """Full-text search across country names."""
    query = request.args.get("q", "").strip().lower()
    df = DATA["investment"]
    if df.empty or not query:
        return jsonify([])
    matches = df[df["country"].str.lower().str.contains(query, na=False)]
    result = matches[["country", "noc_code", "region", "alltime_total_medals"]].to_dict(orient="records")
    return jsonify(result)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*60)
    print("  Olympic Performance Intelligence Platform")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("="*60)
    app.run(debug=True, port=5000)
