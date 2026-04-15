import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import initialize_database, insert_products
from backend.scraper_manager import ScraperManager
from backend.scheduler import start_scheduler, stop_scheduler

app = FastAPI(title="Udsalgstracker Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    initialize_database()
    interval = int(os.getenv("SCRAPER_INTERVAL_MINUTES", "30"))
    start_scheduler(interval_minutes=interval)


@app.get("/")
def read_root():
    return {"message": "Udsalgstracker backend is running"}


@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test")
def test():
    """Test endpoint to verify backend is working."""
    return {
        "status": "ok",
        "message": "Backend is running and accessible",
        "timestamp": datetime.utcnow().isoformat()
    }
def scrape_all():
    """Run all scrapers and save results to database."""
    products = ScraperManager.scrape_all()
    insert_products(products)
    return {
        "total": len(products),
        "products": [product.dict() for product in products],
    }


@app.get("/scrape/{store}")
def scrape_store(store: str):
    """Run scraper for a specific store."""
    products = ScraperManager.scrape_store(store)
    insert_products(products)
    return {
        "store": store.upper(),
        "count": len(products),
        "products": [product.dict() for product in products],
    }


@app.get("/check-sales")
def check_sales():
    """Check if there are sales on all stores without scraping."""
    results = ScraperManager.check_all_sales()
    return {"sales_status": results}
