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

class RosterSettings(BaseModel):
    teams: int = 0
    hitters: int = 0
    sp: int = 0
    rp: int = 0

class DashboardPayload(BaseModel):
    weights: ScoringWeights
    rosters: RosterSettings

def calculate_fantasy_points(df: pd.DataFrame, weights: ScoringWeights, is_pitcher: bool = False, true_decimal_ip=False):
    """Calculates total fantasy points using exhaustive user inputs."""
    df = df.copy()
        
    expected_hitting_cols = [
    'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI', 'BB', 'SO', 'SB', 'AB',
    'GWRBI', 'IBB', 'HBP', 'SH', 'SF', 'CS', 'GIDP', 'CYC', 'GSHR', 'BTW', 'BTL'
    ]
    expected_pitching_cols = [
        'IP', 'ER', 'W', 'L', 'SV', 'BS', 'G', 'GS', 'WP', 'BK', 'PKO',
        'QS', 'CG', 'NH', 'PG', 'TBF', 'Pitches', 'HLD', 'SHO', 'PTW', 'PTL'
    ]

    expected_cols = expected_pitching_cols if is_pitcher else expected_hitting_cols
    for col in expected_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)        
    if not is_pitcher:
        
        # Derive composite stats if they aren't explicitly in the dataset
        singles = df.get('H', 0) - df.get('2B', 0) - df.get('3B', 0) - df.get('HR', 0)
        xbh = df.get('2B', 0) + df.get('3B', 0) + df.get('HR', 0)
        sbn = df.get('SB', 0) - df.get('CS', 0)
        if 'TB' not in df.columns or df['TB'].sum() == 0:
            df['TB'] = df['H'] + df['2B'] + (2 * df['3B']) + (3 * df['HR'])
        
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
        if true_decimal_ip:
            outs = df['IP'] * 3
        else:
            outs = (df['IP'] // 1 * 3) + ((df['IP'] % 1) * 10)

        svhd = df.get('SV', 0) + df.get('HLD', 0)
        sop = df.get('SV', 0) + df.get('BS', 0)

        terms = [
            ('ip_outs',   outs * weights.ip_outs),
            ('er',        df['ER'] * weights.er),
            ('k_pitch',   df['SO'] * weights.k_pitch),
            ('sho',       df['SHO'] * weights.sho),
            ('w',         df['W'] * weights.w),
            ('l',         df['L'] * weights.l),
            ('sv',        df['SV'] * weights.sv),
            ('bs',        df['BS'] * weights.bs),
            ('g',         df['G'] * weights.g),
            ('gs',        df['GS'] * weights.gs),
            ('h_allow',   df['H'] * weights.h_allow),
            ('ra',        df['R'] * weights.ra),
            ('hr_allow',  df['HR'] * weights.hr_allow),
            ('bb_allow',  df['BB'] * weights.bb_allow),
            ('hb_pitch',  df['HBP'] * weights.hb_pitch),
            ('wp',        df['WP'] * weights.wp),
            ('balks',     df['BK'] * weights.balks),
            ('pko',       df['PKO'] * weights.pko),
            ('qs',        df['QS'] * weights.qs),
            ('cg',        df['CG'] * weights.cg),
            ('nh',        df['NH'] * weights.nh),
            ('pg',        df['PG'] * weights.pg),
            ('bf',        df['TBF'] * weights.bf),
            ('pc',        df['Pitches'] * weights.pc),
            ('sop',       sop * weights.sop),
            ('hd',        df['HLD'] * weights.hd),
            ('ptw',       df['PTW'] * weights.ptw),
            ('ptl',       df['PTL'] * weights.ptl),
            ('svhd',      svhd * weights.svhd),
        ]

        running = 0
        for name, term in terms:
            running = running + term
            if hasattr(running, 'isna') and running.isna().any():
                print(f"NaN introduced at: {name}")
                print(f"term head: {term.head(3).tolist()}")
                print(f"term dtype: {term.dtype}")
                break

        df['Fantasy_Points'] = sum(t for _, t in terms)
    return df

def filter_player_pool(df_hitters, df_pitchers, rosters: RosterSettings):
    df_pitchers['is_SP'] = (df_pitchers['GS'] / df_pitchers['G'].replace(0, 1)) > 0.5
    df_starters = df_pitchers[df_pitchers['is_SP']]
    df_relievers = df_pitchers[~df_pitchers['is_SP']]

    # Your 1.5x Waiver Wire Buffer Logic
    hit_limit = round(rosters.teams * rosters.hitters * 1.5)
    sp_limit = round(rosters.teams * rosters.sp * 1.5)
    rp_limit = round(rosters.teams * rosters.rp * 1.5)

    hitters_final = df_hitters.sort_values(by='Fantasy_Points', ascending=False).head(hit_limit)
    starters_final = df_starters.sort_values(by='Fantasy_Points', ascending=False).head(sp_limit)
    relievers_final = df_relievers.sort_values(by='Fantasy_Points', ascending=False).head(rp_limit)

    return hitters_final, starters_final, relievers_final