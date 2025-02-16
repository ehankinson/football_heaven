add = 129

start = 8
start_add = "no_blitz"
diff = add - start


test = {
    "pressure_aimed_passes": 8,
    "pressure_attempts": 9,
    "pressure_avg_depth_of_target": 10,
    "pressure_bats": 12,
    "pressure_big_time_throws": 13,
    "pressure_completions": 16,
    "pressure_def_gen_pressures": 17,
    "pressure_dropbacks": 19,
    "pressure_drops": 21,
    "pressure_first_downs": 22,
    "pressure_hit_as_threw": 30,
    "pressure_interceptions": 31,
    "pressure_passing_snaps": 32,
    "pressure_sacks": 36,
    "pressure_scrambles": 37,
    "pressure_spikes": 38,
    "pressure_thrown_aways": 39,
    "pressure_touchdowns": 40,
    "pressure_turnover_worthy_plays": 41,
    "pressure_yards": 43
}

for key in test:
    test[key] = diff + test[key]
    print(f'"{key}": {test[key]},')