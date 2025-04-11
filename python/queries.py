START = """
    Player_ID INT,
    GAME_ID INT,
    TEAM_ID INT,
    YEAR INT,
    LEAGUE VARCHAR(8),
    TYPE VARCHAR(64),
"""
END = """
FOREIGN KEY (Player_ID) REFERENCES PLAYERS(Player_ID),
FOREIGN KEY (GAME_ID, TEAM_ID) REFERENCES GAME_DATA(Game_ID, Team_ID)
PRIMARY KEY (Player_ID, GAME_ID, TEAM_ID, YEAR, LEAGUE, TYPE)"""



PLAYERS = """
    CREATE TABLE PLAYERS (
        Player_ID INT PRIMARY KEY,
        Player_Name VARCHAR(255),
        Player_Pos VARCHAR(64)
    )
"""



TEAMS = """
    CREATE TABLE TEAMS (
        TEAM_ID INT PRIMARY KEY,
        Team_Name VARCHAR(255)
    )
"""



GAME_DATA = """
    CREATE TABLE GAME_DATA (
        GAME_ID INT PRIMARY KEY,
        Team_ID INT,
        Year INT,
        Week INT,
        Opponent_ID INT,
        FOREIGN KEY (Team_ID) REFERENCES TEAMS(TEAM_ID),
        FOREIGN KEY (Opponent_ID) REFERENCES TEAMS(TEAM_ID)
    )
"""



PASSING = f"""
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

RECEIVING = f"""
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


PASS_SUM = """
    COUNT(DISTINCT PASSING.Game_ID) as gp,
    SUM(PASSING.passing_snaps) as snaps,
    SUM(PASSING.dropbacks) as db,
    SUM(PASSING.completions) as cmp,
    SUM(PASSING.aimed_passes) as aim,
    SUM(PASSING.attempts) as att,
    SUM(PASSING.yards) as yds,
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
    SUM(PASSING.penalties) as pen
"""

PASSING_SELECT = f"""
    SELECT
        PLAYERS.Player_Name,
        PLAYERS.Player_ID,
        PASSING.Year,
        {PASS_SUM}
    FROM PASSING
"""



TEAM_PASSING_SELECT = f"""
    SELECT
        TEAMS.Team_Name,
        TEAMS.Team_ID,
        PASSING.Year,
        {PASS_SUM}
    FROM PASSING
"""



RECEIVING_SELECT = f"""
    SELECT
        PLAYERS.Player_Name,
        PLAYERS.Player_ID,
        RECEIVING.Year,
        TEAMS.Team_Name,
        PLAYERS.Player_Pos,
        COUNT(DISTINCT RECEIVING.Game_ID) as gp,
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
        SUM(RECEIVING.yards_after_catch) as yac,
        SUM(RECEIVING.avoided_tackles) as at,
        SUM(RECEIVING.fumbles) as fum,
        SUM(RECEIVING.contested_targets) as ct,
        SUM(RECEIVING.contested_reception) as cr,
        SUM(RECEIVING.penalties) as pen
    FROM RECEIVING
"""




MAP = {
    'passing': PASSING,
    'receiving': RECEIVING,
    'players': PLAYERS,
    'teams': TEAMS,
    'game_data': GAME_DATA,
}



def generate_table(table_type: str) -> str:
    return MAP[table_type]



def get_players_passing(start_week: int, end_week: int, start_year: int, end_year: int, start_type: str, league: str, pos: list[str]) -> str:
    return f"""
        {PASSING_SELECT}
        JOIN GAME_DATA on PASSING.Game_ID = GAME_DATA.Game_ID
        JOIN PLAYERS on PASSING.Player_ID = PLAYERS.Player_ID
        WHERE Game_DATA.Week BETWEEN {start_week} and {end_week}
        AND PASSING.Year BETWEEN {start_year} and {end_year}
        AND PLAYERS.Player_Pos IN ({', '.join(f'"{p}"' for p in pos)})
        AND PASSING.Type = "{start_type}"
        AND PASSING.League = "{league}"
        GROUP BY PASSING.Player_ID, PASSING.Year
    """



def get_team_passing(start_week: int, end_week: int, start_year: int, end_year: int, start_type: str, league: str) -> str:
    return f"""
        {TEAM_PASSING_SELECT}
        JOIN GAME_DATA on PASSING.Game_ID = GAME_DATA.Game_ID
        JOIN TEAMS on PASSING.Team_ID = TEAMS.Team_ID
        WHERE Game_DATA.Week BETWEEN {start_week} and {end_week}
        AND PASSING.Year BETWEEN {start_year} and {end_year}
        AND PASSING.Type = "{start_type}"
        AND PASSING.League = "{league}"
        GROUP BY PASSING.Team_ID, PASSING.Year
    """



def get_players_receiving(start_week: int, end_week: int, start_year: int, end_year: int, start_type: str, league: str, pos: list[str]) -> str:
    return f"""
        {RECEIVING_SELECT}
        JOIN GAME_DATA on RECEIVING.Game_ID = GAME_DATA.Game_ID
        JOIN TEAMS on RECEIVING.Team_ID = TEAMS.Team_ID
        JOIN PLAYERS on RECEIVING.Player_ID = PLAYERS.Player_ID
        WHERE Game_DATA.Week BETWEEN {start_week} and {end_week}
        AND RECEIVING.Year BETWEEN {start_year} and {end_year}
        AND PLAYERS.Player_Pos IN ({', '.join(f'"{p}"' for p in pos)})
        AND RECEIVING.Type = "{start_type}"
        AND RECEIVING.League = "{league}"
        GROUP BY RECEIVING.Player_ID, RECEIVING.Year
    """



def get_passing_grades(start_week: int, end_week: int, start_year: int, end_year: int, start_type: str, league: str, pos: list[str]) -> str:
    return f"""
        SELECT
            PASSING.Player_ID,
            PASSING.Team_ID,
            PASSING.Year,
            PASSING.dropbacks,
            PASSING.grade_pass
        FROM PASSING
        JOIN GAME_DATA on PASSING.Game_ID = GAME_DATA.Game_ID
        JOIN PLAYERS on PASSING.Player_ID = PLAYERS.Player_ID
        WHERE PASSING.Year BETWEEN {start_year} and {end_year}
        AND GAME_DATA.Week BETWEEN {start_week} and {end_week}
        AND PASSING.Type = "{start_type}"
        AND PASSING.League = "{league}"
        AND PLAYERS.Player_Pos IN ({', '.join(f'"{p}"' for p in pos)})
    """


