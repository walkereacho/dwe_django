"""Views page - configures redirects"""
from typing import Dict

from django.shortcuts import HttpResponse
from espn_api.baseball import League, Team


def baseball(request):
    return HttpResponse(baseball_stats())

teams_wins: Dict[Team, int] = {}
teams_losses: Dict[Team, int] = {}
teams_ties: Dict[Team, int] = {}

def baseball_stats():
    league = League(league_id=67249, year=2022)
    for i in range(1,10):
        matchups = league.scoreboard(matchupPeriod=i)
        avg = get_median_score(matchups)
        populate_team_dict(matchups, avg)
    output_str = ""
    wins = dict(sorted(teams_wins.items(), key=lambda item: item[1], reverse=True))
    for team, score in wins.items():
        wins = score
        ties = teams_ties.get(team, 0)
        losses = teams_losses.get(team, 0)

        output_str += f"{team}: {wins}-{losses}-{ties} ||"
    
    return output_str

def get_median_score(matchups)-> float:
    scores = []
    for matchup in matchups:
        scores.append(matchup.home_final_score)
        scores.append(matchup.away_final_score)
    scores = sorted(scores)
    return (scores[5] + scores[6])/2

def populate_team_dict(matchups, avg):
    for matchup in matchups:
        if matchup.home_final_score > avg:
            incr(matchup.home_team.team_name, teams_wins)
        elif matchup.home_final_score == avg:
            incr(matchup.home_team.team_name, teams_ties)
        elif matchup.home_final_score < avg:            
            incr(matchup.home_team.team_name, teams_losses)


        if matchup.away_final_score > avg:
            incr(matchup.away_team.team_name, teams_wins)
        elif matchup.away_final_score == avg:
            incr(matchup.away_team.team_name, teams_ties)
        elif matchup.away_final_score < avg:            
            incr(matchup.away_team.team_name, teams_losses)

def incr(team, dictionary):
    score = dictionary.get(team, 0)
    dictionary[team] = score + 1
