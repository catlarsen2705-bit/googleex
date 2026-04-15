from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")
DATABASE_FILENAME = os.getenv("DATABASE_PATH", "udsalgstracker.db")
DATABASE_PATH = BASE_DIR.parent / DATABASE_FILENAME


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            url TEXT,
            scraped_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def insert_products(products: Iterable["Product"]) -> None:
    from backend.models import Product

    conn = get_connection()
    cursor = conn.cursor()
    rows = [
        (
            product.store,
            product.name,
            product.price.amount,
            product.price.currency,
            product.url,
            product.scraped_at.isoformat()
            if product.scraped_at
            else datetime.utcnow().isoformat(),
        )
        for product in products
    ]
    cursor.executemany(
        """
        INSERT INTO products (store, name, amount, currency, url, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    conn.close()
