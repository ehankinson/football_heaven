import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties

class Bracket:

    def __init__(self, teams: list):
        self.rounds = {}
        self.bracket = []
        self.teams = teams



    def generate_bracket(self) -> list:
        team_length = len(self.teams)
        rounds = math.ceil(math.log(team_length, 2))
        
        total_teams_needed = 2 ** rounds
        byes = total_teams_needed - team_length
        
        for i in range(rounds):
            if i == 0 and byes > 0:
                self.rounds[i] = self.teams[byes: team_length]
                team_length = self._remove_teams(byes, team_length)
            else:
                total_teams_needed = 2 ** (rounds - i)
                new_teams = self.teams + [None] * (total_teams_needed - team_length)
                self.rounds[i] = new_teams[0: total_teams_needed]
                team_length = self._remove_teams(0, team_length)

        for i in range(rounds):
            teams = self.rounds[i]
            series = []
            l, r = 0, len(teams) - 1
            while l < r:
                series.append((teams[l], teams[r]))
                l, r = l + 1, r - 1

            self.bracket.append(series)

        return self.bracket
    


    def add_winners(self, winners: list[tuple[int, str]], rd: int) -> None:
        round_teams = self.rounds[rd]
        for i, team in enumerate(round_teams):
            if team is None:
                round_teams[i] = winners.pop(0)
        round_teams.sort(key=lambda x: x[0])

        game = 0
        l, r = 0, len(round_teams) - 1
        while l < r:
            self.bracket[rd][game] = (round_teams[l], round_teams[r])
            l, r = l + 1, r - 1
            game += 1
    


    def _remove_teams(self, start: int, end: int) -> None:
        while end > start:
            self.teams.pop(end - 1)
            end -= 1
        return end
    
    
    