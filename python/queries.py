START = """
    Player_ID INT,
    GAME_ID INT,
    TEAM_ID INT,
    TYPE VARCHAR(64),
    YEAR INT,
    LEAGUE VARCHAR(8),
    VERSION VARCHAR(8),
"""
END = """
FOREIGN KEY (Player_ID) REFERENCES PLAYERS(Player_ID),
FOREIGN KEY (GAME_ID, TEAM_ID) REFERENCES GAME_DATA(Game_ID, Team_ID)
PRIMARY KEY (Player_ID, GAME_ID, TEAM_ID, YEAR, LEAGUE, TYPE, VERSION)"""


##########################################################################
#                          CREATE QUERIES                                #
##########################################################################


CREATE_PLAYERS = """
    CREATE TABLE IF NOT EXISTS PLAYERS (
        Player_ID INT PRIMARY KEY,
        Player_Name VARCHAR(255),
        Player_Pos VARCHAR(64)
    )
"""



CREATE_TEAMS = """
    CREATE TABLE IF NOT EXISTS TEAMS (
        TEAM_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Team_Abbr VARCHAR(8),
        League VARCHAR(8),
        Team_Name VARCHAR(255),
        Division VARCHAR(16),
        Conference VARCHAR(16)
    )
"""



CREATE_GAME_DATA = """
    CREATE TABLE IF NOT EXISTS GAME_DATA (
        GAME_ID INTEGER NOT NULL,
        Version VARCHAR(8) NOT NULL,
        Team_ID INT,
        Year INT,
        Week INT,
        Opponent_ID INT,
        Points_For INT,
        Points_Against INT,
        Diff INT,
        TD INT,
        XPA INT,
        XPM INT,
        FGA INT,
        FGM INT,
        "2PA" INT,
        "2PM" INT,
        Sfty INT,
        KRTD INT,
        PRTD INT,
        INTD INT,
        FRTD INT,
        OPP_KRTD INT,
        OPP_PRTD INT,
        OPP_INTD INT,
        OPP_FRTD INT,
        PRIMARY KEY (GAME_ID, Version),
        FOREIGN KEY (Team_ID) REFERENCES TEAMS(TEAM_ID),
        FOREIGN KEY (Opponent_ID) REFERENCES TEAMS(TEAM_ID)
    )
"""



CREATE_PASSING = f"""
    CREATE TABLE IF NOT EXISTS PASSING (
        {START}
        aimed_passes INT,
        attempts INT,
        avg_depth_of_target INT,
        bats INT,
        big_time_throws INT,
        completions INT,
        dropbacks INT,
        drops INT,
        first_downs INT,
        hit_as_threw INT,
        interceptions INT,
        passing_snaps INT,
        penalties INT,
        sacks INT,
        scrambles INT,
        spikes INT,
        thrown_aways INT,
        touchdowns INT,
        turnover_worthy_plays INT,
        yards INT,
        grade_pass INT,
        {END}
)
"""



CREATE_RECEIVING = f"""
    CREATE TABLE IF NOT EXISTS RECEIVING (
        {START}
        avoided_tackles INT,
        contested_reception INT,
        contested_targets INT,
        drops INT,
        first_downs INT,
        fumbles INT,
        inline_snaps INT,
        interceptions INT,
        penalties INT,
        receptions INT,
        routes INT,
        slot_snaps INT,
        targets INT,
        touchdowns INT,
        wide_snaps INT,
        yards INT,
        yards_after_catch INT,
        grades_hands_drop INT,
        grades_pass_route INT,
        {END}
    )
"""



CREATE_RUSHING =f"""
    CREATE TABLE IF NOT EXISTS RUSHING (
        {START}
        attempts INT,
        avoided_tackles INT,
        breakaway_attempts INT,
        breakaway_yards INT,
        designed_yards INT,
        explosive INT,
        first_downs INT,
        fumbles INT,
        gap_attempts INT,
        penalties INT,
        run_play INT,
        scramble_yards INT,
        scramble INT,
        touchdowns INT,
        yards INT,
        yards_after_contact INT,
        zone_attempts INT,
        grades_run INT,
        grades_hands_fumble INT,
        {END}    
    )
"""



