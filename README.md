# Gaming Performance Analysis Tools

This repository contains tools for analyzing gaming performance data collected from hardware monitoring during gameplay sessions. The tools help visualize and understand temperature patterns, performance metrics, and system behavior during gaming sessions.

## Features

### Temperature Analysis (`analyze_temperatures.py`)

- Analyzes GPU temperatures across multiple gaming sessions
- Identifies high and low temperature periods
- Generates separate temperature graphs for each gaming session
- Calculates average, maximum, and minimum temperatures
- Handles corrupted or missing data gracefully

### Key Metrics Tracked

- GPU Temperature
- GPU Hot Spot Temperature
- Temperature trends over time
- High and low temperature periods

## Requirements

- Python 3.x
- Required Python packages:
  - pandas
  - matplotlib
  - seaborn
  - numpy

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install pandas matplotlib seaborn numpy
```

## Usage

### Temperature Analysis

1. Place your CSV files in the `Data` directory
2. Run the analysis script:

```bash
python analyze_temperatures.py
```

The script will:

- Process each CSV file in the Data directory
- Generate temperature statistics for each session
- Create separate graphs for each gaming session
- Display high and low temperature periods

### Data Format

The CSV files should contain the following columns:

- Date: Date of the gaming session
- Time: Timestamp of the measurement
- GPU Temperature columns (automatically detected)

## Output

### Temperature Analysis Output

- Console output showing:
  - Average, maximum, and minimum temperatures
  - High temperature periods (with timestamps)
  - Low temperature periods (with timestamps)
- Separate graphs for each gaming session showing:
  - Temperature trends over time
  - Clear time labels (HH:MM format)
  - Temperature range (40-90°C)
  - Multiple GPU temperature metrics

## Data Cleaning Features

The tools include several data cleaning features:

- Handles missing or corrupted data points
- Filters out unrealistic temperature values
- Resamples data to reduce noise
- Skips sessions with invalid data
- Handles different date/time formats

## Recent Changes

1. Separated temperature graphs for each session
2. Improved time axis formatting
3. Added data validation and cleaning
4. Enhanced error handling
5. Added temperature range validation
6. Improved legend readability
7. Added data resampling for cleaner graphs

## Future Improvements

- Add CPU temperature analysis
- Add performance metrics analysis
- Add power consumption tracking
- Add frame rate correlation
- Add export functionality for reports

## Contributing

Feel free to submit issues and enhancement requests!
