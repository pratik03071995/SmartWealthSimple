#!/usr/bin/env python3
"""
Test script for SmartWealthAI scrapers
Run this to verify that all scrapers are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.yahoo_finance import YahooFinanceScraper
from scrapers.news_scraper import NewsScraper
from scrapers.morningstar_scraper import MorningstarScraper
from scrapers.seeking_alpha_scraper import SeekingAlphaScraper
from scrapers.finviz_scraper import FinvizScraper
from scrapers.data_aggregator import DataAggregator
import json

def test_yahoo_finance_scraper():
    """Test Yahoo Finance scraper"""
    print("🧪 Testing Yahoo Finance Scraper...")
    
    scraper = YahooFinanceScraper()
    
    # Test stock info
    print("  📊 Testing stock info for AAPL...")
    try:
        stock_info = scraper.get_stock_info("AAPL")
        if 'error' not in stock_info:
            print(f"    ✅ Success! Current price: ${stock_info.get('current_price', 'N/A')}")
            print(f"    📈 Price change: {stock_info.get('price_change_pct', 'N/A')}%")
        else:
            print(f"    ❌ Error: {stock_info['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test stock news
    print("  📰 Testing stock news for AAPL...")
    try:
        news = scraper.get_stock_news("AAPL", limit=3)
        if news and 'error' not in news[0]:
            print(f"    ✅ Success! Found {len(news)} news articles")
            for i, article in enumerate(news[:2]):
                print(f"      {i+1}. {article.get('title', 'No title')[:50]}...")
        else:
            print(f"    ❌ Error: {news[0].get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_news_scraper():
    """Test News scraper"""
    print("\n🧪 Testing News Scraper...")
    
    scraper = NewsScraper()
    
    # Test Yahoo Finance news
    print("  📰 Testing Yahoo Finance news...")
    try:
        news = scraper.get_yahoo_finance_news(limit=3)
        if news and 'error' not in news[0]:
            print(f"    ✅ Success! Found {len(news)} news articles")
            for i, article in enumerate(news[:2]):
                print(f"      {i+1}. {article.get('title', 'No title')[:50]}...")
                sentiment = article.get('sentiment', {}).get('sentiment', 'unknown')
                print(f"         Sentiment: {sentiment}")
        else:
            print(f"    ❌ Error: {news[0].get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test aggregated news
    print("  🔄 Testing aggregated news...")
    try:
        aggregated = scraper.get_aggregated_news(limit_per_source=2)
        if 'error' not in aggregated:
            total_count = aggregated.get('total_count', 0)
            print(f"    ✅ Success! Total articles: {total_count}")
            print(f"    📊 Sources: {list(aggregated.get('sources', {}).keys())}")
        else:
            print(f"    ❌ Error: {aggregated['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_morningstar_scraper():
    """Test Morningstar scraper"""
    print("\n🧪 Testing Morningstar Scraper...")
    
    scraper = MorningstarScraper()
    
    # Test stock analysis
    print("  📊 Testing stock analysis for AAPL...")
    try:
        analysis = scraper.get_stock_analysis("AAPL")
        if 'error' not in analysis:
            print(f"    ✅ Success! Fair value: {analysis.get('fair_value', 'N/A')}")
            print(f"    📈 Economic moat: {analysis.get('economic_moat', 'N/A')}")
        else:
            print(f"    ❌ Error: {analysis['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test market news
    print("  📰 Testing Morningstar market news...")
    try:
        news = scraper.get_market_news(limit=3)
        if news and 'error' not in news[0]:
            print(f"    ✅ Success! Found {len(news)} news articles")
            for i, article in enumerate(news[:2]):
                print(f"      {i+1}. {article.get('title', 'No title')[:50]}...")
        else:
            print(f"    ❌ Error: {news[0].get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_seeking_alpha_scraper():
    """Test Seeking Alpha scraper"""
    print("\n🧪 Testing Seeking Alpha Scraper...")
    
    scraper = SeekingAlphaScraper()
    
    # Test stock analysis
    print("  📊 Testing stock analysis for AAPL...")
    try:
        analysis = scraper.get_stock_analysis("AAPL")
        if 'error' not in analysis:
            print(f"    ✅ Success! Quant rating: {analysis.get('quant_rating', 'N/A')}")
            print(f"    📈 Price target: {analysis.get('price_target', 'N/A')}")
        else:
            print(f"    ❌ Error: {analysis['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test earnings data
    print("  📅 Testing earnings data for AAPL...")
    try:
        earnings = scraper.get_earnings_data("AAPL")
        if 'error' not in earnings:
            print(f"    ✅ Success! Next earnings: {earnings.get('next_earnings_date', 'N/A')}")
            print(f"    📊 EPS estimate: {earnings.get('eps_estimate', 'N/A')}")
        else:
            print(f"    ❌ Error: {earnings['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_finviz_scraper():
    """Test Finviz scraper"""
    print("\n🧪 Testing Finviz Scraper...")
    
    scraper = FinvizScraper()
    
    # Test stock overview
    print("  📊 Testing stock overview for AAPL...")
    try:
        overview = scraper.get_stock_overview("AAPL")
        if 'error' not in overview:
            print(f"    ✅ Success! Price: {overview.get('price', 'N/A')}")
            print(f"    📈 Market cap: {overview.get('market_cap', 'N/A')}")
        else:
            print(f"    ❌ Error: {overview['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test technical analysis
    print("  📈 Testing technical analysis for AAPL...")
    try:
        technical = scraper.get_technical_analysis("AAPL")
        if 'error' not in technical:
            print(f"    ✅ Success! RSI: {technical.get('rsi_14', 'N/A')}")
            print(f"    📊 Beta: {technical.get('beta', 'N/A')}")
        else:
            print(f"    ❌ Error: {technical['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_data_aggregator():
    """Test Data Aggregator"""
    print("\n🧪 Testing Data Aggregator...")
    
    aggregator = DataAggregator()
    
    # Test comprehensive stock data
    print("  📊 Testing comprehensive stock data for AAPL...")
    try:
        comprehensive = aggregator.get_comprehensive_stock_data("AAPL")
        if 'error' not in comprehensive:
            sources = list(comprehensive.get('sources', {}).keys())
            print(f"    ✅ Success! Sources: {sources}")
            summary = comprehensive.get('summary', {})
            print(f"    📈 Current price: ${summary.get('current_price', 'N/A')}")
        else:
            print(f"    ❌ Error: {comprehensive['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")
    
    # Test comprehensive news
    print("  📰 Testing comprehensive news...")
    try:
        news = aggregator.get_comprehensive_news(limit=5)
        if 'error' not in news:
            total_count = news.get('total_count', 0)
            sources = news.get('sources', [])
            print(f"    ✅ Success! Total articles: {total_count}")
            print(f"    📊 Sources: {sources}")
        else:
            print(f"    ❌ Error: {news['error']}")
    except Exception as e:
        print(f"    ❌ Exception: {str(e)}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🧪 Testing API Endpoints...")
    
    import requests
    import time
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("  💚 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("    ✅ Health endpoint working")
        else:
            print(f"    ❌ Health endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Health endpoint error: {str(e)}")
    
    # Test comprehensive stock endpoint
    print("  📊 Testing comprehensive stock endpoint...")
    try:
        response = requests.get(f"{base_url}/api/stock/AAPL", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                sources = list(data.get('sources', {}).keys())
                print(f"    ✅ Comprehensive stock endpoint working - Sources: {sources}")
            else:
                print(f"    ❌ Stock endpoint error: {data['error']}")
        else:
            print(f"    ❌ Stock endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Stock endpoint error: {str(e)}")
    
    # Test news endpoint
    print("  📰 Testing news endpoint...")
    try:
        response = requests.get(f"{base_url}/api/news?limit=3", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                print(f"    ✅ News endpoint working")
            else:
                print(f"    ❌ News endpoint error: {data['error']}")
        else:
            print(f"    ❌ News endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ News endpoint error: {str(e)}")
    
    # Test market overview endpoint
    print("  📈 Testing market overview endpoint...")
    try:
        response = requests.get(f"{base_url}/api/market-overview", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                print(f"    ✅ Market overview endpoint working")
            else:
                print(f"    ❌ Market overview error: {data['error']}")
        else:
            print(f"    ❌ Market overview failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Market overview error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 SmartWealthAI Comprehensive Scraper Tests")
    print("=" * 60)
    
    # Test individual scrapers
    test_yahoo_finance_scraper()
    test_news_scraper()
    test_morningstar_scraper()
    test_seeking_alpha_scraper()
    test_finviz_scraper()
    test_data_aggregator()
    
    # Test API endpoints (only if server is running)
    print("\n" + "=" * 60)
    print("🌐 API Endpoint Tests (requires server to be running)")
    print("Start the server with: python app.py")
    
    try:
        test_api_endpoints()
    except Exception as e:
        print(f"❌ API tests failed: {str(e)}")
        print("💡 Make sure the Flask server is running on http://localhost:5000")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📝 Next steps:")
    print("1. Start the server: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Test the web interface")
    print("\n🔗 Available API endpoints:")
    print("- GET /api/stock/<ticker> - Comprehensive stock data")
    print("- GET /api/news - Aggregated financial news")
    print("- GET /api/market-overview - Market overview")
    print("- GET /api/portfolio/analyze - Portfolio analysis")
    print("- GET /api/stock-screener - Stock screening")
    print("- GET /api/earnings-calendar - Earnings calendar")

if __name__ == "__main__":
    main()
