import json
import os
from datetime import datetime

import pytz
import requests
from espn_api.baseball import League, Team

league = None
teams = []
ESPN_S2 = "AECwUpeq2BTp4GvnAFVT6z%2FBkdHNFBLaGt36GZR8rvOR%2BiQ%2BdxPRnNC6bBJtndsBXFYj9PlU8qSvJ3AhAlPu%2Fij4TrmqmtTYPv6v2fCK%2F6T8baVUbSDRJg4HqophgF2%2B7CqvZrkWSS%2F85WpULyzqwuplM9IL0AtLVotkOaudzI%2Fh%2BjQb%2F%2BCw3dLcBMCO%2BfbNUjIAaP9SuzwlwDI7HgZbZ2qFfG67zBOpzONyT9M6IfNu2G3oviQDcbnUIn1wR8VLfxDUwKJyOjLV1cWYnt7Ps%2FsSwsXOxe7TQuv1BpORXgQMjw%3D%3D"
SWID = "{040E3631-9808-4FB9-8E36-3198082FB97D}"
league = League(league_id=67249, year=2022, espn_s2=ESPN_S2, swid=SWID)
teams = league.teams

# I care about: team, recevied X player, On X date
# From there I calculate X player"s stats since X date

class ESPNPlayerStats:
    def get_batting_stats(self, player_id):
        return self.get_stats(player_id, "batting")
    
    def get_pitching_stats(self, player_id):
        return self.get_stats(player_id, "pitching")

    def get_stats(self, player_id, category):
        endpoint = f"https://site.web.api.espn.com/apis/common/v3/sports/baseball/mlb/athletes/{player_id}/gamelog?category={category}"
        r = requests.get(endpoint)
        pretty_json = json.loads(r.text)
        return json.dumps(pretty_json, indent=2)

api = ESPNPlayerStats()

