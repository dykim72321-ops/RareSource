from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import cache manager
from cache_manager import get_cache_manager

app = FastAPI(title="Rare Source - Intelligence Command API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- [1. 데이터 스키마 정의] ---

class StandardPart(BaseModel):
    id: str                 
    mpn: str                
    manufacturer: str       
    distributor: str        
    source_type: str        # API / Direct Scraper / Meta Scraper
    stock: int              
    price: float            
    price_history: List[float] # For sparklines
    currency: str           
    delivery: str           
    condition: str          
    date_code: str          
    is_eol: bool            
    risk_level: str         
    updated_at: datetime
    datasheet: Optional[str] = ""
    description: Optional[str] = ""
    product_url: Optional[str] = ""

class MarketStatus(BaseModel):
    market_temperature: str  # STABLE / VOLATILE / CRITICAL
    global_stock_index: int
    active_brokers: int
    price_drift: float
    last_sync: datetime
    recent_logs: List[str]

class ProcurementLock(BaseModel):
    part_id: str
    quantity: int = 1

class LockConfirmation(BaseModel):
    tracking_id: str
    status: str
    expires_at: datetime

# --- [2. 인텔리전스 소싱 커넥터] ---

from scraper_examples import aggregate_from_multiple_sources
from win_source_connector import WinSourceConnector

# --- [2. 인텔리전스 소싱 커넥터] ---

def generate_mock_logs(query: str):
    sources = ["Digi-Key Global API", "Mouser Electronics", "Win Source Scraper", "Verical Deep-Link", "Global Broker Index #12", "Asian Secondary Market Scan"]
    status = ["[CONNECTING]", "[AUTH_SUCCESS]", "[SCRAPING_DOM]", "[PARSING_JSON]", "[EXTRACTING_STOCK]", "[CALCULATING_MARGIN]"]
    return [f"{random.choice(status)} {random.choice(sources)} for {query.upper()}" for _ in range(5)]

# [UPDATED] Using Real Scraper Module
async def fetch_tier1_api(query: str):
    """[Tier 1] Authorized Distributors (via Scraper Module)"""
    try:
        # Call the scraper module we built
        results = await aggregate_from_multiple_sources(query)
        if results:
            return results
    except Exception as e:
        print(f"[Scraper Error] {e}")
    
    # Fallback if scraper returns nothing
    return [
        {
            "distributor": "Digi-Key Global (Fallback)",
            "mpn": query.upper(),
            "mfr": "Analog Devices",
            "stock": 450, 
            "price_usd": 12.45, 
            "delivery": "3-5 Days",
            "type": "API",
            "condition": "New Factory", 
            "date_code": "2023+" 
        }
    ]

# [RETAINED] Tier 2/3 for variety (can also be replaced with scrapers later)
async def fetch_broker_network(query: str):
    """[Tier 2] Verified Broker Network (Rare/EOL Focus)"""
    await asyncio.sleep(random.uniform(0.8, 1.5))
    return [
        {
            "distributor": "Win Source Asia",
            "mpn": query.upper(),
            "mfr": "Texas Instruments",
            "stock": 12, 
            "price_usd": 85.00, 
            "delivery": "2-4 Days (Air)",
            "type": "Direct Scraper",
            "condition": "New Old Stock",
            "date_code": "2018"
        }
    ]

async def fetch_meta_intel(query: str):
    """[Tier 3] Meta-Aggregator Intel (Deep Secondary Market)"""
    await asyncio.sleep(random.uniform(1.5, 2.5))
    return [
        {
            "distributor": "Flip Electronics (via Intel)",
            "mpn": query.upper(),
            "mfr": "Intel/Altera",
            "stock": 4200,
            "price_usd": 64.20,
            "delivery": "7-12 Days",
            "type": "Meta Scraper",
            "condition": "Refurbished (Certified)",
            "date_code": "Mixed"
        }

    ]

async def fetch_win_source(query: str):
    """[Tier 1.5] Win Source (Direct)"""
    ws = WinSourceConnector()
    results = await ws.fetch_prices(query)
    if results:
        return results
    return []

# --- [3. 핵심 어그리게이터 엔진] ---

class SourcingEngine:
    def __init__(self):
        self.exchange_rate = 1450.0 
        self.active_locks = {}
        
    def _normalize_price(self, price: float, currency: str) -> float:
        if currency == "USD":
            return round(price * self.exchange_rate)
        return price

    def _calculate_margin(self, price_krw: float, source_type: str) -> float:
        # Added new source types from scraper_examples.py
        margins = {
            "Meta Scraper": 1.25, 
            "Direct Scraper": 1.18, 
            "API": 1.12,
            "Official API": 1.10,
            "Deep Link": 1.05,
            "EOL Partner": 1.20,
            "Fallback": 1.0
        }
        return round(price_krw * margins.get(source_type, 1.15))

    def _determine_risk(self, item: dict) -> str:
        condition = item.get('condition', '')
        if "Refurbished" in condition: return "High" 
        if "Old Stock" in condition: return "Medium" 
        return "Low"

    def _generate_price_history(self, current_price: float):
        # Generate 7 simulated historical prices
        return [round(current_price * random.uniform(0.85, 1.15)) for _ in range(7)]

    async def aggregate_intel(self, query: str) -> List[StandardPart]:
        # Use the comprehensive scraper module which includes all sources
        tasks = [
            fetch_tier1_api(query),
            fetch_win_source(query)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        flat_list = []
        for source in results:
            if isinstance(source, list):
                for item in source:
                    # [FIX] Handle field mismatches between Scraper Module and Main logic
                    
                    # 1. Price & Currency
                    raw_price = item.get("price", item.get("price_usd", 0))
                    raw_currency = item.get("currency", "USD")
                    krw_price = self._normalize_price(float(raw_price), raw_currency)
                    
                    # 2. Source Type
                    s_type = item.get("source_type") or item.get("type") or "API"
                    
                    final_price = self._calculate_margin(krw_price, s_type)
                    
                    # 3. Manufacturer
                    mfr = item.get("manufacturer", item.get("mfr", "Unknown"))

                    standard_item = StandardPart(
                        id=str(uuid.uuid4())[:12],
                        mpn=item.get('mpn', 'N/A'),
                        manufacturer=mfr,
                        distributor=item.get('distributor', 'Unknown'),
                        source_type=s_type,
                        stock=item.get('stock', 0),
                        price=final_price,
                        price_history=self._generate_price_history(final_price),
                        currency="KRW",
                        delivery=item.get('delivery', 'Unknown'),
                        condition=item.get('condition', 'New'),
                        date_code=item.get('date_code', 'N/A'),
                        is_eol="Old Stock" in item.get('condition', '') or "Refurbished" in item.get('condition', ''),
                        risk_level=item.get('risk_level', self._determine_risk(item)),
                        updated_at=datetime.now(),
                        datasheet=item.get('datasheet', ''),
                        description=item.get('description', '')
                    )
                    # Pass through extra fields if needed (like datasheet) via extra attributes or dict update if model allows
                    # StandardPart definition in main.py is strict, so we only pass what fits.
                    
                    flat_list.append(standard_item)

        return sorted(flat_list, key=lambda x: x.price)

engine = SourcingEngine()

# --- [4. API Endpoints] ---

@app.get("/market/stats", response_model=MarketStatus)
async def get_market_stats():
    """글로벌 시장 상황 지수 반환"""
    return MarketStatus(
        market_temperature=random.choice(["STABLE", "VOLATILE", "CRITICAL"]),
        global_stock_index=random.randint(120000, 500000),
        active_brokers=random.randint(45, 82),
        price_drift=round(random.uniform(-5.5, 12.4), 2),
        last_sync=datetime.now(),
        recent_logs=generate_mock_logs("MARKET_SCAN")
    )

@app.get("/search", response_model=List[StandardPart])
async def search(q: str = Query(..., min_length=1)):
    """부품 통합 검색 및 지능형 필터링 (캐싱 적용)"""
    
    # Initialize cache manager
    cache_manager = get_cache_manager()
    
    # Check cache first
    cached_results = await cache_manager.get_cached_results(q)
    if cached_results:
        # Convert cached dict results back to StandardPart models
        return [StandardPart(**item) for item in cached_results]
    
    # Cache miss - perform actual search
    results = await engine.aggregate_intel(q)
    
    # Store in cache for future requests
    # Convert Pydantic models to dicts for JSON storage
    results_dict = [item.model_dump(mode='json') for item in results]
    await cache_manager.set_cache(q, results_dict)
    
    return results

@app.post("/procurement/lock", response_model=LockConfirmation)
async def lock_stock(req: ProcurementLock):
    """보안 구매 잠금 시뮬레이션"""
    tracking_id = f"RARE-{uuid.uuid4().hex[:12].upper()}"
    return LockConfirmation(
        tracking_id=tracking_id,
        status="LOCKED_PENDING_PO",
        expires_at=datetime.now() + timedelta(hours=24)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
