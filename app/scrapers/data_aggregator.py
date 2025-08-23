import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from concurrent.futures import ThreadPoolExecutor
import time

from .yahoo_finance import YahooFinanceScraper
from .news_scraper import NewsScraper
from .morningstar_scraper import MorningstarScraper
from .seeking_alpha_scraper import SeekingAlphaScraper
from .finviz_scraper import FinvizScraper

class DataAggregator:
    def __init__(self):
        self.yahoo_scraper = YahooFinanceScraper()
        self.news_scraper = NewsScraper()
        self.morningstar_scraper = MorningstarScraper()
        self.seeking_alpha_scraper = SeekingAlphaScraper()
        self.finviz_scraper = FinvizScraper()
        
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def get_comprehensive_stock_data(self, ticker: str) -> Dict:
        """Get comprehensive stock data from all sources"""
        try:
            ticker = ticker.upper()
            
            # Get data from all sources concurrently
            with self.executor as executor:
                # Submit all scraping tasks
                yahoo_future = executor.submit(self.yahoo_scraper.get_stock_info, ticker)
                finviz_future = executor.submit(self.finviz_scraper.get_stock_overview, ticker)
                technical_future = executor.submit(self.finviz_scraper.get_technical_analysis, ticker)
                morningstar_future = executor.submit(self.morningstar_scraper.get_stock_analysis, ticker)
                seeking_alpha_future = executor.submit(self.seeking_alpha_scraper.get_stock_analysis, ticker)
                
                # Get results
                yahoo_data = yahoo_future.result()
                finviz_data = finviz_future.result()
                technical_data = technical_future.result()
                morningstar_data = morningstar_future.result()
                seeking_alpha_data = seeking_alpha_future.result()
            
            # Combine all data
            comprehensive_data = {
                'ticker': ticker,
                'last_updated': datetime.now().isoformat(),
                'sources': {
                    'yahoo_finance': yahoo_data,
                    'finviz': finviz_data,
                    'technical_analysis': technical_data,
                    'morningstar': morningstar_data,
                    'seeking_alpha': seeking_alpha_data
                },
                'summary': self._create_summary(yahoo_data, finviz_data, technical_data, morningstar_data, seeking_alpha_data)
            }
            
            return comprehensive_data
        except Exception as e:
            return {
                'ticker': ticker,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def get_comprehensive_news(self, ticker: str = None, limit: int = 20) -> Dict:
        """Get comprehensive news from all sources"""
        try:
            with self.executor as executor:
                # Submit news scraping tasks
                yahoo_news_future = executor.submit(self.yahoo_scraper.get_stock_news, ticker, limit//4) if ticker else None
                seeking_alpha_news_future = executor.submit(self.seeking_alpha_scraper.get_stock_news, ticker, limit//4) if ticker else None
                finviz_news_future = executor.submit(self.finviz_scraper.get_news, ticker, limit//4) if ticker else None
                
                # Get general news from all sources
                yahoo_general_future = executor.submit(self.news_scraper.get_yahoo_finance_news, 'general', limit//4)
                marketwatch_future = executor.submit(self.news_scraper.get_marketwatch_news, limit//4)
                cnbc_future = executor.submit(self.news_scraper.get_cnbc_news, limit//4)
                morningstar_news_future = executor.submit(self.morningstar_scraper.get_market_news, limit//4)
                
                # Collect results
                all_news = []
                
                if ticker:
                    if yahoo_news_future:
                        yahoo_news = yahoo_news_future.result()
                        all_news.extend(yahoo_news)
                    
                    if seeking_alpha_news_future:
                        seeking_alpha_news = seeking_alpha_news_future.result()
                        all_news.extend(seeking_alpha_news)
                    
                    if finviz_news_future:
                        finviz_news = finviz_news_future.result()
                        all_news.extend(finviz_news)
                else:
                    yahoo_general = yahoo_general_future.result()
                    marketwatch_news = marketwatch_future.result()
                    cnbc_news = cnbc_future.result()
                    morningstar_news = morningstar_news_future.result()
                    
                    all_news.extend(yahoo_general)
                    all_news.extend(marketwatch_news)
                    all_news.extend(cnbc_news)
                    all_news.extend(morningstar_news)
                
                # Remove duplicates and sort by date
                unique_news = self._deduplicate_news(all_news)
                sorted_news = sorted(unique_news, key=lambda x: x.get('published_time', ''), reverse=True)
                
                return {
                    'news': sorted_news[:limit],
                    'total_count': len(sorted_news),
                    'sources': ['yahoo_finance', 'marketwatch', 'cnbc', 'morningstar', 'seeking_alpha', 'finviz'],
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_market_overview(self) -> Dict:
        """Get comprehensive market overview"""
        try:
            with self.executor as executor:
                # Submit market data tasks
                yahoo_movers_future = executor.submit(self.yahoo_scraper.get_market_movers)
                finviz_market_future = executor.submit(self.finviz_scraper.get_market_overview)
                morningstar_sectors_future = executor.submit(self.morningstar_scraper.get_sector_performance)
                aggregated_news_future = executor.submit(self.news_scraper.get_aggregated_news, 5)
                
                # Get results
                movers = yahoo_movers_future.result()
                finviz_market = finviz_market_future.result()
                sector_performance = morningstar_sectors_future.result()
                news = aggregated_news_future.result()
                
                return {
                    'market_movers': movers,
                    'market_indices': finviz_market.get('indices', []),
                    'sector_performance': sector_performance,
                    'news': news,
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_portfolio_analysis(self, tickers: List[str]) -> Dict:
        """Get comprehensive portfolio analysis"""
        try:
            portfolio_data = []
            total_value = 0
            
            # Get data for each ticker
            with self.executor as executor:
                futures = []
                for ticker in tickers:
                    future = executor.submit(self.get_comprehensive_stock_data, ticker)
                    futures.append(future)
                
                # Collect results
                for future in futures:
                    stock_data = future.result()
                    if 'error' not in stock_data:
                        portfolio_data.append(stock_data)
                        # Add to total value (using Yahoo Finance price as primary)
                        yahoo_data = stock_data.get('sources', {}).get('yahoo_finance', {})
                        if yahoo_data and yahoo_data.get('current_price'):
                            total_value += yahoo_data['current_price']
            
            # Calculate portfolio metrics
            portfolio_metrics = self._calculate_portfolio_metrics(portfolio_data)
            
            return {
                'stocks': portfolio_data,
                'total_value': total_value,
                'stock_count': len(portfolio_data),
                'metrics': portfolio_metrics,
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_earnings_calendar(self, date: str = None) -> Dict:
        """Get earnings calendar from multiple sources"""
        try:
            with self.executor as executor:
                yahoo_earnings_future = executor.submit(self.yahoo_scraper.get_earnings_calendar, date)
                seeking_alpha_earnings_future = executor.submit(self.seeking_alpha_scraper.get_earnings_data, 'AAPL')  # Example
                
                yahoo_earnings = yahoo_earnings_future.result()
                seeking_alpha_earnings = seeking_alpha_earnings_future.result()
                
                return {
                    'yahoo_earnings': yahoo_earnings,
                    'seeking_alpha_earnings': seeking_alpha_earnings,
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _create_summary(self, yahoo_data: Dict, finviz_data: Dict, technical_data: Dict, 
                       morningstar_data: Dict, seeking_alpha_data: Dict) -> Dict:
        """Create a summary from all data sources"""
        summary = {
            'current_price': yahoo_data.get('current_price') or finviz_data.get('price'),
            'price_change': yahoo_data.get('price_change'),
            'price_change_pct': yahoo_data.get('price_change_pct'),
            'market_cap': yahoo_data.get('market_cap') or finviz_data.get('market_cap'),
            'pe_ratio': yahoo_data.get('pe_ratio') or finviz_data.get('pe_ratio'),
            'volume': yahoo_data.get('volume') or finviz_data.get('volume'),
            'sector': yahoo_data.get('sector') or finviz_data.get('sector'),
            'industry': yahoo_data.get('industry') or finviz_data.get('industry'),
            'technical_signals': {
                'rsi': technical_data.get('rsi_14'),
                'sma_20': technical_data.get('sma_20'),
                'sma_50': technical_data.get('sma_50'),
                'beta': technical_data.get('beta')
            },
            'analyst_ratings': {
                'morningstar_fair_value': morningstar_data.get('fair_value'),
                'seeking_alpha_quant_rating': seeking_alpha_data.get('quant_rating'),
                'seeking_alpha_price_target': seeking_alpha_data.get('price_target')
            }
        }
        
        return summary
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """Remove duplicate news articles based on title similarity"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            if 'error' in news:
                continue
                
            title = news.get('title', '').lower()
            # Simple deduplication - you might want to use more sophisticated methods
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(news)
        
        return unique_news
    
    def _calculate_portfolio_metrics(self, portfolio_data: List[Dict]) -> Dict:
        """Calculate portfolio-level metrics"""
        if not portfolio_data:
            return {}
        
        total_market_cap = 0
        total_pe_ratios = []
        total_betas = []
        
        for stock in portfolio_data:
            yahoo_data = stock.get('sources', {}).get('yahoo_finance', {})
            finviz_data = stock.get('sources', {}).get('finviz', {})
            technical_data = stock.get('sources', {}).get('technical_analysis', {})
            
            # Market cap
            market_cap = yahoo_data.get('market_cap') or finviz_data.get('market_cap')
            if market_cap and isinstance(market_cap, (int, float)):
                total_market_cap += market_cap
            
            # P/E ratio
            pe_ratio = yahoo_data.get('pe_ratio') or finviz_data.get('pe_ratio')
            if pe_ratio and isinstance(pe_ratio, (int, float)):
                total_pe_ratios.append(pe_ratio)
            
            # Beta
            beta = technical_data.get('beta')
            if beta and isinstance(beta, (int, float)):
                total_betas.append(beta)
        
        metrics = {
            'total_market_cap': total_market_cap,
            'avg_pe_ratio': sum(total_pe_ratios) / len(total_pe_ratios) if total_pe_ratios else 0,
            'avg_beta': sum(total_betas) / len(total_betas) if total_betas else 0,
            'stock_count': len(portfolio_data)
        }
        
        return metrics
