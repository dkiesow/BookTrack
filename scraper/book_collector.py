import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def parse_detail_bullets(detail_div):
    parsed = []
    def parse_ul(ul):
        items = []
        for li in ul.find_all("li", recursive=False):
            label = None
            value = None
            label_span = li.find("span", class_="a-text-bold")
            if label_span:
                label = label_span.get_text(strip=True).rstrip(":")
                label_span.extract()
                value = li.get_text(strip=True)
            else:
                value = li.get_text(strip=True)
            # Check for nested <ul>
            sub_ul = li.find("ul", recursive=False)
            if sub_ul:
                subitems = parse_ul(sub_ul)
                if label:
                    items.append({label: {"value": value, "subitems": subitems}})
                else:
                    items.append({"value": value, "subitems": subitems})
            else:
                if label:
                    items.append({label: value})
                else:
                    items.append(value)
        return items

    for ul in detail_div.find_all("ul", recursive=False):
        parsed.extend(parse_ul(ul))
    return parsed

def find_details_div(header):
    # Try to find the nearest ancestor <div>
    ancestor = header.find_parent("div")
    if ancestor:
        return ancestor
    # If not found, try next siblings
    sibling = header.find_next_sibling()
    while sibling:
        if getattr(sibling, "name", None) == "div":
            return sibling
        sibling = sibling.find_next_sibling()
    return None

def scrape_listing(url):
    # Use undetected-chromedriver to avoid bot detection
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = uc.Chrome(options=options)
    try:
        driver.get(url)
        # Wait for product title to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "productTitle"))
        )
        html = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    # Title
    title = soup.find(id="productTitle")

    # Formats and prices: look for slot-title and slot-price pattern
    formats = []
    for slot_title in soup.find_all("span", class_="slot-title"):
        fmt = slot_title.get_text(strip=True)
        price = None
        # Look for adjacent slot-price span (next siblings)
        slot_price = slot_title.find_next_sibling("span", class_="slot-price")
        if slot_price:
            price_span = slot_price.find("span")
            if price_span:
                price = price_span.get_text(strip=True)
            else:
                price = slot_price.get_text(strip=True)
        formats.append({
            "format": fmt,
            "price": price
        })
    # Fallback to Northstar-Buybox logic if no slot-title found
    if not formats:
        def find_formats_prices(northstar_div):
            found = []
            for tag in northstar_div.find_all(['li', 'div', 'span', 'button'], recursive=True):
                text = tag.get_text(" ", strip=True)
                for fmt in ["Kindle", "Hardcover", "Paperback"]:
                    if fmt.lower() in text.lower():
                        price = None
                        price_tag = tag.find(string=re.compile(r"\$\d"))
                        if price_tag:
                            price = price_tag.strip()
                        else:
                            price_match = re.search(r"\$\d[\d,\.]*", text)
                            if price_match:
                                price = price_match.group(0)
                        found.append({
                            "format": fmt,
                            "price": price
                        })
            return found

        northstar_div = soup.find("div", id=re.compile("Northstar-Buybox", re.I))
        if not northstar_div:
            for div in soup.find_all("div"):
                if div.get("data-csa-c-type") and "Northstar-Buybox" in div.get("data-csa-c-type"):
                    northstar_div = div
                    break
                if "northstar-buybox" in " ".join(div.get("class", [])).lower():
                    northstar_div = div
                    break
        if northstar_div:
            formats = find_formats_prices(northstar_div)
        else:
            price = soup.find("span", {"class": "a-offscreen"})
            if price:
                formats.append({
                    "format": "Unknown",
                    "price": price.get_text(strip=True)
                })

    # Look for a header with "Product Details"
    header = None
    for tag in soup.find_all(['h1', 'h2', 'h3']):
        if "product details" in tag.get_text(strip=True).lower():
            header = tag
            break

    detail_div = None
    if header:
        detail_div = find_details_div(header)

    if detail_div:
        parsed_details = parse_detail_bullets(detail_div)
    else:
        parsed_details = []

    # Best Sellers Rank extraction (unchanged)
    ranks = []
    if detail_div:
        bsr_label = detail_div.find("span", class_="a-text-bold", string=re.compile(r"Best Sellers Rank"))
        if bsr_label:
            overall_text = bsr_label.next_sibling
            if overall_text:
                overall_match = re.search(r'#([\d,]+)\s+in\s+([^\(]+)', str(overall_text))
                if overall_match:
                    overall_rank = overall_match.group(1).replace(",", "")
                    overall_category = overall_match.group(2).strip()
                    ranks.append({
                        "rank": overall_rank,
                        "category": overall_category
                    })
            for item in detail_div.find_all("span", class_="a-list-item"):
                cat_match = re.search(r'#([\d,]+)\s+in\s+([^\n\(]+)', item.get_text())
                if cat_match:
                    rank_clean = cat_match.group(1).replace(",", "")
                    category_clean = cat_match.group(2).strip()
                    if not any(r["rank"] == rank_clean and r["category"] == category_clean for r in ranks):
                        ranks.append({
                            "rank": rank_clean,
                            "category": category_clean
                        })
    return {
        "title": title.get_text(strip=True) if title else None,
        "formats": formats,
        "best_sellers_rank": ranks,
        "product_details": parsed_details,
        "url": url
    }