CREATE_BLOCKING = f"""
    CREATE TABLE IF NOT EXISTS BLOCKING (
        {START}
        grades_pass_block INT,
        grades_run_block INT,
        penalties INT,
        snap_counts_ce INT,
        snap_counts_lg INT,
        snap_counts_lt INT,
        snap_counts_offense INT,
        snap_counts_pass_block INT,
        snap_counts_pass_play INT,
        snap_counts_rg INT,
        snap_counts_rt INT,
        snap_counts_run_block INT,
        snap_counts_te INT,
        {END}
    )
"""



CREATE_PASS_BLOCKING = f"""
    CREATE TABLE IF NOT EXISTS PASS_BLOCKING (
        {START}
        grades_pass_block INT,
        hits_allowed INT,
        hurries_allowed INT,
        pressures_allowed INT,
        sacks_allowed INT,
        snap_counts_pass_play INT,
        true_pass_set_grades_pass_block INT,
        true_pass_set_hits_allowed INT,
        true_pass_set_hurries_allowed INT,
        true_pass_set_pressures_allowed INT,
        true_pass_set_sacks_allowed INT,
        true_pass_set_snap_counts_pass_play INT,
        {END}
    )
"""



CREATE_RUN_BLOCKING = f"""
    CREATE TABLE IF NOT EXISTS RUN_BLOCKING (
        {START}
        gap_grades_run_block INT,
        gap_snap_counts_run_block INT,
        grades_run_block INT,
        snap_counts_run_block INT,
        penalties INT,
        zone_grades_run_block INT,
        zone_snap_counts_run_block INT,
        {END}
    )
"""



CREATE_PASS_RUSH = f"""
    CREATE TABLE IF NOT EXISTS PASS_RUSH (
        {START}
        batted_passes INT,
        grades_pass_rush_defense INT,
        hits INT,
        hurries INT,
        pass_rush_opp INT,
        pass_rush_wins INT,
        penalties INT,
        sacks INT,
        snap_counts_pass_play INT,
        snap_counts_pass_rush INT,
        total_pressures INT,
        true_pass_set_batted_passes INT,
        true_pass_set_grades_pass_rush_defense INT,
        true_pass_set_hits INT,
        true_pass_set_hurries INT,
        true_pass_set_pass_rush_opp INT,
        true_pass_set_pass_rush_wins INT,
        true_pass_set_sacks INT,
        true_pass_set_snap_counts_pass_play INT,
        true_pass_set_snap_counts_pass_rush INT,
        true_pass_set_total_pressures INT,
        {END}
    )
"""



CREATE_RUN_DEFENSE = f"""
    CREATE TABLE IF NOT EXISTS RUN_DEFENSE (
        {START}
        assists INT,
        avg_depth_of_tackle INT,
        forced_fumbles INT,
        grades_run_defense INT,
        grades_tackle INT,
        missed_tackles INT,
        penalties INT,
        run_stop_opp INT,
        stops INT,
        tackles INT,
        {END}        
    )
"""



CREATE_COVERAGE = f"""
    CREATE TABLE IF NOT EXISTS COVERAGE (
        {START}
        avg_depth_of_target INT,
        dropped_ints INT,
        forced_incompletes INT,
        grades_coverage_defense INT,
        interceptions INT,
        pass_break_ups INT,
        receptions INT,
        snap_counts_coverage INT,
        targets INT,
        touchdowns INT,
        yards INT,
        yards_after_catch INT,
        {END}
    )
"""



##########################################################################
#                          INSERT QUERIES                                #
##########################################################################



