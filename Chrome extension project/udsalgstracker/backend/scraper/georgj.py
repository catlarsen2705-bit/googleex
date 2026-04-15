from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from backend.models import Price, Product

GEORGJ_HOMEPAGE_URL = "https://www.georgjensenmuseet.dk"


def check_for_sales() -> bool:
    """Check if there are active sales on Georg Jensen homepage."""
    try:
        response = requests.get(
            GEORGJ_HOMEPAGE_URL,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for sale/campaign indicators
        sale_patterns = [
            soup.find("a", href=lambda h: h and "udsalg" in h.lower()),
            soup.find("a", href=lambda h: h and "sale" in h.lower()),
            soup.find(class_=lambda c: c and "sale" in c.lower()),
        ]

        has_sales = any(pattern is not None for pattern in sale_patterns)
        return has_sales
    except Exception as e:
        print(f"Error checking Georg Jensen sales: {e}")
        return False


def scrape_georgj_sale() -> List[Product]:
    """
    Scrape Georg Jensen sale section for products on sale.
    """
    sale_url = f"{GEORGJ_HOMEPAGE_URL}/udsalg"

    try:
        response = requests.get(
            sale_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching Georg Jensen sale page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Try multiple selectors for Georg Jensen product items
    selectors = [
        "div[class*='product']",
        "article[class*='product']",
        "li[class*='product']",
        "a[href*='/produkt/']",
    ]

    product_cards = []
    for selector in selectors:
        product_cards = soup.select(selector)
        if product_cards:
            break

    products: List[Product] = []

    for card in product_cards[:20]:
        try:
            # Extract product name
            name_tag = (
                card.select_one("h2")
                or card.select_one("h3")
                or card.select_one("[class*='name']")
                or card.select_one("[class*='title']")
            )
            name = name_tag.get_text(strip=True) if name_tag else None

            # Extract price
            price_tag = (
                card.select_one("span[class*='price']")
                or card.select_one("div[class*='price']")
                or card.select_one("[class*='amount']")
            )
            price_text = price_tag.get_text(strip=True) if price_tag else None

            # Extract product URL
            link_tag = card if card.name == "a" else card.select_one("a")
            url = None
            if link_tag and link_tag.has_attr("href"):
                url = link_tag["href"]
                if url.startswith("/"):
                    url = f"{GEORGJ_HOMEPAGE_URL}{url}"

            # Skip if no name or price
            if not name or not price_text:
                continue

            # Parse price
            cleaned_price = (
                price_text.replace("kr.", "")
                .replace("DKK", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            try:
                amount = float(cleaned_price)
            except ValueError:
                continue

            products.append(
                Product(
                    store="GEORG JENSEN",
                    name=name,
                    price=Price(amount=amount, currency="DKK"),
                    url=url,
                    scraped_at=datetime.utcnow(),
                )
            )
        except Exception as e:
            print(f"Error parsing Georg Jensen product card: {e}")
            continue

    return products
