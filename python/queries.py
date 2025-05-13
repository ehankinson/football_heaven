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



TEAM_SELECT = """
    SELECT
        TEAMS.Team_Name,
        {TABLE}.YEAR,
        {TABLE}.VERSION,
        COUNT(DISTINCT {TABLE}.Game_ID) as gp,
        {SUM}
    FROM {TABLE}
"""



PASSING_SUM = """
    SUM(PASSING.passing_snaps) as snaps,
    SUM(PASSING.dropbacks) as db,
    SUM(PASSING.completions) as cmp,
    SUM(PASSING.aimed_passes) as aim,
    SUM(PASSING.attempts) as att,
    SUM(PASSING.yards) as yds,
    ROUND(CAST(SUM(PASSING.avg_depth_of_target) AS FLOAT) / NULLIF(SUM(PASSING.attempts), 0), 5) as adot,
    SUM(PASSING.touchdowns) as td,
    SUM(PASSING.interceptions) as int,
    SUM(PASSING.first_downs) as "1d",
    SUM(PASSING.big_time_throws) as btt,
    SUM(PASSING.turnover_worthy_plays) as twp,
    SUM(PASSING.drops) as drp,
    SUM(PASSING.bats) as bat,
    SUM(PASSING.hit_as_threw) as hat,
    SUM(PASSING.thrown_aways) as ta,
    SUM(PASSING.spikes) as spk,
    SUM(PASSING.sacks) as sk,
    SUM(PASSING.scrambles) as scrm,
    SUM(PASSING.penalties) as pen,
    ROUND(SUM(PASSING.grade_pass * PASSING.dropbacks) / NULLIF(SUM(PASSING.dropbacks), 0), 1) as grade_pass 
"""



RECEIVING_SUM = """
    SUM(RECEIVING.wide_snaps) + SUM(RECEIVING.slot_snaps) + SUM(RECEIVING.inline_snaps) as snaps,
    SUM(RECEIVING.wide_snaps) as ws,
    SUM(RECEIVING.slot_snaps) as slt,
    SUM(RECEIVING.inline_snaps) as ins,
    SUM(RECEIVING.routes) as rts,
    SUM(RECEIVING.targets) as tgt,
    SUM(RECEIVING.receptions) as rec,
    SUM(RECEIVING.yards) as yds,
    SUM(RECEIVING.touchdowns) as td,
    SUM(RECEIVING.interceptions) as int,
    SUM(RECEIVING.first_downs) as "1d",
    SUM(RECEIVING.drops) as drp,
    SUM(RECEIVING.yards) - SUM(RECEIVING.yards_after_catch) as ybc,
    SUM(RECEIVING.yards_after_catch) as yac,
    SUM(RECEIVING.avoided_tackles) as at,
    SUM(RECEIVING.fumbles) as fum,
    SUM(RECEIVING.contested_targets) as ct,
    SUM(RECEIVING.contested_reception) as cr,
    SUM(RECEIVING.penalties) as pen,
    ROUND(SUM(RECEIVING.grades_pass_route * RECEIVING.routes) / NULLIF(SUM(RECEIVING.routes), 0), 1) as grade_recv,
    ROUND(SUM(RECEIVING.grades_hands_drop * RECEIVING.routes) / NULLIF(SUM(RECEIVING.routes), 0), 1) as grade_drp
"""



RUSHING_SUM = """
    SUM(RUSHING.run_play) as r_play,
    SUM(RUSHING.attempts) as att,
    SUM(RUSHING.yards) as yds,
    SUM(RUSHING.touchdowns) as td,
    SUM(RUSHING.fumbles) as fum,
    SUM(RUSHING.first_downs) as "1d",
    SUM(RUSHING.avoided_tackles) as avt,
    SUM(RUSHING.explosive) as exp,
    SUM(RUSHING.yards) - SUM(RUSHING.yards_after_contact) as ybc,
    SUM(RUSHING.yards_after_contact) as yac,
    SUM(RUSHING.breakaway_attempts) as baa,
    SUM(RUSHING.breakaway_yards) as bay,
    SUM(RUSHING.designed_yards) as dey,
    SUM(RUSHING.gap_attempts) as g_att,
    SUM(RUSHING.zone_attempts) as z_att, 
    SUM(RUSHING.scramble) as scrm,
    SUM(RUSHING.scramble_yards) as scrm_yds,
    SUM(RUSHING.penalties) as pen,
    ROUND(SUM(RUSHING.grades_run * RUSHING.attempts) / NULLIF(SUM(RUSHING.attempts), 0), 1) as grade_run,
    ROUND(SUM(RUSHING.grades_hands_fumble * RUSHING.run_play) / NULLIF(SUM(RUSHING.run_play), 0), 1) as grade_fumble
"""



