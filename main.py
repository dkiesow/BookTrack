from db.database import init_db, save_listing
from config import ITEM_ID, BOOK_BASE_URL
from scraper.book_collector import scrape_listing

def main():
    init_db()
    url = f"{BOOK_BASE_URL}/dp/{ITEM_ID}"
    print(f"Scraping {url}")
    data = scrape_listing(url)
    save_listing(data)
    print("Listing saved.")
    print("Scraped data:")
    print(data)

if __name__ == "__main__":
    main()
