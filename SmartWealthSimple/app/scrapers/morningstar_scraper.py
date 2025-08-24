import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
import re

class MorningstarScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.morningstar.com"
    
    def get_fund_info(self, fund_symbol: str) -> Dict:
        """Get comprehensive fund information from Morningstar"""
        try:
            url = f"{self.base_url}/funds/{fund_symbol}"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            fund_data = {
                'symbol': fund_symbol,
                'name': '',
                'category': '',
                'expense_ratio': '',
                'nav': '',
                'ytd_return': '',
                'morningstar_rating': '',
                'risk_rating': '',
                'sustainability_rating': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Extract fund name
            name_elem = soup.find('h1', {'class': 'fund-name'})
            if name_elem:
                fund_data['name'] = name_elem.get_text(strip=True)
            
            # Extract category
            category_elem = soup.find('span', {'class': 'category'})
            if category_elem:
                fund_data['category'] = category_elem.get_text(strip=True)
            
            # Extract NAV
            nav_elem = soup.find('span', {'class': 'nav'})
            if nav_elem:
                fund_data['nav'] = nav_elem.get_text(strip=True)
            
            # Extract YTD return
            ytd_elem = soup.find('span', {'class': 'ytd-return'})
            if ytd_elem:
                fund_data['ytd_return'] = ytd_elem.get_text(strip=True)
            
            # Extract expense ratio
            expense_elem = soup.find('span', {'class': 'expense-ratio'})
            if expense_elem:
                fund_data['expense_ratio'] = expense_elem.get_text(strip=True)
            
            # Extract Morningstar rating
            rating_elem = soup.find('div', {'class': 'star-rating'})
            if rating_elem:
                fund_data['morningstar_rating'] = rating_elem.get_text(strip=True)
            
            return fund_data
        except Exception as e:
            return {
                'symbol': fund_symbol,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_stock_analysis(self, ticker: str) -> Dict:
        """Get stock analysis and ratings from Morningstar"""
        try:
            url = f"{self.base_url}/stocks/{ticker}"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis_data = {
                'ticker': ticker,
                'fair_value': '',
                'fair_value_estimate': '',
                'economic_moat': '',
                'stewardship_rating': '',
                'uncertainty_rating': '',
                'analyst_rating': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Extract fair value
            fair_value_elem = soup.find('span', {'class': 'fair-value'})
            if fair_value_elem:
                analysis_data['fair_value'] = fair_value_elem.get_text(strip=True)
            
            # Extract economic moat
            moat_elem = soup.find('span', {'class': 'economic-moat'})
            if moat_elem:
                analysis_data['economic_moat'] = moat_elem.get_text(strip=True)
            
            # Extract stewardship rating
            stewardship_elem = soup.find('span', {'class': 'stewardship'})
            if stewardship_elem:
                analysis_data['stewardship_rating'] = stewardship_elem.get_text(strip=True)
            
            # Extract uncertainty rating
            uncertainty_elem = soup.find('span', {'class': 'uncertainty'})
            if uncertainty_elem:
                analysis_data['uncertainty_rating'] = uncertainty_elem.get_text(strip=True)
            
            return analysis_data
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_market_news(self, limit: int = 20) -> List[Dict]:
        """Get market news from Morningstar"""
        try:
            url = f"{self.base_url}/news"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            articles = soup.find_all('article', {'class': 'mdc-article'})
            
            for article in articles[:limit]:
                title_elem = article.find('h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = article.find('a')
                    url = self.base_url + link_elem.get('href', '') if link_elem else ''
                    
                    summary_elem = article.find('p', {'class': 'mdc-article__summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    time_elem = article.find('time')
                    published_time = time_elem.get('datetime', '') if time_elem else ''
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'published_time': published_time,
                        'source': 'Morningstar',
                        'category': 'market_analysis'
                    })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_market_commentary(self) -> List[Dict]:
        """Get market commentary and analysis"""
        try:
            url = f"{self.base_url}/markets/market-commentary"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            commentary_items = []
            articles = soup.find_all('div', {'class': 'commentary-article'})
            
            for article in articles:
                title_elem = article.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    author_elem = article.find('span', {'class': 'author'})
                    author = author_elem.get_text(strip=True) if author_elem else ''
                    
                    date_elem = article.find('time')
                    published_date = date_elem.get('datetime', '') if date_elem else ''
                    
                    summary_elem = article.find('p', {'class': 'summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    commentary_items.append({
                        'title': title,
                        'author': author,
                        'summary': summary,
                        'published_date': published_date,
                        'source': 'Morningstar',
                        'type': 'market_commentary'
                    })
            
            return commentary_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_sector_performance(self) -> Dict:
        """Get sector performance data"""
        try:
            url = f"{self.base_url}/markets/sector-performance"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            sectors = []
            sector_rows = soup.find_all('tr', {'class': 'sector-row'})
            
            for row in sector_rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    sector_name = cells[0].get_text(strip=True)
                    performance = cells[1].get_text(strip=True)
                    change = cells[2].get_text(strip=True)
                    
                    sectors.append({
                        'sector': sector_name,
                        'performance': performance,
                        'change': change
                    })
            
            return {
                'sectors': sectors,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_etf_screener(self, category: str = None, limit: int = 20) -> List[Dict]:
        """Get ETF screener data"""
        try:
            url = f"{self.base_url}/etfs/screener"
            if category:
                url += f"?category={category}"
            
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            etfs = []
            etf_rows = soup.find_all('tr', {'class': 'etf-row'})
            
            for row in etf_rows[:limit]:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    symbol = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)
                    category = cells[2].get_text(strip=True)
                    expense_ratio = cells[3].get_text(strip=True)
                    ytd_return = cells[4].get_text(strip=True)
                    
                    etfs.append({
                        'symbol': symbol,
                        'name': name,
                        'category': category,
                        'expense_ratio': expense_ratio,
                        'ytd_return': ytd_return
                    })
            
            return etfs
        except Exception as e:
            return [{'error': str(e)}]