BLOCKING_SUM = """
    SUM(BLOCKING.snap_counts_offense) as s_off,
    SUM(BLOCKING.snap_counts_pass_play) as s_pas,
    SUM(BLOCKING.snap_counts_run_block) as s_run,
    SUM(BLOCKING.snap_counts_lt) as s_lt,
    SUM(BLOCKING.snap_counts_lg) as c_lg,
    SUM(BLOCKING.snap_counts_ce) as s_ce,
    SUM(BLOCKING.snap_counts_rg) as s_rg,
    SUM(BLOCKING.snap_counts_rt) as s_rt,
    SUM(BLOCKING.snap_counts_te) as s_te,
    SUM(BLOCKING.penalties) as pen,
    ROUND(SUM(BLOCKING.grades_pass_block * BLOCKING.snap_counts_pass_block) / NULLIF(SUM(BLOCKING.snap_counts_pass_block), 0), 1) as grade_pass_block,
    ROUND(SUM(BLOCKING.grades_run_block * BLOCKING.snap_counts_run_block) / NULLIF(SUM(BLOCKING.snap_counts_run_block), 0), 1) as grade_run_block
"""



PASS_BLOCKING_SUM = """
    SUM(PASS_BLOCKING.snap_counts_pass_play) as snap_pp,
    SUM(PASS_BLOCKING.hurries_allowed) as hur,
    SUM(PASS_BLOCKING.hits_allowed) as hit,
    SUM(PASS_BLOCKING.sacks_allowed) as sk,
    SUM(PASS_BLOCKING.pressures_allowed) as pr,
    ROUND(SUM(PASS_BLOCKING.grades_pass_block * PASS_BLOCKING.snap_counts_pass_play) / NULLIF(SUM(PASS_BLOCKING.snap_counts_pass_play), 0), 1) as grade_pass_block,
    SUM(PASS_BLOCKING.true_pass_set_snap_counts_pass_play) as t_snap_pp,
    SUM(PASS_BLOCKING.true_pass_set_hurries_allowed) as t_hur,
    SUM(PASS_BLOCKING.true_pass_set_hits_allowed) as t_hit,
    SUM(PASS_BLOCKING.true_pass_set_sacks_allowed) as t_sk,
    SUM(PASS_BLOCKING.true_pass_set_pressures_allowed) as t_pr,
    ROUND(SUM(PASS_BLOCKING.true_pass_set_grades_pass_block * PASS_BLOCKING.true_pass_set_snap_counts_pass_play) / NULLIF(SUM(PASS_BLOCKING.true_pass_set_snap_counts_pass_play), 0), 1) as t_grade_pass_block
"""



RUN_BLOCKING_SUM = """
    SUM(RUN_BLOCKING.gap_grades_run_block) as gap_grades_run_block,
    SUM(RUN_BLOCKING.gap_snap_counts_run_block) as gap_snap_counts,
    SUM(RUN_BLOCKING.grades_run_block) as grades_run_block,
    SUM(RUN_BLOCKING.snap_counts_run_block) as snap_run_blcok,
    SUM(RUN_BLOCKING.penalties) as pen,
    SUM(RUN_BLOCKING.zone_grades_run_block) as grade_zone_run_block,
    SUM(RUN_BLOCKING.zone_snap_counts_run_block) as zone_snap_counts,
"""



PASS_RUSH_SUM = """
    SUM(PASS_RUSH.snap_counts_pass_play) as snap_pp,
    SUM(PASS_RUSH.snap_counts_pass_rush) as snap_pr,
    SUM(PASS_RUSH.hurries) as hur,
    SUM(PASS_RUSH.hits) as hit,
    SUM(PASS_RUSH.sacks) as sk,
    SUM(PASS_RUSH.total_pressures) as pr,
    SUM(PASS_RUSH.pass_rush_opp) as pass_rush,
    SUM(PASS_RUSH.pass_rush_wins) as pass_win, 
    SUM(PASS_RUSH.batted_passes) as bat,
    SUM(PASS_RUSH.penalties) as pen,
    ROUND(SUM(PASS_RUSH.grades_pass_rush_defense * PASS_RUSH.snap_counts_pass_rush) / NULLIF(SUM(PASS_RUSH.snap_counts_pass_rush), 0), 1) as rush,
    SUM(PASS_RUSH.true_pass_set_snap_counts_pass_play) as t_snap_pp,
    SUM(PASS_RUSH.true_pass_set_snap_counts_pass_rush) as t_snap_pr,
    SUM(PASS_RUSH.true_pass_set_hurries) as t_hur,
    SUM(PASS_RUSH.true_pass_set_hits) as t_hit,
    SUM(PASS_RUSH.true_pass_set_sacks) as t_sk,
    SUM(PASS_RUSH.true_pass_set_total_pressures) as t_pr,
    SUM(PASS_RUSH.true_pass_set_pass_rush_opp) as t_pass_rush,
    SUM(PASS_RUSH.true_pass_set_pass_rush_wins) as t_pass_win,
    SUM(PASS_RUSH.true_pass_set_batted_passes) as t_bat,
    ROUND(SUM(PASS_RUSH.true_pass_set_grades_pass_rush_defense * PASS_RUSH.true_pass_set_snap_counts_pass_rush) / NULLIF(SUM(PASS_RUSH.true_pass_set_snap_counts_pass_rush), 0), 1) as t_rush
"""



