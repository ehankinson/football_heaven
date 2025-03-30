-- Drop existing table if it exists
DROP TABLE IF EXISTS RECEIVING;

-- Create RECEIVING table with appropriate columns and constraints
CREATE TABLE RECEIVING (
    ROWID INTEGER PRIMARY KEY AUTOINCREMENT,
    Player_ID INTEGER NOT NULL,
    Game_ID INTEGER NOT NULL,
    Team_ID INTEGER NOT NULL,
    Type TEXT NOT NULL,
    Year INTEGER NOT NULL,
    avoided_tackles INTEGER DEFAULT 0,
    contested_reception_ INTEGER DEFAULT 0,  -- Number of contested catches
    depth_of_target REAL DEFAULT 0,  -- Average depth of target in yards
    drops INTEGER DEFAULT 0,
    first_downs INTEGER DEFAULT 0,
    fumbles INTEGER DEFAULT 0,
    interceptions INTEGER DEFAULT 0,
    pass_blocks INTEGER DEFAULT 0,  -- Number of pass blocking snaps
    pass_plays INTEGER DEFAULT 0,  -- Total passing plays
    penalties INTEGER DEFAULT 0,
    receptions INTEGER DEFAULT 0,
    routes INTEGER DEFAULT 0,
    slot_snaps INTEGER DEFAULT 0,  -- Snaps in slot position
    targets INTEGER DEFAULT 0,
    touchdowns INTEGER DEFAULT 0,
    wide_snaps INTEGER DEFAULT 0,  -- Snaps in wide position
    yards INTEGER DEFAULT 0,
    yards_after_catch INTEGER DEFAULT 0,
    grades_hands_drop REAL DEFAULT 0.0,  -- PFF grade for hands/drops
    grades_pass_route REAL DEFAULT 0.0,  -- PFF grade for route running
    FOREIGN KEY (Player_ID) REFERENCES PLAYERS(Player_ID),
    FOREIGN KEY (Game_ID) REFERENCES GAME_DATA(Game_ID),
    FOREIGN KEY (Team_ID) REFERENCES TEAMS(Team_ID),
    UNIQUE (Player_ID, Game_ID, Type)
); 