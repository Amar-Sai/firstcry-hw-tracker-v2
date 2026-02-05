#!/usr/bin/env python3
"""
FirstCry Hot Wheels Real-Time Monitor
Multi-layered discovery with state-based notifications
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from typing import Dict, Set, List, Optional
from enum import Enum
import sqlite3
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductState(Enum):
    """Product lifecycle states"""
    NEW = "NEW"              # Never seen before
    BUYABLE = "BUYABLE"      # Currently in stock and purchasable
    OUT_OF_STOCK = "OUT_OF_STOCK"  # Exists but not buyable
    HIDDEN = "HIDDEN"        # No longer visible in any discovery surface


@dataclass
class Product:
    """Product data model"""
    product_id: str
    name: str
    url: str
    price: Optional[float]
    state: ProductState
    last_seen: str
    first_discovered: str
    brand_verified: bool = False


class ProductDatabase:
    """SQLite database for persistent state tracking"""
    
    def __init__(self, db_path: str = "hotwheels_products.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id TEXT PRIMARY KEY,
                name TEXT,
                url TEXT,
                price REAL,
                state TEXT,
                last_seen TEXT,
                first_discovered TEXT,
                brand_verified INTEGER,
                notification_sent INTEGER DEFAULT 0
            )
        """)
        
        cursor.execute("""
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
        """Retrieve product from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM products WHERE product_id = ?",
            (product_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
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
        return None
    
    def save_product(self, product: Product):
        """Save or update product in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
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
    
    def log_transition(self, product_id: str, from_state: ProductState, 
                      to_state: ProductState, notified: bool):
        """Log state transition"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
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
    
    def get_all_products(self) -> List[Product]:
        """Get all tracked products"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        conn.close()
        
        products = []
        for row in rows:
            products.append(Product(
                product_id=row[0],
                name=row[1],
                url=row[2],
                price=row[3],
                state=ProductState(row[4]),
                last_seen=row[5],
                first_discovered=row[6],
                brand_verified=bool(row[7])
            ))
        
        return products


class FirstCryScraper:
    """Multi-layered product discovery"""
    
    BASE_URL = "https://www.firstcry.com"
    
    DISCOVERY_SURFACES = {
        "brand_listing": "/hot-wheels/0/0/113",
        "search_results": "/search?searchstring=hot%20wheels",
        "toy_cars_category": "/hot-wheels/toy-cars,-trains-and-vehicles/5/94/113"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def discover_products(self) -> Set[str]:
        """
        Multi-layered discovery: collect product URLs from all surfaces
        Returns set of product URLs (candidates for validation)
        """
        candidates = set()
        
        for surface_name, path in self.DISCOVERY_SURFACES.items():
            logger.info(f"Scanning discovery surface: {surface_name}")
            
            try:
                url = self.BASE_URL + path
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract product links
                    product_links = soup.find_all('a', href=re.compile(r'/hot-wheels/.*?/\d+/product-detail'))
                    
                    for link in product_links:
                        href = link.get('href')
                        if href:
                            full_url = self.BASE_URL + href if href.startswith('/') else href
                            candidates.add(full_url)
                    
                    logger.info(f"Found {len(product_links)} products on {surface_name}")
                else:
                    logger.warning(f"Failed to fetch {surface_name}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error scanning {surface_name}: {e}")
        
        logger.info(f"Total unique candidates discovered: {len(candidates)}")
        return candidates
    
    def validate_product(self, url: str) -> Optional[Dict]:
        """
        Validate product and extract detailed information
        Returns dict with product data or None if invalid
        """
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product ID from URL
            product_id = self._extract_product_id(url)
            if not product_id:
                return None
            
            # Extract product name
            name_elem = soup.find('h1', class_='prod-name') or soup.find('span', itemprop='name')
            name = name_elem.get_text(strip=True) if name_elem else None
            
            if not name:
                return None
            
            # Verify it's actually Hot Wheels
            brand_verified = self._verify_hot_wheels_brand(soup, name)
            
            # Determine buyability
            is_buyable = self._check_buyability(soup)
            
            # Extract price
            price = self._extract_price(soup)
            
            return {
                'product_id': product_id,
                'name': name,
                'url': url,
                'price': price,
                'is_buyable': is_buyable,
                'brand_verified': brand_verified
            }
            
        except Exception as e:
            logger.error(f"Error validating product {url}: {e}")
            return None
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """Extract product ID from URL"""
        match = re.search(r'/(\d+)/product-detail', url)
        return match.group(1) if match else None
    
    def _verify_hot_wheels_brand(self, soup: BeautifulSoup, name: str) -> bool:
        """Verify product is actually Hot Wheels brand"""
        # Check in product name
        if 'hot wheels' in name.lower() or 'hotwheels' in name.lower():
            return True
        
        # Check brand field
        brand_elem = soup.find('span', itemprop='brand') or soup.find('a', href=re.compile(r'/hot-wheels'))
        if brand_elem and 'hot wheels' in brand_elem.get_text(strip=True).lower():
            return True
        
        return False
    
    def _check_buyability(self, soup: BeautifulSoup) -> bool:
        """
        Determine if product is currently buyable
        Uses multiple signals to avoid false negatives
        """
        signals = []
        
        # Signal 1: Add to Cart button presence
        add_to_cart = soup.find('button', text=re.compile(r'ADD TO CART', re.I))
        signals.append(add_to_cart is not None)
        
        # Signal 2: No "Out of Stock" indicator
        out_of_stock = soup.find(text=re.compile(r'out of stock', re.I)) or \
                       soup.find('span', class_='out-of-stock')
        signals.append(out_of_stock is None)
        
        # Signal 3: Price is displayed
        price_elem = soup.find('span', class_='prod-price') or \
                    soup.find('span', itemprop='price')
        signals.append(price_elem is not None)
        
        # Signal 4: No "Notify Me" button (indicates out of stock)
        notify_me = soup.find(text=re.compile(r'notify me', re.I))
        signals.append(notify_me is None)
        
        # Product is buyable if majority of signals are positive
        return sum(signals) >= 3
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product price"""
        price_elem = soup.find('span', class_='prod-price') or \
                    soup.find('span', itemprop='price')
        
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            # Remove currency symbols and commas
            price_text = re.sub(r'[₹,]', '', price_text)
            try:
                return float(price_text)
            except ValueError:
                pass
        
        return None


class TelegramNotifier:
    """Send notifications via Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_notification(self, product: Product, is_restock: bool = False):
        """Send Telegram notification for new/restocked product"""
        
        status = "🔄 RESTOCK ALERT" if is_restock else "🆕 NEW PRODUCT ALERT"
        
        message = f"""
{status}

🏎️ *{product.name}*

💰 Price: ₹{product.price if product.price else 'N/A'}

🛒 Buy Now: {product.url}

⏰ Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Notification sent for {product.product_id}")
                return True
            else:
                logger.error(f"Failed to send notification: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False


class HotWheelsMonitor:
    """Main monitoring orchestrator"""
    
    def __init__(self, telegram_bot_token: str, telegram_chat_id: str):
        self.db = ProductDatabase()
        self.scraper = FirstCryScraper()
        self.notifier = TelegramNotifier(telegram_bot_token, telegram_chat_id)
    
    def should_notify(self, old_state: Optional[ProductState], 
                     new_state: ProductState) -> bool:
        """
        Determine if state transition warrants notification
        
        Valid transitions for notification:
        - NEW → BUYABLE
        - OUT_OF_STOCK → BUYABLE
        - HIDDEN → BUYABLE
        """
        if new_state != ProductState.BUYABLE:
            return False
        
        if old_state is None:  # NEW → BUYABLE
            return True
        
        if old_state in [ProductState.OUT_OF_STOCK, ProductState.HIDDEN]:
            return True
        
        return False
    
    def process_product(self, product_data: Dict) -> bool:
        """
        Process a validated product and determine notification
        Returns True if notification was sent
        """
        product_id = product_data['product_id']
        
        # Get existing product state
        existing = self.db.get_product(product_id)
        old_state = existing.state if existing else None
        
        # Determine new state
        if product_data['is_buyable']:
            new_state = ProductState.BUYABLE
        else:
            new_state = ProductState.OUT_OF_STOCK
        
        # Create/update product record
        now = datetime.now().isoformat()
        
        product = Product(
            product_id=product_id,
            name=product_data['name'],
            url=product_data['url'],
            price=product_data['price'],
            state=new_state,
            last_seen=now,
            first_discovered=existing.first_discovered if existing else now,
            brand_verified=product_data['brand_verified']
        )
        
        # Check if we should notify
        should_notify = self.should_notify(old_state, new_state)
        is_restock = old_state == ProductState.OUT_OF_STOCK
        
        # Save product state
        self.db.save_product(product)
        
        # Log transition
        if old_state != new_state:
            self.db.log_transition(product_id, old_state, new_state, should_notify)
            logger.info(
                f"State transition: {product.name} "
                f"{old_state.value if old_state else 'NEW'} → {new_state.value}"
            )
        
        # Send notification if warranted
        if should_notify:
            success = self.notifier.send_notification(product, is_restock)
            return success
        
        return False
    
    def run_scan(self):
        """Execute one complete scan cycle"""
        logger.info("=" * 60)
        logger.info("Starting scan cycle")
        logger.info("=" * 60)
        
        # Phase 1: Discovery
        candidates = self.scraper.discover_products()
        
        # Phase 2: Validation and Processing
        notifications_sent = 0
        
        for url in candidates:
            product_data = self.scraper.validate_product(url)
            
            if product_data and product_data['brand_verified']:
                if self.process_product(product_data):
                    notifications_sent += 1
            
            # Rate limiting
            time.sleep(0.5)
        
        logger.info(f"Scan complete. Notifications sent: {notifications_sent}")
    
    def run_continuous(self, interval_seconds: int = 120):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.run_scan()
                logger.info(f"Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scan cycle: {e}")
                time.sleep(60)  # Wait before retrying


def main():
    """Main entry point"""
    import os
    
    # Get credentials from environment variables
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return
    
    # Initialize and run monitor
    monitor = HotWheelsMonitor(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    
    # Run one scan or continuous monitoring
    import sys
    if '--once' in sys.argv:
        monitor.run_scan()
    else:
        monitor.run_continuous(interval_seconds=120)


if __name__ == "__main__":
    main()
