from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.graphs import build_dashboard_graphs
from backend.fetcher import fetch_raw_data
from backend.processing import DashboardPayload, calculate_fantasy_points, filter_player_pool

raw_data_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    hit_act, pit_act, hit_proj, pit_proj = fetch_raw_data()
    raw_data_cache['hit_act'] = hit_act
    raw_data_cache['pit_act'] = pit_act
    raw_data_cache['hit_proj'] = hit_proj
    raw_data_cache['pit_proj'] = pit_proj
    yield

app = FastAPI(title="Fantasy Baseball Scoring Sandbox", lifespan=lifespan)

# Mount the static directory to serve the vanilla HTML, CSS, and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_frontend():
    """Serves the main vanilla HTML interface."""
    return FileResponse("static/index.html")

@app.post("/api/calculate")
async def generate_dashboard_data(payload: DashboardPayload):
    """
    Receives user weights and roster settings, calculates points, 
    filters pools dynamically, and returns Plotly JSON graphs.
    """
    hit_act, pit_act, hit_proj, pit_proj = fetch_raw_data()
    
    # Process Actuals (Pass payload.weights for math, payload.rosters for filtering)
    hit_act = calculate_fantasy_points(hit_act, payload.weights, is_pitcher=False)
    pit_act = calculate_fantasy_points(pit_act, payload.weights, is_pitcher=True)
    hit_act_final, sp_act_final, rp_act_final = filter_player_pool(hit_act, pit_act, payload.rosters)
    
    # Process Projections
    hit_proj = calculate_fantasy_points(hit_proj, payload.weights, is_pitcher=False)
    pit_proj = calculate_fantasy_points(pit_proj, payload.weights, is_pitcher=True, true_decimal_ip=True)
    hit_proj_final, sp_proj_final, rp_proj_final = filter_player_pool(hit_proj, pit_proj, payload.rosters)
    
    # Generate Graphs
    actuals_graphs = build_dashboard_graphs(hit_act_final, sp_act_final, rp_act_final, payload.weights, pitcher_talent_stat='xFIP')
    proj_graphs = build_dashboard_graphs(hit_proj_final, sp_proj_final, rp_proj_final, payload.weights, pitcher_talent_stat='FIP')
        
    return {
        "status": "success", 
        "actuals": actuals_graphs,
        "projections": proj_graphs
    }

# Run the server using: uvicorn main:app --reload