import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Slider,
    ToggleButton,
    ToggleButtonGroup,
} from '@mui/material';

// Regular season weeks
const regularSeasonMarks = [
    { value: 1, label: '1' },
    { value: 18, label: '18' },
];

// Playoff rounds with their week numbers
const playoffMarks = [
    { value: 29, label: 'WC' },
    { value: 30, label: 'DIV' },
    { value: 31, label: 'CONF' },
    { value: 32, label: 'SB' },
];

// Combined marks for both
const combinedMarks = [
    { value: 1, label: '1' },
    { value: 18, label: '18' },
    { value: 22, label: 'SB' },
];

// Map continuous weeks to actual weeks for the "both" view
const mapContinuousWeekToActual = (week) => {
    if (week <= 18) return week;
    return week + 10; // Maps 19->29, 20->30, 21->31, 22->32
};

// Map week numbers to readable labels
const getWeekLabel = (week) => {
    // For the "both" view with continuous weeks
    if (week >= 19 && week <= 22) {
        switch (week) {
            case 19: return 'Wild Card';
            case 20: return 'Divisional';
            case 21: return 'Conference';
            case 22: return 'Super Bowl';
        }
    }
    // For normal playoff weeks
    if (week >= 29) {
        switch (week) {
            case 29: return 'Wild Card';
            case 30: return 'Divisional';
            case 31: return 'Conference';
            case 32: return 'Super Bowl';
            default: return `Week ${week}`;
        }
    }
    // Regular season weeks
    return `Week ${week}`;
};
  
export default function DiscreteSliderValues() {
    const [seasonType, setSeasonType] = useState('regular');
    const [sliderConfig, setSliderConfig] = useState({
        min: 1,
        max: 18,
        marks: regularSeasonMarks,
        value: [1, 18]
    });
    
    // Update slider configuration when season type changes
    useEffect(() => {
        switch (seasonType) {
            case 'regular':
                setSliderConfig({
                    min: 1,
                    max: 18,
                    marks: regularSeasonMarks,
                    value: [1, 18]
                });
                break;
            case 'playoffs':
                setSliderConfig({
                    min: 29,
                    max: 32,
                    marks: playoffMarks,
                    value: [29, 32]
                });
                break;
            case 'both':
                setSliderConfig({
                    min: 1,
                    max: 22,
                    marks: combinedMarks,
                    value: [1, 22]
                });
                break;
            default:
                break;
        }
    }, [seasonType]);
    
    const handleChange = (event, newValue) => {
        setSliderConfig(prev => ({
            ...prev,
            value: newValue
        }));
    };
    
    const handleSeasonTypeChange = (event, newSeasonType) => {
        if (newSeasonType !== null) {
            setSeasonType(newSeasonType);
        }
    };
    
    // Get the actual week value for API calls
    const getActualWeekValue = (displayedWeek) => {
        return seasonType === 'both' ? mapContinuousWeekToActual(displayedWeek) : displayedWeek;
    };
    
    return (
        <>
        <div style={{
            textAlign: 'center',
            marginBottom: '20px',
            fontSize: '24px'
        }}>
            Select Season Type
        </div>
        <Box sx={{ 
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '20px'
        }}>
            <ToggleButtonGroup
                value={seasonType}
                exclusive
                onChange={handleSeasonTypeChange}
                aria-label="season type"
            >
                <ToggleButton value="regular" aria-label="regular season">
                    Regular Season
                </ToggleButton>
                <ToggleButton value="playoffs" aria-label="playoffs">
                    Playoffs
                </ToggleButton>
                <ToggleButton value="both" aria-label="both">
                    Both
                </ToggleButton>
            </ToggleButtonGroup>
        </Box>
        
        <div style={{
            textAlign: 'center',
            marginBottom: '20px',
            fontSize: '24px'
        }}>
            Select Week Range
        </div>
        <Box sx={{ 
            width: 300,
            margin: '0 auto'
        }}>
            <Slider
            value={sliderConfig.value}
            onChange={handleChange}
            valueLabelDisplay="auto"
            aria-labelledby="range-slider"
            getAriaValueText={(value) => getWeekLabel(value)}
            step={1}
            marks={sliderConfig.marks}
            min={sliderConfig.min}
            max={sliderConfig.max}
            />
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                <div>Start: {getWeekLabel(sliderConfig.value[0])}</div>
                <div>End: {getWeekLabel(sliderConfig.value[1])}</div>
            </Box>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button 
                variant="contained" 
                color="primary"
                onClick={() => {
                    const actualStartWeek = getActualWeekValue(sliderConfig.value[0]);
                    const actualEndWeek = getActualWeekValue(sliderConfig.value[1]);
                    console.log(`Generate for weeks ${actualStartWeek} to ${actualEndWeek}`);
                    // Here you would call your API with the actual week values
                }}
            >
                Generate
            </Button>
        </Box>
        </>
    );
}