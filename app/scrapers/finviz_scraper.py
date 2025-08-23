import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
import re

class FinvizScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://finviz.com"
    
    def get_stock_overview(self, ticker: str) -> Dict:
        """Get comprehensive stock overview from Finviz"""
        try:
            url = f"{self.base_url}/quote.ashx?t={ticker.upper()}"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            overview_data = {
                'ticker': ticker.upper(),
                'price': '',
                'change': '',
                'change_pct': '',
                'volume': '',
                'market_cap': '',
                'pe_ratio': '',
                'forward_pe': '',
                'peg_ratio': '',
                'price_to_book': '',
                'price_to_sales': '',
                'debt_to_equity': '',
                'profit_margin': '',
                'operating_margin': '',
                'roa': '',
                'roe': '',
                'revenue': '',
                'revenue_per_share': '',
                'revenue_growth': '',
                'earnings_growth': '',
                'sector': '',
                'industry': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Find the main quote table
            quote_table = soup.find('table', {'class': 'snapshot-table2'})
            if quote_table:
                rows = quote_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            key = cells[i].get_text(strip=True)
                            value = cells[i + 1].get_text(strip=True)
                            
                            # Map Finviz keys to our data structure
                            if key == 'Price':
                                overview_data['price'] = value
                            elif key == 'Change':
                                overview_data['change'] = value
                            elif key == 'Volume':
                                overview_data['volume'] = value
                            elif key == 'Market Cap':
                                overview_data['market_cap'] = value
                            elif key == 'P/E':
                                overview_data['pe_ratio'] = value
                            elif key == 'Forward P/E':
                                overview_data['forward_pe'] = value
                            elif key == 'PEG':
                                overview_data['peg_ratio'] = value
                            elif key == 'P/B':
                                overview_data['price_to_book'] = value
                            elif key == 'P/S':
                                overview_data['price_to_sales'] = value
                            elif key == 'Debt/Eq':
                                overview_data['debt_to_equity'] = value
                            elif key == 'Profit Margin':
                                overview_data['profit_margin'] = value
                            elif key == 'Oper. Margin':
                                overview_data['operating_margin'] = value
                            elif key == 'ROA':
                                overview_data['roa'] = value
                            elif key == 'ROE':
                                overview_data['roe'] = value
                            elif key == 'Revenue':
                                overview_data['revenue'] = value
                            elif key == 'Revenue Per Share':
                                overview_data['revenue_per_share'] = value
                            elif key == 'Revenue Q/Q':
                                overview_data['revenue_growth'] = value
                            elif key == 'Earnings Q/Q':
                                overview_data['earnings_growth'] = value
                            elif key == 'Sector':
                                overview_data['sector'] = value
                            elif key == 'Industry':
                                overview_data['industry'] = value
            
            return overview_data
        except Exception as e:
            return {
                'ticker': ticker.upper(),
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_technical_analysis(self, ticker: str) -> Dict:
        """Get technical analysis data"""
        try:
            url = f"{self.base_url}/quote.ashx?t={ticker.upper()}"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            technical_data = {
                'ticker': ticker.upper(),
                'rsi': '',
                'rsi_14': '',
                'sma_20': '',
                'sma_50': '',
                'sma_200': '',
                'ema_20': '',
                'ema_50': '',
                'ema_200': '',
                'beta': '',
                'atr': '',
                'shares_outstanding': '',
                'shares_float': '',
                'insider_ownership': '',
                'institutional_ownership': '',
                'short_float': '',
                'short_ratio': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Find the technical table
            technical_table = soup.find('table', {'class': 'snapshot-table2'})
            if technical_table:
                rows = technical_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    for i in range(0, len(cells), 2):
                        if i + 1 < len(cells):
                            key = cells[i].get_text(strip=True)
                            value = cells[i + 1].get_text(strip=True)
                            
                            if key == 'RSI (14)':
                                technical_data['rsi_14'] = value
                            elif key == 'SMA20':
                                technical_data['sma_20'] = value
                            elif key == 'SMA50':
                                technical_data['sma_50'] = value
                            elif key == 'SMA200':
                                technical_data['sma_200'] = value
                            elif key == 'EMA20':
                                technical_data['ema_20'] = value
                            elif key == 'EMA50':
                                technical_data['ema_50'] = value
                            elif key == 'EMA200':
                                technical_data['ema_200'] = value
                            elif key == 'Beta':
                                technical_data['beta'] = value
                            elif key == 'ATR':
                                technical_data['atr'] = value
                            elif key == 'Shs Outstand':
                                technical_data['shares_outstanding'] = value
                            elif key == 'Shs Float':
                                technical_data['shares_float'] = value
                            elif key == 'Insider Own':
                                technical_data['insider_ownership'] = value
                            elif key == 'Inst Own':
                                technical_data['institutional_ownership'] = value
                            elif key == 'Short Float':
                                technical_data['short_float'] = value
                            elif key == 'Short Ratio':
                                technical_data['short_ratio'] = value
            
            return technical_data
        except Exception as e:
            return {
                'ticker': ticker.upper(),
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_stock_screener(self, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """Get stock screener results"""
        try:
            url = f"{self.base_url}/screener.ashx"
            
            # Build filter parameters
            params = []
            if filters:
                for key, value in filters.items():
                    if value:
                        params.append(f"{key}={value}")
            
            if params:
                url += "?" + "&".join(params)
            
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            # Find the screener results table
            table = soup.find('table', {'class': 'table-light'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows[:limit]:
                    cells = row.find_all('td')
                    if len(cells) >= 10:
                        ticker_elem = cells[1].find('a')
                        ticker = ticker_elem.get_text(strip=True) if ticker_elem else ''
                        
                        stocks.append({
                            'ticker': ticker,
                            'company': cells[2].get_text(strip=True),
                            'sector': cells[3].get_text(strip=True),
                            'industry': cells[4].get_text(strip=True),
                            'country': cells[5].get_text(strip=True),
                            'market_cap': cells[6].get_text(strip=True),
                            'pe_ratio': cells[7].get_text(strip=True),
                            'price': cells[8].get_text(strip=True),
                            'change': cells[9].get_text(strip=True),
                            'volume': cells[10].get_text(strip=True) if len(cells) > 10 else ''
                        })
            
            return stocks
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_market_overview(self) -> Dict:
        """Get market overview and major indices"""
        try:
            url = f"{self.base_url}/screener.ashx"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            market_data = {
                'indices': [],
                'sectors': [],
                'last_updated': datetime.now().isoformat()
            }
            
            # Find market indices
            indices_table = soup.find('table', {'class': 'table-light'})
            if indices_table:
                rows = indices_table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        market_data['indices'].append({
                            'name': cells[0].get_text(strip=True),
                            'price': cells[1].get_text(strip=True),
                            'change': cells[2].get_text(strip=True),
                            'change_pct': cells[3].get_text(strip=True)
                        })
            
            return market_data
        except Exception as e:
            return {'error': str(e)}
    
    def get_insider_trading(self, ticker: str = None, limit: int = 20) -> List[Dict]:
        """Get insider trading data"""
        try:
            url = f"{self.base_url}/insidertrading.ashx"
            if ticker:
                url += f"?t={ticker.upper()}"
            
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            insider_trades = []
            table = soup.find('table', {'class': 'table-light'})
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:limit]:
                    cells = row.find_all('td')
                    if len(cells) >= 6:
                        insider_trades.append({
                            'ticker': cells[0].get_text(strip=True),
                            'owner': cells[1].get_text(strip=True),
                            'relationship': cells[2].get_text(strip=True),
                            'date': cells[3].get_text(strip=True),
                            'transaction': cells[4].get_text(strip=True),
                            'cost': cells[5].get_text(strip=True),
                            'shares': cells[6].get_text(strip=True) if len(cells) > 6 else '',
                            'value': cells[7].get_text(strip=True) if len(cells) > 7 else ''
                        })
            
            return insider_trades
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_news(self, ticker: str = None, limit: int = 20) -> List[Dict]:
        """Get news from Finviz"""
        try:
            if ticker:
                url = f"{self.base_url}/quote.ashx?t={ticker.upper()}"
            else:
                url = f"{self.base_url}/news.ashx"
            
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            news_table = soup.find('table', {'class': 'table-light'})
            if news_table:
                rows = news_table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:limit]:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        date = cells[0].get_text(strip=True)
                        title_elem = cells[1].find('a')
                        title = title_elem.get_text(strip=True) if title_elem else ''
                        url = title_elem.get('href', '') if title_elem else ''
                        source = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                        
                        news_items.append({
                            'date': date,
                            'title': title,
                            'url': url,
                            'source': source,
                            'ticker': ticker.upper() if ticker else ''
                        })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
