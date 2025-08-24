#!/usr/bin/env python3
"""
Comprehensive test script for all sector and subsector combinations
Tests the dynamic scraping functionality with various combinations
"""

import asyncio
import time
from datetime import datetime
from scrapers.yahoo_finance_scraper import YahooFinanceScraper

def test_sector_combinations():
    """Test all individual sectors"""
    print("=" * 60)
    print("TESTING INDIVIDUAL SECTORS")
    print("=" * 60)
    
    sectors = [
        'Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical',
        'Communication Services', 'Industrials', 'Energy', 'Consumer Defensive',
        'Real Estate', 'Utilities', 'Basic Materials'
    ]
    
    scraper = YahooFinanceScraper()
    results = {}
    
    for sector in sectors:
        print(f"\n🔍 Testing sector: {sector}")
        start_time = time.time()
        
        try:
            companies = scraper.get_companies_dynamic(sectors=[sector], limit=10)
            end_time = time.time()
            
            if companies and len(companies) > 0 and 'error' not in companies[0]:
                print(f"✅ Success: Found {len(companies)} companies in {end_time - start_time:.2f}s")
                print(f"   Top 3: {[c['ticker'] for c in companies[:3]]}")
                results[sector] = {
                    'count': len(companies),
                    'time': end_time - start_time,
                    'top_tickers': [c['ticker'] for c in companies[:3]]
                }
            else:
                print(f"❌ No companies found or error occurred")
                results[sector] = {'error': 'No companies found'}
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[sector] = {'error': str(e)}
    
    return results

def test_subsector_combinations():
    """Test all individual subsectors"""
    print("\n" + "=" * 60)
    print("TESTING INDIVIDUAL SUBSECTORS")
    print("=" * 60)
    
    subsectors = [
        'Software & Services', 'Hardware & Equipment', 'Semiconductors',
        'Internet Services', 'Cloud Computing', 'Artificial Intelligence',
        'Pharmaceuticals', 'Biotechnology', 'Medical Devices', 'Healthcare Services',
        'Banks', 'Insurance', 'Investment Services', 'Retail', 'Automotive',
        'Travel & Leisure', 'Media', 'Telecommunications', 'Aerospace & Defense',
        'Transportation', 'Manufacturing', 'Oil & Gas', 'Renewable Energy',
        'Food & Beverages', 'Consumer Goods', 'Real Estate Investment Trusts',
        'Electric Utilities', 'Gas Utilities', 'Chemicals', 'Metals & Mining'
    ]
    
    scraper = YahooFinanceScraper()
    results = {}
    
    for subsector in subsectors:
        print(f"\n🔍 Testing subsector: {subsector}")
        start_time = time.time()
        
        try:
            companies = scraper.get_companies_dynamic(subsectors=[subsector], limit=10)
            end_time = time.time()
            
            if companies and len(companies) > 0 and 'error' not in companies[0]:
                print(f"✅ Success: Found {len(companies)} companies in {end_time - start_time:.2f}s")
                print(f"   Top 3: {[c['ticker'] for c in companies[:3]]}")
                results[subsector] = {
                    'count': len(companies),
                    'time': end_time - start_time,
                    'top_tickers': [c['ticker'] for c in companies[:3]]
                }
            else:
                print(f"❌ No companies found or error occurred")
                results[subsector] = {'error': 'No companies found'}
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[subsector] = {'error': str(e)}
    
    return results