INSERT_START = "Player_ID, Game_ID, Team_ID, TYPE, YEAR, LEAGUE, VERSION"
PASSING_INSERT = """
    INSERT OR IGNORE INTO PASSING (
        {start}, aimed_passes, attempts, avg_depth_of_target,
        bats, big_time_throws, completions, dropbacks, drops, first_downs, hit_as_threw, 
        interceptions, passing_snaps, penalties, sacks, scrambles, spikes, thrown_aways, 
        touchdowns, turnover_worthy_plays, yards, grade_pass
    ) 
    VALUES ({result});
"""


RECEIVING_INSERT = """
    INSERT OR IGNORE INTO RECEIVING (
        {start}, avoided_tackles, contested_reception,
        contested_targets, drops, first_downs, fumbles, inline_snaps, interceptions,
        penalties, receptions, routes, slot_snaps, targets, touchdowns, wide_snaps,
        yards, yards_after_catch, grades_hands_drop, grades_pass_route
    )
    VALUES ({result})
"""



RUSHING_INSERT = """
    INSERT INTO RUSHING (
        {start}, attempts, avoided_tackles, breakaway_attempts,
        breakaway_yards, designed_yards, explosive, first_downs, fumbles, gap_attempts,
        penalties, run_play, scramble_yards, scramble, touchdowns, yards, yards_after_contact,
        zone_attempts, grades_run, grades_hands_fumble
    )
    VALUES ({result})
"""



BLOCKING_INSERT = """
    INSERT OR IGNORE INTO BLOCKING (
        {start}, grades_pass_block, grades_run_block, penalties, snap_counts_ce, snap_counts_lg,
        snap_counts_lt, snap_counts_offense, snap_counts_pass_block, snap_counts_pass_play, snap_counts_rg,
        snap_counts_rt, snap_counts_run_block, snap_counts_te
    )
    VALUES ({result})
"""



PASS_BLOCKING_INSERT = """
    INSERT OR IGNORE INTO PASS_BLOCKING (
        {start}, grades_pass_block, hits_allowed, hurries_allowed, pressures_allowed,
        sacks_allowed, snap_counts_pass_play, true_pass_set_grades_pass_block, true_pass_set_hits_allowed,
        true_pass_set_hurries_allowed, true_pass_set_pressures_allowed, true_pass_set_sacks_allowed,
        true_pass_set_snap_counts_pass_play
    )
    values ({result})
"""



RUN_BLOCKING_INSERT = """
    INSERT OR IGNORE INTO RUN_BLOCKING (
        {start}, gap_grades_run_block, gap_snap_counts_run_block, grades_run_block,
        snap_counts_run_block, penalties, zone_grades_run_block, zone_snap_counts_run_block
    )
    VALUES ({result})
"""



PASS_RUSH_INSERT = """
    INSERT OR IGNORE INTO PASS_RUSH (
        {start}, batted_passes, grades_pass_rush_defense, hits, hurries, pass_rush_opp,
        pass_rush_wins, penalties, sacks, snap_counts_pass_play, snap_counts_pass_rush,
        total_pressures, true_pass_set_batted_passes, true_pass_set_grades_pass_rush_defense,
        true_pass_set_hits, true_pass_set_hurries, true_pass_set_pass_rush_opp,
        true_pass_set_pass_rush_wins, true_pass_set_sacks, true_pass_set_snap_counts_pass_play,
        true_pass_set_snap_counts_pass_rush, true_pass_set_total_pressures
    )
    VALUES ({result})
"""



RUN_DEFENSE_INSERT = """
    INSERT OR IGNORE INTO RUN_DEFENSE (
        {start}, assists, avg_depth_of_tackle, forced_fumbles, grades_run_defense, grades_tackle,
        missed_tackles, penalties, run_stop_opp, stops, tackles
    )
    VALUES ({result})
"""