RUN_DEFENSE_SUM = """
    SUM(RUN_DEFENSE.assists) as ast,
    SUM(RUN_DEFENSE.avg_depth_of_tackle) as adot,
    SUM(RUN_DEFENSE.forced_fumbles) as ff,
    SUM(RUN_DEFENSE.grades_run_defense) 
    SUM(RUN_DEFENSE.grades_tackle)
    SUM(RUN_DEFENSE.missed_tackles) as mtk,
    SUM(RUN_DEFENSE.penalties) as pen,
    SUM(RUN_DEFENSE.run_stop_opp) as snaps,
    SUM(RUN_DEFENSE.stops) as stp,
    SUM(RUN_DEFENSE.tackles) as tkl,
"""



COVERAGE_SUM = """
    SUM(COVERAGE.avg_depth_of_target) as adot,
    SUM(COVERAGE.dropped_ints) dint,
    SUM(COVERAGE.forced_incompletes) finc,
    SUM(COVERAGE.grades_coverage_defense)
    SUM(COVERAGE.interceptions) as int,
    SUM(COVERAGE.pass_break_ups) as pbu,
    SUM(COVERAGE.receptions) as rec,
    SUM(COVERAGE.snap_counts_coverage) as snap,
    SUM(COVERAGE.targets) as tgt,
    SUM(COVERAGE.touchdowns) as td,
    SUM(COVERAGE.yards) as yds,
    SUM(COVERAGE.yards_after_catch) as yac
"""



SUM_TABLE = {
    "passing": {"query": PASSING_SUM, "table": "PASSING"},
    "rushing": {"query": RUSHING_SUM, "table": "RUSHING"},
    "receiving": {"query": RECEIVING_SUM, "table": "RECEIVING"},
    "blocking": {"query": BLOCKING_SUM, "table": "BLOCKING"},
    "pass_blocking": {"query": PASS_BLOCKING_SUM, "table": "PASS_BLOCKING"},
    "run_blocking": {"query": RUN_BLOCKING_SUM, "table": "RUN_BLOCKING"},
    "pass_rush": {"query": PASS_RUSH_SUM, "table": "PASS_RUSH"},
    "run_defense": {"query": RUN_DEFENSE_SUM, "table": "RUN_DEFENCE"},
    "coverage": {"query": COVERAGE_SUM, "table": "COVERAGE"}
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
    "run_defence": RUN_DEFENSE_INSERT,
    "coverage": COVERAGE_INSERT
}



def get_query(args: dict, _type: str, is_player: bool) -> str:
    start_week, end_week, start_year, end_year, stat_type, league, version, pos, limit, team = args.values()
    
    query, table = SUM_TABLE[_type].values()
    select = PLAYER_SELECT if is_player else TEAM_SELECT
    select = select.format(SUM=query, TABLE=table)

    conditions = []
    select += f"JOIN GAME_DATA on {table}.Game_ID = GAME_DATA.Game_ID\n"
    select += f"JOIN TEAMS on {table}.Team_ID = TEAMS.Team_ID\n"
    select += (f"JOIN PLAYERS on {table}.Player_ID = PLAYERS.Player_ID\n")

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
    # if pos is not None:
    #     conditions.append(f"PLAYERS.Pos IN [{','.join(f"'{p}'" for p in pos)}]")
    if team is not None:
        conditions.append(f"TEAMS.Team_Abbr = '{team}'")

    if conditions:
        select += "WHERE " + " \nAND ".join(conditions)
    
    key = f"{table}.Player_ID" if is_player else f"{table}.Team_ID"
    select += f"\nGROUP BY {key}, {table}.Year"
    # if limit is not None:
    #     select += f"\nLIMIT {limit}"
    return select



if __name__ == "__main__":
    start_week = 1
    end_week = 18
    start_year = 2006
    end_year = 2024
    stat_type = "rushing"
    league = "NFL"
    version = "0.0"
    pos = None
    limit = None
    team = "IND"
    args = {"start_week": start_week, "end_week": end_week, "start_year": start_year, "end_year": end_year, "stat_type": stat_type, "league": league, "version": version, "pos": pos, "limit": limit, "team": team}
    get_query(args, "passing", False)