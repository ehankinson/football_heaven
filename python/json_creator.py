import csv
import json

KEYS = { "cmp": 16, "p_att": 17, "p_yds": 20, "p_td": 21, "int": 22, "sk": 26, "yds": 27, "r_att": 34, "r_yds": 35, "r_td": 37, "fum": (43, 22) }

with open("json/teams.json", "r") as j:
    teams = json.load(j)

data = {}
year = 2024
with open(f"csv/{year} NFL Team Stats.csv") as c:
    reader = csv.reader(c)

    for row in reader:

        team = row[1]
        if team == "Team":
            continue

        team_id = teams[team]
        if team_id not in data:
            data[team_id] = {}
        

        
        


