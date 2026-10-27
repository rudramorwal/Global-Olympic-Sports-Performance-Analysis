# Olympic Performance Intelligence Platform

A full-stack data analytics web application built with **Python, Flask, Pandas, and Plotly** — analyzing over 35 years of Olympic Games data (1992–2026) across 60 nations, 25 sports, and 800+ athletes.

---

## 🏅 Features

- **8 interactive Plotly charts** — medal trends, regional treemaps, investment vs efficiency scatter, gender split, top sports, and more
- **Host Nation Advantage** — original analytical feature quantifying home-advantage per Games
- **Medal Efficiency Leaderboard** — ranks nations by medals-per-athlete sent
- **Country Deep-Dive** — dynamic chart for any of 60 countries via REST API
- **Live KPI cards** — computed in real-time from Pandas DataFrames
- **29 automated tests** — covering data loading, chart generation, and all API routes

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3, Flask |
| Data | Pandas, NumPy |
| Charts | Plotly (server) + Plotly.js (client) |
| Frontend | Bootstrap 5, custom CSS |
| Tests | Python `unittest` |

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate.bat   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py

# 5. Open in browser
# http://127.0.0.1:5000
```

## 🧪 Run Tests

```bash
python test_app.py
# Expected: Ran 29 tests in ~0.6s   OK
```

## 📁 Project Structure

```
├── app.py                  # Flask backend — routes, data loading, Plotly charts
├── requirements.txt        # Python dependencies
├── test_app.py             # 29 automated tests
├── templates/
│   └── index.html          # Frontend — Bootstrap 5 + Plotly.js
└── DataSets - .../
    └── Cleaned Datasets/
        ├── medal_results.csv       # 910 rows — per-country per-Games medals
        ├── athletes_cleaned.csv    # 1,548 rows — athlete & sport data
        ├── games_summary.csv       # 18 rows — Games host/year summary
        └── alltime_investment.csv  # 60 rows — country investment & efficiency
```

## 📊 Key Insights from the Data

- **China** leads all-time medals (427), followed by **Great Britain** (417) and **USA** (405)
- **Tunisia** and **Slovenia** are the most medal-efficient nations (45%+)
- Host nations consistently outperform their historical average — home advantage is measurable
- Sports investment correlates with total medals but shows diminishing returns for large delegations

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Homepage (server-rendered HTML) |
| `GET /api/charts/overview` | All 8 chart figures as JSON |
| `GET /api/charts/country?name=X` | Medal breakdown for country X |
| `GET /api/leaderboard` | Top 20 nations table data |
| `GET /api/search?q=X` | Country search |

## 📄 License

Academic project — for educational purposes.