COVERAGE_INSERT = """
    INSERT OR IGNORE INTO COVERAGE (
        {start}, avg_depth_of_target, dropped_ints, forced_incompletes, grades_coverage_defense,
        interceptions, pass_break_ups, receptions, snap_counts_coverage, targets, touchdowns,
        yards, yards_after_catch
    )
    VALUES ({result})
"""



##########################################################################
#                             SUM QUERIES                                #
##########################################################################



PLAYER_SELECT = """
    SELECT
        PLAYERS.Player_Name,
        {TABLE}.Year,
        {TABLE}.Version,
        TEAMS.Team_Abbr,
        PLAYERS.Player_Pos,
        COUNT(DISTINCT {TABLE}.Game_ID) as gp,
        {SUM}
    FROM {TABLE}
"""



SINGLE_PLAYER_SELECT = """
    SELECT
        PLAYERS.Player_Name,
        {TABLE}.Year,
        {TABLE}.Version,
        TEAMS.Team_Abbr,
        PLAYERS.Player_Pos,
        GAME_DATA.Week,
        COUNT(DISTINCT {TABLE}.Game_ID) as gp,
        {SUM}
    FROM {TABLE}
"""



TEAM_SELECT = """
    SELECT
        TEAMS.Team_Name,
        {TABLE}.YEAR,
        {TABLE}.VERSION,
        COUNT(DISTINCT {TABLE}.Game_ID) as gp,
        {SUM}
    FROM {TABLE}
"""



SINGLE_TEAM_SELECT = """
    SELECT
        TEAMS.Team_Name,
        {TABLE}.YEAR,
        {TABLE}.VERSION,
        GAME_DATA.Week,
        COUNT(DISTINCT {TABLE}.Game_ID) as gp,
        {SUM}
    FROM {TABLE}
"""



PASSING_SUM = """
    SUM(PASSING.passing_snaps),
    SUM(PASSING.dropbacks),
    SUM(PASSING.completions),
    SUM(PASSING.aimed_passes),
    SUM(PASSING.attempts),
    SUM(PASSING.yards),
    ROUND(CAST(SUM(PASSING.avg_depth_of_target) AS FLOAT) / NULLIF(SUM(PASSING.attempts), 0), 1),
    SUM(PASSING.touchdowns),
    SUM(PASSING.interceptions),
    SUM(PASSING.first_downs),
    SUM(PASSING.big_time_throws),
    SUM(PASSING.turnover_worthy_plays),
    SUM(PASSING.drops),
    SUM(PASSING.bats),
    SUM(PASSING.hit_as_threw),
    SUM(PASSING.thrown_aways),
    SUM(PASSING.spikes),
    SUM(PASSING.sacks),
    SUM(PASSING.scrambles),
    SUM(PASSING.penalties),
    ROUND(SUM(PASSING.grade_pass * PASSING.dropbacks) / NULLIF(SUM(PASSING.dropbacks), 0), 1)
"""



RECEIVING_SUM = """
    SUM(RECEIVING.wide_snaps) + SUM(RECEIVING.slot_snaps) + SUM(RECEIVING.inline_snaps),
    SUM(RECEIVING.wide_snaps),
    SUM(RECEIVING.slot_snaps),
    SUM(RECEIVING.inline_snaps),
    SUM(RECEIVING.routes),
    SUM(RECEIVING.targets),
    SUM(RECEIVING.receptions),
    SUM(RECEIVING.yards),
    SUM(RECEIVING.touchdowns),
    SUM(RECEIVING.interceptions),
    SUM(RECEIVING.first_downs),
    SUM(RECEIVING.drops),
    SUM(RECEIVING.yards) - SUM(RECEIVING.yards_after_catch),
    SUM(RECEIVING.yards_after_catch),
    SUM(RECEIVING.avoided_tackles),
    SUM(RECEIVING.fumbles),
    SUM(RECEIVING.contested_targets),
    SUM(RECEIVING.contested_reception),
    SUM(RECEIVING.penalties),
    ROUND(SUM(RECEIVING.grades_pass_route * RECEIVING.routes) / NULLIF(SUM(RECEIVING.routes), 0), 1),
    ROUND(SUM(RECEIVING.grades_hands_drop * RECEIVING.routes) / NULLIF(SUM(RECEIVING.routes), 0), 1)
"""



