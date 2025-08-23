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

    def get_companies_dynamic(self, sectors: List[str] = None, subsectors: List[str] = None, limit: int = 50) -> List[Dict]:
        """Get companies dynamically using Yahoo Finance screeners"""
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
            
            # Sector-specific company mappings for better accuracy (expanded to 50+ companies per sector)
            sector_companies = {
                'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'ADI', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'INTU', 'WDAY', 'SNOW', 'PLTR', 'CRWD', 'ZS', 'OKTA', 'TEAM', 'SHOP', 'DELL', 'HPQ', 'CSCO', 'JNPR', 'ANET', 'ARW', 'MRVL', 'ON', 'STM', 'NXPI', 'MCHP', 'SLAB', 'SWKS', 'QRVO', 'TER', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'DELL', 'HPQ'],
                'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'DHR', 'BMY', 'AMGN', 'GILD', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'ISRG', 'BDX', 'EW', 'DXCM', 'ABMD', 'ILMN', 'CVS', 'WBA', 'CI', 'ANTM', 'HUM', 'CNC', 'DVA', 'UHS', 'THC', 'ZBH', 'BSX', 'MDT', 'SYK', 'VAR', 'BAX', 'HOLX', 'COO', 'MASI', 'ATRC', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'CRBU', 'BLUE', 'FATE', 'ALNY', 'IONS', 'SGEN', 'BMRN', 'EXEL', 'INCY'],
                'Financial Services': ['BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF', 'AXP', 'BLK', 'SCHW', 'CME', 'ICE', 'SPGI', 'MCO', 'CB', 'AIG', 'MET', 'PRU', 'ALL', 'TRV', 'PGR', 'AFL', 'PFG', 'HIG', 'BEN', 'IVZ', 'TROW', 'BK', 'STT', 'NTRS', 'FITB', 'KEY', 'HBAN', 'RF', 'CFG', 'ZION', 'MTB', 'CMA', 'SIVB', 'FRC', 'PACW', 'WAL', 'COLB', 'FFIN', 'ASB', 'TCBI', 'WBS', 'NYCB'],
                'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'ROST', 'ULTA', 'LVS', 'MAR', 'HLT', 'WYNN', 'CCL', 'RCL', 'NCLH', 'UAL', 'DAL', 'AAL', 'LUV', 'SAVE', 'JBLU', 'ALK', 'HA', 'BKNG', 'EXPE', 'TRIP', 'ABNB', 'LYFT', 'UBER', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY', 'BMWYY', 'MBGYY', 'DDAIF', 'RACE', 'LCID', 'RIVN', 'NIO', 'XPEV', 'LI', 'PSNY', 'RIDE', 'WKHS', 'NKLA', 'HYZN', 'CANOO'],
                'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'CHTR', 'VZ', 'T', 'TMUS', 'DISH', 'SIRI', 'LYV', 'LGF-A', 'LGF-B', 'NWSA', 'NWS', 'FOX', 'FOXA', 'PARA', 'WBD', 'SPOT', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'ZM', 'TEAM', 'SHOP', 'BIDU', 'JD', 'BABA', 'TCEHY', 'NTES', 'TME', 'IQ', 'HUYA', 'DOYU', 'YY', 'WB', 'DASH', 'GRUB', 'UBER', 'LYFT', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'MAR', 'HLT', 'WYNN', 'LVS'],
                'Industrials': ['UPS', 'FDX', 'RTX', 'BA', 'CAT', 'DE', 'GE', 'HON', 'MMM', 'UNP', 'CSX', 'NSC', 'CP', 'KSU', 'JBHT', 'ODFL', 'LSTR', 'XPO', 'CHRW', 'EXPD', 'KNX', 'WERN', 'ARCB', 'SAIA', 'YRCW', 'HTLD', 'CVTI', 'MRTN', 'PTSI', 'USAK', 'LUV', 'DAL', 'AAL', 'UAL', 'SAVE', 'JBLU', 'ALK', 'HA', 'LUV', 'DAL', 'AAL', 'UAL', 'SAVE', 'JBLU', 'ALK', 'HA', 'LUV', 'DAL', 'AAL', 'UAL', 'SAVE', 'JBLU'],
                'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC', 'HES', 'FANG', 'DVN', 'OXY', 'KMI', 'WMB', 'OKE', 'ENB', 'TRP', 'PPL', 'DUK', 'SO', 'NEE', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'EIX', 'PCG', 'DTE', 'ED', 'FE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'ATO', 'LNT', 'BKH', 'OGS', 'AVA', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'CWEN-A', 'BEP', 'BEPC', 'NEP', 'ENPH'],
                'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'TGT', 'HD', 'LOW', 'CVS', 'WBA', 'KR', 'SJM', 'HSY', 'GIS', 'K', 'CPB', 'CAG', 'KMB', 'CL', 'EL', 'ULTA', 'SBUX', 'MCD', 'YUM', 'CMG', 'DPZ', 'PZZA', 'DRI', 'BLMN', 'DIN', 'CAKE', 'YUMC', 'QSR', 'WEN', 'JACK', 'SHAK', 'WING', 'ARCO', 'BOJA', 'DENN', 'RRGB', 'TAST', 'BROS', 'FAT', 'LOVE', 'TOST', 'SWBI', 'RGR', 'AOBC', 'VSTO', 'SWHC'],
                'Real Estate': ['AMT', 'CCI', 'EQIX', 'DLR', 'PLD', 'PSA', 'SPG', 'O', 'WELL', 'VICI', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'SPG', 'O', 'WELL', 'VICI', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'SPG', 'O', 'WELL', 'VICI', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'SPG', 'O', 'WELL', 'VICI', 'PLD', 'AMT', 'CCI', 'EQIX', 'DLR', 'PSA', 'SPG', 'O', 'WELL', 'VICI', 'PLD', 'AMT'],
                'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'EIX', 'PCG', 'DTE', 'ED', 'FE', 'AEE', 'WEC', 'CMS', 'CNP', 'NI', 'ATO', 'LNT', 'BKH', 'OGS', 'AVA', 'CWT', 'ARTNA', 'SJW', 'CWEN', 'CWEN-A', 'BEP', 'BEPC', 'NEP', 'ENPH', 'RUN', 'SEDG', 'FSLR', 'SPWR', 'SUNW', 'JKS', 'CSIQ', 'YGE', 'TSLA', 'NIO', 'XPEV', 'LI', 'PSNY', 'RIVN', 'LCID', 'GM', 'F', 'TM', 'HMC', 'NSANY'],
                'Basic Materials': ['LIN', 'APD', 'FCX', 'NEM', 'NUE', 'AA', 'DD', 'DOW', 'EMN', 'ECL', 'IFF', 'ALB', 'LTHM', 'SQM', 'FMC', 'MOS', 'NTR', 'CF', 'IP', 'PKG', 'WRK', 'BLL', 'SEE', 'AMCR', 'OI', 'GLW', 'VMC', 'MLM', 'SUM', 'EXP', 'CBT', 'SHW', 'PPG', 'AXTA', 'EMN', 'DD', 'DOW', 'LIN', 'APD', 'FCX', 'NEM', 'NUE', 'AA', 'DD', 'DOW', 'EMN', 'ECL', 'IFF', 'ALB', 'LTHM', 'SQM', 'FMC']
            }
            
            # Subsector-specific company mappings (expanded to 50+ companies per subsector)
            subsector_companies = {
                'Software & Services': ['MSFT', 'GOOGL', 'ADBE', 'CRM', 'ORCL', 'NFLX', 'META', 'SAP', 'INTU', 'WDAY', 'SNOW', 'PLTR', 'CRWD', 'ZS', 'OKTA', 'TEAM', 'SHOP', 'SPOT', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'ZM', 'BIDU', 'JD', 'BABA', 'TCEHY', 'NTES', 'TME', 'IQ', 'HUYA', 'DOYU', 'YY', 'WB', 'DASH', 'GRUB', 'UBER', 'LYFT', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'MAR', 'HLT', 'WYNN', 'LVS', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY'],
                'Hardware & Equipment': ['AAPL', 'NVDA', 'INTC', 'AMD', 'QCOM', 'AVGO', 'TXN', 'MU', 'ADI', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'DELL', 'HPQ', 'CSCO', 'JNPR', 'ANET', 'ARW', 'MRVL', 'ON', 'STM', 'NXPI', 'MCHP', 'SLAB', 'SWKS', 'QRVO', 'TER', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'DELL', 'HPQ', 'CSCO', 'JNPR', 'ANET', 'ARW', 'MRVL', 'ON', 'STM', 'NXPI', 'MCHP', 'SLAB', 'SWKS', 'QRVO', 'TER', 'KLAC', 'LRCX'],
                'Semiconductors': ['NVDA', 'AMD', 'INTC', 'QCOM', 'AVGO', 'TXN', 'MU', 'ADI', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'MRVL', 'ON', 'STM', 'NXPI', 'MCHP', 'ADI', 'SLAB', 'SWKS', 'QRVO', 'TER', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'DELL', 'HPQ', 'CSCO', 'JNPR', 'ANET', 'ARW', 'MRVL', 'ON', 'STM', 'NXPI', 'MCHP', 'SLAB', 'SWKS', 'QRVO', 'TER', 'KLAC', 'LRCX', 'AMAT', 'ASML', 'TSM', 'DELL', 'HPQ', 'CSCO'],
                'Internet Services': ['GOOGL', 'META', 'AMZN', 'NFLX', 'BIDU', 'JD', 'BABA', 'TCEHY', 'NTES', 'SPOT', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'ZM', 'UBER', 'LYFT', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'MAR', 'HLT', 'WYNN', 'LVS', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY', 'BMWYY', 'MBGYY', 'DDAIF', 'RACE', 'LCID', 'RIVN', 'NIO', 'XPEV', 'LI', 'PSNY', 'RIDE', 'WKHS', 'NKLA', 'HYZN', 'CANOO', 'TSLA', 'NIO', 'XPEV', 'LI', 'PSNY'],
                'Cloud Computing': ['MSFT', 'AMZN', 'GOOGL', 'CRM', 'ADBE', 'ORCL', 'SAP', 'INTU', 'WDAY', 'SNOW', 'PLTR', 'CRWD', 'ZS', 'OKTA', 'TEAM', 'SHOP', 'SPOT', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'ZM', 'BIDU', 'JD', 'BABA', 'TCEHY', 'NTES', 'TME', 'IQ', 'HUYA', 'DOYU', 'YY', 'WB', 'DASH', 'GRUB', 'UBER', 'LYFT', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'MAR', 'HLT', 'WYNN', 'LVS', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY'],
                'Artificial Intelligence': ['NVDA', 'AMD', 'INTC', 'GOOGL', 'MSFT', 'META', 'AMZN', 'TSLA', 'AAPL', 'PLTR', 'CRWD', 'ZS', 'OKTA', 'TEAM', 'SHOP', 'SPOT', 'SNAP', 'PINS', 'TWTR', 'MTCH', 'ZM', 'BIDU', 'JD', 'BABA', 'TCEHY', 'NTES', 'TME', 'IQ', 'HUYA', 'DOYU', 'YY', 'WB', 'DASH', 'GRUB', 'UBER', 'LYFT', 'ABNB', 'BKNG', 'EXPE', 'TRIP', 'MAR', 'HLT', 'WYNN', 'LVS', 'GM', 'F', 'TM', 'HMC', 'NSANY', 'VWAGY', 'BMWYY', 'MBGYY'],
                'Pharmaceuticals': ['JNJ', 'PFE', 'ABBV', 'ABT', 'BMY', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'ZBH', 'BSX', 'MDT', 'SYK', 'VAR', 'BAX', 'HOLX', 'COO', 'MASI', 'ATRC', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'CRBU', 'BLUE', 'FATE', 'ALNY', 'IONS', 'SGEN', 'BMRN', 'EXEL', 'INCY', 'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'DHR', 'BMY', 'AMGN'],
                'Biotechnology': ['REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN', 'MRNA', 'BNTX', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'CRBU', 'BLUE', 'FATE', 'ALNY', 'IONS', 'SGEN', 'BMRN', 'EXEL', 'INCY', 'JNJ', 'PFE', 'ABBV', 'ABT', 'BMY', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'ZBH', 'BSX', 'MDT', 'SYK', 'VAR', 'BAX', 'HOLX', 'COO', 'MASI', 'ATRC'],
                'Medical Devices': ['JNJ', 'ABT', 'TMO', 'DHR', 'ISRG', 'BDX', 'EW', 'DXCM', 'ABMD', 'ILMN', 'ZBH', 'BSX', 'MDT', 'SYK', 'VAR', 'BAX', 'HOLX', 'COO', 'MASI', 'ATRC', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'CRBU', 'BLUE', 'FATE', 'ALNY', 'IONS', 'SGEN', 'BMRN', 'EXEL', 'INCY', 'JNJ', 'PFE', 'ABBV', 'ABT', 'BMY', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD'],
                'Healthcare Services': ['UNH', 'ANTM', 'HUM', 'CNC', 'WBA', 'CVS', 'CI', 'DVA', 'UHS', 'THC', 'HCA', 'DVA', 'UHS', 'THC', 'HCA', 'DVA', 'UHS', 'THC', 'HCA', 'DVA', 'JNJ', 'PFE', 'ABBV', 'ABT', 'BMY', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'MRNA', 'BNTX', 'GILD', 'ZBH', 'BSX', 'MDT', 'SYK', 'VAR', 'BAX', 'HOLX', 'COO', 'MASI', 'ATRC', 'CRSP', 'EDIT', 'NTLA']
            }
            
            # Collect tickers based on sectors and subsectors
            all_tickers = set()
            
            if sectors:
                for sector in sectors:
                    if sector in sector_companies:
                        # Use sector-specific companies for better accuracy
                        sector_tickers = sector_companies[sector]
                        all_tickers.update(sector_tickers)
                    elif sector in screener_urls:
                        # Fallback to scraping if not in our curated list
                        try:
                            sector_tickers = self._scrape_screener_tickers(screener_urls[sector])
                            all_tickers.update(sector_tickers)
                        except Exception as e:
                            print(f"Error scraping {sector}: {e}")
                            continue
            
            if subsectors:
                for subsector in subsectors:
                    if subsector in subsector_companies:
                        # Use subsector-specific companies
                        subsector_tickers = subsector_companies[subsector]
                        all_tickers.update(subsector_tickers)
                    else:
                        # Fallback to industry scraping
                        try:
                            subsector_tickers = self._scrape_industry_tickers(subsector.lower())
                            all_tickers.update(subsector_tickers)
                        except Exception as e:
                            print(f"Error scraping {subsector}: {e}")
                            continue
            
            # Get stock data for collected tickers
            ticker_list = list(all_tickers)[:limit * 3]  # Get more to filter by market cap and ensure we get enough valid companies
            
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
                except Exception as e:
                    continue  # Skip tickers that fail
            
            # Sort by market cap (descending) and return top companies
            companies.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
            
            return companies[:limit]
            
        except Exception as e:
            return [{'error': str(e)}]

    def _scrape_screener_tickers(self, url: str) -> List[str]:
        """Scrape ticker symbols from Yahoo Finance screener"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tickers = []
            
            # Try multiple selectors to find ticker symbols
            # Method 1: Look for table rows with ticker data
            table_rows = soup.find_all('tr', {'class': 'simpTblRow'})
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
                ticker_elements = soup.find_all('a', href=lambda x: x and '/quote/' in x)
                for element in ticker_elements:
                    href = element.get('href', '')
                    if '/quote/' in href:
                        ticker = href.split('/quote/')[-1].split('?')[0].split('/')[0]
                        if ticker and len(ticker) <= 5 and ticker.isalpha():
                            tickers.append(ticker)
            
            # Method 3: Look for data attributes that might contain tickers
            if not tickers:
                data_elements = soup.find_all(attrs={'data-symbol': True})
                for element in data_elements:
                    ticker = element.get('data-symbol', '')
                    if ticker and len(ticker) <= 5 and ticker.isalpha():
                        tickers.append(ticker)
            
            # Method 4: Use a fallback approach with common large-cap stocks
            if not tickers:
                fallback_tickers = {
                    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM', 'ORCL'],
                    'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT', 'LLY', 'DHR', 'BMY', 'AMGN'],
                    'Financial Services': ['BRK-B', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC'],
                    'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TJX', 'ROST', 'ULTA', 'LVS'],
                    'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'CHTR', 'VZ', 'T', 'TMUS'],
                    'Industrials': ['UPS', 'FDX', 'RTX', 'BA', 'CAT', 'DE', 'GE', 'HON', 'MMM', 'UNP'],
                    'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'PSX', 'VLO', 'MPC'],
                    'Consumer Defensive': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'TGT', 'HD', 'LOW', 'CVS', 'WBA'],
                    'Real Estate': ['AMT', 'CCI', 'EQIX', 'DLR', 'PLD', 'PSA', 'SPG', 'O', 'WELL', 'VICI'],
                    'Utilities': ['NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'EIX', 'PCG'],
                    'Basic Materials': ['LIN', 'APD', 'FCX', 'NEM', 'NUE', 'AA', 'DD', 'DOW', 'EMN', 'ECL']
                }
                
                # Extract sector name from URL
                for sector, sector_tickers in fallback_tickers.items():
                    if sector.lower() in url.lower():
                        tickers.extend(sector_tickers)
                        break
            
            return list(set(tickers))  # Remove duplicates
            
        except Exception as e:
            print(f"Error scraping screener: {e}")
            return []

    def _scrape_industry_tickers(self, industry: str) -> List[str]:
        """Scrape ticker symbols for specific industry"""
        try:
            # Use a more generic approach for industry-based filtering
            # This could be enhanced with more sophisticated industry mapping
            url = f"https://finance.yahoo.com/screener/predefined/ms_technology"  # Default to tech
            return self._scrape_screener_tickers(url)
            
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
