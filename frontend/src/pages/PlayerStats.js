import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  CircularProgress,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import api from '../services/api';

// Register ChartJS components
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const PlayerStats = () => {
  const { playerId, year } = useParams();
  const [playerData, setPlayerData] = useState(null);
  const [playerInfo, setPlayerInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch player stats
        const statsResponse = await api.getPlayerStats(playerId, parseInt(year));
        setPlayerData(statsResponse.data);
        
        // Fetch player info separately if needed
        // const playersResponse = await api.getPlayers();
        // const playerInfo = playersResponse.data.find(p => p.id === parseInt(playerId));
        // setPlayerInfo(playerInfo);
        
        setError(null);
      } catch (error) {
        console.error('Error fetching player stats:', error);
        setError('Failed to load player statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [playerId, year]);

  // Prepare radar chart data for QB performance metrics
  const radarData = {
    labels: ['Completion %', 'Big Time Throws', 'TD Rate', 'INT Rate', 'Yards/Att', 'Grade'],
    datasets: [
      {
        label: `${year} Performance`,
        data: playerData?.passing ? [
          (playerData.passing.completions / Math.max(1, playerData.passing.attempts)) * 100,
          (playerData.passing.big_time_throws / Math.max(1, playerData.passing.dropbacks)) * 100 * 5, // Scale up for visibility
          (playerData.passing.touchdowns / Math.max(1, playerData.passing.attempts)) * 100 * 3, // Scale up for visibility
          (1 - (playerData.passing.interceptions / Math.max(1, playerData.passing.attempts))) * 100, // Invert so higher is better
          (playerData.passing.yards / Math.max(1, playerData.passing.attempts)),
          playerData.passing.grade_pass || 0,
        ] : [0, 0, 0, 0, 0, 0],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
      },
    ],
  };

  const radarOptions = {
    scales: {
      r: {
        angleLines: {
          display: true,
        },
        suggestedMin: 0,
        suggestedMax: 100,
      },
    },
  };

  if (loading) {
    return (
      <Container sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography color="error">{error}</Typography>
      </Container>
    );
  }

  // If no passing data, show message
  if (!playerData?.passing) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography>No passing statistics available for this player in {year}.</Typography>
      </Container>
    );
  }

  const { passing } = playerData;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Player #{playerId} - {year} Season Stats
      </Typography>
      
      <Divider sx={{ mb: 3 }} />
      
      <Grid container spacing={3}>
        {/* Player Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Season Overview</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Games Played:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {passing.games || 0}
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Passing Grade:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {passing.grade_pass?.toFixed(1) || 'N/A'}/100
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Completion %:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {passing.completions && passing.attempts 
                  ? ((passing.completions / passing.attempts) * 100).toFixed(1) 
                  : 'N/A'}%
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                TD/INT Ratio:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {passing.touchdowns && passing.interceptions 
                  ? (passing.touchdowns / Math.max(1, passing.interceptions)).toFixed(2) 
                  : 'N/A'}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        {/* Radar Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Box sx={{ height: '100%' }}>
              <Radar data={radarData} options={radarOptions} />
            </Box>
          </Paper>
        </Grid>
        
        {/* Passing Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Passing Statistics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Completions</Typography>
                <Typography variant="h6">{passing.completions || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Attempts</Typography>
                <Typography variant="h6">{passing.attempts || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Passing Yards</Typography>
                <Typography variant="h6">{passing.yards || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Touchdowns</Typography>
                <Typography variant="h6">{passing.touchdowns || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Interceptions</Typography>
                <Typography variant="h6">{passing.interceptions || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Yards/Attempt</Typography>
                <Typography variant="h6">
                  {passing.yards && passing.attempts 
                    ? (passing.yards / passing.attempts).toFixed(1) 
                    : '0.0'}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Big Time Throws</Typography>
                <Typography variant="h6">{passing.big_time_throws || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Turnover Worthy</Typography>
                <Typography variant="h6">{passing.turnover_worthy_plays || 0}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
        
        {/* Advanced Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Advanced Metrics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Dropbacks</Typography>
                <Typography variant="h6">{passing.dropbacks || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Avg Depth of Target</Typography>
                <Typography variant="h6">
                  {passing.avg_depth_of_target && passing.attempts 
                    ? (passing.avg_depth_of_target / passing.attempts).toFixed(1) 
                    : '0.0'}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Sacks</Typography>
                <Typography variant="h6">{passing.sacks || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">First Downs</Typography>
                <Typography variant="h6">{passing.first_downs || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Drops</Typography>
                <Typography variant="h6">{passing.drops || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Bats</Typography>
                <Typography variant="h6">{passing.bats || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Hit As Threw</Typography>
                <Typography variant="h6">{passing.hit_as_threw || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Throwaways</Typography>
                <Typography variant="h6">{passing.thrown_aways || 0}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default PlayerStats; 