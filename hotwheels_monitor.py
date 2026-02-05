#!/usr/bin/env python3
"""
FirstCry Hot Wheels Real-Time Monitor
State-aware discovery with Telegram notifications
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from typing import Dict, Set, List, Optional
from enum import Enum
import sqlite3
from dataclasses import dataclass
import logging
import os
import sys

# -------------------- Logging --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------- Models --------------------

class ProductState(Enum):
    NEW = "NEW"
    BUYABLE = "BUYABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    HIDDEN = "HIDDEN"


@dataclass
class Product:
    product_id: str
    name: str
    url: str
    price: Optional[float]
    state: ProductState
    last_seen: str
    first_discovered: str
    brand_verified: bool


# -------------------- Database --------------------

class ProductDatabase:
    def __init__(self, db_path: str = "hotwheels_products.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT,
                url TEXT,
                price REAL,
                state TEXT,
                last_seen TEXT,
                first_discovered TEXT,
                brand_verified INTEGER
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS state_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id TEXT,
                from_state TEXT,
                to_state TEXT,
                timestamp TEXT,
                notified INTEGER
            )
        """)

        conn.commit()
        conn.close()

    def get_product(self, product_id: str) -> Optional[Product]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return Product(
            product_id=row[0],
            name=row[1],
            url=row[2],
            price=row[3],
            state=ProductState(row[4]),
            last_seen=row[5],
            first_discovered=row[6],
            brand_verified=bool(row[7])
        )

    def save_product(self, product: Product):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT OR REPLACE INTO products
            (product_id, name, url, price, state, last_seen, first_discovered, brand_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.product_id,
            product.name,
            product.url,
            product.price,
            product.state.value,
            product.last_seen,
            product.first_discovered,
            int(product.brand_verified)
        ))

        conn.commit()
        conn.close()

    def log_transition(self, product_id, from_state, to_state, notified):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO state_transitions
            (product_id, from_state, to_state, timestamp, notified)
            VALUES (?, ?, ?, ?, ?)
        """, (
            product_id,
            from_state.value if from_state else None,
            to_state.value,
            datetime.now().isoformat(),
            int(notified)
        ))

        conn.commit()
        conn.close()


# -------------------- Scraper --------------------

class FirstCryScraper:
    BASE_URL = "https://www.firstcry.com"

    DISCOVERY_SURFACES = {
        "brand": "/hot-wheels/0/0/113",
        "search": "/search?searchstring=hot%20wheels",
        "category": "/hot-wheels/toy-cars,-trains-and-vehicles/5/94/113"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def discover_products(self) -> Set[str]:
        urls = set()

        for name, path in self.DISCOVERY_SURFACES.items():
            logger.info(f"Scanning {name}")
            try:
                r = self.session.get(self.BASE_URL + path, timeout=10)
                if r.status_code != 200:
                    continue

                soup = BeautifulSoup(r.content, "html.parser")
                links = soup.find_all("a", href=re.compile(r"/hot-wheels/.*/\d+/product-detail"))

                for a in links:
                    href = a.get("href")
                    if href:
                        urls.add(self.BASE_URL + href)
            except Exception as e:
                logger.error(f"Discovery error: {e}")

        logger.info(f"Discovered {len(urls)} candidates")
        return urls

    def validate_product(self, url: str) -> Optional[Dict]:
        try:
            r = self.session.get(url, timeout=10)
            if r.status_code != 200:
                return None

            soup = BeautifulSoup(r.content, "html.parser")
            product_id = self._extract_product_id(url)
            if not product_id:
                return None

            name_el = soup.find("h1", class_="prod-name") or soup.find("span", itemprop="name")
            if not name_el:
                return None

            name = name_el.get_text(strip=True)
            brand_verified = "hot wheels" in name.lower()
            is_buyable = self._check_buyable(soup)
            price = self._extract_price(soup)

            return {
                "product_id": product_id,
                "name": name,
                "url": url,
                "price": price,
                "is_buyable": is_buyable,
                "brand_verified": brand_verified
            }

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return None

    def _extract_product_id(self, url):
        m = re.search(r"/(\d+)/product-detail", url)
        return m.group(1) if m else None

    def _check_buyable(self, soup):
        if soup.find(text=re.compile("out of stock", re.I)):
            return False
        if soup.find(text=re.compile("notify me", re.I)):
            return False
        return soup.find("button", text=re.compile("add to cart", re.I)) is not None

    def _extract_price(self, soup):
        price_el = soup.find("span", class_="prod-price") or soup.find("span", itemprop="price")
        if not price_el:
            return None
        txt = re.sub(r"[₹,]", "", price_el.get_text(strip=True))
        try:
            return float(txt)
        except:
            return None


# -------------------- Telegram --------------------

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send(self, product: Product, kind: str):
        emoji = "🆕" if kind == "NEW" else "🔄"
        msg = (
            f"{emoji} *{kind} HOT WHEELS ALERT*\n\n"
            f"🏎️ {product.name}\n"
            f"💰 Price: ₹{product.price or 'N/A'}\n"
            f"🛒 {product.url}\n"
            f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        r = requests.post(self.url, json={
            "chat_id": self.chat_id,
            "text": msg,
            "parse_mode": "Markdown"
        })

        return r.status_code == 200


# -------------------- Monitor --------------------

class HotWheelsMonitor:
    def __init__(self, token, chat_id):
        self.db = ProductDatabase()
        self.scraper = FirstCryScraper()
        self.notifier = TelegramNotifier(token, chat_id)

    def should_notify(self, old_state, new_state):
        # Notify on first discovery
        if old_state is None:
            return True, "NEW"

        # Notify on restock
        if new_state == ProductState.BUYABLE and old_state != ProductState.BUYABLE:
            return True, "RESTOCK"

        return False, None

    def run_scan(self):
        logger.info("Starting scan")
        urls = self.scraper.discover_products()

        sent = 0
        for url in urls:
            data = self.scraper.validate_product(url)
            if not data or not data["brand_verified"]:
                continue

            existing = self.db.get_product(data["product_id"])
            old_state = existing.state if existing else None
            new_state = ProductState.BUYABLE if data["is_buyable"] else ProductState.OUT_OF_STOCK

            now = datetime.now().isoformat()
            product = Product(
                product_id=data["product_id"],
                name=data["name"],
                url=data["url"],
                price=data["price"],
                state=new_state,
                last_seen=now,
                first_discovered=existing.first_discovered if existing else now,
                brand_verified=True
            )

            notify, kind = self.should_notify(old_state, new_state)

            self.db.save_product(product)
            if old_state != new_state:
                self.db.log_transition(data["product_id"], old_state, new_state, notify)

            if notify:
                if self.notifier.send(product, kind):
                    sent += 1

            time.sleep(0.5)

        logger.info(f"Scan done. Notifications sent: {sent}")


# -------------------- Entry --------------------

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Missing Telegram credentials")
        return

    monitor = HotWheelsMonitor(token, chat_id)

    if "--once" in sys.argv:
        monitor.run_scan()
    else:
        while True:
            monitor.run_scan()
            time.sleep(120)


if __name__ == "__main__":
    main()

