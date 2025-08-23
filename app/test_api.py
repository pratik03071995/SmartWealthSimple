#!/usr/bin/env python3
"""
API Testing Script for SmartWealthAI
Tests all Yahoo Finance and news-related endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

def test_endpoint(endpoint, description, params=None):
    """Test a single API endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"   URL: {BASE_URL}{endpoint}")
    
    try:
        if params:
            response = requests.get(f"{BASE_URL}{endpoint}", params=params, timeout=10)
        else:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success!")
            
            # Show sample data
            if isinstance(data, list):
                print(f"   📊 Items returned: {len(data)}")
                if data:
                    print(f"   📝 Sample: {json.dumps(data[0], indent=2)[:200]}...")
            elif isinstance(data, dict):
                print(f"   📊 Keys: {list(data.keys())}")
                if 'news' in data:
                    print(f"   📰 News count: {len(data.get('news', []))}")
                if 'stock' in data:
                    print(f"   📈 Stock data available: {bool(data.get('stock'))}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")

def main():
    """Run all API tests"""
    print("🚀 SmartWealthAI API Testing")
    print("=" * 50)
    
    # Test health endpoint
    test_endpoint("/health", "Health Check")
    
    # Test stock data endpoints
    test_endpoint("/api/stock/AAPL/simple", "Basic Stock Info (AAPL)")
    test_endpoint("/api/stock/TSLA/simple", "Basic Stock Info (TSLA)")
    
    # Test news endpoints
    test_endpoint("/api/news", "General News (All Sources)")
    test_endpoint("/api/news", "Yahoo Finance News", {"source": "yahoo", "limit": 5})
    test_endpoint("/api/news", "MarketWatch News", {"source": "marketwatch", "limit": 5})
    test_endpoint("/api/news", "CNBC News", {"source": "cnbc", "limit": 5})
    
    # Test stock-specific news
    test_endpoint("/api/stock/AAPL/news", "AAPL Stock News", {"limit": 5})
    test_endpoint("/api/stock/TSLA/news", "TSLA Stock News", {"limit": 5})
    
    # Test Yahoo-specific endpoints
    test_endpoint("/api/sources/yahoo/AAPL", "Yahoo Data for AAPL")
    test_endpoint("/api/sources/yahoo/TSLA", "Yahoo Data for TSLA")
    
    # Test market data
    test_endpoint("/api/market-movers", "Market Movers")
    test_endpoint("/api/market-overview", "Market Overview")
    
    # Test AI endpoints
    test_endpoint("/api/ai/sectors", "Available Sectors")
    test_endpoint("/api/ai/sectors/Technology", "Technology Sector Details")
    
    # Test search functionality
    test_endpoint("/api/news/search", "News Search", {"q": "Apple", "limit": 5})
    
    print("\n" + "=" * 50)
    print("✅ API Testing Complete!")
    print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
