import React, { useState, useEffect } from 'react';
import {
    Slider,
    Box,
} from '@mui/material';

const marks = [
    {
        value: 1,
        label: '1',
    },
    {
        value: 18,
        label: '18',
    },
];
  
export default function DiscreteSliderValues() {
    const [weekRange, setWeekRange] = useState([1, 18]);
    
    const handleChange = (event, newValue) => {
        setWeekRange(newValue);
    };
    
    return (
        <>
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
            value={weekRange}
            onChange={handleChange}
            valueLabelDisplay="auto"
            aria-labelledby="range-slider"
            getAriaValueText={(value) => `Week ${value}`}
            step={1}
            marks={marks}
            min={1}
            max={18}
            />
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between' }}>
                <div>Beginning Week: {weekRange[0]}</div>
                <div>End Week: {weekRange[1]}</div>
            </Box>
        </Box>
        </>
    );
}