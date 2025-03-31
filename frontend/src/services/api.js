import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const api = {
  // Teams
  getTeams: () => {
    return axios.get(`${API_URL}/teams`);
  },
  
  // Players
  getPlayers: (position = null) => {
    let url = `${API_URL}/players`;
    if (position) {
      url += `?position=${position}`;
    }
    return axios.get(url);
  },
  
  // Team Stats
  getTeamStats: (team, year, startWeek = null, endWeek = null) => {
    let url = `${API_URL}/team-stats/${team}/${year}`;
    
    const params = new URLSearchParams();
    if (startWeek) params.append('start_week', startWeek);
    if (endWeek) params.append('end_week', endWeek);
    
    if (params.toString()) {
      url += `?${params.toString()}`;
    }
    
    return axios.get(url);
  },
  
  // Player Stats
  getPlayerStats: (playerId, year) => {
    return axios.get(`${API_URL}/player-stats/${playerId}/${year}`);
  }
};

export default api; 