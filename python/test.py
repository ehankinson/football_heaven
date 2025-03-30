
add = 40

start = 8
place = "zone"
depth = ""
diff = add - start


test = {
    f"{place}_avoided_tackles": 8,
    f"{place}_contested_receptions": 11,
    f"{place}_contested_targets": 12,
    f"{place}_drops": 14,
    f"{place}_first_downs": 15,
    f"{place}_fumbles": 16,
    f"{place}_inline_snaps": None,
    f"{place}_interceptions": 19,
    f"{place}_penalties": None,
    f"{place}_receptions": 24,
    f"{place}_routes": 26,
    f"{place}_slot_snaps": None,
    f"{place}_targets": 28,
    f"{place}_touchdows": 30,
    f"{place}_wide_snaps": None,
    f"{place}_yards": 31,
    f"{place}_yards_after_catch": 32,
    f"{place}_grades_hands_drop": 17,
    f"{place}_grades_pass_route": 18
}

for key in test:
    if test[key] is None:
        print(f'"{key}": {test[key]},')
    else:   
        test[key] = diff + test[key]
        print(f'"{key}": {test[key]},')




            