import pandas as pd
from pydantic import BaseModel

class ScoringWeights(BaseModel):
    # Offense
    r: float = 0.0
    b1: float = 0.0
    b2: float = 0.0
    b3: float = 0.0
    hr: float = 0.0
    tb: float = 0.0
    rbi: float = 0.0
    bb_hit: float = 0.0
    k_hit: float = 0.0
    sb: float = 0.0
    ab: float = 0.0
    h_hit: float = 0.0
    xbh: float = 0.0
    gwrbi: float = 0.0
    ibb: float = 0.0
    hbp_hit: float = 0.0
    sac: float = 0.0
    cs: float = 0.0
    sbn: float = 0.0
    gidp: float = 0.0
    cyc: float = 0.0
    gshr: float = 0.0
    btw: float = 0.0
    btl: float = 0.0
    
    # Pitching
    ip_outs: float = 0.0
    er: float = 0.0
    k_pitch: float = 0.0
    sho: float = 0.0
    w: float = 0.0
    l: float = 0.0
    sv: float = 0.0
    bs: float = 0.0
    g: float = 0.0
    gs: float = 0.0
    h_allow: float = 0.0
    ra: float = 0.0
    hr_allow: float = 0.0
    bb_allow: float = 0.0
    hb_pitch: float = 0.0
    wp: float = 0.0
    balks: float = 0.0
    pko: float = 0.0
    qs: float = 0.0
    cg: float = 0.0
    nh: float = 0.0
    pg: float = 0.0
    bf: float = 0.0
    pc: float = 0.0
    sop: float = 0.0
    hd: float = 0.0
    ptw: float = 0.0
    ptl: float = 0.0
    svhd: float = 0.0

def calculate_fantasy_points(df: pd.DataFrame, weights: ScoringWeights, is_pitcher: bool = False):
    """Calculates total fantasy points using exhaustive user inputs."""
    df = df.copy()
    
    if not is_pitcher:
        # Derive composite stats if they aren't explicitly in the dataset
        singles = df.get('H', 0) - df.get('2B', 0) - df.get('3B', 0) - df.get('HR', 0)
        xbh = df.get('2B', 0) + df.get('3B', 0) + df.get('HR', 0)
        sbn = df.get('SB', 0) - df.get('CS', 0)
        
        # Use .get() to prevent KeyError on rare stats like GWRBI or CYC
        df['Fantasy_Points'] = (
            (df.get('R', 0) * weights.r) +
            (singles * weights.b1) +
            (df.get('2B', 0) * weights.b2) +
            (df.get('3B', 0) * weights.b3) +
            (df.get('HR', 0) * weights.hr) +
            (df.get('TB', 0) * weights.tb) +
            (df.get('RBI', 0) * weights.rbi) +
            (df.get('BB', 0) * weights.bb_hit) +
            (df.get('SO', 0) * weights.k_hit) + 
            (df.get('SB', 0) * weights.sb) +
            (df.get('AB', 0) * weights.ab) +
            (df.get('H', 0) * weights.h_hit) +
            (xbh * weights.xbh) +
            (df.get('GWRBI', 0) * weights.gwrbi) +
            (df.get('IBB', 0) * weights.ibb) +
            (df.get('HBP', 0) * weights.hbp_hit) +
            (df.get('SH', 0) + df.get('SF', 0)) * weights.sac + 
            (df.get('CS', 0) * weights.cs) +
            (sbn * weights.sbn) +
            (df.get('GIDP', 0) * weights.gidp) +
            (df.get('CYC', 0) * weights.cyc) +
            (df.get('GSHR', 0) * weights.gshr) +
            (df.get('BTW', 0) * weights.btw) +
            (df.get('BTL', 0) * weights.btl)
        )
    else:
        # Calculate outs from IP. Standard fractional IP: 1.1 = 1 inning, 1 out (4 total outs)
        # We handle this by multiplying whole innings by 3, and adding the remainder decimal * 10
        # e.g., 5.2 IP -> (5 * 3) + (2) = 17 outs. 
        # (FanGraphs/pybaseball typically provide IP as floats like 5.1, 5.2)
        outs = (df.get('IP', 0) // 1 * 3) + ((df.get('IP', 0) % 1) * 10)
        
        svhd = df.get('SV', 0) + df.get('HLD', 0)
        sop = df.get('SV', 0) + df.get('BS', 0)
        
        df['Fantasy_Points'] = (
            (outs * weights.ip_outs) +
            (df.get('ER', 0) * weights.er) +
            (df.get('SO', 0) * weights.k_pitch) +
            (df.get('SHO', 0) * weights.sho) +
            (df.get('W', 0) * weights.w) +
            (df.get('L', 0) * weights.l) +
            (df.get('SV', 0) * weights.sv) +
            (df.get('BS', 0) * weights.bs) +
            (df.get('G', 0) * weights.g) +
            (df.get('GS', 0) * weights.gs) +
            (df.get('H', 0) * weights.h_allow) +
            (df.get('R', 0) * weights.ra) +
            (df.get('HR', 0) * weights.hr_allow) +
            (df.get('BB', 0) * weights.bb_allow) +
            (df.get('HBP', 0) * weights.hb_pitch) +
            (df.get('WP', 0) * weights.wp) +
            (df.get('BK', 0) * weights.balks) +
            (df.get('PKO', 0) * weights.pko) +
            (df.get('QS', 0) * weights.qs) +
            (df.get('CG', 0) * weights.cg) +
            (df.get('NH', 0) * weights.nh) +
            (df.get('PG', 0) * weights.pg) +
            (df.get('TBF', 0) * weights.bf) +
            (df.get('Pitches', 0) * weights.pc) +
            (sop * weights.sop) +
            (df.get('HLD', 0) * weights.hd) +
            (df.get('PTW', 0) * weights.ptw) +
            (df.get('PTL', 0) * weights.ptl) +
            (svhd * weights.svhd)
        )
    return df

def filter_player_pool(df_hitters: pd.DataFrame, df_pitchers: pd.DataFrame):
    """Splits pitchers and applies the volume + fantasy points threshold."""
    df_pitchers['is_SP'] = (df_pitchers.get('GS', 0) / df_pitchers.get('G', 1)) > 0.5
    df_starters = df_pitchers[df_pitchers['is_SP']]
    df_relievers = df_pitchers[~df_pitchers['is_SP']]

    hitters_final = df_hitters[df_hitters.get('PA', 0) >= 250].sort_values(by='Fantasy_Points', ascending=False).head(250)
    starters_final = df_starters[df_starters.get('IP', 0) >= 80].sort_values(by='Fantasy_Points', ascending=False).head(150)
    relievers_final = df_relievers[df_relievers.get('G', 0) >= 30].sort_values(by='Fantasy_Points', ascending=False).head(100)
    
    return hitters_final, starters_final, relievers_final