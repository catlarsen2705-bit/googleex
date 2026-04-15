"""
Scheduler for automatic scraping and notifications.
Uses APScheduler to run scrapers at regular intervals.
"""

from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from backend.database import insert_products
from backend.notifications import send_sale_notification
from backend.scraper_manager import ScraperManager

scheduler = BackgroundScheduler()


def scheduled_scrape():
    """Run all scrapers and send notifications if sales are found."""
    print(f"[{datetime.utcnow().isoformat()}] Starting scheduled scrape...")

    products = ScraperManager.scrape_all()

    if products:
        insert_products(products)
        print(f"✓ Found {len(products)} products on sale")

        # Group products by store for notifications
        by_store = {}
        for product in products:
            store = product.store
            if store not in by_store:
                by_store[store] = []
            by_store[store].append(product)

        # Send notification for each store with sales
        for store, store_products in by_store.items():
            send_sale_notification(store, store_products)
    else:
        print("No sales found")


def start_scheduler(interval_minutes: int = 30) -> None:
    """Start the background scheduler."""
    if scheduler.running:
        print("Scheduler already running")
        return

    scheduler.add_job(
        scheduled_scrape,
        "interval",
        minutes=interval_minutes,
        id="scrape_job",
        name="Automatic scraping job",
        replace_existing=True,
    )

    scheduler.start()
    print(f"✓ Scheduler started (interval: {interval_minutes} minutes)")


def stop_scheduler() -> None:
    """Stop the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        print("✓ Scheduler stopped")
