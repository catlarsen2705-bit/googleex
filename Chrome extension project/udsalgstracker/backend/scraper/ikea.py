from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from backend.models import Price, Product

IKEA_HOMEPAGE_URL = "https://www.ikea.com/dk/da"


def check_for_sales() -> bool:
    """Check if there are active sales on IKEA homepage."""
    try:
        response = requests.get(
            IKEA_HOMEPAGE_URL,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for sale/campaign indicators
        sale_patterns = [
            soup.find("a", href=lambda h: h and "sale" in h.lower()),
            soup.find("a", href=lambda h: h and "tilbud" in h.lower()),
            soup.find(class_=lambda c: c and "sale" in c.lower()),
            soup.find(class_=lambda c: c and "campaign" in c.lower()),
        ]

        has_sales = any(pattern is not None for pattern in sale_patterns)
        return has_sales
    except Exception as e:
        print(f"Error checking IKEA sales: {e}")
        return False


def scrape_ikea_sale() -> List[Product]:
    """
    Scrape IKEA sale/tilbud section for products on sale.
    """
    sale_url = f"{IKEA_HOMEPAGE_URL}/da/campaigns"

    try:
        response = requests.get(
            sale_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching IKEA sale page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Try multiple selectors for IKEA product items
    selectors = [
        "[data-product-id]",
        "div[class*='product']",
        "article[class*='product']",
        "li[class*='product']",
        "a[href*='/p/']",
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
                card.select_one("span[class*='name']")
                or card.select_one("h2")
                or card.select_one("h3")
                or card.select_one("[data-testid*='name']")
            )
            name = name_tag.get_text(strip=True) if name_tag else None

            # Extract price
            price_tag = (
                card.select_one("[class*='price']")
                or card.select_one("span[class*='price']")
                or card.select_one("[data-testid*='price']")
            )
            price_text = price_tag.get_text(strip=True) if price_tag else None

            # Extract product URL
            link_tag = card if card.name == "a" else card.select_one("a")
            url = None
            if link_tag and link_tag.has_attr("href"):
                url = link_tag["href"]
                if url.startswith("/"):
                    url = f"{IKEA_HOMEPAGE_URL}{url}"

            # Skip if no name or price
            if not name or not price_text:
                continue

            # Parse price
            cleaned_price = (
                price_text.replace("kr", "")
                .replace("DKK", "")
                .replace(",", ".")
                .replace(".", "", price_text.count(".") - 1)
                .strip()
            )
            try:
                amount = float(cleaned_price)
            except ValueError:
                continue

            products.append(
                Product(
                    store="IKEA",
                    name=name,
                    price=Price(amount=amount, currency="DKK"),
                    url=url,
                    scraped_at=datetime.utcnow(),
                )
            )
        except Exception as e:
            print(f"Error parsing IKEA product card: {e}")
            continue

    return products
