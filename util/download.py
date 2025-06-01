import os
import requests
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('download_montreal_climate_data.log'),
        logging.StreamHandler()
    ]
)

# Configuration
BASE_URL = "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID="
           "https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&timeframe=2&submit=Download+Data"
STATIONS = [
    {"id": "7025250", "name": "Montreal_Trudeau_YUL"},
    {"id": "7024745", "name": "Montreal_McGill"}
]
DATA_DIR = "data"
START_YEAR = 2015
START_MONTH = 6  # June 2015
END_YEAR = 2025
END_MONTH = 5   # May 2025
TIMEFRAME = 2   # Daily data

# Headers to mimic a browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}

def create_directory(path):
    """Create a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def download_csv(url, save_path):
    """Download a CSV file from a URL and save it to the specified path."""
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True)
        if response.status_code == 200:
            # Check if the response is a CSV (not a redirect to HTML)
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type or 'application/octet-stream' in content_type:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                logging.warning(f"Non-CSV response for {url}. Content-Type: {content_type}")
                return False
        else:
            logging.warning(f"Failed to download {url}. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return False

def main():
    # Create base data directory
    create_directory(DATA_DIR)

    # Loop through each station
    for station in STATIONS:
        station_id = station['id']
        station_name = station['name']
        logging.info(f"Processing station: {station_name} (ID: {station_id})")

        # Create station directory
        station_dir = os.path.join(DATA_DIR, station_name)
        create_directory(station_dir)

        # Loop through years and months
        for year in range(START_YEAR, END_YEAR + 1):
            start_month = START_MONTH if year == START_YEAR else 1
            end_month = END_MONTH if year == END_YEAR else 12
            for month in range(start_month, end_month + 1):
                # Generate URL
                url = f"{BASE_URL}{station_id}&Year={year}&Month={month}&Day=1&timeframe={TIMEFRAME}&submit=Download+Data"
                filename = f"{year}-{month:02d}.csv"
                save_path = os.path.join(station_dir, filename)

                # Skip if file already exists
                if os.path.exists(save_path):
                    logging.info(f"Skipping {save_path} (already exists)")
                    continue

                logging.info(f"Downloading {filename} for {station_name}")
                success = download_csv(url, save_path)

                if success:
                    logging.info(f"Successfully downloaded {save_path}")
                else:
                    logging.warning(f"Failed to download {filename} for {station_name}")

                # Avoid overwhelming the server
                time.sleep(1)

    logging.info("Download process completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Download interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")