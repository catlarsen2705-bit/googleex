from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from backend.models import Price, Product

JYSK_HOMEPAGE_URL = "https://www.jysk.dk"


def check_for_sales() -> bool:
    """Check if there are active sales on JYSK homepage."""
    try:
        response = requests.get(
            JYSK_HOMEPAGE_URL,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Look for sale indicators (common patterns)
        sale_patterns = [
            soup.find("a", href="/udsalg"),
            soup.find("span", string=lambda s: s and "udsalg" in s.lower()),
            soup.find("button", string=lambda s: s and "udsalg" in s.lower()),
            soup.find(class_=lambda c: c and "sale" in c.lower()),
            soup.find(class_=lambda c: c and "udsalg" in c.lower()),
        ]

        # If any sale indicator is found, there are sales
        has_sales = any(pattern is not None for pattern in sale_patterns)
        return has_sales
    except Exception as e:
        print(f"Error checking JYSK sales: {e}")
        return False


def scrape_jysk_sale() -> List[Product]:
    """
    Scrape JYSK sale page for products on sale.
    Returns a list of products with sale prices.
    """
    sale_url = f"{JYSK_HOMEPAGE_URL}/udsalg"

    try:
        response = requests.get(
            sale_url,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching JYSK sale page: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    # Try multiple selectors to find sale products
    selectors = [
        "a.product-tile",
        "div.product-tile",
        "a.product-card",
        "div.product-card",
        "[data-test-id*='product']",
        "article[class*='product']",
        "li[class*='product']",
    ]

    product_cards = []
    for selector in selectors:
        product_cards = soup.select(selector)
        if product_cards:
            break

    products: List[Product] = []

    for card in product_cards[:20]:  # Get top 20 sale items
        try:
            # Extract product name
            name_tag = (
                card.select_one("span.product-tile__name")
                or card.select_one("div.product-card__name")
                or card.select_one("h3")
                or card.select_one("[data-test-id*='name']")
            )
            name = name_tag.get_text(strip=True) if name_tag else None

            # Extract sale price
            price_tag = (
                card.select_one("span.product-tile__price")
                or card.select_one("div.price")
                or card.select_one("[data-test-id*='price']")
                or card.select_one("span.price")
            )
            price_text = price_tag.get_text(strip=True) if price_tag else None

            # Extract product URL
            link_tag = card if card.name == "a" else card.select_one("a")
            url = None
            if link_tag and link_tag.has_attr("href"):
                url = link_tag["href"]
                if url.startswith("/"):
                    url = f"{JYSK_HOMEPAGE_URL}{url}"

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
                    name=name,
                    price=Price(amount=amount, currency="DKK"),
                    url=url,
                    scraped_at=datetime.utcnow(),
                )
            )
        except Exception as e:
            print(f"Error parsing product card: {e}")
            continue

    return products