RUSHING_SUM = """
    SUM(RUSHING.run_play),
    SUM(RUSHING.attempts),
    SUM(RUSHING.yards),
    SUM(RUSHING.touchdowns),
    SUM(RUSHING.fumbles),
    SUM(RUSHING.first_downs),
    SUM(RUSHING.avoided_tackles),
    SUM(RUSHING.explosive),
    SUM(RUSHING.yards) - SUM(RUSHING.yards_after_contact),
    SUM(RUSHING.yards_after_contact),
    SUM(RUSHING.breakaway_attempts),
    SUM(RUSHING.breakaway_yards),
    SUM(RUSHING.designed_yards),
    SUM(RUSHING.gap_attempts),
    SUM(RUSHING.zone_attempts),
    SUM(RUSHING.scramble),
    SUM(RUSHING.scramble_yards),
    SUM(RUSHING.penalties),
    ROUND(SUM(RUSHING.grades_run * RUSHING.attempts) / NULLIF(SUM(RUSHING.attempts), 0), 1),
    ROUND(SUM(RUSHING.grades_hands_fumble * RUSHING.run_play) / NULLIF(SUM(RUSHING.run_play), 0), 1)
"""



BLOCKING_SUM = """
    SUM(BLOCKING.snap_counts_offense),
    SUM(BLOCKING.snap_counts_pass_play),
    SUM(BLOCKING.snap_counts_run_block),
    SUM(BLOCKING.snap_counts_lt),
    SUM(BLOCKING.snap_counts_lg),
    SUM(BLOCKING.snap_counts_ce),
    SUM(BLOCKING.snap_counts_rg),
    SUM(BLOCKING.snap_counts_rt),
    SUM(BLOCKING.snap_counts_te),
    SUM(BLOCKING.penalties),
    ROUND(SUM(BLOCKING.grades_pass_block * BLOCKING.snap_counts_pass_block) / NULLIF(SUM(BLOCKING.snap_counts_pass_block), 0), 1),
    ROUND(SUM(BLOCKING.grades_run_block * BLOCKING.snap_counts_run_block) / NULLIF(SUM(BLOCKING.snap_counts_run_block), 0), 1)
"""



PASS_BLOCKING_SUM = """
    SUM(PASS_BLOCKING.snap_counts_pass_play),
    SUM(PASS_BLOCKING.hurries_allowed),
    SUM(PASS_BLOCKING.hits_allowed),
    SUM(PASS_BLOCKING.sacks_allowed),
    SUM(PASS_BLOCKING.pressures_allowed),
    ROUND(SUM(PASS_BLOCKING.grades_pass_block * PASS_BLOCKING.snap_counts_pass_play) / NULLIF(SUM(PASS_BLOCKING.snap_counts_pass_play), 0), 1),
    SUM(PASS_BLOCKING.true_pass_set_snap_counts_pass_play),
    SUM(PASS_BLOCKING.true_pass_set_hurries_allowed),
    SUM(PASS_BLOCKING.true_pass_set_hits_allowed),
    SUM(PASS_BLOCKING.true_pass_set_sacks_allowed),
    SUM(PASS_BLOCKING.true_pass_set_pressures_allowed),
    ROUND(SUM(PASS_BLOCKING.true_pass_set_grades_pass_block * PASS_BLOCKING.true_pass_set_snap_counts_pass_play) / NULLIF(SUM(PASS_BLOCKING.true_pass_set_snap_counts_pass_play), 0), 1)
"""