class Player:
    def __init__(self, name, player_id):
        self.player_id = player_id
        self.name = name
        self.maybe_download_player_stats()
    
    def maybe_download_player_stats(self):
        if not os.path.exists(f"batters/{self.player_id}.json"):
            print(f"Downloading Batting stats for {self.name}, {self.player_id}")
            self.download_batting_stats()

        if not os.path.exists(f"pitchers/{self.player_id}.json"):
            print(f"Downloading Pitching stats for {self.name}, {self.player_id}")
            self.download_pitching_stats()
    
    def download_batting_stats(self):
        data = api.get_batting_stats(self.player_id)
        with open(f"batters/{self.player_id}.json", "w") as outfile:
            outfile.write(data)
    
    def download_pitching_stats(self):
        data = api.get_pitching_stats(self.player_id)
        with open(f"pitchers/{self.player_id}.json", "w") as outfile:
            outfile.write(data)
    
    def get_points(self):
        batting_stats = self.get_batting_stats()
        pitching_stats = self.get_pitching_stats()
        batting_stats.update(pitching_stats)
        return batting_stats

    
    def get_batting_stats(self):
        return self.get_stats("batting")

    def get_pitching_stats(self):
        return self.get_stats("pitching")

    # Player file
    def get_stats(self, category_type):
        folder = "batters" if category_type == "batting" else "pitchers"
        data = None
        # TODO: Get batter data per-player
        with open(f"{folder}/{self.player_id}.json", "r") as stats:
            data = json.load(stats)
        if not data: # TODO validation on pitcher or batter
            return
        
        # Load up timestamps
        event_times = {}
        events = data.get("events", {})
        for event in events.values():
            timestamp = datetime.strptime(event["gameDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
            event_times[event["id"]] = timestamp
        
        # Load up game stats
        event_stats = {}
        season = data.get("seasonTypes",[{}])[0]
        categories = season.get("categories", [])
        for category in categories:
            events = category.get("events")
            for event in events:
                event_stats[event["eventId"]] = self.get_points_for_stats(category_type, event["stats"])

        scores_map = {}
        for event_id, timestamp in event_times.items():
            scores_map[timestamp] = event_stats[event_id]
        return scores_map

    def get_points_for_stats(self, category, stats):
        return self.get_batting_points_for_stats(stats) if category == "batting" else self.get_pitching_points_for_stats(stats)
    
    def get_batting_points_for_stats(self, stats):
        return int(stats[1]) + int(stats[2]) + int(stats[3]) + 2*int(stats[4])+ 3*int(stats[5]) + int(stats[6])+int(stats[7])+int(stats[8])-int(stats[9])+int(stats[10])

    def get_pitching_points_for_stats(self, stats):
        score = 0
        score -= int(stats[1]) # Hits
        score -= 2 * int(stats[3]) # ER
        score -= int(stats[5]) # Balls
        score += int(stats[6]) # Strikeouts

        split_ip = str(stats[0]).split('.')
        score += 3*int(split_ip[0]) + int(split_ip[1])

        if str(stats[12]).startswith("W"):
            score += 3
        if str(stats[12]).startswith("L"):
            score -=3
        
        if str(stats[13]).startswith("SV"):
            score+=5
        if str(stats[13]).startswith("HLD"):
            score+=2

        if (float(stats[0]) >= 6.0 and int(stats[3]) < 4):
            score+=3 # Quality Starts

        if(self.player_id == 32116):
            print(stats)
            print(score)
        return score

final_trades = []
# List[Dict[{
#   date: timestamp
#   owner_one: {
#      owner_name: ""
#      players_received: [
#        {player_name => score_since_date}
#        ...
#      ]
#   }
#   owner_two: {
#      owner_name: ""
#      players_received: [
#         ibid
#      ]
#   }
# }]]

class Trade:
    def __init__(self, date, players_received, from_owner):
        self.date = date
        self.players_received = players_received
        self.from_owner = from_owner

def create_trade(date, owner_one, owner_one_gets, owner_two, owner_two_gets):
    trade = {
        "date": date,
        "owner_one": create_dict_for_owner(date, owner_one, owner_one_gets),
        "owner_two": create_dict_for_owner(date, owner_two, owner_two_gets)
    }
    final_trades.append(trade)

def create_dict_for_owner(date, owner, players_received):
    owner_dict = {
        "owner_name": owner
    }
    players_received_array = []
    for player in players_received:
        points_since_trade = get_points_since_date(date, player)
        players_received_array.append({player.name: points_since_trade})
    owner_dict["players_received"] = players_received_array
    return owner_dict

def get_points_since_date(date, player):
    stats = player.get_points()
    points_since_trade = 0
    date = date / 1000
    date = datetime.fromtimestamp(date).replace(tzinfo=pytz.UTC)
    for game_day, points in stats.items():
        game_day = game_day.replace(tzinfo=pytz.UTC)
        if game_day > date:
            points_since_trade += points
    return points_since_trade

def process_all_trades(trades_to_process):
    for trade in trades_to_process:
        owner_one: str = ""
        owner_two: str = ""

        date = trade.date
        owner_one_gets = []
        owner_two_gets = []
        for action in trade.actions:
            current_team = action[0]
            player_leaving_roster: str = action[2]
            player = Player(player_leaving_roster, league.player_map[player_leaving_roster])
            if owner_one in ["", current_team.team_name]:
                owner_one = current_team.team_name
                owner_two_gets.append(player)
            else:
                owner_two = current_team.team_name
                owner_one_gets.append(player)
        create_trade(date, owner_one, owner_one_gets, owner_two, owner_two_gets)

process_all_trades(league.trades())
print("Trade Date, Owner, Player Received, Points Since Trade, Owner Two, Player Recevied, Points Since Trade")
for trade in final_trades:
    owner_one_dict = trade.get("owner_one",{})
    owner_two_dict = trade.get("owner_two",{})
    owner_one_players_received = owner_one_dict.get("players_received")
    owner_two_players_received = owner_two_dict.get("players_received")
    #        Date              Owner One                              Player,    Points,    Owner Two, Player, Points
    date = trade["date"]
    o_1_name = owner_one_dict.get("owner_name", "")
    o_2_name = owner_two_dict.get("owner_name", "")
    counter = 0
    no_player_one = False
    no_player_two = False
    while(True):
        if (counter < len(owner_one_players_received)):
            player_one = list(owner_one_players_received)[counter]
            player_one_name = list(player_one.keys())[0]
            player_one_score = player_one.get(player_one_name, 0)
        else:
            player_one_name = ""
            player_one_score = ""
            no_player_one = True
        if (counter < len(owner_two_players_received)):
            player_two = list(owner_two_players_received)[counter]
            player_two_name = list(player_two.keys())[0]
            player_two_score = player_two.get(player_two_name, 0)
        else:
            no_player_two = True
            player_two_name = ""
            player_two_score = ""

        print(f"{date}, {o_1_name}, {player_one_name}, {player_one_score}, {o_2_name}, {player_two_name}, {player_two_score}")
        date = ""
        o_1_name = ""
        o_2_name = ""
        counter += 1
        if no_player_one and no_player_two:
            break

# miles = Player("Miles", 32116)
# miles.get_pitching_points_for_stats(
#     ['8.0', '4', '2', '2', '1', '0', '6', '11', '10', '99', '27', '72.0', 'W(9-9)', '-', '3.44']
# )
