"""
Rare Source - Web Scraping Utilities
Example module for scraping real component distributors.
"""

import asyncio
import re
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Necessary libraries
try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️  httpx and beautifulsoup4 are required. Please pip install them.")

# --- MOUSER API CONNECTOR (Real Data) ---
class MouserConnector:
    """
    Connects to Mouser Search API (v1)
    """
    def __init__(self):
        self.api_key = os.getenv("MOUSER_API_KEY")
        self.base_url = "https://api.mouser.com/api/v1/search/partnumber"
        
    async def fetch_prices(self, query: str) -> List[Dict]:
        if not self.api_key or self.api_key == "YOUR_MOUSER_KEY":
            print("⚠️  Mouser API Key missing or invalid.")
            return []
            
        headers = {'Content-Type': 'application/json'}
        params = {'apiKey': self.api_key}
        body = {
            "SearchByPartRequest": {
                "mouserPartNumber": query,
                "partSearchOptions": "string"
            }
        }
        
        try:
            print(f"🔌 Connecting to Mouser API for: {query}...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.base_url, params=params, json=body, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_results(data, query)
                else:
                    print(f"❌ Mouser API Error: {response.status_code} - {response.text[:100]}")
                    return []
        except Exception as e:
            print(f"❌ Mouser Connector Exception: {e}")
            return []
            
    def _parse_results(self, data, query):
        parts = []
        try:
            search_results = data.get('SearchResults', {})
            items = search_results.get('Parts', [])
            
            for item in items:
                # Stock normalization
                availability = item.get('Availability', '0')
                stock_str = ''.join(filter(str.isdigit, availability.split(' ')[0]))
                stock = int(stock_str) if stock_str else 0
                
                # Price extraction
                price_breaks = item.get('PriceBreaks', [])
                price = 0.0
                currency = 'USD'
                
                if price_breaks:
                    # Prefer price for quantity 1, or the first available
                    pb = price_breaks[0]
                    price_str = pb.get('Price', '0').replace('$', '').replace(',', '')
                    currency = pb.get('Currency', 'USD')
                    try: 
                        price = float(price_str)
                    except: 
                        price = 0.0
                        
                parts.append({
                    "distributor": "Mouser Electronics (API)",
                    "mpn": item.get('ManufacturerPartNumber', query),
                    "manufacturer": item.get('Manufacturer', 'Unknown'),
                    "stock": stock,
                    "price": price,
                    "currency": currency,
                    "condition": "New",
                    "risk_level": "Low",
                    "source_type": "Official API",
                    "datasheet": item.get('DataSheetUrl', ''),
                    "description": item.get('Description', ''),
                    "date_code": "2024+", # Placeholder
                    "delivery": item.get('LeadTime', 'In Stock')
                })
        except Exception as parse_err:
            print(f"⚠️ Mouser Parse Error: {parse_err}")
            
        return parts

# --- DIGI-KEY API CONNECTOR (Real Data) ---
class DigiKeyConnector:
    """
    Connects to Digi-Key Product Information API v4.
    Requires OAuth2 Token traversal.
    """
    def __init__(self):
        self.client_id = os.getenv("DIGIKEY_CLIENT_ID")
        self.client_secret = os.getenv("DIGIKEY_CLIENT_SECRET")
        self.token_url = "https://api.digikey.com/v1/oauth2/token"
        self.base_url = "https://api.digikey.com/Search/v3/Products/Keyword" # v3 is simpler, or v4
        # Note: v4 path is often /products/v4/search/keyword or similar. Let's use v3 for simplicity if available, or check specific endpoint.
        # Actually, let's use the standard "Keyword Search" which is often mapped to /Search/v3/Products/Keyword within many SDKs, 
        # but the raw API documentation specifies: https://api.digikey.com/products/v4/search/keyword
        self.search_url = "https://api.digikey.com/products/v4/search/keyword"
        self.access_token = None
        self.token_expires_at = 0

    async def _get_token(self):
        """Fetch or refresh OAuth2 Access Token"""
        import time
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        if not self.client_id or not self.client_secret:
            return None

        # Prepare for application/x-www-form-urlencoded
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.token_url, data=data)
                if resp.status_code == 200:
                    token_data = resp.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = time.time() + expires_in - 60 # buffer
                    return self.access_token
                else:
                    print(f"❌ Digi-Key Token Error: {resp.status_code} - {resp.text}")
                    return None
        except Exception as e:
            print(f"❌ Digi-Key Token Exception: {e}")
            return None

    async def fetch_prices(self, query: str) -> List[Dict]:
        token = await self._get_token()
        if not token:
            print("⚠️ Skipping Digi-Key (No Token)")
            return []

        headers = {
            "Authorization": f"Bearer {token}",
            "X-DIGIKEY-Client-Id": self.client_id,
            "X-DIGIKEY-Locale-Site": "US",
            "X-DIGIKEY-Locale-Language": "en",
            "Content-Type": "application/json"
        }

        body = {
            "Keywords": query,
            "Limit": 10
        }

        try:
            print(f"🔌 Connecting to Digi-Key API for: {query}...")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.search_url, json=body, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_results(data, query)
                else:
                    print(f"❌ Digi-Key API Error: {response.status_code}")
                    return []
        except Exception as e:
            print(f"❌ Digi-Key Connector Exception: {e}")
            return []

    def _parse_results(self, data, query):
        parts = []
        try:
            products = data.get("Products", [])
            for item in products:
                # Price logic
                price = 0.0
                currency = "USD"
                
                # Check StandardPricing or UnitPrice
                unit_price = item.get("UnitPrice", 0)
                if unit_price > 0:
                    price = unit_price
                
                # Stock
                stock = item.get("QuantityAvailable", 0)
                
                parts.append({
                    "distributor": "Digi-Key Electronics (API)",
                    "mpn": item.get("ManufacturerPartNumber", query),
                    "manufacturer": item.get("Manufacturer", {}).get("Value", "Unknown"),
                    "stock": stock,
                    "price": price,
                    "currency": currency,
                    "condition": "New",
                    "risk_level": "Low",
                    "source_type": "Official API",
                    "datasheet": item.get("DatasheetUrl", ""),
                    "description": item.get("ProductDescription", ""),
                    "date_code": "2024+",
                    "delivery": "Immediate" if stock > 0 else "Backorder"
                })
        except Exception as e:
            print(f"⚠️ Digi-Key Parse Error: {e}")
            
        return parts