RUN_BLOCKING_SUM = """
    SUM(RUN_BLOCKING.snap_counts_run_block),
    SUM(RUN_BLOCKING.gap_snap_counts_run_block),
    SUM(RUN_BLOCKING.zone_snap_counts_run_block),
    SUM(RUN_BLOCKING.penalties),
    ROUND(SUM(RUN_BLOCKING.grades_run_block * RUN_BLOCKING.snap_counts_run_block) / NULLIF(SUM(RUN_BLOCKING.snap_counts_run_block), 0), 1),
    ROUND(SUM(RUN_BLOCKING.gap_grades_run_block * RUN_BLOCKING.gap_snap_counts_run_block) / NULLIF(SUM(RUN_BLOCKING.gap_snap_counts_run_block), 0), 1),
    ROUND(SUM(RUN_BLOCKING.zone_grades_run_block * RUN_BLOCKING.zone_snap_counts_run_block) / NULLIF(SUM(RUN_BLOCKING.zone_snap_counts_run_block), 0), 1)
"""



PASS_RUSH_SUM = """
    SUM(PASS_RUSH.snap_counts_pass_play),
    SUM(PASS_RUSH.snap_counts_pass_rush),
    SUM(PASS_RUSH.hurries),
    SUM(PASS_RUSH.hits),
    SUM(PASS_RUSH.sacks),
    SUM(PASS_RUSH.total_pressures),
    SUM(PASS_RUSH.pass_rush_opp),
    SUM(PASS_RUSH.pass_rush_wins),
    SUM(PASS_RUSH.batted_passes),
    SUM(PASS_RUSH.penalties),
    ROUND(SUM(PASS_RUSH.grades_pass_rush_defense * PASS_RUSH.snap_counts_pass_rush) / NULLIF(SUM(PASS_RUSH.snap_counts_pass_rush), 0), 1),
    SUM(PASS_RUSH.true_pass_set_snap_counts_pass_play),
    SUM(PASS_RUSH.true_pass_set_snap_counts_pass_rush),
    SUM(PASS_RUSH.true_pass_set_hurries),
    SUM(PASS_RUSH.true_pass_set_hits),
    SUM(PASS_RUSH.true_pass_set_sacks),
    SUM(PASS_RUSH.true_pass_set_total_pressures),
    SUM(PASS_RUSH.true_pass_set_pass_rush_opp),
    SUM(PASS_RUSH.true_pass_set_pass_rush_wins),
    SUM(PASS_RUSH.true_pass_set_batted_passes),
    ROUND(SUM(PASS_RUSH.true_pass_set_grades_pass_rush_defense * PASS_RUSH.true_pass_set_snap_counts_pass_rush) / NULLIF(SUM(PASS_RUSH.true_pass_set_snap_counts_pass_rush), 0), 1)
"""



RUN_DEFENSE_SUM = """
    SUM(RUN_DEFENSE.run_stop_opp),
    SUM(RUN_DEFENSE.tackles) + SUM(RUN_DEFENSE.assists),
    SUM(RUN_DEFENSE.tackles),
    SUM(RUN_DEFENSE.assists),
    SUM(RUN_DEFENSE.stops),
    ROUND(SUM(RUN_DEFENSE.avg_depth_of_tackle) / NULLIF(SUM(RUN_DEFENSE.tackles), 0), 1),
    SUM(RUN_DEFENSE.missed_tackles),
    SUM(RUN_DEFENSE.forced_fumbles),
    SUM(RUN_DEFENSE.penalties),
    ROUND(SUM(RUN_DEFENSE.grades_run_defense * RUN_DEFENSE.run_stop_opp) / NULLIF(SUM(RUN_DEFENSE.run_stop_opp), 0), 1),
    ROUND(SUM(RUN_DEFENSE.grades_tackle * RUN_DEFENSE.tackles) / NULLIF(SUM(RUN_DEFENSE.tackles), 0), 1)
"""



