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
    from openai import AsyncOpenAI
except ImportError:
    print("⚠️  httpx, beautifulsoup4, and openai are required. Please pip install them.")

# =============================================================================
# FINDCHIPS + OPENAI CONNECTORS (Intelligent Scraping)
# =============================================================================

class OpenAIParserConnector:
    """
    Uses OpenAI API to intelligently parse HTML and extract structured data.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = AsyncOpenAI(api_key=self.api_key) if self.api_key else None
        
    async def parse_html_to_json(self, html_content: str, part_number: str) -> List[Dict]:
        """Parse HTML content using GPT-4o-mini to extract component data"""
        if not self.client:
            print("⚠️  OpenAI API Key missing. Skipping AI parsing.")
            return []
            
        # Truncate HTML to reduce token usage
        max_html_length = 8000
        if len(html_content) > max_html_length:
            html_content = html_content[:max_html_length] + "..."
            
        prompt = f"""Extract electronic component data from the following HTML and return ONLY a JSON array.
Each item should have these fields:
- distributor (string)
- mpn (string, the manufacturer part number)
- manufacturer (string)
- stock (integer, 0 if unknown)
- price (float, 0 if unknown)
- currency (string, default "USD")
- delivery (string)
- description (string, brief)

Part Number: {part_number}

HTML:
{html_content}

Return ONLY the JSON array, no markdown formatting or explanations."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Return only valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = re.sub(r'^```(?:json)?\n?', '', content)
                content = re.sub(r'\n?```$', '', content)
            
            # Parse JSON
            import json
            data = json.loads(content)
            
            print(f"✓ OpenAI parsed {len(data)} items from HTML")
            return data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  OpenAI returned invalid JSON: {e}")
            print(f"Response: {content[:200]}...")
            return []
        except Exception as e:
            print(f"❌ OpenAI Parser Exception: {e}")
            return []

class FindChipsConnector:
    """
    Scrapes FindChips.com and uses OpenAI to parse results intelligently.
    """
    def __init__(self):
        self.base_url = "https://www.findchips.com/search"
        self.openai_parser = OpenAIParserConnector()
        
    async def fetch_prices(self, query: str) -> List[Dict]:
        """Fetch component data from FindChips using AI-powered parsing"""
        url = f"{self.base_url}/{query}"
        
        try:
            print(f"🔍 Scraping FindChips for: {query}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code != 200:
                    print(f"⚠️  FindChips returned status {response.status_code}")
                    return []
                
                html_content = response.text
                
                # Use OpenAI to parse the HTML
                parsed_data = await self.openai_parser.parse_html_to_json(html_content, query)
                
                # Normalize to our format
                results = []
                for item in parsed_data:
                    results.append({
                        "distributor": item.get("distributor", "FindChips Source"),
                        "mpn": item.get("mpn", query.upper()),
                        "manufacturer": item.get("manufacturer", "Unknown"),
                        "stock": item.get("stock", 0),
                        "price": item.get("price", 0.0),
                        "currency": item.get("currency", "USD"),
                        "condition": "New",
                        "risk_level": "Low",
                        "source_type": "FindChips (AI Parsed)",
                        "description": item.get("description", "Multi-source aggregated data"),
                        "delivery": item.get("delivery", "Check Distributor"),
                        "date_code": "2024+",
                        "datasheet": f"https://www.findchips.com/search/{query}"
                    })
                
                if results:
                    print(f"✓ FindChips found {len(results)} results via AI parsing")
                else:
                    print("⚠️  No results extracted from FindChips")
                    
                return results
                
        except Exception as e:
            print(f"❌ FindChips Connector Exception: {e}")
            import traceback
            traceback.print_exc()
            return []

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
            # DEBUG: Log response structure
            print(f"📊 Mouser Response Keys: {list(data.keys()) if data else 'None'}")
            
            search_results = data.get('SearchResults', {})
            if not search_results:
                print(f"⚠️  No 'SearchResults' in response. Available keys: {list(data.keys())}")
                return []
            
            items = search_results.get('Parts', [])
            if not items:
                print(f"⚠️  No 'Parts' found. SearchResults keys: {list(search_results.keys())}")
                return []
            
            print(f"✓ Found {len(items)} parts from Mouser")
            
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
            import traceback
            traceback.print_exc()
            
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
            # DEBUG: Log response structure
            print(f"📊 Digi-Key Response Keys: {list(data.keys()) if data else 'None'}")
            
            products = data.get("Products", [])
            if not products:
                print(f"⚠️  No 'Products' in response. Available keys: {list(data.keys())}")
                return []
            
            print(f"✓ Found {len(products)} products from Digi-Key")
            
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
            import traceback
            traceback.print_exc()
            
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
            "datasheet": f"https://www.rocelec.com/search?q={query}"
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
            "datasheet": f"https://www.flipelectronics.com/?s={query}"
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
            "datasheet": "https://www.arrow.com" # Bot protection blocks direct search
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
            "datasheet": f"https://www.futureelectronics.com/c/semiconductors/{query}"
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
            "datasheet": f"https://uk.rs-online.com/web/c/?searchTerm={query}" # This format works
        }]

# =============================================================================
# UNIFIED AGGREGATOR
# =============================================================================

async def aggregate_from_multiple_sources(mpn: str) -> List[Dict]:
    """
    Aggregates data from 8 Sources: FindChips+AI, Mouser, Digi-Key, Rochester, Flip, Arrow, Future, RS.
    """
    results = []
    
    # Run Connectors in Parallel
    findchips = FindChipsConnector()
    mouser = MouserConnector()
    digikey = DigiKeyConnector()
    rochester = RochesterConnector()
    flip = FlipElectronicsConnector()
    arrow = ArrowConnector()
    future = FutureElectronicsConnector()
    rs = RSComponentsConnector()
    
    # Execute ALL API calls concurrently
    tasks = [
        findchips.fetch_prices(mpn),  # NEW: FindChips with AI parsing
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
