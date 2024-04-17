# module to define the types of the data

import enum
from typing import List, Optional
from pydantic import BaseModel

# Countries leagues


class LeagueByCountry(BaseModel):
    id: int
    name: str
    ccode: str


class CountryLeagueList(BaseModel):
    ccode: str
    leagues: List[LeagueByCountry]


class FirstUnplayedMatch(BaseModel):
    firstUnplayedMatchId: int
    firstUnplayedMatchIndex: int


class LeagueMatchTeam(BaseModel):
    name: str
    id: int


class LeagueMatch(BaseModel):
    id: int
    pageUrl: str
    round: int | str
    roundName: int | str
    away: LeagueMatchTeam
    home: LeagueMatchTeam


class LeagueMatches(BaseModel):
    allMatches: List[LeagueMatch]
    firstUnplayedMatch: FirstUnplayedMatch | None


class League(BaseModel):
    allAvailableSeasons: List[str]
    details: LeagueByCountry
    matches: LeagueMatches


# Match

class MatchFacts(BaseModel):
    matchId: int
    # contains top players of the match (playerRating)


class StatsKeysEnum(enum.Enum):
    BallPossesion = "BallPossesion"
    total_shots = "total_shots"
    big_chance = "big_chance"
    big_chance_missed_title = "big_chance_missed_title"
    fouls = "fouls"
    corners = "corners"
    shots = "shots"
    ShotsOffTarget = "ShotsOffTarget"
    ShotsOnTarget = "ShotsOnTarget"
    blocked_shots = "blocked_shots"
    shots_woodwork = "shots_woodwork"
    shots_inside_box = "shots_inside_box"
    shots_outside_box = "shots_outside_box"
    expected_goals = "expected_goals"
    expected_goals_open_play = "expected_goals_open_play"
    expected_goals_set_play = "expected_goals_set_play"
    expected_goals_non_penalty = "expected_goals_non_penalty"
    expected_goals_on_target = "expected_goals_on_target"
    passes = "passes"
    accurate_passes = "accurate_passes"
    own_half_passes = "own_half_passes"
    opposition_half_passes = "opposition_half_passes"
    long_balls_accurate = "long_balls_accurate"
    accurate_crosses = "accurate_crosses"
    player_throws = "player_throws"
    touches_opp_box = "touches_opp_box"
    Offsides = "Offsides"
    tackles_succeeded = "tackles_succeeded"
    interceptions = "interceptions"
    shot_blocks = "shot_blocks"
    clearances = "clearances"
    keeper_saves = "keeper_saves"
    duel_won = "duel_won"
    ground_duels_won = "ground_duels_won"
    aerials_won = "aerials_won"
    dribbles_succeeded = "dribbles_succeeded"
    yellow_cards = "yellow_cards"
    red_cards = "red_cards"
    accurate_passes_percentage = "accurate_passes_percentage"
    long_balls_accurate_percentage = "long_balls_accurate_percentage"
    accurate_crosses_percentage = "accurate_crosses_percentage"
    tackles_succeeded_percentage = "tackles_succeeded_percentage"
    ground_duels_won_percentage = "ground_duels_won_percentage"
    aerials_won_percentage = "aerials_won_percentage"
    dribbles_succeeded_percentage = "dribbles_succeeded_percentage"


class MatchStatsByKey(BaseModel):
    title: str
    key: StatsKeysEnum
    type: str  # TODO: if title then ignore
    # a list of two elemnts i.e. [5, 4] indicates home team 5, away team 4 or a list of nulls
    stats: List[Optional[float]] = [None, None]


class MatchStats(BaseModel):
    title: str
    key: str  # TODO: convert to enum
    stats: List[MatchStatsByKey]


class H2HMatchStatus(BaseModel):
    # nullable string
    # i.e. "1 - 0" Home team score - Away team score
    scoreStr: Optional[str] = None


class H2HMatch(BaseModel):
    status: H2HMatchStatus


class MatchH2H(BaseModel):
    summary: List[int]  # [home, draw, away]
    matches: List[H2HMatch]


class MatchDetails(BaseModel):
    matchFacts: MatchFacts
    stats: List[Optional[MatchStats]] = []
    h2h: MatchH2H | bool
    leagueId: int
    leagueName: str
    leagueSeason: str
    homeTeam: str
    awayTeam: str
    ccode: Optional[str] = None
    homeScore: int
    awayScore: int
    result: int