COVERAGE_SUM = """
    SUM(COVERAGE.snap_counts_coverage),
    SUM(COVERAGE.targets),
    SUM(COVERAGE.receptions),
    SUM(COVERAGE.yards),
    SUM(COVERAGE.touchdowns),
    SUM(COVERAGE.interceptions),
    SUM(COVERAGE.avg_depth_of_target),
    SUM(COVERAGE.yards) - SUM(COVERAGE.yards_after_catch),
    SUM(COVERAGE.yards_after_catch),
    SUM(COVERAGE.pass_break_ups),
    SUM(COVERAGE.forced_incompletes),
    SUM(COVERAGE.dropped_ints),
    ROUND(SUM(COVERAGE.grades_coverage_defense * COVERAGE.snap_counts_coverage) / NULLIF(SUM(COVERAGE.snap_counts_coverage), 0), 1)
"""



GAME_DATA_SUM = """
    SELECT
        TEAMS.Team_Name,
        GAME_DATA.YEAR,
        GAME_DATA.VERSION,
        GAME_DATA.Week,
        COUNT(DISTINCT GAME_DATA.Game_ID) as gp,
        SUM(GAME_DATA.Points_For) as PTS_F,
        SUM(GAME_DATA.Points_Against) as PTS_AGAINST,
        SUM(GAME_DATA.FGM) as FGM,
        SUM(GAME_DATA.FGA) as FGA,
        SUM(GAME_DATA.XPM) as XPM,
        SUM(GAME_DATA.XPA) as XPA
    FROM GAME_DATA
    JOIN TEAMS on GAME_DATA.Team_ID = TEAMS.Team_ID
"""



# TOTAL_SUM = f"""
#     SELECT
#         TEAMS.Team_Name,
#         GAME_DATA.Year,
#         GAME_DATA.Version,
#         COUNT(DISTINCT GAME_DATA.Game_ID) as gp,
#         SUM(GAME_DATA.Points_For) as Points_For,
#         {PASSING_SUM},
#         {RUSHING_SUM},
#         {RECEIVING_SUM},
#         {BLOCKING_SUM},
#         {PASS_BLOCKING_SUM},
#         {RUN_BLOCKING_SUM},
#         {PASS_RUSH_SUM},
#         {RUN_DEFENSE_SUM},
#         {COVERAGE_SUM}
#     FROM GAME_DATA
#     JOIN PASSING on GAME_DATA.Game_ID = PASSING.Game_ID
#     JOIN RUSHING on GAME_DATA.Game_ID = RUSHING.Game_ID
#     JOIN RECEIVING on GAME_DATA.Game_ID = RECEIVING.Game_ID
#     JOIN BLOCKING on GAME_DATA.Game_ID = BLOCKING.Game_ID
#     JOIN PASS_BLOCKING on GAME_DATA.Game_ID = PASS_BLOCKING.Game_ID
#     JOIN RUN_BLOCKING on GAME_DATA.Game_ID = RUN_BLOCKING.Game_ID
#     JOIN PASS_RUSH on GAME_DATA.Game_ID = PASS_RUSH.Game_ID
#     JOIN RUN_DEFENSE on GAME_DATA.Game_ID = RUN_DEFENSE.Game_ID
#     JOIN COVERAGE on GAME_DATA.Game_ID = COVERAGE.Game_ID
#     JOIN TEAMS on GAME_DATA.Team_ID = TEAMS.Team_ID
# """



SUM_TABLE = {
    "passing": {"query": PASSING_SUM, "table": "PASSING"},
    "rushing": {"query": RUSHING_SUM, "table": "RUSHING"},
    "receiving": {"query": RECEIVING_SUM, "table": "RECEIVING"},
    "blocking": {"query": BLOCKING_SUM, "table": "BLOCKING"},
    "pass_blocking": {"query": PASS_BLOCKING_SUM, "table": "PASS_BLOCKING"},
    "run_blocking": {"query": RUN_BLOCKING_SUM, "table": "RUN_BLOCKING"},
    "pass_rush": {"query": PASS_RUSH_SUM, "table": "PASS_RUSH"},
    "run_defense": {"query": RUN_DEFENSE_SUM, "table": "RUN_DEFENSE"},
    "coverage": {"query": COVERAGE_SUM, "table": "COVERAGE"},
    "game_data": {"query": GAME_DATA_SUM, "table": "GAME_DATA"}
}