# --- EOL SPECIALIST CONNECTORS (Rochester, Flip) ---

class RochesterConnector:
    """
    Connects to Rochester Electronics (Authorized EOL Distributor).
    Uses Search URL Scraping / Deep Linking.
    """
    def __init__(self):
        self.base_url = "https://www.rocelec.com/search"
    
    async def fetch_prices(self, query: str) -> List[Dict]:
        # Note: Real scraping requires handling anti-bot protections.
        # For this version, we provide a 'Deep Link' result that acts as a connector.
        # If we had a direct API or if the site was simple HTML, we would parse it here.
        
        return [{
            "distributor": "Rochester Electronics (EOL)",
            "mpn": query.upper(),
            "manufacturer": "Various (EOL Authorized)",
            "stock": 0, # Unknown without deep scrape
            "price": 0.0,
            "currency": "USD",
            "condition": "Authorized EOL",
            "risk_level": "Low",
            "source_type": "EOL Partner",
            "description": "Click to check EOL stock directly.",
            "delivery": "Check Website",
            "datasheet": f"https://www.rocelec.com/search?q={query}" # Deep link
        }]

class FlipElectronicsConnector:
    """
    Connects to Flip Electronics (EOL Specialist).
    """
    async def fetch_prices(self, query: str) -> List[Dict]:
        return [{
            "distributor": "Flip Electronics",
            "mpn": query.upper(),
            "manufacturer": "Various",
            "stock": 0,
            "price": 0.0,
            "currency": "USD",
            "condition": "EOL / Obsolete",
            "risk_level": "Low",
            "source_type": "EOL Partner",
            "description": "Authorized EOL Reseller",
            "delivery": "Contact for Quote",
            "datasheet": f"https://www.flipelectronics.com/search?q={query}"
        }]

