from flask import Flask, jsonify, request
from flask_cors import CORS
from db import DB

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/teams', methods=['GET'])
def get_teams():
    db = DB()
    try:
        db.cursor.execute("SELECT Team_ID, Team_Name FROM TEAMS")
        teams = [{"id": team[0], "name": team[1]} for team in db.cursor.fetchall()]
        return jsonify(teams)
    finally:
        db.kill()

@app.route('/api/players', methods=['GET'])
def get_players():
    position = request.args.get('position')
    db = DB()
    try:
        query = "SELECT Player_ID, Player_Name, Player_Pos FROM PLAYERS"
        params = []
        
        if position:
            query += " WHERE Player_Pos = ?"
            params.append(position)
            
        db.cursor.execute(query, params)
        players = [{"id": p[0], "name": p[1], "position": p[2]} for p in db.cursor.fetchall()]
        return jsonify(players)
    finally:
        db.kill()

@app.route('/api/team-stats/<team>/<int:year>', methods=['GET'])
def get_team_stats(team, year):
    start_week = request.args.get('start_week', type=int)
    end_week = request.args.get('end_week', type=int)
    
    db = DB()
    try:
        stats = db.sum_team_stats(team, year, start_week, end_week)
        if not stats:
            return jsonify({"error": "No stats found"}), 404
            
        # Create a formatted response with proper column names
        result = {
            "games": stats[0],
            "aimed_passes": stats[1],
            "attempts": stats[2],
            "avg_depth_of_target": stats[3],
            "bats": stats[4],
            "big_time_throws": stats[5],
            "completions": stats[6],
            "dropbacks": stats[7],
            "drops": stats[8],
            "first_downs": stats[9],
            "hit_as_threw": stats[10],
            "interceptions": stats[11],
            "passing_snaps": stats[12],
            "penalties": stats[13],
            "sacks": stats[14],
            "scrambles": stats[15],
            "spikes": stats[16],
            "thrown_aways": stats[17],
            "touchdowns": stats[18],
            "turnover_worthy_plays": stats[19],
            "yards": stats[20],
            "grade_pass": stats[21]
        }
        return jsonify(result)
    finally:
        db.kill()

@app.route('/api/player-stats/<int:player_id>/<int:year>', methods=['GET'])
def get_player_stats(player_id, year):
    db = DB()
    try:
        # Get passing stats
        query = """
        SELECT 
            COUNT(DISTINCT Game_ID) as games,
            SUM(aimed_passes), SUM(attempts), SUM(avg_depth_of_target), 
            SUM(bats), SUM(big_time_throws), SUM(completions), SUM(dropbacks),
            SUM(drops), SUM(first_downs), SUM(hit_as_threw), SUM(interceptions),
            SUM(passing_snaps), SUM(penalties), SUM(sacks), SUM(scrambles),
            SUM(spikes), SUM(thrown_aways), SUM(touchdowns), SUM(turnover_worthy_plays),
            SUM(yards), AVG(grade_pass)
        FROM PASSING
        JOIN GAME_DATA ON PASSING.Game_ID = GAME_DATA.Game_ID
        WHERE PASSING.Player_ID = ? AND GAME_DATA.Year = ? AND Type = 'passing'
        """
        
        db.cursor.execute(query, (player_id, year))
        passing = db.cursor.fetchone()
        
        if not passing or passing[0] == 0:
            passing_stats = None
        else:
            # Format stats with column names
            passing_stats = {
                "games": passing[0],
                "aimed_passes": passing[1],
                "attempts": passing[2],
                "avg_depth_of_target": passing[3],
                "bats": passing[4],
                "big_time_throws": passing[5],
                "completions": passing[6],
                "dropbacks": passing[7],
                "drops": passing[8],
                "first_downs": passing[9],
                "hit_as_threw": passing[10],
                "interceptions": passing[11],
                "passing_snaps": passing[12],
                "penalties": passing[13],
                "sacks": passing[14],
                "scrambles": passing[15],
                "spikes": passing[16],
                "thrown_aways": passing[17],
                "touchdowns": passing[18],
                "turnover_worthy_plays": passing[19],
                "yards": passing[20],
                "grade_pass": passing[21]
            }
        
        return jsonify({"passing": passing_stats})
    finally:
        db.kill()

if __name__ == '__main__':
    app.run(debug=True, port=5000) 