from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.graphs import build_dashboard_graphs

# Import our custom backend modules
from backend.fetcher import fetch_raw_data
from backend.processing import ScoringWeights, calculate_fantasy_points, filter_player_pool

app = FastAPI(title="Fantasy Baseball Scoring Sandbox")

# Mount the static directory to serve the vanilla HTML, CSS, and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main vanilla HTML interface."""
    return FileResponse("static/index.html")

@app.post("/api/calculate")
async def generate_dashboard_data(weights: ScoringWeights):
    """
    Receives user weights, calculates points, filters pools, 
    and returns Plotly JSON graphs for the dashboard.
    """
    # 1. Fetch the raw Actuals and Projections data
    hit_act, pit_act, hit_proj, pit_proj = fetch_raw_data()
    print(pit_proj.columns.tolist())
    
    # 2. Process Actuals
    hit_act = calculate_fantasy_points(hit_act, weights, is_pitcher=False)
    pit_act = calculate_fantasy_points(pit_act, weights, is_pitcher=True)
    hit_act_final, sp_act_final, rp_act_final = filter_player_pool(hit_act, pit_act)
    
    # 3. Process Projections
    hit_proj = calculate_fantasy_points(hit_proj, weights, is_pitcher=False)
    pit_proj = calculate_fantasy_points(pit_proj, weights, is_pitcher=True, true_decimal_ip=True)
    hit_proj_final, sp_proj_final, rp_proj_final = filter_player_pool(hit_proj, pit_proj)
    
    # 4. Generate Plotly JSON objects (To be implemented next)
    actuals_graphs = build_dashboard_graphs(hit_act_final, sp_act_final, rp_act_final, weights, pitcher_talent_stat='xFIP')
    proj_graphs = build_dashboard_graphs(hit_proj_final, sp_proj_final, rp_proj_final, weights, pitcher_talent_stat='FIP')
        
    return {
        "status": "success", 
        "message": "Calculations complete. Ready for graph generation.",
        "actuals": actuals_graphs,
        "projections": proj_graphs
    }

# Run the server using: uvicorn main:app --reload