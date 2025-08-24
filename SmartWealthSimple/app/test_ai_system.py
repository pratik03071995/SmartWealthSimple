#!/usr/bin/env python3
"""
Test script for SmartWealthAI AI-powered stock recommendation system
Run this to verify that the AI components are working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.sector_analyzer import SectorAnalyzer
from ai.stock_recommender import AIStockRecommender
import json
import requests

def test_sector_analyzer():
    """Test the sector analyzer functionality"""
    print("🧠 Testing Sector Analyzer...")
    
    analyzer = SectorAnalyzer()
    
    # Test sector hierarchy
    print("  📊 Testing sector hierarchy...")
    try:
        hierarchy = analyzer.get_sector_hierarchy()
        sectors = list(hierarchy.keys())
        print(f"    ✅ Success! Found {len(sectors)} sectors")
        print(f"    📋 Sectors: {', '.join(sectors[:5])}...")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test sector analysis
    print("  🔍 Testing sector analysis...")
    try:
        sector = analyzer.analyze_sector("Technology")
        print(f"    ✅ Success! Analyzed {sector.name}")
        print(f"    📈 Growth potential: {sector.growth_potential}")
        print(f"    ⚠️ Risk level: {sector.risk_level}")
        print(f"    🏢 Subsectors: {len(sector.subsectors)}")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test subsector retrieval
    print("  🏭 Testing subsector retrieval...")
    try:
        subsectors = analyzer.get_subsectors("Technology")
        print(f"    ✅ Success! Found {len(subsectors)} subsectors")
        print(f"    📋 Subsectors: {', '.join(subsectors[:3])}...")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test stock recommendations
    print("  💼 Testing stock recommendations...")
    try:
        recommendations = analyzer.get_stock_recommendations(
            "Technology", 
            ["Software & Services", "Semiconductors"], 
            "all", 
            "medium"
        )
        print(f"    ✅ Success! Generated {len(recommendations)} recommendations")
        if recommendations:
            top_rec = recommendations[0]
            print(f"    🏆 Top pick: {top_rec.ticker} - {top_rec.company_name}")
            print(f"    📊 Confidence: {top_rec.confidence_score:.2f}")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test LLM analysis
    print("  🤖 Testing LLM analysis...")
    try:
        analysis = analyzer.generate_llm_analysis(
            "Technology", 
            ["Software & Services"], 
            "all"
        )
        print(f"    ✅ Success! Generated LLM analysis")
        print(f"    📝 Analysis length: {len(analysis)} characters")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")

def test_ai_stock_recommender():
    """Test the AI stock recommender functionality"""
    print("\n🧠 Testing AI Stock Recommender...")
    
    recommender = AIStockRecommender()
    
    # Test intelligent recommendations
    print("  🎯 Testing intelligent recommendations...")
    try:
        recommendations = recommender.get_intelligent_recommendations(
            sector="Technology",
            subsectors=["Software & Services", "Semiconductors"],
            market_cap_preference="all",
            risk_tolerance="medium",
            investment_horizon="long_term",
            max_recommendations=5
        )
        
        if 'error' not in recommendations:
            print(f"    ✅ Success! Generated {recommendations.get('total_recommendations', 0)} recommendations")
            
            # Check summary
            summary = recommendations.get('summary', {})
            if summary:
                print(f"    📊 Average confidence: {summary.get('average_confidence_score', 0):.2f}")
                print(f"    🎯 Top picks: {', '.join(summary.get('top_picks', [])[:3])}")
            
            # Check risk analysis
            risk_analysis = recommendations.get('risk_analysis', {})
            if risk_analysis:
                print(f"    ⚠️ Portfolio risk score: {risk_analysis.get('risk_score', 0):.2f}")
            
            # Check diversification
            diversification = recommendations.get('diversification_analysis', {})
            if diversification:
                print(f"    🌐 Sector diversification: {diversification.get('sector_diversification', 0):.2f}")
        else:
            print(f"    ❌ Error: {recommendations['error']}")
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")

def test_api_endpoints():
    """Test the AI-powered API endpoints"""
    print("\n🌐 Testing AI API Endpoints...")
    
    base_url = "http://localhost:5000"
    
    # Test sectors endpoint
    print("  📊 Testing sectors endpoint...")
    try:
        response = requests.get(f"{base_url}/api/ai/sectors", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sectors = data.get('sectors', [])
            print(f"    ✅ Success! Found {len(sectors)} sectors")
            if sectors:
                print(f"    📋 First sector: {sectors[0].get('name', 'Unknown')}")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test sector details endpoint
    print("  🔍 Testing sector details endpoint...")
    try:
        response = requests.get(f"{base_url}/api/ai/sectors/Technology", timeout=10)
        if response.status_code == 200:
            data = response.json()
            sector = data.get('sector', {})
            print(f"    ✅ Success! Retrieved {sector.get('name', 'Unknown')} details")
            print(f"    📈 Growth potential: {sector.get('growth_potential', 'Unknown')}")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test subsectors endpoint
    print("  🏭 Testing subsectors endpoint...")
    try:
        response = requests.get(f"{base_url}/api/ai/sectors/Technology/subsectors", timeout=10)
        if response.status_code == 200:
            data = response.json()
            subsectors = data.get('subsectors', [])
            print(f"    ✅ Success! Found {len(subsectors)} subsectors")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test AI recommendations endpoint
    print("  🎯 Testing AI recommendations endpoint...")
    try:
        payload = {
            "sector": "Technology",
            "subsectors": ["Software & Services", "Semiconductors"],
            "market_cap_preference": "all",
            "risk_tolerance": "medium",
            "investment_horizon": "long_term",
            "max_recommendations": 5
        }
        
        response = requests.post(
            f"{base_url}/api/ai/recommendations", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print(f"    ✅ Success! Generated {len(recommendations)} recommendations")
            
            if recommendations:
                top_rec = recommendations[0]
                print(f"    🏆 Top pick: {top_rec.get('ticker', 'Unknown')}")
                print(f"    📊 Confidence: {top_rec.get('confidence_score', 0):.2f}")
        else:
            print(f"    ❌ Failed: {response.status_code}")
            print(f"    📝 Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")
    
    # Test sector analysis endpoint
    print("  🤖 Testing sector analysis endpoint...")
    try:
        payload = {
            "sector": "Technology",
            "subsectors": ["Software & Services"],
            "market_cap_preference": "all"
        }
        
        response = requests.post(
            f"{base_url}/api/ai/analysis", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', '')
            print(f"    ✅ Success! Generated analysis")
            print(f"    📝 Analysis length: {len(analysis)} characters")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")

def test_portfolio_analysis():
    """Test portfolio analysis with AI insights"""
    print("\n💼 Testing Portfolio Analysis with AI...")
    
    base_url = "http://localhost:5000"
    
    try:
        payload = {
            "tickers": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"],
            "risk_tolerance": "medium",
            "investment_horizon": "long_term"
        }
        
        response = requests.post(
            f"{base_url}/api/ai/portfolio-analysis", 
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            portfolio_data = data.get('portfolio_data', {})
            ai_insights = data.get('ai_insights', {})
            
            print(f"    ✅ Success! Analyzed portfolio")
            print(f"    📊 Portfolio stocks: {len(portfolio_data.get('stocks', []))}")
            print(f"    🌐 Sector diversification: {ai_insights.get('sector_diversification', 0):.2f}")
            
            risk_assessment = ai_insights.get('risk_assessment', {})
            recommendations = risk_assessment.get('recommendations', [])
            if recommendations:
                print(f"    💡 AI recommendations: {len(recommendations)}")
                for rec in recommendations[:2]:
                    print(f"       - {rec}")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 SmartWealthAI AI-Powered Stock Recommendation System Tests")
    print("=" * 70)
    
    # Test AI components
    test_sector_analyzer()
    test_ai_stock_recommender()
    
    # Test API endpoints (only if server is running)
    print("\n" + "=" * 70)
    print("🌐 AI API Endpoint Tests (requires server to be running)")
    print("Start the server with: python app.py")
    
    try:
        test_api_endpoints()
        test_portfolio_analysis()
    except Exception as e:
        print(f"❌ API tests failed: {str(e)}")
        print("💡 Make sure the Flask server is running on http://localhost:5000")
    
    print("\n" + "=" * 70)
    print("✅ All AI tests completed!")
    print("\n📝 Next steps:")
    print("1. Start the server: python app.py")
    print("2. Open http://localhost:5000 in your browser")
    print("3. Test the AI-powered recommendation system")
    print("\n🔗 Available AI endpoints:")
    print("- GET /api/ai/sectors - Get all available sectors")
    print("- GET /api/ai/sectors/<sector> - Get sector details")
    print("- GET /api/ai/sectors/<sector>/subsectors - Get subsectors")
    print("- POST /api/ai/recommendations - Get AI stock recommendations")
    print("- POST /api/ai/analysis - Get LLM sector analysis")
    print("- POST /api/ai/portfolio-analysis - Analyze portfolio with AI")
    print("\n💡 Usage Examples:")
    print("1. Browse sectors: GET /api/ai/sectors")
    print("2. Get Technology subsectors: GET /api/ai/sectors/Technology/subsectors")
    print("3. Get AI recommendations:")
    print("   POST /api/ai/recommendations")
    print("   {")
    print('     "sector": "Technology",')
    print('     "subsectors": ["Software & Services", "Semiconductors"],')
    print('     "risk_tolerance": "medium"')
    print("   }")

if __name__ == "__main__":
    main()
