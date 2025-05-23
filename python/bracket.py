import math

class Bracket:

    def __init__(self, teams: list):
        self.bracket = []
        self.teams = teams
        self.bracket = self.generate_bracket()



    def generate_bracket(self) -> list:
        team_length = len(self.teams)
        rounds = math.ceil(math.log(team_length, 2))
        
        total_teams_needed = 2 ** rounds
        byes = total_teams_needed - team_length
        
        for i in range(rounds):
            if i == 0 and byes > 0:
                self._create_round(team_length, byes, team_length - 1)
            else:
                self._create_round(team_length, 0, team_length - 1)

            team_length = (rounds - (i + 1)) ** 2

        return self.bracket
    


    def _create_round(self, team_length: int, start: int, end: int) -> list:
        current_round = []
        l, r = start, end
        while l < r:
            current_round.append([l, r])
            l, r = l + 1, r - 1
        return current_round
    
    
    