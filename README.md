# YouTube Trending Videos Analysis

A Python and Flask web application that analyzes a dataset of 300 YouTube trending videos to surface engagement metrics and regional trends.

## Features

- **Real-time filtering** - filter trending videos by region, category, and date range
- **Live statistics** - view metrics such as views, likes, comments, and engagement rate as they update
- **CSV export** - download filtered results for offline analysis
- **Regional trend view** - compare how trending content differs across regions

## How It Works

1. The app loads a dataset of 300 YouTube trending videos
2. Flask serves a web interface where users can apply filters
3. Engagement metrics are calculated and displayed live as filters are applied
4. Users can export any filtered view as a CSV file

## Tech Stack

- **Backend:** Python, Flask
- **Data Handling:** Pandas (or equivalent) for dataset processing
- **Output:** CSV export, live dashboard view

## Why This Project

Built to practice translating raw, unstructured data into clear, actionable insights - the same core skill used in product analytics to understand user behavior and content performance.

## Setup

```bash
# Clone the repository
git clone <repo-url>
cd youtube-trending-analysis

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## Usage

1. Launch the app and open it in your browser
2. Use the filter panel to narrow down by region, category, or date
3. View live stats update automatically
4. Click "Export CSV" to download the current filtered view

## Future Improvements

- Add visualizations (charts/graphs) for engagement trends
- Support additional datasets beyond the initial 300 videos
- Add predictive trend forecasting
