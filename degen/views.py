"""Views page - configures redirects"""
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from django.shortcuts import HttpResponse


class BasketballGame:
    team_one: str
    team_two: str
    ou: int
    spread: float
    team_one_favorite: bool

    def __init__(
        self,
        team_one: str,
        team_two: str,
        ou: int,
        spread: float,
        team_one_favorite: bool,
    ) -> None: 
        self.team_one = team_one
        self.team_two = team_two
        self.ou = ou
        self.spread = spread
        self.team_one_favorite = team_one_favorite

def degen(request, input_query: Optional[str] = None):

    return HttpResponse(barttorvik())


def barttorvik(): 
    response = requests.get("https://barttorvik.com/schedule.php?date=20220116&conlimit=")
    soup = BeautifulSoup(response.content, "html.parser")
    results = soup.find(id="content")
    table = results.find_all("tr")
    table.pop(0)
    table.pop(len(table)-1)
    if len(table) < 1:
        return HttpResponse("error")

    team_ones = 0
    games = []
    for row in table:
        game = barttorvik_row_to_game(row)
        if game is not None:
            games.append(game)

    return game.ou

def barttorvik_row_to_game(row) -> Optional[BasketballGame]:
    try:
        matchup = row.find_all("a")
        team_one = matchup[0]
        team_two = matchup[1]
        line = matchup[2].text
        line_split = line.split(" ")
        l = len(line_split)
        probability = line_split[l-1]
        score = line_split[l-2]
        score_split = score.split("-")
        ou = int(score_split[0]) + int(score_split[1])
        spread = float(line_split[l-3].strip(","))
        favorite = str(' '.join(line_split[0:l-3])) == str(team_one.text)
        return BasketballGame(
            team_one,
            team_two,
            ou,
            spread,
            favorite
        )
    except Exception:
        return None