def test_mixed_combinations():
    """Test mixed sector and subsector combinations"""
    print("\n" + "=" * 60)
    print("TESTING MIXED SECTOR + SUBSECTOR COMBINATIONS")
    print("=" * 60)
    
    combinations = [
        # Technology sector + tech subsectors
        {'sectors': ['Technology'], 'subsectors': ['Software & Services']},
        {'sectors': ['Technology'], 'subsectors': ['Semiconductors']},
        {'sectors': ['Technology'], 'subsectors': ['Artificial Intelligence']},
        
        # Healthcare sector + healthcare subsectors
        {'sectors': ['Healthcare'], 'subsectors': ['Pharmaceuticals']},
        {'sectors': ['Healthcare'], 'subsectors': ['Biotechnology']},
        {'sectors': ['Healthcare'], 'subsectors': ['Medical Devices']},
        
        # Financial sector + financial subsectors
        {'sectors': ['Financial Services'], 'subsectors': ['Banks']},
        {'sectors': ['Financial Services'], 'subsectors': ['Insurance']},
        
        # Consumer sector + consumer subsectors
        {'sectors': ['Consumer Cyclical'], 'subsectors': ['Retail']},
        {'sectors': ['Consumer Cyclical'], 'subsectors': ['Automotive']},
        
        # Multiple sectors
        {'sectors': ['Technology', 'Healthcare'], 'subsectors': []},
        {'sectors': ['Financial Services', 'Consumer Cyclical'], 'subsectors': []},
        
        # Multiple subsectors
        {'sectors': [], 'subsectors': ['Software & Services', 'Semiconductors']},
        {'sectors': [], 'subsectors': ['Pharmaceuticals', 'Biotechnology']},
        
        # Complex combinations
        {'sectors': ['Technology', 'Healthcare'], 'subsectors': ['Software & Services', 'Pharmaceuticals']},
    ]
    
    scraper = YahooFinanceScraper()
    results = {}
    
    for i, combo in enumerate(combinations, 1):
        sectors_str = ', '.join(combo['sectors']) if combo['sectors'] else 'None'
        subsectors_str = ', '.join(combo['subsectors']) if combo['subsectors'] else 'None'
        
        print(f"\n🔍 Test {i}: Sectors=[{sectors_str}], Subsectors=[{subsectors_str}]")
        start_time = time.time()
        
        try:
            companies = scraper.get_companies_dynamic(
                sectors=combo['sectors'], 
                subsectors=combo['subsectors'], 
                limit=15
            )
            end_time = time.time()
            
            if companies and len(companies) > 0 and 'error' not in companies[0]:
                print(f"✅ Success: Found {len(companies)} companies in {end_time - start_time:.2f}s")
                print(f"   Top 5: {[c['ticker'] for c in companies[:5]]}")
                results[f"Test_{i}"] = {
                    'sectors': combo['sectors'],
                    'subsectors': combo['subsectors'],
                    'count': len(companies),
                    'time': end_time - start_time,
                    'top_tickers': [c['ticker'] for c in companies[:5]]
                }
            else:
                print(f"❌ No companies found or error occurred")
                results[f"Test_{i}"] = {'error': 'No companies found'}
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results[f"Test_{i}"] = {'error': str(e)}
    
    return results

def test_streaming_functionality():
    """Test the streaming functionality"""
    print("\n" + "=" * 60)
    print("TESTING STREAMING FUNCTIONALITY")
    print("=" * 60)
    
    scraper = YahooFinanceScraper()
    
    def progress_callback(company, index, total):
        print(f"   📈 Company {index}: {company['ticker']} - ${company['current_price']:.2f}")
    
    print("🔍 Testing streaming with Technology sector...")
    start_time = time.time()
    
    try:
        companies = scraper.get_companies_dynamic_streaming(
            sectors=['Technology'], 
            limit=10,
            callback=progress_callback
        )
        end_time = time.time()
        
        print(f"✅ Streaming completed: {len(companies)} companies in {end_time - start_time:.2f}s")
        return {'success': True, 'count': len(companies), 'time': end_time - start_time}
        
    except Exception as e:
        print(f"❌ Streaming error: {str(e)}")
        return {'error': str(e)}

def generate_summary_report(sector_results, subsector_results, mixed_results, streaming_results):
    """Generate a comprehensive summary report"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sector summary
    print(f"\n📊 SECTOR TESTS:")
    successful_sectors = sum(1 for r in sector_results.values() if 'error' not in r)
    total_sectors = len(sector_results)
    print(f"   Success Rate: {successful_sectors}/{total_sectors} ({successful_sectors/total_sectors*100:.1f}%)")
    
    # Subsector summary
    print(f"\n📊 SUBSECTOR TESTS:")
    successful_subsectors = sum(1 for r in subsector_results.values() if 'error' not in r)
    total_subsectors = len(subsector_results)
    print(f"   Success Rate: {successful_subsectors}/{total_subsectors} ({successful_subsectors/total_subsectors*100:.1f}%)")
    
    # Mixed combinations summary
    print(f"\n📊 MIXED COMBINATION TESTS:")
    successful_mixed = sum(1 for r in mixed_results.values() if 'error' not in r)
    total_mixed = len(mixed_results)
    print(f"   Success Rate: {successful_mixed}/{total_mixed} ({successful_mixed/total_mixed*100:.1f}%)")
    
    # Streaming summary
    print(f"\n📊 STREAMING TEST:")
    if 'error' not in streaming_results:
        print(f"   ✅ Success: {streaming_results['count']} companies in {streaming_results['time']:.2f}s")
    else:
        print(f"   ❌ Error: {streaming_results['error']}")
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE ANALYSIS:")
    all_times = []
    for results in [sector_results, subsector_results, mixed_results]:
        for result in results.values():
            if 'time' in result:
                all_times.append(result['time'])
    
    if all_times:
        avg_time = sum(all_times) / len(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        print(f"   Average Response Time: {avg_time:.2f}s")
        print(f"   Fastest Response: {min_time:.2f}s")
        print(f"   Slowest Response: {max_time:.2f}s")
    
    print("\n" + "=" * 60)

def main():
    """Run all tests"""
    print("🚀 STARTING COMPREHENSIVE DYNAMIC SCRAPING TESTS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    sector_results = test_sector_combinations()
    subsector_results = test_subsector_combinations()
    mixed_results = test_mixed_combinations()
    streaming_results = test_streaming_functionality()
    
    # Generate summary report
    generate_summary_report(sector_results, subsector_results, mixed_results, streaming_results)
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