# --- BROADLINE DISTRIBUTOR DEEP LINKS (No API Key Required) ---

class ArrowConnector:
    """Generates direct search links for Arrow Electronics."""
    async def fetch_prices(self, query: str) -> List[Dict]:
        return [{
            "distributor": "Arrow Electronics",
            "mpn": query.upper(),
            "manufacturer": "Various",
            "stock": -1, # Check website
            "price": 0.0,
            "currency": "USD",
            "condition": "New",
            "risk_level": "Low",
            "source_type": "Deep Link",
            "description": "Global Distributor",
            "delivery": "Check Website",
            "datasheet": f"https://www.arrow.com/en/products/search?q={query}"
        }]

class FutureElectronicsConnector:
    """Generates direct search links for Future Electronics."""
    async def fetch_prices(self, query: str) -> List[Dict]:
        return [{
            "distributor": "Future Electronics",
            "mpn": query.upper(),
            "manufacturer": "Various",
            "stock": -1,
            "price": 0.0,
            "currency": "USD",
            "condition": "New",
            "risk_level": "Low",
            "source_type": "Deep Link",
            "description": "Global Distributor",
            "delivery": "Check Website",
            "datasheet": f"https://www.futureelectronics.com/search/?q={query}"
        }]

class RSComponentsConnector:
    """Generates direct search links for RS Components."""
    async def fetch_prices(self, query: str) -> List[Dict]:
        return [{
            "distributor": "RS Components",
            "mpn": query.upper(),
            "manufacturer": "Various",
            "stock": -1,
            "price": 0.0,
            "currency": "USD",
            "condition": "New",
            "risk_level": "Low",
            "source_type": "Deep Link",
            "description": "Global Distributor",
            "delivery": "Check Website",
            "datasheet": f"https://uk.rs-online.com/web/c/?searchTerm={query}"
        }]

# =============================================================================
# UNIFIED AGGREGATOR
# =============================================================================

async def aggregate_from_multiple_sources(mpn: str) -> List[Dict]:
    """
    Aggregates data from 7 Sources: Mouser, Digi-Key, Rochester, Flip, Arrow, Future, RS.
    """
    results = []
    
    # Run Connectors in Parallel
    mouser = MouserConnector()
    digikey = DigiKeyConnector()
    rochester = RochesterConnector()
    flip = FlipElectronicsConnector()
    arrow = ArrowConnector()
    future = FutureElectronicsConnector()
    rs = RSComponentsConnector()
    
    # Execute ALL API calls concurrently
    tasks = [
        mouser.fetch_prices(mpn),
        digikey.fetch_prices(mpn),
        rochester.fetch_prices(mpn),
        flip.fetch_prices(mpn),
        arrow.fetch_prices(mpn),
        future.fetch_prices(mpn),
        rs.fetch_prices(mpn)
    ]
    
    connector_results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process Results
    for res in connector_results:
        if isinstance(res, list):
            results.extend(res)
        else:
            print(f"⚠️ A connector failed: {res}")

    # Fallback only if absolutely no data found from real APIs
    if not results:
        print("⚠️ No API results found. Falling back to mock data.")
        # Minimal mock fallback
        results.append({
            "distributor": "System (No Results)",
            "mpn": mpn,
            "manufacturer": "N/A",
            "stock": 0,
            "price": 0.0,
            "currency": "USD",
            "condition": "Unknown",
            "risk_level": "High",
            "source_type": "Fallback",
            "description": "No stock found in verified distributors.",
            "delivery": "Unavailable",
            "date_code": "N/A"
        })
    
    return results

# Test logic
async def test_scrapers():
    print("🔍 Testing Real Mouser API...")
    mpn = "LM358"
    results = await aggregate_from_multiple_sources(mpn)
    for r in results:
        print(f"{r['distributor']}: {r['mpn']} - {r['price']} {r['currency']}")

if __name__ == "__main__":
    asyncio.run(test_scrapers())
