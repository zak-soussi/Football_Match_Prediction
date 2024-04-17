import pandas as pd
from api_types import CountryLeagueList, MatchDetails, MatchStats
from typing import List
from constants import country_names


def flatten_stats_by_key(stats: List[MatchStats], key: str):
    '''
      flattens the stats by keys
      stats: List[MatchStats]
      key: str
      return: dict of stats of format 'key_home' and 'key_away'
    '''
    stats_dict = {}
    for statGrouped in stats:
        for stat in statGrouped.stats:
            # check for duplicates
            if stat.key in stats_dict:
                stats_dict[stat.key.value + '_home_duplicate'] = stat.stats[0]
                stats_dict[stat.key.value + '_away_duplicate'] = stat.stats[1]
            else:
                stats_dict[stat.key.value + '_home'] = stat.stats[0]
                stats_dict[stat.key.value + '_away'] = stat.stats[1]
    return stats_dict


def preprocess_data(matches: List[MatchDetails]):
    preprocessed_data = []
    print("LENGTH", len(matches))
    for match in matches:
        try:
            new_match = {}
            new_match['matchId'] = match.matchFacts.matchId
            new_match['homeTeam'] = match.homeTeam
            new_match['awayTeam'] = match.awayTeam
            new_match['result'] = match.result
            new_match['homeScore'] = match.homeScore
            new_match['awayScore'] = match.awayScore
            new_match['leagueId'] = int(match.leagueId or -1)
            new_match['leagueName'] = match.leagueName
            new_match['countryName'] = country_names[match.ccode]
            new_match['leagueSeason'] = match.leagueSeason
            if (not type(match.h2h) is bool):
                new_match['h2h_home_win'] = match.h2h.summary[0]
                new_match['h2h_draw'] = match.h2h.summary[1]
                new_match['h2h_away_win'] = match.h2h.summary[2]
            statsKeys = []
            from api_types import StatsKeysEnum
            for key in StatsKeysEnum:
                statsKeys.append(key.value)
            # add stats keys to the match
            stats_dict = flatten_stats_by_key(match.stats, statsKeys)
            for key, value in stats_dict.items():
                new_match[key] = value
            preprocessed_data.append(new_match)
        except Exception as e:
            print("Error while processing data: ", e)
    return preprocessed_data


def filter_women_leagues(all_leagues: List[CountryLeagueList]) -> List[CountryLeagueList]:
    mens_leagues = []
    for country in all_leagues:
        for league in country.leagues:
            if not ('women' in league.name.lower()) and not ('fem' in league.name.lower()):
                mens_leagues.append(league)
    return mens_leagues


def export_data(matches: List[MatchDetails], fname: str = 'matches'):
    # export to csv

    data = preprocess_data(matches)
    print('\n####################################')
    print("NUM MATCHES TOTAL: ", len(data))
    # create file
    fname = fname\
        .replace(' ', '_')\
        .replace('/', '_')\
        .replace(':', '_')\
        .replace(',', '_')\
        .replace('(', '_')\
        .replace(')', '_')

    pd.DataFrame(data).to_csv('data/'+fname, index=False)
