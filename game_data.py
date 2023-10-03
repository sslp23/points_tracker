import pandas as pd
from tqdm import tqdm
tqdm.pandas()
import numpy as np
import sys

from downloader import *

def get_matches_data(cid, sns):
    full_matches = []#pd.DataFrame([])

    for season in tqdm(sns):
        base_link = f"https://fbref.com/en/comps/{cid}/{season}/schedule/{season}-Scores-and-Fixtures"
        page = get_page(base_link)
        time.sleep(2)
        matches = pd.read_html(page.content)[0]

        soup = BeautifulSoup(page.content, features = "lxml")
        mrs = soup.find_all("td", {"data-stat": "match_report"})
        
        game_links = []
        ids = []

        for mr, note in zip(mrs, matches.Notes):
            try:
                game_links.append(mr.find("a")["href"])
                ids.append(mr.find("a")["href"].split("/")[3])
            except:
                if note == "Match Postponed":
                    print("match postponed")
                    game_links.append(" ")
                    ids.append(" ")
                pass

        matches = matches.dropna(how="all")
        #try:
        matches["game_link"] = game_links
        matches["ids"] = ids
        #except:
       # 	matches["game_link"] = [" "]*len(matches)
        #	matches["ids"] = [" "]*len(matches)
        

        matches["Season"] = [season]*len(matches)
        full_matches.append(matches)

    fm_df = pd.concat(full_matches)
        
    return fm_df


def main():
	## USAGE EXAMPLE
	## python game_data.py Brasileirao 2019 2023 -> to populate db
	## python game_data.py Brasileirao 2023 2023 update -> to update 2023 season
	leagues = {"Premier League": "9", "Championship": "10", "Bundesliga": "9", "La Liga": "12", "Liga Portugal": "32", "Ligue 1": "13", "Serie A": "11", "Eredivisie": "23", "MLS": "22", "Brasileirao": "24"}

	try:
		how = sys.agrv[4]
		
	except:
		how = "full"

	league = sys.argv[1].replace("_", " ")
	season_st = int(sys.argv[2])
	season_end = int(sys.argv[3])
	comp_id = leagues[league]

	if league not in ["MLS", "Brasileirao"]:
		seasons_raw = np.arange(season_st, season_end+1)
		seasons = [str(a-1)+"-"+str(a) for a in seasons_raw]
	else:
		seasons = np.arange(season_st, season_end+1)
	fm = get_matches_data(comp_id, seasons)

	fm["Home_Score"] = fm.Score.str.split("–").str[0]
	fm["Away_Score"] = fm.Score.str.split("–").str[1]

	fm = fm.rename({"xG": "Home_xG", "xG.1": "Away_xG"}, axis=1)

	#print(fm)


	if how == "full":
		fm.to_csv(f"game_db/{league}_games.csv", index=False)
	else:
		old_data = pd.read_csv(f"game_db/{league}_games.csv")
		past_data = old_data[old_data["Season"] != season_end]
		new_data = pd.concat([past_data, fm])
		new_data.to_csv(f"game_db/{league}_games.csv", index=False)
	#fm.to_csv("test.csv", index=False)

if __name__ == '__main__':
	main()