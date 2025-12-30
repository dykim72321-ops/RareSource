"""
Quick test script for FindChips + OpenAI integration
"""
import asyncio
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from scraper_examples import FindChipsConnector, OpenAIParserConnector

async def test_findchips():
    print("=" * 60)
    print("Testing FindChips + OpenAI Connector")
    print("=" * 60)
    
    # Test part numbers
    test_parts = ["LM358", "TMS320F28335"]
    
    connector = FindChipsConnector()
    
    for part in test_parts:
        print(f"\n{'='*60}")
        print(f"Searching for: {part}")
        print(f"{'='*60}\n")
        
        results = await connector.fetch_prices(part)
        
        if results:
            print(f"\n✓ Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['distributor']}")
                print(f"   MPN: {result['mpn']}")
                print(f"   Manufacturer: {result['manufacturer']}")
                print(f"   Stock: {result['stock']}")
                print(f"   Price: ${result['price']} {result['currency']}")
                print(f"   Description: {result['description'][:80]}...")
                print()
        else:
            print("✗ No results found\n")
    
    print("="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_findchips())
