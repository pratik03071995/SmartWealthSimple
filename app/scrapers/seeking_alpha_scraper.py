import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
import re

class SeekingAlphaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://seekingalpha.com"
    
    def get_stock_analysis(self, ticker: str) -> Dict:
        """Get comprehensive stock analysis from Seeking Alpha"""
        try:
            url = f"{self.base_url}/symbol/{ticker.upper()}"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis_data = {
                'ticker': ticker.upper(),
                'quant_rating': '',
                'author_rating': '',
                'wall_street_rating': '',
                'price_target': '',
                'upside_potential': '',
                'dividend_yield': '',
                'pe_ratio': '',
                'market_cap': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Extract Quant Rating
            quant_elem = soup.find('div', {'data-test-id': 'quant-rating'})
            if quant_elem:
                analysis_data['quant_rating'] = quant_elem.get_text(strip=True)
            
            # Extract Author Rating
            author_elem = soup.find('div', {'data-test-id': 'author-rating'})
            if author_elem:
                analysis_data['author_rating'] = author_elem.get_text(strip=True)
            
            # Extract Wall Street Rating
            ws_elem = soup.find('div', {'data-test-id': 'wall-street-rating'})
            if ws_elem:
                analysis_data['wall_street_rating'] = ws_elem.get_text(strip=True)
            
            # Extract Price Target
            target_elem = soup.find('span', {'data-test-id': 'price-target'})
            if target_elem:
                analysis_data['price_target'] = target_elem.get_text(strip=True)
            
            # Extract Upside Potential
            upside_elem = soup.find('span', {'data-test-id': 'upside-potential'})
            if upside_elem:
                analysis_data['upside_potential'] = upside_elem.get_text(strip=True)
            
            return analysis_data
        except Exception as e:
            return {
                'ticker': ticker.upper(),
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_earnings_data(self, ticker: str) -> Dict:
        """Get earnings data and estimates"""
        try:
            url = f"{self.base_url}/symbol/{ticker.upper()}/earnings"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            earnings_data = {
                'ticker': ticker.upper(),
                'next_earnings_date': '',
                'eps_estimate': '',
                'revenue_estimate': '',
                'eps_actual': '',
                'revenue_actual': '',
                'surprise': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Extract next earnings date
            date_elem = soup.find('div', {'data-test-id': 'next-earnings-date'})
            if date_elem:
                earnings_data['next_earnings_date'] = date_elem.get_text(strip=True)
            
            # Extract EPS estimate
            eps_est_elem = soup.find('span', {'data-test-id': 'eps-estimate'})
            if eps_est_elem:
                earnings_data['eps_estimate'] = eps_est_elem.get_text(strip=True)
            
            # Extract revenue estimate
            rev_est_elem = soup.find('span', {'data-test-id': 'revenue-estimate'})
            if rev_est_elem:
                earnings_data['revenue_estimate'] = rev_est_elem.get_text(strip=True)
            
            return earnings_data
        except Exception as e:
            return {
                'ticker': ticker.upper(),
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_stock_news(self, ticker: str, limit: int = 10) -> List[Dict]:
        """Get news articles for a specific stock"""
        try:
            url = f"{self.base_url}/symbol/{ticker.upper()}/news"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            articles = soup.find_all('div', {'data-test-id': 'article-item'})
            
            for article in articles[:limit]:
                title_elem = article.find('a', {'data-test-id': 'article-title'})
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = self.base_url + title_elem.get('href', '')
                    
                    author_elem = article.find('span', {'data-test-id': 'author-name'})
                    author = author_elem.get_text(strip=True) if author_elem else ''
                    
                    date_elem = article.find('time')
                    published_time = date_elem.get('datetime', '') if date_elem else ''
                    
                    summary_elem = article.find('p', {'data-test-id': 'article-summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'author': author,
                        'published_time': published_time,
                        'source': 'Seeking Alpha',
                        'ticker': ticker.upper()
                    })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_market_news(self, category: str = 'general', limit: int = 20) -> List[Dict]:
        """Get market news from Seeking Alpha"""
        try:
            categories = {
                'general': '/news',
                'earnings': '/earnings',
                'dividends': '/dividends',
                'market-outlook': '/market-outlook'
            }
            
            url = self.base_url + categories.get(category, categories['general'])
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            articles = soup.find_all('div', {'data-test-id': 'article-item'})
            
            for article in articles[:limit]:
                title_elem = article.find('a', {'data-test-id': 'article-title'})
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = self.base_url + title_elem.get('href', '')
                    
                    author_elem = article.find('span', {'data-test-id': 'author-name'})
                    author = author_elem.get_text(strip=True) if author_elem else ''
                    
                    date_elem = article.find('time')
                    published_time = date_elem.get('datetime', '') if date_elem else ''
                    
                    summary_elem = article.find('p', {'data-test-id': 'article-summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'author': author,
                        'published_time': published_time,
                        'source': 'Seeking Alpha',
                        'category': category
                    })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_dividend_data(self, ticker: str) -> Dict:
        """Get dividend information for a stock"""
        try:
            url = f"{self.base_url}/symbol/{ticker.upper()}/dividends"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            dividend_data = {
                'ticker': ticker.upper(),
                'dividend_yield': '',
                'annual_dividend': '',
                'payout_ratio': '',
                'ex_dividend_date': '',
                'payment_date': '',
                'dividend_growth_rate': '',
                'last_updated': datetime.now().isoformat()
            }
            
            # Extract dividend yield
            yield_elem = soup.find('span', {'data-test-id': 'dividend-yield'})
            if yield_elem:
                dividend_data['dividend_yield'] = yield_elem.get_text(strip=True)
            
            # Extract annual dividend
            annual_elem = soup.find('span', {'data-test-id': 'annual-dividend'})
            if annual_elem:
                dividend_data['annual_dividend'] = annual_elem.get_text(strip=True)
            
            # Extract payout ratio
            payout_elem = soup.find('span', {'data-test-id': 'payout-ratio'})
            if payout_elem:
                dividend_data['payout_ratio'] = payout_elem.get_text(strip=True)
            
            return dividend_data
        except Exception as e:
            return {
                'ticker': ticker.upper(),
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_stock_screener(self, criteria: Dict = None, limit: int = 20) -> List[Dict]:
        """Get stock screener results"""
        try:
            url = f"{self.base_url}/screener"
            
            # Add criteria to URL if provided
            if criteria:
                params = []
                if 'market_cap_min' in criteria:
                    params.append(f"market_cap_min={criteria['market_cap_min']}")
                if 'dividend_yield_min' in criteria:
                    params.append(f"dividend_yield_min={criteria['dividend_yield_min']}")
                if 'pe_ratio_max' in criteria:
                    params.append(f"pe_ratio_max={criteria['pe_ratio_max']}")
                
                if params:
                    url += "?" + "&".join(params)
            
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            stock_rows = soup.find_all('tr', {'data-test-id': 'screener-row'})
            
            for row in stock_rows[:limit]:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    ticker = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)
                    price = cells[2].get_text(strip=True)
                    market_cap = cells[3].get_text(strip=True)
                    pe_ratio = cells[4].get_text(strip=True)
                    dividend_yield = cells[5].get_text(strip=True)
                    
                    stocks.append({
                        'ticker': ticker,
                        'name': name,
                        'price': price,
                        'market_cap': market_cap,
                        'pe_ratio': pe_ratio,
                        'dividend_yield': dividend_yield
                    })
            
            return stocks
        except Exception as e:
            return [{'error': str(e)}]
