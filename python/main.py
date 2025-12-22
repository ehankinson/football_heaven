import time
from simulation import Simulation, Team

VERSION = '0.0'
GAMES = 100
team1 = Team('CAR', 2015, VERSION)
team2 = Team('ATL', 2016, VERSION)

sim = Simulation()
start_time = time.time()
sim.best_of(team1, team2, GAMES, league_sim=True)
end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")
