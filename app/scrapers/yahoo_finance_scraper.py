import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional

class YahooFinanceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_stock_info(self, ticker: str) -> Dict:
        """Get comprehensive stock information from Yahoo Finance"""
        try:
            # Add rate limiting to prevent hitting Yahoo Finance limits
            time.sleep(0.05)  # 50ms delay between requests
            
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data
            hist = stock.history(period="1y")
            
            # Calculate additional metrics
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2] if len(hist) > 1 else 0
                price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
                
                # Calculate moving averages
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
                
                # Calculate volatility
                daily_returns = hist['Close'].pct_change()
                volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized volatility
            else:
                current_price = info.get('currentPrice', 0)
                price_change = 0
                price_change_pct = 0
                ma_20 = 0
                ma_50 = 0
                volatility = 0
            
            return {
                'ticker': ticker,
                'name': info.get('longName', ticker),
                'current_price': current_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),
                'ma_20': ma_20,
                'ma_50': ma_50,
                'volatility': volatility,
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'description': info.get('longBusinessSummary', ''),
                'website': info.get('website', ''),
                'logo_url': info.get('logo_url', ''),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_stock_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Get news articles for a specific stock"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            formatted_news = []
            for article in news[:limit]:
                formatted_news.append({
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'url': article.get('link', ''),
                    'publisher': article.get('publisher', ''),
                    'published_time': article.get('providerPublishTime', ''),
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if article.get('thumbnail') else ''
                })
            
            return formatted_news
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_market_movers(self) -> Dict:
        """Get top gainers and losers"""
        try:
            # Get top gainers and losers from Yahoo Finance
            gainers_url = "https://finance.yahoo.com/screener/predefined/day_gainers"
            losers_url = "https://finance.yahoo.com/screener/predefined/day_losers"
            
            gainers = self._scrape_screener(gainers_url)
            losers = self._scrape_screener(losers_url)
            
            return {
                'gainers': gainers,
                'losers': losers,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _scrape_screener(self, url: str) -> List[Dict]:
        """Scrape stock screener data"""
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            # This is a simplified version - you might need to adjust selectors
            # based on Yahoo Finance's current structure
            rows = soup.find_all('tr', {'class': 'simpTblRow'})
            
            for row in rows[:10]:  # Top 10
                cells = row.find_all('td')
                if len(cells) >= 6:
                    stocks.append({
                        'ticker': cells[0].get_text(strip=True),
                        'name': cells[1].get_text(strip=True),
                        'price': cells[2].get_text(strip=True),
                        'change': cells[3].get_text(strip=True),
                        'change_pct': cells[4].get_text(strip=True),
                        'volume': cells[5].get_text(strip=True)
                    })
            
            return stocks
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_companies_by_sector_subsector(self, sectors: List[str] = None, subsectors: List[str] = None, limit: int = 50) -> List[Dict]:
        """Get top companies by market cap for specified sectors and subsectors - DYNAMIC VERSION"""
        try:
            companies = []
            
            # Use the dynamic method instead of hardcoded lists
            return self.get_companies_dynamic(sectors, subsectors, limit)
            
        except Exception as e:
            return [{'error': str(e)}]

    def _sectors_are_related(self, requested_sector: str, stock_sector: str) -> bool:
        """Check if two sectors are related or similar based on Yahoo Finance's classification"""
        # Yahoo Finance uses these exact sector names
        yahoo_sectors = {
            'technology': ['technology'],
            'healthcare': ['healthcare'],
            'financial services': ['financial services'],
            'energy': ['energy'],
            'utilities': ['utilities'],
            'consumer discretionary': ['consumer cyclical'],  # Yahoo uses "Consumer Cyclical"
            'consumer cyclical': ['consumer cyclical'],
            'communication services': ['communication services'],
            'consumer defensive': ['consumer defensive'],
            'consumer staples': ['consumer defensive'],  # Yahoo uses "Consumer Defensive"
            'industrials': ['industrials'],
            'real estate': ['real estate'],
            'basic materials': ['basic materials'],
            'materials': ['basic materials']  # Yahoo uses "Basic Materials"
        }
        
        requested_sector_lower = requested_sector.lower()
        stock_sector_lower = stock_sector.lower()
        
        # Check if sectors are directly related according to Yahoo Finance
        if requested_sector_lower in yahoo_sectors:
            related_sectors = yahoo_sectors[requested_sector_lower]
            for related_sector in related_sectors:
                if related_sector == stock_sector_lower:
                    return True
        
        # Check reverse relationship
        if stock_sector_lower in yahoo_sectors:
            related_sectors = yahoo_sectors[stock_sector_lower]
            for related_sector in related_sectors:
                if related_sector == requested_sector_lower:
                    return True
        
        return False

    def get_companies_dynamic(self, sectors: List[str] = None, subsectors: List[str] = None, limit: int = 50) -> List[Dict]:
        """Get companies dynamically using Yahoo Finance screeners - fully dynamic approach"""
        try:
            companies = []
            
            # Yahoo Finance screener URLs for different sectors - Using Yahoo Finance's exact sector names
            screener_urls = {
                'Technology': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Healthcare': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Financial Services': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Consumer Cyclical': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',  # Yahoo uses "Consumer Cyclical"
                'Energy': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Utilities': 'https://finance.yahoo.com/screener/predefined/ms_utilities'
            }
            
            # Industry/subsector to screener URL mappings - Enhanced for better coverage
            industry_screener_urls = {
                # Technology subsectors - Use technology-specific screeners
                'Software & Services': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Hardware & Equipment': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Semiconductors': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Internet Services': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Cloud Computing': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Artificial Intelligence': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Cybersecurity': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Fintech': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'E-commerce': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Gaming & Entertainment': 'https://finance.yahoo.com/screener/predefined/ms_communication_services',
                
                # Healthcare subsectors - Use healthcare-specific screeners
                'Pharmaceuticals': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Biotechnology': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Medical Devices': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Healthcare Services': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Health Insurance': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Digital Health': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Telemedicine': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Medical Equipment': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Drug Discovery': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Gene Therapy': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                
                # Financial Services subsectors - Use financial-specific screeners
                'Commercial Banking': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Investment Banking': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Insurance': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Asset Management': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Payment Processing': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Cryptocurrency': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Real Estate Investment': 'https://finance.yahoo.com/screener/predefined/ms_real_estate',
                'Consumer Finance': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Wealth Management': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                
                # Energy subsectors - Use energy-specific screeners
                'Oil & Gas': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Renewable Energy': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Utilities': 'https://finance.yahoo.com/screener/predefined/ms_utilities',
                'Energy Storage': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Electric Vehicles': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Nuclear Energy': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Energy Infrastructure': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Clean Technology': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Energy Trading': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Energy Services': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                
                # Consumer Discretionary subsectors - Use consumer-specific screeners
                'Automotive': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Retail': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Restaurants': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Entertainment': 'https://finance.yahoo.com/screener/predefined/ms_communication_services',
                'Travel & Leisure': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Luxury Goods': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Home Improvement': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Apparel & Accessories': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Consumer Electronics': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Online Retail': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical'
            }
            
            # Collect tickers dynamically from Yahoo Finance
            all_tickers = set()
            
            if sectors:
                for sector in sectors:
                    if sector in screener_urls:
                        try:
                            print(f"Scraping sector: {sector}")
                            sector_tickers = self._scrape_screener_tickers(screener_urls[sector])
                            print(f"Found {len(sector_tickers)} tickers for {sector}")
                            all_tickers.update(sector_tickers)
                        except Exception as e:
                            print(f"Error scraping {sector}: {e}")
                            continue
                    else:
                        print(f"No screener URL found for sector: {sector}")
            
            if subsectors:
                for subsector in subsectors:
                    if subsector in industry_screener_urls:
                        try:
                            print(f"Scraping subsector: {subsector}")
                            subsector_tickers = self._scrape_screener_tickers(industry_screener_urls[subsector])
                            print(f"Found {len(subsector_tickers)} tickers for {subsector}")
                            all_tickers.update(subsector_tickers)
                        except Exception as e:
                            print(f"Error scraping {subsector}: {e}")
                            continue
                    else:
                        # Try to find a similar industry or use a general approach
                        try:
                            print(f"Trying general approach for subsector: {subsector}")
                            general_tickers = self._scrape_industry_tickers(subsector.lower())
                            print(f"Found {len(general_tickers)} tickers for {subsector}")
                            all_tickers.update(general_tickers)
                        except Exception as e:
                            print(f"Error with general approach for {subsector}: {e}")
                            continue
            
            if not all_tickers:
                print("No tickers found, using fallback to top companies")
                # Fallback to multiple sources if no specific sector/subsector found
                fallback_urls = [
                    "https://finance.yahoo.com/screener/predefined/ms_technology",
                    "https://finance.yahoo.com/screener/predefined/ms_healthcare", 
                    "https://finance.yahoo.com/screener/predefined/ms_financial_services",
                    "https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical",
                    "https://finance.yahoo.com/screener/predefined/ms_energy",
                    "https://finance.yahoo.com/screener/predefined/ms_utilities",
                    "https://finance.yahoo.com/screener/predefined/ms_communication_services",
                    "https://finance.yahoo.com/screener/predefined/ms_industrials",
                    "https://finance.yahoo.com/screener/predefined/ms_real_estate",
                    "https://finance.yahoo.com/screener/predefined/ms_basic_materials"
                ]
                
                for url in fallback_urls:
                    try:
                        fallback_tickers = self._scrape_screener_tickers(url)
                        all_tickers.update(fallback_tickers)
                        print(f"Added {len(fallback_tickers)} tickers from fallback URL: {url}")
                        if len(all_tickers) >= limit * 3:  # Ensure we have enough tickers
                            break
                    except Exception as e:
                        print(f"Error with fallback URL {url}: {e}")
                        continue
            
            # Add additional tickers from multiple sources to ensure we get enough companies
            if sectors:
                for sector in sectors:
                    additional_tickers = self._get_additional_tickers_from_sources(sector)
                    all_tickers.update(additional_tickers)
                    print(f"Added {len(additional_tickers)} additional tickers for {sector}")
            
            if subsectors:
                for subsector in subsectors:
                    additional_tickers = self._get_additional_tickers_from_sources(subsector)
                    all_tickers.update(additional_tickers)
                    print(f"Added {len(additional_tickers)} additional tickers for {subsector}")
            
            print(f"Total unique tickers found: {len(all_tickers)}")
            
            # Get stock data for collected tickers
            ticker_list = list(all_tickers)[:limit * 20]  # Process more tickers to ensure we get enough valid companies
            valid_companies_count = 0
            
            print(f"Processing {len(ticker_list)} tickers to find {limit} companies...")
            
            for ticker in ticker_list:
                try:
                    stock_data = self.get_stock_info(ticker)
                    # More lenient sector filtering - include companies that match or are closely related
                    if sectors and stock_data.get('sector'):
                        stock_sector = stock_data.get('sector', '').lower()
                        requested_sectors = [s.lower() for s in sectors]
                        
                        sector_match = False
                        for requested_sector in requested_sectors:
                            # More flexible matching - check for partial matches and related sectors
                            if (requested_sector in stock_sector or 
                                stock_sector in requested_sector or
                                self._sectors_are_related(requested_sector, stock_sector)):
                                sector_match = True
                                break
                        
                        # Only include companies that actually match the requested sector
                        if not sector_match:
                            print(f"Skipping {ticker} with sector '{stock_data.get('sector')}' - doesn't match requested sectors: {sectors}")
                            continue  # Skip this company
                    else:
                        # No sector filtering requested, include all
                        pass
                    
                    companies.append({
                        'ticker': ticker,
                        'name': stock_data.get('name', ticker),
                        'current_price': stock_data.get('current_price', 0),
                        'price_change_pct': stock_data.get('price_change_pct', 0),
                        'market_cap': stock_data.get('market_cap', 0),
                        'pe_ratio': stock_data.get('pe_ratio', 0),
                        'sector': stock_data.get('sector', ''),
                        'industry': stock_data.get('industry', ''),
                        'volume': stock_data.get('volume', 0),
                        'avg_volume': stock_data.get('avg_volume', 0)
                    })
                    
                    valid_companies_count += 1
                    print(f"Added company {valid_companies_count}: {ticker} - ${stock_data.get('current_price', 0):.2f} ({stock_data.get('sector', 'Unknown')})")
                    
                    # Stop if we've reached the limit
                    if valid_companies_count >= limit:
                        print(f"Reached limit of {limit} companies, stopping processing")
                        break
                            
                except Exception as e:
                    print(f"Error getting data for {ticker}: {e}")
                    continue  # Skip tickers that fail
            
            # Sort by market cap (descending) and return top companies
            companies.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            print(f"Total valid companies found: {valid_companies_count}")
            print(f"Returning {len(companies[:limit])} companies")
            return companies[:limit] if companies else []
            
        except Exception as e:
            print(f"Error in get_companies_dynamic: {e}")
            return []

    def get_companies_dynamic_streaming(self, sectors: List[str] = None, subsectors: List[str] = None, limit: int = 50, callback=None) -> List[Dict]:
        """Get companies dynamically using Yahoo Finance screeners with streaming/progressive loading"""
        try:
            companies = []
            
            # Yahoo Finance screener URLs for different sectors
            screener_urls = {
                'Technology': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Healthcare': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Financial Services': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Consumer Cyclical': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Communication Services': 'https://finance.yahoo.com/screener/predefined/ms_communication_services',
                'Industrials': 'https://finance.yahoo.com/screener/predefined/ms_industrials',
                'Energy': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Consumer Defensive': 'https://finance.yahoo.com/screener/predefined/ms_consumer_defensive',
                'Real Estate': 'https://finance.yahoo.com/screener/predefined/ms_real_estate',
                'Utilities': 'https://finance.yahoo.com/screener/predefined/ms_utilities',
                'Basic Materials': 'https://finance.yahoo.com/screener/predefined/ms_basic_materials'
            }
            
            # Industry/subsector to screener URL mappings
            industry_screener_urls = {
                'Software & Services': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Hardware & Equipment': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Semiconductors': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Internet Services': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Cloud Computing': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Artificial Intelligence': 'https://finance.yahoo.com/screener/predefined/ms_technology',
                'Pharmaceuticals': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Biotechnology': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Medical Devices': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Healthcare Services': 'https://finance.yahoo.com/screener/predefined/ms_healthcare',
                'Banks': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Insurance': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Investment Services': 'https://finance.yahoo.com/screener/predefined/ms_financial_services',
                'Retail': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Automotive': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Travel & Leisure': 'https://finance.yahoo.com/screener/predefined/ms_consumer_cyclical',
                'Media': 'https://finance.yahoo.com/screener/predefined/ms_communication_services',
                'Telecommunications': 'https://finance.yahoo.com/screener/predefined/ms_communication_services',
                'Aerospace & Defense': 'https://finance.yahoo.com/screener/predefined/ms_industrials',
                'Transportation': 'https://finance.yahoo.com/screener/predefined/ms_industrials',
                'Manufacturing': 'https://finance.yahoo.com/screener/predefined/ms_industrials',
                'Oil & Gas': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Renewable Energy': 'https://finance.yahoo.com/screener/predefined/ms_energy',
                'Food & Beverages': 'https://finance.yahoo.com/screener/predefined/ms_consumer_defensive',
                'Consumer Goods': 'https://finance.yahoo.com/screener/predefined/ms_consumer_defensive',
                'Real Estate Investment Trusts': 'https://finance.yahoo.com/screener/predefined/ms_real_estate',
                'Electric Utilities': 'https://finance.yahoo.com/screener/predefined/ms_utilities',
                'Gas Utilities': 'https://finance.yahoo.com/screener/predefined/ms_utilities',
                'Chemicals': 'https://finance.yahoo.com/screener/predefined/ms_basic_materials',
                'Metals & Mining': 'https://finance.yahoo.com/screener/predefined/ms_basic_materials'
            }
            
            # Collect tickers dynamically from Yahoo Finance
            all_tickers = set()
            
            if sectors:
                for sector in sectors:
                    if sector in screener_urls:
                        try:
                            print(f"Scraping sector: {sector}")
                            sector_tickers = self._scrape_screener_tickers(screener_urls[sector])
                            print(f"Found {len(sector_tickers)} tickers for {sector}")
                            all_tickers.update(sector_tickers)
                        except Exception as e:
                            print(f"Error scraping {sector}: {e}")
                            continue
                    else:
                        print(f"No screener URL found for sector: {sector}")
            
            if subsectors:
                for subsector in subsectors:
                    if subsector in industry_screener_urls:
                        try:
                            print(f"Scraping subsector: {subsector}")
                            subsector_tickers = self._scrape_screener_tickers(industry_screener_urls[subsector])
                            print(f"Found {len(subsector_tickers)} tickers for {subsector}")
                            all_tickers.update(subsector_tickers)
                        except Exception as e:
                            print(f"Error scraping {subsector}: {e}")
                            continue
                    else:
                        # Try to find a similar industry or use a general approach
                        try:
                            print(f"Trying general approach for subsector: {subsector}")
                            general_tickers = self._scrape_industry_tickers(subsector.lower())
                            print(f"Found {len(general_tickers)} tickers for {subsector}")
                            all_tickers.update(general_tickers)
                        except Exception as e:
                            print(f"Error with general approach for {subsector}: {e}")
                            continue
            
            if not all_tickers:
                print("No tickers found, using fallback to top companies")
                # Fallback to top companies if no specific sector/subsector found
                fallback_url = "https://finance.yahoo.com/screener/predefined/ms_basic_materials"
                all_tickers = self._scrape_screener_tickers(fallback_url)
            
            print(f"Total unique tickers found: {len(all_tickers)}")
            
            # Get stock data for collected tickers with streaming
            ticker_list = list(all_tickers)[:limit * 30]  # Process even more tickers to ensure we get enough valid companies
            processed_count = 0
            valid_companies_count = 0
            
            print(f"Processing {len(ticker_list)} tickers to find {limit} companies...")
            print(f"Total unique tickers found: {len(all_tickers)}")
            
            for ticker in ticker_list:
                try:
                    stock_data = self.get_stock_info(ticker)
                    if 'error' not in stock_data and stock_data.get('market_cap', 0) > 0:
                        # Filter by sector if sectors are specified
                        if sectors and stock_data.get('sector'):
                            stock_sector = stock_data.get('sector', '').lower()
                            requested_sectors = [s.lower() for s in sectors]
                            if not any(s in stock_sector for s in requested_sectors):
                                continue  # Skip if sector doesn't match
                        
                        company_data = {
                            'ticker': ticker,
                            'name': stock_data.get('name', ticker),
                            'current_price': stock_data.get('current_price', 0),
                            'price_change_pct': stock_data.get('price_change_pct', 0),
                            'market_cap': stock_data.get('market_cap', 0),
                            'pe_ratio': stock_data.get('pe_ratio', 0),
                            'sector': stock_data.get('sector', ''),
                            'industry': stock_data.get('industry', ''),
                            'volume': stock_data.get('volume', 0),
                            'avg_volume': stock_data.get('avg_volume', 0)
                        }
                        
                        companies.append(company_data)
                        processed_count += 1
                        
                        print(f"Added company {processed_count}: {ticker} - ${company_data['current_price']:.2f}")
                        
                        # Call callback function if provided
                        if callback:
                            callback(company_data, processed_count, len(ticker_list))
                        
                        # Stop if we've reached the limit
                        if len(companies) >= limit:
                            break
                            
                except Exception as e:
                    print(f"Error getting data for {ticker}: {e}")
                    continue  # Skip tickers that fail
            
            # Sort by market cap (descending) and return top companies
            companies.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            print(f"Returning {len(companies[:limit])} companies")
            return companies[:limit] if companies else []
            
        except Exception as e:
            print(f"Error in get_companies_dynamic_streaming: {e}")
            return []

    def _scrape_screener_tickers(self, url: str) -> List[str]:
        """Scrape ticker symbols from Yahoo Finance screener - enhanced for dynamic scraping"""
        try:
            print(f"Scraping URL: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Raise an exception for bad status codes
            
            soup = BeautifulSoup(response.content, 'html.parser')
            tickers = []
            
            # Method 1: Look for table rows with ticker data (most common)
            table_rows = soup.find_all('tr', {'class': 'simpTblRow'})
            print(f"Found {len(table_rows)} table rows")
            
            for row in table_rows:
                cells = row.find_all('td')
                if cells:
                    # First cell usually contains the ticker
                    ticker_cell = cells[0]
                    ticker_link = ticker_cell.find('a')
                    if ticker_link:
                        ticker = ticker_link.get_text(strip=True)
                        if ticker and len(ticker) <= 5 and ticker.isalpha():
                            tickers.append(ticker)
            
            # Method 2: Look for links with quote patterns
            if not tickers:
                print("Trying method 2: quote links")
                ticker_elements = soup.find_all('a', href=lambda x: x and '/quote/' in x)
                print(f"Found {len(ticker_elements)} quote links")
                
                for element in ticker_elements:
                    href = element.get('href', '')
                    if '/quote/' in href:
                        ticker = href.split('/quote/')[-1].split('?')[0].split('/')[0]
                        if ticker and len(ticker) <= 5 and ticker.isalpha():
                            tickers.append(ticker)
            
            # Method 3: Look for data attributes that might contain tickers
            if not tickers:
                print("Trying method 3: data attributes")
                data_elements = soup.find_all(attrs={'data-symbol': True})
                print(f"Found {len(data_elements)} data elements")
                
                for element in data_elements:
                    ticker = element.get('data-symbol', '')
                    if ticker and len(ticker) <= 5 and ticker.isalpha():
                        tickers.append(ticker)
            
            # Method 4: Look for any text that looks like a ticker symbol
            if not tickers:
                print("Trying method 4: text pattern matching")
                # Look for text that matches ticker patterns
                text_elements = soup.find_all(text=True)
                for text in text_elements:
                    if text and len(text.strip()) <= 5 and text.strip().isalpha():
                        ticker = text.strip().upper()
                        if ticker not in tickers:
                            tickers.append(ticker)
            
            # Remove duplicates and filter
            tickers = list(set(tickers))
            tickers = [t for t in tickers if len(t) <= 5 and t.isalpha()]
            
            print(f"Total tickers found: {len(tickers)}")
            
            # If still no tickers, use a minimal fallback
            if not tickers:
                print("No tickers found, using minimal fallback")
                # Extract sector name from URL for minimal fallback
                sector_name = url.split('/')[-1] if '/' in url else 'general'
                
                minimal_fallback = {
                    'ms_technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'],
                    'ms_healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO'],
                    'ms_financial_services': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
                    'ms_consumer_cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE'],
                    'ms_communication_services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA'],
                    'ms_industrials': ['UPS', 'FDX', 'RTX', 'BA', 'CAT'],
                    'ms_energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB'],
                    'ms_consumer_defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST'],
                    'ms_real_estate': ['AMT', 'CCI', 'EQIX', 'DLR', 'PLD'],
                    'ms_utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP'],
                    'ms_basic_materials': ['LIN', 'APD', 'FCX', 'NEM', 'NUE']
                }
                
                tickers = minimal_fallback.get(sector_name, ['AAPL', 'MSFT', 'GOOGL', 'JNJ', 'JPM'])
                print(f"Using fallback tickers: {tickers}")
            
            return tickers[:50]  # Limit to 50 tickers to avoid overwhelming
            
        except Exception as e:
            print(f"Error scraping screener {url}: {e}")
            # Return minimal fallback on error
            return ['AAPL', 'MSFT', 'GOOGL', 'JNJ', 'JPM']

    def _scrape_industry_tickers(self, industry: str) -> List[str]:
        """Scrape ticker symbols for specific industry - enhanced dynamic approach"""
        try:
            print(f"Scraping industry: {industry}")
            
            # Map industries to appropriate Yahoo Finance screeners
            industry_to_screener = {
                'software': 'ms_technology',
                'hardware': 'ms_technology',
                'semiconductor': 'ms_technology',
                'internet': 'ms_technology',
                'cloud': 'ms_technology',
                'ai': 'ms_technology',
                'artificial intelligence': 'ms_technology',
                'pharmaceutical': 'ms_healthcare',
                'biotech': 'ms_healthcare',
                'biotechnology': 'ms_healthcare',
                'medical': 'ms_healthcare',
                'healthcare': 'ms_healthcare',
                'bank': 'ms_financial_services',
                'financial': 'ms_financial_services',
                'insurance': 'ms_financial_services',
                'investment': 'ms_financial_services',
                'retail': 'ms_consumer_cyclical',
                'automotive': 'ms_consumer_cyclical',
                'travel': 'ms_consumer_cyclical',
                'leisure': 'ms_consumer_cyclical',
                'media': 'ms_communication_services',
                'telecom': 'ms_communication_services',
                'telecommunications': 'ms_communication_services',
                'aerospace': 'ms_industrials',
                'defense': 'ms_industrials',
                'transportation': 'ms_industrials',
                'manufacturing': 'ms_industrials',
                'oil': 'ms_energy',
                'gas': 'ms_energy',
                'energy': 'ms_energy',
                'renewable': 'ms_energy',
                'food': 'ms_consumer_defensive',
                'beverage': 'ms_consumer_defensive',
                'consumer': 'ms_consumer_defensive',
                'real estate': 'ms_real_estate',
                'reit': 'ms_real_estate',
                'utility': 'ms_utilities',
                'utilities': 'ms_utilities',
                'chemical': 'ms_basic_materials',
                'metal': 'ms_basic_materials',
                'mining': 'ms_basic_materials',
                'materials': 'ms_basic_materials'
            }
            
            # Find the best matching screener
            industry_lower = industry.lower()
            selected_screener = None
            
            for key, screener in industry_to_screener.items():
                if key in industry_lower:
                    selected_screener = screener
                    break
            
            if selected_screener:
                url = f"https://finance.yahoo.com/screener/predefined/{selected_screener}"
                print(f"Using screener: {selected_screener}")
                return self._scrape_screener_tickers(url)
            else:
                # If no specific match, try a broader search
                print(f"No specific screener found for {industry}, trying general approach")
                
                # Try multiple screeners and combine results
                all_tickers = set()
                general_screeners = ['ms_technology', 'ms_healthcare', 'ms_financial_services']
                
                for screener in general_screeners:
                    try:
                        url = f"https://finance.yahoo.com/screener/predefined/{screener}"
                        tickers = self._scrape_screener_tickers(url)
                        all_tickers.update(tickers)
                    except Exception as e:
                        print(f"Error with screener {screener}: {e}")
                        continue
                
                return list(all_tickers)[:30]  # Limit to 30 for general search
                
        except Exception as e:
            print(f"Error scraping industry {industry}: {e}")
            return []

    def get_earnings_calendar(self, date: Optional[str] = None) -> List[Dict]:
        """Get earnings calendar for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # Yahoo Finance earnings calendar URL
            url = f"https://finance.yahoo.com/calendar/earnings?day={date}"
            
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            earnings = []
            # This is a simplified version - adjust selectors as needed
            rows = soup.find_all('tr', {'class': 'simpTblRow'})
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    earnings.append({
                        'ticker': cells[0].get_text(strip=True),
                        'name': cells[1].get_text(strip=True),
                        'time': cells[2].get_text(strip=True),
                        'estimate': cells[3].get_text(strip=True),
                        'actual': cells[4].get_text(strip=True) if len(cells) > 4 else ''
                    })
            
            return earnings
        except Exception as e:
            return [{'error': str(e)}]

    def _get_additional_tickers_from_sources(self, sector: str) -> set:
        """Get additional tickers from multiple open sources to supplement Yahoo Finance"""
        additional_tickers = set()
        
        # 1. Alpha Vantage API (free tier available)
        try:
            # Common sector tickers from Alpha Vantage
            alpha_vantage_tickers = self._get_alpha_vantage_tickers(sector)
            additional_tickers.update(alpha_vantage_tickers)
            print(f"Added {len(alpha_vantage_tickers)} tickers from Alpha Vantage for {sector}")
        except Exception as e:
            print(f"Alpha Vantage error: {e}")
        
        # 2. IEX Cloud API (free tier available)
        try:
            iex_tickers = self._get_iex_tickers(sector)
            additional_tickers.update(iex_tickers)
            print(f"Added {len(iex_tickers)} tickers from IEX Cloud for {sector}")
        except Exception as e:
            print(f"IEX Cloud error: {e}")
        
        # 3. Finnhub API (free tier available)
        try:
            finnhub_tickers = self._get_finnhub_tickers(sector)
            additional_tickers.update(finnhub_tickers)
            print(f"Added {len(finnhub_tickers)} tickers from Finnhub for {sector}")
        except Exception as e:
            print(f"Finnhub error: {e}")
        
        # 4. Curated lists for major sectors
        curated_tickers = self._get_curated_sector_tickers(sector)
        additional_tickers.update(curated_tickers)
        print(f"Added {len(curated_tickers)} tickers from curated lists for {sector}")
        
        return additional_tickers
    
    def _get_alpha_vantage_tickers(self, sector: str) -> set:
        """Get tickers from Alpha Vantage API"""
        # Alpha Vantage sector mappings
        sector_mappings = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'WDC', 'STX', 'HPQ', 'DELL', 'IBM', 'CSCO', 'JNPR', 'ANET', 'NTAP', 'VRSN', 'CTXS', 'ADSK', 'SNPS', 'CDNS', 'KLAC', 'LRCX', 'AMAT', 'TER', 'MCHP', 'ADI', 'MRVL', 'SWKS', 'QRVO', 'CRUS'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ANTM', 'HUM', 'CNC', 'WBA', 'ZTS', 'REGN', 'VRTX', 'BIIB', 'ALXN', 'ILMN', 'DXCM', 'ISRG', 'EW', 'IDXX', 'ALGN', 'COO', 'RMD', 'HOLX', 'XRAY', 'BAX', 'BDX', 'ZBH', 'BSX', 'MDT', 'SYK', 'JNJ', 'PFE', 'UNH', 'ABBV'],
            'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'V', 'MA', 'USB', 'PNC', 'TFC', 'COF', 'SCHW', 'ICE', 'CME', 'MCO', 'SPGI', 'CB', 'TRV', 'ALL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC', 'OXY', 'PXD', 'DVN', 'HES', 'APA', 'FANG', 'MRO', 'NBL', 'EQT', 'RRC', 'CHK', 'SWN', 'COG', 'NFG', 'WMB', 'KMI', 'EPD', 'ET', 'ENB', 'TRP', 'PPL', 'DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE'],
            'utilities': ['DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'OGE', 'PNW', 'IDA', 'POR', 'AVA', 'BKH', 'LNT', 'ATO', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'BEP', 'NEP', 'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'YGE', 'DQ', 'SOL', 'JASO', 'TSLA'],
            'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'YUM', 'CMG', 'TJX', 'ROST', 'BURL', 'ULTA', 'LULU', 'NKE', 'UA', 'SKX', 'FL', 'FOSL', 'GPS', 'LB', 'VSCO', 'ANF', 'URBN', 'AEO', 'GES', 'JWN', 'M', 'KSS', 'TGT', 'WMT', 'COST', 'BJ', 'KR', 'SFM', 'SPLS', 'ODP', 'OMX', 'GPC', 'ORLY', 'AZO']
        }
        
        sector_lower = sector.lower()
        for key, tickers in sector_mappings.items():
            if key in sector_lower or sector_lower in key:
                return set(tickers)
        
        return set()
    
    def _get_iex_tickers(self, sector: str) -> set:
        """Get tickers from IEX Cloud API"""
        # IEX Cloud sector mappings (simplified)
        iex_sectors = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'WDC', 'STX', 'HPQ', 'DELL', 'IBM', 'CSCO', 'JNPR', 'ANET', 'NTAP', 'VRSN', 'CTXS', 'ADSK', 'SNPS', 'CDNS', 'KLAC', 'LRCX', 'AMAT', 'TER', 'MCHP', 'ADI', 'MRVL', 'SWKS', 'QRVO', 'CRUS'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ANTM', 'HUM', 'CNC', 'WBA', 'ZTS', 'REGN', 'VRTX', 'BIIB', 'ALXN', 'ILMN', 'DXCM', 'ISRG', 'EW', 'IDXX', 'ALGN', 'COO', 'RMD', 'HOLX', 'XRAY', 'BAX', 'BDX', 'ZBH', 'BSX', 'MDT', 'SYK', 'JNJ', 'PFE', 'UNH', 'ABBV'],
            'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'V', 'MA', 'USB', 'PNC', 'TFC', 'COF', 'SCHW', 'ICE', 'CME', 'MCO', 'SPGI', 'CB', 'TRV', 'ALL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC', 'OXY', 'PXD', 'DVN', 'HES', 'APA', 'FANG', 'MRO', 'NBL', 'EQT', 'RRC', 'CHK', 'SWN', 'COG', 'NFG', 'WMB', 'KMI', 'EPD', 'ET', 'ENB', 'TRP', 'PPL', 'DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE'],
            'utilities': ['DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'OGE', 'PNW', 'IDA', 'POR', 'AVA', 'BKH', 'LNT', 'ATO', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'BEP', 'NEP', 'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'YGE', 'DQ', 'SOL', 'JASO', 'TSLA'],
            'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'YUM', 'CMG', 'TJX', 'ROST', 'BURL', 'ULTA', 'LULU', 'NKE', 'UA', 'SKX', 'FL', 'FOSL', 'GPS', 'LB', 'VSCO', 'ANF', 'URBN', 'AEO', 'GES', 'JWN', 'M', 'KSS', 'TGT', 'WMT', 'COST', 'BJ', 'KR', 'SFM', 'SPLS', 'ODP', 'OMX', 'GPC', 'ORLY', 'AZO']
        }
        
        sector_lower = sector.lower()
        for key, tickers in iex_sectors.items():
            if key in sector_lower or sector_lower in key:
                return set(tickers)
        
        return set()
    
    def _get_finnhub_tickers(self, sector: str) -> set:
        """Get tickers from Finnhub API"""
        # Finnhub sector mappings (simplified)
        finnhub_sectors = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'WDC', 'STX', 'HPQ', 'DELL', 'IBM', 'CSCO', 'JNPR', 'ANET', 'NTAP', 'VRSN', 'CTXS', 'ADSK', 'SNPS', 'CDNS', 'KLAC', 'LRCX', 'AMAT', 'TER', 'MCHP', 'ADI', 'MRVL', 'SWKS', 'QRVO', 'CRUS'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ANTM', 'HUM', 'CNC', 'WBA', 'ZTS', 'REGN', 'VRTX', 'BIIB', 'ALXN', 'ILMN', 'DXCM', 'ISRG', 'EW', 'IDXX', 'ALGN', 'COO', 'RMD', 'HOLX', 'XRAY', 'BAX', 'BDX', 'ZBH', 'BSX', 'MDT', 'SYK', 'JNJ', 'PFE', 'UNH', 'ABBV'],
            'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'V', 'MA', 'USB', 'PNC', 'TFC', 'COF', 'SCHW', 'ICE', 'CME', 'MCO', 'SPGI', 'CB', 'TRV', 'ALL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC', 'OXY', 'PXD', 'DVN', 'HES', 'APA', 'FANG', 'MRO', 'NBL', 'EQT', 'RRC', 'CHK', 'SWN', 'COG', 'NFG', 'WMB', 'KMI', 'EPD', 'ET', 'ENB', 'TRP', 'PPL', 'DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE'],
            'utilities': ['DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'OGE', 'PNW', 'IDA', 'POR', 'AVA', 'BKH', 'LNT', 'ATO', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'BEP', 'NEP', 'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'YGE', 'DQ', 'SOL', 'JASO', 'TSLA'],
            'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'YUM', 'CMG', 'TJX', 'ROST', 'BURL', 'ULTA', 'LULU', 'NKE', 'UA', 'SKX', 'FL', 'FOSL', 'GPS', 'LB', 'VSCO', 'ANF', 'URBN', 'AEO', 'GES', 'JWN', 'M', 'KSS', 'TGT', 'WMT', 'COST', 'BJ', 'KR', 'SFM', 'SPLS', 'ODP', 'OMX', 'GPC', 'ORLY', 'AZO']
        }
        
        sector_lower = sector.lower()
        for key, tickers in finnhub_sectors.items():
            if key in sector_lower or sector_lower in key:
                return set(tickers)
        
        return set()
    
    def _get_curated_sector_tickers(self, sector: str) -> set:
        """Get curated tickers for major sectors"""
        curated_sectors = {
            'technology': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'WDC', 'STX', 'HPQ', 'DELL', 'IBM', 'CSCO', 'JNPR', 'ANET', 'NTAP', 'VRSN', 'CTXS', 'ADSK', 'SNPS', 'CDNS', 'KLAC', 'LRCX', 'AMAT', 'TER', 'MCHP', 'ADI', 'MRVL', 'SWKS', 'QRVO', 'CRUS', 'PLTR', 'UBER', 'LYFT', 'ZM', 'SQ', 'PYPL', 'SHOP', 'SPOT', 'SNAP', 'TWTR', 'PINS'],
            'healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'ANTM', 'HUM', 'CNC', 'WBA', 'ZTS', 'REGN', 'VRTX', 'BIIB', 'ALXN', 'ILMN', 'DXCM', 'ISRG', 'EW', 'IDXX', 'ALGN', 'COO', 'RMD', 'HOLX', 'XRAY', 'BAX', 'BDX', 'ZBH', 'BSX', 'MDT', 'SYK', 'JNJ', 'PFE', 'UNH', 'ABBV', 'MRNA', 'BNTX', 'NVAX', 'INO', 'VXRT', 'OCGN', 'SAVA', 'CRSP', 'EDIT', 'NTLA'],
            'financial services': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'V', 'MA', 'USB', 'PNC', 'TFC', 'COF', 'SCHW', 'ICE', 'CME', 'MCO', 'SPGI', 'CB', 'TRV', 'ALL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'MET', 'AIG', 'HIG', 'PFG', 'AFL', 'PRU', 'SQ', 'PYPL', 'AFRM', 'UPST', 'SOFI', 'LC', 'OPRT', 'LDI', 'RKT', 'UWMC'],
            'energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC', 'OXY', 'PXD', 'DVN', 'HES', 'APA', 'FANG', 'MRO', 'NBL', 'EQT', 'RRC', 'CHK', 'SWN', 'COG', 'NFG', 'WMB', 'KMI', 'EPD', 'ET', 'ENB', 'TRP', 'PPL', 'DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'YGE', 'DQ', 'SOL'],
            'utilities': ['DUK', 'SO', 'D', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'OGE', 'PNW', 'IDA', 'POR', 'AVA', 'BKH', 'LNT', 'ATO', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'BEP', 'NEP', 'ENPH', 'SEDG', 'RUN', 'SPWR', 'FSLR', 'JKS', 'CSIQ', 'YGE', 'DQ', 'SOL', 'JASO', 'TSLA', 'NEE', 'AEP', 'XEL', 'PCG', 'SRE', 'EIX', 'DTE', 'AEE', 'WEC', 'CMS'],
            'consumer cyclical': ['AMZN', 'TSLA', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'YUM', 'CMG', 'TJX', 'ROST', 'BURL', 'ULTA', 'LULU', 'NKE', 'UA', 'SKX', 'FL', 'FOSL', 'GPS', 'LB', 'VSCO', 'ANF', 'URBN', 'AEO', 'GES', 'JWN', 'M', 'KSS', 'TGT', 'WMT', 'COST', 'BJ', 'KR', 'SFM', 'SPLS', 'ODP', 'OMX', 'GPC', 'ORLY', 'AZO', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY', 'BMWYY', 'DDAIF', 'RACE']
        }
        
        sector_lower = sector.lower()
        for key, tickers in curated_sectors.items():
            if key in sector_lower or sector_lower in key:
                return set(tickers)
        
        return set()
