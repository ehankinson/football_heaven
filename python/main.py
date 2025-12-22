import time
from simulation import Simulation, Team

VERSION = '0.0'
GAMES = 70000
YEAR = 2007
team1 = Team('IND', YEAR, VERSION)
team2 = Team('NE', YEAR, VERSION)

sim = Simulation()
start_time = time.time()
sim.best_of(team1, team2, GAMES, print_result=True)
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
