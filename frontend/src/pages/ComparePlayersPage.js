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
  Divider,
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

const ComparePlayersPage = () => {
  const [players, setPlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState('QB');
  const [selectedYear, setSelectedYear] = useState(2023);
  const [loading, setLoading] = useState(false);
  const [playersData, setPlayersData] = useState([]);
  const [error, setError] = useState(null);

  // Fetch available players on load
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        setLoading(true);
        const response = await api.getPlayers(selectedPosition);
        setPlayers(response.data);
      } catch (error) {
        console.error('Error fetching players:', error);
        setError('Failed to load players. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchPlayers();
  }, [selectedPosition]);

  // Handle position change
  const handlePositionChange = (event) => {
    setSelectedPosition(event.target.value);
    setSelectedPlayers([]);
    setPlayersData([]);
  };

  // Handle year change
  const handleYearChange = (event) => {
    setSelectedYear(event.target.value);
    if (selectedPlayers.length > 0) {
      fetchPlayersStats(selectedPlayers, event.target.value);
    }
  };

  // Handle player selection
  const handlePlayerChange = (event) => {
    const playerIds = event.target.value;
    setSelectedPlayers(playerIds);
    if (playerIds.length > 0) {
      fetchPlayersStats(playerIds, selectedYear);
    } else {
      setPlayersData([]);
    }
  };

  // Fetch stats for selected players
  const fetchPlayersStats = async (playerIds, year) => {
    setLoading(true);
    setError(null);
    setPlayersData([]);
    
    try {
      const statsPromises = playerIds.map(playerId => 
        api.getPlayerStats(playerId, year)
      );
      
      const responses = await Promise.all(statsPromises);
      
      // Combine player data with player info
      const playerDataWithInfo = responses.map((response, index) => {
        const playerId = playerIds[index];
        const playerInfo = players.find(p => p.id === parseInt(playerId));
        return {
          id: playerId,
          name: playerInfo?.name || `Player #${playerId}`,
          position: playerInfo?.position || selectedPosition,
          stats: response.data
        };
      });
      
      setPlayersData(playerDataWithInfo);
    } catch (error) {
      console.error('Error fetching player stats:', error);
      setError('Failed to load player statistics. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Prepare bar chart data for comparison
  const barChartData = {
    labels: playersData.map(p => p.name),
    datasets: [
      {
        label: 'Passing Yards',
        data: playersData.map(p => p.stats?.passing?.yards || 0),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
      },
      {
        label: 'Touchdowns',
        data: playersData.map(p => p.stats?.passing?.touchdowns || 0),
        backgroundColor: 'rgba(75, 192, 192, 0.6)',
      },
      {
        label: 'Interceptions',
        data: playersData.map(p => p.stats?.passing?.interceptions || 0),
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
        text: 'Player Comparison',
      },
    },
  };

  // Array of available years
  const years = Array.from({ length: 19 }, (_, i) => 2023 - i);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Compare Players
      </Typography>
      
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {/* Position selector */}
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel>Position</InputLabel>
              <Select
                value={selectedPosition}
                label="Position"
                onChange={handlePositionChange}
              >
                <MenuItem value="QB">Quarterback</MenuItem>
                <MenuItem value="WR">Wide Receiver</MenuItem>
                <MenuItem value="TE">Tight End</MenuItem>
                <MenuItem value="RB">Running Back</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* Year selector */}
          <Grid item xs={12} sm={3}>
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
          
          {/* Player selector */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Select Players</InputLabel>
              <Select
                multiple
                value={selectedPlayers}
                label="Select Players"
                onChange={handlePlayerChange}
                renderValue={(selected) => {
                  return selected.map(playerId => {
                    const player = players.find(p => p.id === parseInt(playerId));
                    return player ? player.name : playerId;
                  }).join(', ');
                }}
              >
                {loading ? (
                  <MenuItem disabled>Loading players...</MenuItem>
                ) : (
                  players.map(player => (
                    <MenuItem key={player.id} value={player.id.toString()}>
                      {player.name}
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
      
      {!loading && playersData.length > 0 && (
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
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.name}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  <TableRow>
                    <TableCell>Games</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.games || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Completion %</TableCell>
                    {playersData.map(player => {
                      const passing = player.stats?.passing;
                      const completionPct = passing && passing.attempts > 0
                        ? ((passing.completions / passing.attempts) * 100).toFixed(1)
                        : '0.0';
                      return <TableCell key={player.id}>{completionPct}%</TableCell>;
                    })}
                  </TableRow>
                  <TableRow>
                    <TableCell>Yards</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.yards || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>TD</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.touchdowns || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>INT</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.interceptions || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Yards/Att</TableCell>
                    {playersData.map(player => {
                      const passing = player.stats?.passing;
                      const ypa = passing && passing.attempts > 0
                        ? (passing.yards / passing.attempts).toFixed(1)
                        : '0.0';
                      return <TableCell key={player.id}>{ypa}</TableCell>;
                    })}
                  </TableRow>
                  <TableRow>
                    <TableCell>Big Time Throws</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.big_time_throws || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Turnover Worthy</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>{player.stats?.passing?.turnover_worthy_plays || 0}</TableCell>
                    ))}
                  </TableRow>
                  <TableRow>
                    <TableCell>Grade</TableCell>
                    {playersData.map(player => (
                      <TableCell key={player.id}>
                        {player.stats?.passing?.grade_pass 
                          ? player.stats.passing.grade_pass.toFixed(1) 
                          : 'N/A'}
                      </TableCell>
                    ))}
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

export default ComparePlayersPage; 