CREATE_TABLE = {
    "TEAM": CREATE_TEAMS,
    "GAME_DATA": CREATE_GAME_DATA,
    "PLAYERS": CREATE_PLAYERS,
    "PASSING": CREATE_PASSING,
    "RECEIVING": CREATE_RECEIVING,
    "RUSHING": CREATE_RUSHING,
    "BLOCKING": CREATE_BLOCKING,
    "PASS_BLOCKING": CREATE_PASS_BLOCKING,
    "RUN_BLOCKING": CREATE_RUN_BLOCKING,
    "PASS_RUSH": CREATE_PASS_RUSH,
    "RUN_DEFENSE": CREATE_RUN_DEFENSE,
    "COVERAGE": CREATE_COVERAGE
}



INSERT_TABLE = {
    "passing": PASSING_INSERT,
    "receiving": RECEIVING_INSERT,
    "rushing": RUSHING_INSERT,
    "blocking": BLOCKING_INSERT,
    "pass_blocking": PASS_BLOCKING_INSERT,
    "run_blocking": RUN_BLOCKING_INSERT,
    "pass_rush": PASS_RUSH_INSERT,
    "run_defense": RUN_DEFENSE_INSERT,
    "coverage": COVERAGE_INSERT
}



def _where_conditions(args: dict, select: str, table: str, opp: bool) -> str:
    start_week, end_week, start_year, end_year, stat_type, league, version, pos, limit, team = args.values()

    conditions = []
    if version is not None:
        conditions.append(f"{table}.VERSION = {version}")
    if start_year is not None:
        conditions.append(f"{table}.YEAR >= {start_year}")
    if end_year is not None:
        conditions.append(f"{table}.YEAR <= {end_year}")
    if start_week is not None:
        conditions.append(f"GAME_DATA.WEEK >= {start_week}")
    if end_week is not None:
        conditions.append(f"GAME_DATA.WEEK <= {end_week}")
    if stat_type is not None:
        conditions.append(f"{table}.TYPE = '{stat_type}'")
    if league is not None:
        conditions.append(f"{table}.LEAGUE = '{league}'")
    if pos is not None:
        conditions.append(f"PLAYERS.Player_Pos IN [{','.join(f"'{p}'" for p in pos)}]")
    if team is not None:
        if opp:
            conditions.append(f"GAME_DATA.Opponent_ID = (SELECT Team_ID FROM TEAMS WHERE Team_Abbr = '{team}')")
        else:
            conditions.append(f"TEAMS.Team_Abbr = '{team}'")

    if conditions:
        select += "WHERE " + " \nAND ".join(conditions)
    
    return select



def get_query(args: dict, _type: str, is_player: bool, by_game: bool = False, opp: bool = False) -> str:
    query, table = SUM_TABLE[_type].values()
    if by_game:
        select = SINGLE_TEAM_SELECT if is_player else SINGLE_TEAM_SELECT
    else:
        select = PLAYER_SELECT if is_player else TEAM_SELECT
    select = select.format(SUM=query, TABLE=table)

    select += f"JOIN GAME_DATA on {table}.Game_ID = GAME_DATA.Game_ID\n"
    
    select += f"JOIN TEAMS on {table}.Team_ID = TEAMS.Team_ID\n"
    select += f"JOIN PLAYERS on {table}.Player_ID = PLAYERS.Player_ID\n"

    select = _where_conditions(args, select, table, opp)
    
    key = f"{table}.Player_ID" if is_player else f"{table}.Team_ID"
    select += f"\nGROUP BY {key}, {table}.Year"
    if by_game:
        select += f", {table}.Game_ID"

    return select
