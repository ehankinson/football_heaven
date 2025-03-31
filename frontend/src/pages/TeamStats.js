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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import api from '../services/api';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const TeamStats = () => {
  const { teamName, year } = useParams();
  const [teamStats, setTeamStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedWeeks, setSelectedWeeks] = useState({ start: 1, end: 17 });

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.getTeamStats(
          teamName, 
          parseInt(year), 
          selectedWeeks.start, 
          selectedWeeks.end
        );
        setTeamStats(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching team stats:', error);
        setError('Failed to load team statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [teamName, year, selectedWeeks]);

  const handleWeekChange = (type) => (event) => {
    setSelectedWeeks({
      ...selectedWeeks,
      [type]: event.target.value,
    });
  };

  // Prepare chart data for passing stats
  const passingChartData = {
    labels: ['Completions', 'Attempts', 'Yards', 'Touchdowns', 'Interceptions'],
    datasets: [
      {
        label: 'Passing Statistics',
        data: teamStats ? [
          teamStats.completions,
          teamStats.attempts,
          teamStats.yards / 10, // Scale down yards for better visualization
          teamStats.touchdowns,
          teamStats.interceptions,
        ] : [],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(255, 99, 132, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Team Passing Statistics',
      },
    },
    maintainAspectRatio: false,
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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {teamName} - {year} Season Stats
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>Start Week</InputLabel>
              <Select
                value={selectedWeeks.start}
                label="Start Week"
                onChange={handleWeekChange('start')}
              >
                {[...Array(17)].map((_, i) => (
                  <MenuItem key={`start-${i+1}`} value={i+1}>Week {i+1}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth>
              <InputLabel>End Week</InputLabel>
              <Select
                value={selectedWeeks.end}
                label="End Week"
                onChange={handleWeekChange('end')}
              >
                {[...Array(17)].map((_, i) => (
                  <MenuItem key={`end-${i+1}`} value={i+1}>Week {i+1}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Box>

      <Divider sx={{ mb: 3 }} />
      
      <Grid container spacing={3}>
        {/* Team Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>Team Overview</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Games Played:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {teamStats?.games || 0}
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Passing Grade:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {teamStats?.grade_pass?.toFixed(1) || 'N/A'}/100
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                Completion %:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {teamStats?.completions && teamStats?.attempts 
                  ? ((teamStats.completions / teamStats.attempts) * 100).toFixed(1) 
                  : 'N/A'}%
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" component="span" color="text.secondary">
                TD/INT Ratio:
              </Typography>
              <Typography variant="body1" component="span" sx={{ ml: 1 }}>
                {teamStats?.touchdowns && teamStats?.interceptions 
                  ? (teamStats.touchdowns / Math.max(1, teamStats.interceptions)).toFixed(2) 
                  : 'N/A'}
              </Typography>
            </Box>
          </Paper>
        </Grid>
        
        {/* Passing Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400 }}>
            <Box sx={{ height: '100%' }}>
              <Bar data={passingChartData} options={chartOptions} />
            </Box>
          </Paper>
        </Grid>
        
        {/* Detailed Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Detailed Passing Statistics</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Dropbacks</Typography>
                <Typography variant="h6">{teamStats?.dropbacks || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Passing Yards</Typography>
                <Typography variant="h6">{teamStats?.yards || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Yards per Attempt</Typography>
                <Typography variant="h6">
                  {teamStats?.yards && teamStats?.attempts 
                    ? (teamStats.yards / teamStats.attempts).toFixed(1) 
                    : '0.0'}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Avg Depth of Target</Typography>
                <Typography variant="h6">
                  {teamStats?.avg_depth_of_target && teamStats?.attempts 
                    ? (teamStats.avg_depth_of_target / teamStats.attempts).toFixed(1) 
                    : '0.0'}
                </Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">First Downs</Typography>
                <Typography variant="h6">{teamStats?.first_downs || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Big Time Throws</Typography>
                <Typography variant="h6">{teamStats?.big_time_throws || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Turnover Worthy Plays</Typography>
                <Typography variant="h6">{teamStats?.turnover_worthy_plays || 0}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="body2" color="text.secondary">Sacks</Typography>
                <Typography variant="h6">{teamStats?.sacks || 0}</Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default TeamStats; 