from joblib import Parallel, delayed
import api_service

import api_service
import pandas as pd

from api_types import MatchDetails
from typing import List

from processing import export_data, filter_women_leagues, preprocess_data
from constants import country_names


from processing import export_data, filter_women_leagues
from constants import country_names

def scrap_league(league):
  all_matches_details = []
  try:
    print("Getting league details for League: ", league.id)
    seasons_cor = api_service.get_all_available_seasons(league.id)
    seasons = asyncio.run(seasons_cor)
    print("  Found ", seasons, " Seasons for league: ", league.id)
    for season in seasons:
      try:
        league_season_cor = api_service.get_league_by_id_season(league.id, league.ccode, season)
        league_season = asyncio.run(league_season_cor)
        if league_season is None:
          continue

        first_unplayed_match_idx = -1

        if league_season.matches.firstUnplayedMatch is not None:
          first_unplayed_match_idx = league_season.matches.firstUnplayedMatch.firstUnplayedMatchIndex

        print("Getting match details for League: ", league_season.details.name)
        print("  Found ", first_unplayed_match_idx, " Matches")

        # get all played matches
        for match in league_season.matches.allMatches[:first_unplayed_match_idx]:
          try:
            match_details_cor= api_service.get_match_details_by_id(match.id, season)
            match_details = asyncio.run(match_details_cor)
            if (match_details is not None):
              match_details.ccode = league_season.details.ccode
              all_matches_details.append(match_details)
          except Exception as e:
            print("Error: ", e)

        print('Total', len(all_matches_details), 'matches found')
        fname = 'matches_{}_{}_{}.csv'.format(
          country_names[league_season.details.ccode], league_season.details.name, season
        )
        print('Exporting data to csv file: ', fname, '...')

        export_data(
          all_matches_details,
          fname)
      except Exception as e:
          err = "Error while getting league {} season {} matches: {}\n".format(league.id, season, e)
          print(err)
          # log error to logs/ folder
          with open('logs/errors.log'.format(
              country_names[league_season.details.ccode], league_season.details.name, season
          ), 'a+') as f:
              f.write(err)
      all_matches_details = []

  except Exception as e:
      print("Error: ", e)





async def main():
  all_leagues = await api_service.get_all_leagues_by_country()
  mens_leagues = filter_women_leagues(all_leagues)
  # remove france ligue 1
  mens_leagues = [league for league in mens_leagues]

  Parallel(n_jobs=16)(delayed(scrap_league)(league) for league in mens_leagues)
     
    

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
