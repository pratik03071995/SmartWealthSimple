import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
import re

# Try to import TextBlob, but handle gracefully if NLTK data is not available
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except Exception as e:
    print(f"Warning: TextBlob not available: {e}")
    TEXTBLOB_AVAILABLE = False

# Import simple sentiment analyzer as fallback
from simple_sentiment import SimpleSentimentAnalyzer

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Initialize sentiment analyzer
        self.sentiment_analyzer = SimpleSentimentAnalyzer()
    
    def get_yahoo_finance_news(self, category: str = 'general', limit: int = 20) -> List[Dict]:
        """Get news from Yahoo Finance"""
        try:
            categories = {
                'general': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
                'market': 'https://feeds.finance.yahoo.com/rss/2.0/headline?category=market',
                'technology': 'https://feeds.finance.yahoo.com/rss/2.0/headline?category=technology',
                'economy': 'https://feeds.finance.yahoo.com/rss/2.0/headline?category=economy'
            }
            
            url = categories.get(category, categories['general'])
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:limit]:
                # Analyze sentiment
                sentiment = self._analyze_sentiment(entry.title + ' ' + entry.get('summary', ''))
                
                news_items.append({
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'url': entry.link,
                    'published_time': entry.get('published', ''),
                    'source': 'Yahoo Finance',
                    'category': category,
                    'sentiment': sentiment,
                    'thumbnail': self._extract_image_from_content(entry.get('summary', ''))
                })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_marketwatch_news(self, limit: int = 20) -> List[Dict]:
        """Get news from MarketWatch"""
        try:
            url = "https://www.marketwatch.com/latest-news"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            articles = soup.find_all('div', {'class': 'article__content'})
            
            for article in articles[:limit]:
                title_elem = article.find('a', {'class': 'link'})
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = 'https://www.marketwatch.com' + title_elem.get('href', '')
                    
                    summary_elem = article.find('p', {'class': 'article__summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    time_elem = article.find('time')
                    published_time = time_elem.get('datetime', '') if time_elem else ''
                    
                    sentiment = self._analyze_sentiment(title + ' ' + summary)
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'published_time': published_time,
                        'source': 'MarketWatch',
                        'category': 'general',
                        'sentiment': sentiment,
                        'thumbnail': self._extract_image_from_content(summary)
                    })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_cnbc_news(self, limit: int = 20) -> List[Dict]:
        """Get news from CNBC"""
        try:
            url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
            feed = feedparser.parse(url)
            
            news_items = []
            for entry in feed.entries[:limit]:
                sentiment = self._analyze_sentiment(entry.title + ' ' + entry.get('summary', ''))
                
                news_items.append({
                    'title': entry.title,
                    'summary': entry.get('summary', ''),
                    'url': entry.link,
                    'published_time': entry.get('published', ''),
                    'source': 'CNBC',
                    'category': 'general',
                    'sentiment': sentiment,
                    'thumbnail': self._extract_image_from_content(entry.get('summary', ''))
                })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_morningstar_news(self, limit: int = 20) -> List[Dict]:
        """Get news from Morningstar"""
        try:
            url = "https://www.morningstar.com/news"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            articles = soup.find_all('article', {'class': 'mdc-article'})
            
            for article in articles[:limit]:
                title_elem = article.find('h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = article.find('a')
                    url = 'https://www.morningstar.com' + link_elem.get('href', '') if link_elem else ''
                    
                    summary_elem = article.find('p', {'class': 'mdc-article__summary'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ''
                    
                    time_elem = article.find('time')
                    published_time = time_elem.get('datetime', '') if time_elem else ''
                    
                    sentiment = self._analyze_sentiment(title + ' ' + summary)
                    
                    news_items.append({
                        'title': title,
                        'summary': summary,
                        'url': url,
                        'published_time': published_time,
                        'source': 'Morningstar',
                        'category': 'general',
                        'sentiment': sentiment,
                        'thumbnail': self._extract_image_from_content(summary)
                    })
            
            return news_items
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_aggregated_news(self, limit_per_source: int = 10) -> Dict:
        """Get news from multiple sources"""
        try:
            all_news = {
                'yahoo_finance': self.get_yahoo_finance_news(limit=limit_per_source),
                'marketwatch': self.get_marketwatch_news(limit=limit_per_source),
                'cnbc': self.get_cnbc_news(limit=limit_per_source),
                'morningstar': self.get_morningstar_news(limit=limit_per_source)
            }
            
            # Combine all news and sort by sentiment
            combined_news = []
            for source, news_list in all_news.items():
                for news in news_list:
                    if 'error' not in news:
                        news['source_name'] = source
                        combined_news.append(news)
            
            # Sort by sentiment (positive first)
            combined_news.sort(key=lambda x: x.get('sentiment', {}).get('polarity', 0), reverse=True)
            
            return {
                'sources': all_news,
                'combined': combined_news,
                'total_count': len(combined_news),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob or fallback to simple analyzer"""
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                return {
                    'polarity': blob.sentiment.polarity,  # -1 to 1
                    'subjectivity': blob.sentiment.subjectivity,  # 0 to 1
                    'sentiment': 'positive' if blob.sentiment.polarity > 0.1 else 'negative' if blob.sentiment.polarity < -0.1 else 'neutral'
                }
            except Exception:
                pass
        
        # Fallback to simple sentiment analyzer
        return self.sentiment_analyzer.analyze_sentiment(text)
    
    def _extract_image_from_content(self, content: str) -> str:
        """Extract image URL from content if available"""
        # This is a simple implementation - you might want to enhance it
        img_pattern = r'https?://[^\s<>"]+\.(?:jpg|jpeg|png|gif)'
        matches = re.findall(img_pattern, content)
        return matches[0] if matches else ''
    
    def search_news(self, query: str, sources: List[str] = None, limit: int = 20) -> List[Dict]:
        """Search for news articles containing specific keywords"""
        try:
            if not sources:
                sources = ['yahoo_finance', 'marketwatch', 'cnbc']
            
            all_news = []
            
            if 'yahoo_finance' in sources:
                yahoo_news = self.get_yahoo_finance_news(limit=50)
                all_news.extend(yahoo_news)
            
            if 'marketwatch' in sources:
                mw_news = self.get_marketwatch_news(limit=50)
                all_news.extend(mw_news)
            
            if 'cnbc' in sources:
                cnbc_news = self.get_cnbc_news(limit=50)
                all_news.extend(cnbc_news)
            
            # Filter by query
            query_lower = query.lower()
            filtered_news = []
            
            for news in all_news:
                if 'error' not in news:
                    title_lower = news.get('title', '').lower()
                    summary_lower = news.get('summary', '').lower()
                    
                    if query_lower in title_lower or query_lower in summary_lower:
                        filtered_news.append(news)
            
            # Sort by relevance (simple keyword matching)
            filtered_news.sort(key=lambda x: 
                (query_lower in x.get('title', '').lower(), 
                 x.get('sentiment', {}).get('polarity', 0)), reverse=True)
            
            return filtered_news[:limit]
        except Exception as e:
            return [{'error': str(e)}]
