import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    Typography,
    Button,
    Box,
    Container,
    IconButton,
    Menu,
    MenuItem,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import SportsSoccerIcon from '@mui/icons-material/SportsSoccer';

const Navbar = () => {
const navigate = useNavigate();
const [anchorEl, setAnchorEl] = React.useState(null);
const open = Boolean(anchorEl);

const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
};

const handleClose = () => {
    setAnchorEl(null);
};

const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Team Stats', path: '/compare-teams' },
    { name: 'Player Stats', path: '/compare-players' },
];

return (
    <AppBar position="static">
    <Container maxWidth="xl">
        <Toolbar disableGutters>
        {/* Logo and brand name */}
        <SportsSoccerIcon sx={{ display: { xs: 'none', md: 'flex' }, mr: 1 }} />
        <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
            mr: 2,
            display: { xs: 'none', md: 'flex' },
            fontWeight: 700,
            letterSpacing: '.1rem',
            color: 'inherit',
            textDecoration: 'none',
            }}
        >
            FOOTBALL HEAVEN
        </Typography>

        {/* Mobile menu */}
        <Box sx={{ flexGrow: 1, display: { xs: 'flex', md: 'none' } }}>
            <IconButton
            size="large"
            aria-controls="menu-appbar"
            aria-haspopup="true"
            onClick={handleMenu}
            color="inherit"
            >
            <MenuIcon />
            </IconButton>
            <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
            }}
            keepMounted
            transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
            }}
            open={open}
            onClose={handleClose}
            sx={{
                display: { xs: 'block', md: 'none' },
            }}
            >
            {navItems.map((item) => (
                <MenuItem key={item.name} onClick={() => {
                navigate(item.path);
                handleClose();
                }}>
                <Typography textAlign="center">{item.name}</Typography>
                </MenuItem>
            ))}
            </Menu>
        </Box>

        {/* Mobile logo */}
        <SportsSoccerIcon sx={{ display: { xs: 'flex', md: 'none' }, mr: 1 }} />
        <Typography
            variant="h6"
            noWrap
            component={Link}
            to="/"
            sx={{
            mr: 2,
            display: { xs: 'flex', md: 'none' },
            flexGrow: 1,
            fontWeight: 700,
            letterSpacing: '.1rem',
            color: 'inherit',
            textDecoration: 'none',
            }}
        >
            FOOTBALL HEAVEN
        </Typography>

        {/* Desktop menu */}
        <Box sx={{ flexGrow: 1, display: { xs: 'none', md: 'flex' } }}>
            {navItems.map((item) => (
            <Button
                key={item.name}
                component={Link}
                to={item.path}
                sx={{ my: 2, color: 'white', display: 'block' }}
            >
                {item.name}
            </Button>
            ))}
        </Box>
        </Toolbar>
    </Container>
    </AppBar>
);
};

export default Navbar; 