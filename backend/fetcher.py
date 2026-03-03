import datetime
import pandas as pd
import requests
from pybaseball import batting_stats, pitching_stats

def get_dynamic_years():
    """Determines actuals and projections years based on the current date."""
    today = datetime.date.today()
    # If before November, actuals = last year, projections = this year.
    if today.month < 11:
        return today.year - 1, today.year
    return today.year, today.year + 1

def fetch_raw_data():
    """Fetches FanGraphs actuals and Steamer projections."""
    actuals_yr, proj_yr = get_dynamic_years()
    
    # 1. Actuals via pybaseball (loose volume floor to capture injured stars)
    # qual=200 for hitters, qual=30 for pitchers speeds up the query significantly
    hit_actuals = batting_stats(actuals_yr, qual=200)
    pitch_actuals = pitching_stats(actuals_yr, qual=30)
    
    # 2. Projections via FanGraphs API directly
    # Steamer projections are natively returned as JSON, which pandas handles beautifully
    bat_url = "https://www.fangraphs.com/api/projections?stats=bat&pos=all&type=steamer"
    pit_url = "https://www.fangraphs.com/api/projections?stats=pit&pos=all&type=steamer"
    
    steamer_bat = pd.DataFrame(requests.get(bat_url).json())
    steamer_pit = pd.DataFrame(requests.get(pit_url).json())
    
    return hit_actuals, pitch_actuals, steamer_bat, steamer_pit