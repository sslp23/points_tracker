import pandas as pd
from tqdm import tqdm
tqdm.pandas()
import numpy as np
import sys

from downloader import *


def get_match_shots(links, ids, hts, ats):
    fb_link = f"https://fbref.com"
    full_teams = []
    for l, id_, ht, at  in tqdm(zip(links, ids, hts, ats)):
        page = get_page(fb_link+l)
        time.sleep(2)
        ##matches = pd.read_html(page.content)[0]
        

        shots = pd.read_html(page.content)[-3]
        
        #COLUMN ADJUSTMENT
        level1 = shots.columns.droplevel(1)
        level0 = shots.columns.droplevel(0)
        
        new_cols = []
        for l1, l0 in zip(level1, level0):
            
            if "Unnamed" in l1:
                col_base = l0
            else:
                col_base = l0+"_"+l1
            
            new_cols.append(col_base)
        shots.columns = new_cols#shots.columns.droplevel(0)
        shots = shots[~shots.Minute.isna()]
        
        shots["match_id"] = [id_]*len(shots)
        full_teams.append(shots)
    
    match_shots = pd.concat(full_teams)
    #match_shots[]
    return match_shots

def main():
    ## USAGE EXAMPLE
    
    ## python match_details.py Brasileirao 2023 -> add details to brasileirao 2023, adding data from games that didn't happened yet
    ## needed -> game_db/{league}_games.csv and game_db/{league}_games_det.csv
    leagues = {"Premier League": "9", "Championship": "10", "Bundesliga": "9", "La Liga": "12", "Liga Portugal": "32", "Ligue 1": "13", "Serie A": "11", "Eredivisie": "23", "MLS": "22", "Brasileirao": "24"}

    league = sys.argv[1].replace("_", " ")
    season_st = int(sys.argv[2])

    full_matches = pd.read_csv(f'game_db/{league}_games.csv')
    try:    
        det_matches = pd.read_csv(f'game_db/{league}_games_det.csv')
    except:
        pd.DataFrame([], columns=["match_id"]).to_csv(f"game_db/{league}_games_det.csv", index=False)
        det_matches = pd.read_csv(f'game_db/{league}_games_det.csv')

    det_ids = det_matches.match_id.unique()
    full_matches = full_matches[~full_matches.Score.isna()]

    matches_to_add = full_matches[~full_matches.ids.isin(det_ids)]
    print(len(matches_to_add.ids.values))

    ms = get_match_shots(matches_to_add.game_link.values, matches_to_add.ids.values, matches_to_add.Home.values, matches_to_add.Away.values)

    ms.reset_index(inplace=True, drop=True)

    new_det_matches = pd.concat([det_matches, ms])

    new_det_matches.to_csv(f"game_db/{league}_games_det.csv", index=False)

if __name__ == '__main__':
    main()