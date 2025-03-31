import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
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

const CompareTeams = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeams, setSelectedTeams] = useState([]);
  const [selectedYear, setSelectedYear] = useState(2023);
  const [loading, setLoading] = useState(false);
  const [teamsData, setTeamsData] = useState([]);
  const [error, setError] = useState(null);

  // Fetch available teams on load
  useEffect(() => {
    const fetchTeams = async () => {
      try {
        setLoading(true);
        const response = await api.getTeams();
        setTeams(response.data);
      } catch (error) {
        console.error('Error fetching teams:', error);
        setError('Failed to load teams. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchTeams();
  }, []);

  // Handle year change
  const handleYearChange = (event) => {
    setSelectedYear(event.target.value);
    if (selectedTeams.length > 0) {
      fetchTeamsStats(selectedTeams, event.target.value);
    }
  };

  // Handle team selection
  const handleTeamChange = (event) => {
    const teamNames = event.target.value;
    setSelectedTeams(teamNames);
    if (teamNames.length > 0) {
      fetchTeamsStats(teamNames, selectedYear);
    } else {
      setTeamsData([]);
    }
  };

  // Fetch stats for selected teams
  const fetchTeamsStats = async (teamNames, year) => {
    setLoading(true);
    setError(null);
    setTeamsData([]);
    
    try {
      const statsPromises = teamNames.map(teamName => 
        api.getTeamStats(teamName, year)
      );
      
      const responses = await Promise.all(statsPromises);
      
      // Combine team data with team info
      const teamDataWithInfo = responses.map((response, index) => {
        const teamName = teamNames[index];
        return {
          name: teamName,
          stats: response.data
        };
      });
      
      setTeamsData(teamDataWithInfo);
    } catch (error) {
      console.error('Error fetching team stats:', error);
      setError('Failed to load team statistics. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare bar chart data for comparison
  const barChartData = {
    labels: teamsData.map(t => t.name),
    datasets: [
      {
        label: 'Passing Yards',
        data: teamsData.map(t => t.stats?.yards || 0),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Touchdowns',
        data: teamsData.map(t => t.stats?.touchdowns || 0),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'Interceptions',
        data: teamsData.map(t => t.stats?.interceptions || 0),
        backgroundColor: 'rgba(255, 99, 132, 0.6)',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Team Comparison',
      },
    },
  };

  // Array of available years
  const years = Array.from({ length: 19 }, (_, i) => 2023 - i);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Compare Teams
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {/* Year selector */}
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Year</InputLabel>
              <Select
                value={selectedYear}
                label="Year"
                onChange={handleYearChange}
              >
                {years.map(year => (
                  <MenuItem key={year} value={year}>{year}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          {/* Team selector */}
          <Grid item xs={12} sm={8}>
            <FormControl fullWidth>
              <InputLabel>Select Teams</InputLabel>
              <Select
                multiple
                value={selectedTeams}
                label="Select Teams"
                onChange={handleTeamChange}
                renderValue={(selected) => selected.join(', ')}
              >
                {loading ? (
                  <MenuItem disabled>Loading teams...</MenuItem>
                ) : (
                  teams.map(team => (
                    <MenuItem key={team.id} value={team.name}>
                      {team.name}
                    </MenuItem>
                  ))
                )}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>
      
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}
      
      {error && (
        <Typography color="error" sx={{ my: 2 }}>
          {error}
        </Typography>
      )}
      
      {!loading && teamsData.length > 0 && (
        <>
          {/* Chart Comparison */}
          <Paper sx={{ p: 3, mb: 3, height: 400 }}>
            <Bar data={barChartData} options={chartOptions} />
          </Paper>
          
          {/* Table Comparison */}
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Detailed Comparison</Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Stat</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.name}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Games</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.games || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Passing Grade</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>
                        {team.stats?.grade_pass 
                          ? team.stats.grade_pass.toFixed(1) 
                          : 'N/A'}
                      </TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Completion %</TableCell>
                    {teamsData.map(team => {
                      const stats = team.stats;
                      const completionPct = stats && stats.attempts > 0
                        ? ((stats.completions / stats.attempts) * 100).toFixed(1)
                        : '0.0';
                      return <TableCell key={team.name}>{completionPct}%</TableCell>;
                    })}
                  </TableRow>
                  <TableRow>
                    <TableCell>Attempts</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.attempts || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Completions</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.completions || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Yards</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.yards || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>TD</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.touchdowns || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>INT</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.interceptions || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Yards/Att</TableCell>
                    {teamsData.map(team => {
                      const stats = team.stats;
                      const ypa = stats && stats.attempts > 0
                        ? (stats.yards / stats.attempts).toFixed(1)
                        : '0.0';
                      return <TableCell key={team.name}>{ypa}</TableCell>;
                    })}
                  </TableRow>
                  <TableRow>
                    <TableCell>Big Time Throws</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.big_time_throws || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Turnover Worthy</TableCell>
                    {teamsData.map(team => (
                      <TableCell key={team.name}>{team.stats?.turnover_worthy_plays || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Depth of Target</TableCell>
                    {teamsData.map(team => {
                      const stats = team.stats;
                      const dot = stats && stats.attempts > 0
                        ? (stats.avg_depth_of_target / stats.attempts).toFixed(1)
                        : '0.0';
                      return <TableCell key={team.name}>{dot}</TableCell>;
                    })}
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </>
      )}
    </Container>
  );
};

export default CompareTeams; 