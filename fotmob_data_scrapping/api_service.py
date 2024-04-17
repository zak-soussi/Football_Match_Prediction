# module to fetch the data from the API

# Path: api_service.py

from typing import List
import requests
import json
from api_types import CountryLeagueList, League, MatchDetails
from constants import base_url, allowed_ccodes


async def get_all_leagues_by_country() -> List[CountryLeagueList]:
    url = f'{base_url}/allLeagues'
    response = requests.get(url)
    countriesLeagues = json.loads(response.text).get('countries')
    # filter by allowed_ccodes
    countriesLeagues = [country for country in countriesLeagues if country.get(
        'ccode') in allowed_ccodes]
    for country in countriesLeagues:
        for league in country.get('leagues'):
            league['ccode'] = country.get('ccode')

    return [CountryLeagueList(**country) for country in countriesLeagues]


async def get_all_available_seasons(league_id: int) -> List[str]:
    url = f'{base_url}/leagues?id={league_id}'
    response = requests.get(url)
    if response.status_code != 200:
        print(f'  ERROR: {response.status_code} {response.text}')
        return []
    return json.loads(response.text).get('allAvailableSeasons')


async def get_league_by_id_season(league_id: int, ccode: str, season: str) -> League | None:
    url = f'{base_url}/leagues?id={league_id}&season={season}'
    response = requests.get(url)
    if response.status_code != 200 or response.text == 'null':
        print(f'  ERROR: {response.status_code} {response.text}')
        return None
    league = json.loads(response.text)
    # change league.details.ccde to the ccode passed as parameter
    league['details']['ccode'] = ccode
    return League(**league)


async def get_match_details_by_id(match_id: int, season: str) -> MatchDetails | None:
    url = f'{base_url}/matchDetails?matchId={match_id}'
    print(f'  GET {url}')
    response = requests.get(url)
    if (response.status_code != 200):
        print(f'  ERROR: {response.status_code} {response.text}')
        return None
    return MatchDetails.model_validate(transform_match(response.text, season))


def transform_match(response: str, season: str) -> dict:
    json_response = json.loads(response)
    match = json_response.get('content')
    match['leagueId'] = json_response['general']['leagueId']
    match['leagueName'] = json_response['general']['leagueName']
    match['leagueSeason'] = season
    match['homeTeam'] = json_response['general']['homeTeam']['name']
    match['awayTeam'] = json_response['general']['awayTeam']['name']
    scoreStr = json_response['header']['status']['scoreStr'].split(' - ')
    homeScore = int(scoreStr[0])
    awayScore = int(scoreStr[1])
    result = 0 if homeScore == awayScore else 1 if homeScore > awayScore else 2
    match['homeScore'] = homeScore
    match['awayScore'] = awayScore
    match['result'] = result
    if (match.get('stats') is None):
        match['stats'] = []
        return match
    statsAll = match.get('stats').get('Periods').get('All')
    if (statsAll is None):
        match['stats'] = []
        return match
    stats = statsAll.get('stats')
    # filter stats based on type!="title"
    stats = [stat for stat in stats if stat.get('type') != 'title']
    for matchStats in stats:
        filtered_stats = []
        for matchStatsByKey in matchStats['stats']:
            if (matchStatsByKey['type'] == 'title'):
                continue
            split_stats = split_stats_with_percentage(matchStatsByKey['stats'])
            if len(split_stats) == 2:
                matchStatsByKey['stats'] = split_stats[0]
                # create a new matchStatsByKey with the percentageù
                new_matchStatsByKey = matchStatsByKey.copy()
                new_matchStatsByKey['stats'] = split_stats[1]
                new_matchStatsByKey['title'] += ' Percentage'
                new_matchStatsByKey['key'] += '_percentage'
                filtered_stats.append(new_matchStatsByKey)
            filtered_stats.append(matchStatsByKey)
        matchStats['stats'] = filtered_stats
    match['stats'] = stats
    return match


# def split_stats_with_percentage(stat: List) -> List[List[float]]:
#     # input : ['50 (51%)', '12 (85%)']
#     # output: ['50', '12'] and ['51', '85']
#     for s in stat:
#         stype = type(s)
#         if (s is None) or (stype is float):
#             return [stat]
#         if stype is int:
#             return [[float(i) for i in stat]]
#         if ((stype is str) and (not '%' in s)):
#             return [[float(i) for i in stat]]

#     new_stats = [[], []]
#     for s in stat:
#         # remove all non-numeric characters except space
#         s = s.replace('(', '').replace(')', '').replace('%', '')
#         new_stats[0].append(float(s.split(' ')[0]))
#         new_stats[1].append(float(s.split(' ')[1]))
#     return new_stats

def split_stats_with_percentage(stat: List) -> List[List[float]]:
    # input : ['50 (51%)', '12 (85%)']
    # output: ['50', '12'] and ['51', '85']
    for s in stat:
        stype = type(s)
        if ((stype is str) and ('%' in s)):
            return convert_percentage_stats(stat)
    new_stats = [[]]
    for s in stat:
        if (s is None):
            new_stats[0].append(0)
        else:
            new_stats[0].append(float(s))
    return new_stats


def convert_percentage_stats(stat: List) -> List[List[float]]:
    # input : ['50 (51%)', '12 (85%)'] or [50 (51%)', 0]
    # output: ['50', '12'] and ['51', '85'] or ['50', 0] and [51, 0]

    new_stats = [[], []]
    for s in stat:
        if s is None or type(s) is int or type(s) is float:
            new_stats[0].append(0)
            new_stats[1].append(0)
            continue
        # remove all non-numeric characters except space
        s = s.replace('(', '').replace(')', '').replace('%', '')
        new_stats[0].append(float(s.split(' ')[0]))
        new_stats[1].append(float(s.split(' ')[1]))
    return new_stats
