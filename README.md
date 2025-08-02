# BookTrack

A basic Python application to scrape book listings from a Big Bookseller and save results to a local SQLite database.
You can also export the database contents to an XLSX file.

I was interested by the changes in price and the rankings for my textbook and run these scripts 
as a launchd daemon (using LaunchControl for Mac) to track this over time. No guarantees that this will work for others
but it has been effective enough for my needs.

## Structure

- `main.py`: Entry point for the application. Scrapes a Big Bookseller and saves results to the database.
- `scraper/`: Contains scraping logic.
- `db/`: Contains database logic and export utilities.
- `models/`: Data models (if needed).
- `config_template.py`: Template for sensitive configuration variables. Copy to `config_private.py` and fill in your values.
- `requirements.txt`: Python dependencies.

## Configuration

1. Copy `config_template.py` to `config_private.py` and fill in your values for `ITEM_ID` and `EXPORT_PATH`.
2. Do **not** commit `config_private.py` to version control.

## Usage

1. Install dependencies:  
   `pip install -r requirements.txt`

2. Run the application to scrape and save a listing:  
   `python main.py`

3. To export all database entries to an XLSX file, run the export script:  
   `python db/export_to_xls.py`  
   The export path is set in your config file (`EXPORT_PATH`).

## Notes

- The export script (`db/export_to_xls.py`) is a stand-alone script. Run it whenever you want to generate an XLSX file from the current database contents.
- The application uses Selenium with undetected-chromedriver for reliable scraping.
- All sensitive configuration should be kept in `config.py` (not versioned).
