import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import './App.css';

// Components
import Navbar from './components/Navbar';
import Home from './pages/Home';
import TeamStats from './pages/TeamStats';
import PlayerStats from './pages/PlayerStats';
import CompareTeams from './pages/CompareTeams';
import ComparePlayersPage from './pages/ComparePlayersPage';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1e3a8a', // Football blue
    },
    secondary: {
      main: '#d97706', // Football brown/gold
    },
    background: {
      default: '#f3f4f6',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/team-stats/:teamName/:year" element={<TeamStats />} />
          <Route path="/player-stats/:playerId/:year" element={<PlayerStats />} />
          <Route path="/compare-teams" element={<CompareTeams />} />
          <Route path="/compare-players" element={<ComparePlayersPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App; 