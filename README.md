# Fantasy Baseball Scoring Sandbox

A web app for visualizing how different fantasy baseball scoring systems affect player values. Adjust scoring weights, run calculations, and explore interactive charts showing positional distributions, talent-to-points relationships, and the scoring economy across hitters, starting pitchers, and relief pitchers.

**Live demo:** [fantasysandbox.onrender.com](https://fantasysandbox.onrender.com)

> Note: The app is hosted on Render's free tier, so it may take 30–60 seconds to load if it hasn't been used recently.

---

## Features

- **Custom scoring weights** for an exhaustive list of hitting and pitching categories
- **Preset configurations** for ESPN, Ottoneu, and a custom league
- **Actuals vs. Projections** — compare last season's results against Steamer projections for the upcoming season
- **Six interactive Plotly charts** per tab:
  - Positional raincloud plot (distribution & scarcity across hitters, SPs, RPs)
  - Hitter scatter plot: wRC+ vs. Fantasy Points
  - Starting pitcher scatter plot: xFIP (actuals) / FIP (projections) vs. Fantasy Points
  - Scoring economy pie charts for hitters, SPs, and RPs
- **PDF export** of the full dashboard
- Dark mode UI with a monospace aesthetic

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| Data | pybaseball, FanGraphs API (Steamer projections) |
| Visualization | Plotly |
| Frontend | Vanilla HTML, CSS, JavaScript |

---

## Local Development

**Requirements:** Python 3.9+

1. Clone the repository:
   ```bash
   git clone https://github.com/calebfinamore/fantasy-scoring-visualizer
   cd fantasy-scoring-visualizer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

4. Open your browser and navigate to `http://localhost:8000`

---

## Usage

1. Select a preset or manually enter scoring weights for hitting and pitching categories
2. Click **RUN CALCULATIONS**
3. Explore the **Actuals** and **Projections** tabs to compare results
4. Use **Generate PDF** to export the dashboard

---

## Data Sources

- **Actuals** — FanGraphs batting and pitching stats via [pybaseball](https://github.com/jldbc/pybaseball), filtered to your league's size based on roster inputs.
- **Projections** — [Steamer projections](https://www.fangraphs.com/projections) via the FanGraphs API

Player pool is dynamically determined by the current date: before November, actuals reflect the previous season and projections reflect the current season; after November, both shift forward one year.

---

## Notes on Scoring

- **IP scoring** is calculated per out. If your league awards points per inning (e.g. 3 pts/IP), divide by 3 to get the per-out value (e.g. 1.0).
- Some categories (Cycles, Grand Slams, Team Wins/Losses, No-Hitters, Perfect Games, Pick Offs) are not available in the FanGraphs data sources and will always contribute 0 points regardless of the weight assigned. These are included in the UI for completeness.
- Steamer projections do not include xFIP, so the pitcher scatter plot uses xFIP for actuals and FIP for projections.

---

## Project Structure

```
fantasy-scoring-visualizer/
├── main.py               # FastAPI app and API endpoint
├── backend/
│   ├── fetcher.py        # Data fetching (pybaseball + FanGraphs API)
│   ├── processing.py     # Scoring calculations and player pool filtering
│   └── graphs.py         # Plotly graph generation
└── static/
    ├── index.html
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```
