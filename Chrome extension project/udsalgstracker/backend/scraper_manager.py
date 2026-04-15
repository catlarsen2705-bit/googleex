"""
Scraper manager that runs all scrapers and collects their results.
"""

from typing import Dict, List

from backend.models import Product
from backend.scraper import jysk, ikea, imerco, hmhome, georgj


class ScraperManager:
    """Manages and runs all available scrapers."""

    SCRAPERS = {
        "jysk": {
            "check_sales": jysk.check_for_sales,
            "scrape": jysk.scrape_jysk_sale,
        },
        "ikea": {
            "check_sales": ikea.check_for_sales,
            "scrape": ikea.scrape_ikea_sale,
        },
        "imerco": {
            "check_sales": imerco.check_for_sales,
            "scrape": imerco.scrape_imerco_sale,
        },
        "hmhome": {
            "check_sales": hmhome.check_for_sales,
            "scrape": hmhome.scrape_hmhome_sale,
        },
        "georgj": {
            "check_sales": georgj.check_for_sales,
            "scrape": georgj.scrape_georgj_sale,
        },
    }

    @classmethod
    def check_all_sales(cls) -> Dict[str, bool]:
        """Check if there are sales on all stores."""
        results = {}
        for store_name, scraper_funcs in cls.SCRAPERS.items():
            try:
                has_sales = scraper_funcs["check_sales"]()
                results[store_name] = has_sales
            except Exception as e:
                print(f"Error checking sales for {store_name}: {e}")
                results[store_name] = False
        return results

    @classmethod
    def scrape_all(cls) -> List[Product]:
        """Run all scrapers and return combined results."""
        all_products: List[Product] = []

        for store_name, scraper_funcs in cls.SCRAPERS.items():
            try:
                products = scraper_funcs["scrape"]()
                all_products.extend(products)
                print(f"✓ {store_name.upper()}: {len(products)} products found")
            except Exception as e:
                print(f"✗ Error scraping {store_name}: {e}")
                continue

        return all_products

    @classmethod
    def scrape_store(cls, store_name: str) -> List[Product]:
        """Run a specific scraper by store name."""
        if store_name.lower() not in cls.SCRAPERS:
            raise ValueError(f"Unknown store: {store_name}")

        try:
            products = cls.SCRAPERS[store_name.lower()]["scrape"]()
            return products
        except Exception as e:
            print(f"Error scraping {store_name}: {e}")
            return []
