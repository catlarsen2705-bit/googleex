from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl


class Price(BaseModel):
    amount: float
    currency: str = "DKK"


class Product(BaseModel):
    store: str = "JYSK"
    name: str
    price: Price
    url: Optional[HttpUrl] = None
    scraped_at: Optional[datetime] = None
