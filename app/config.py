import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for SmartWealthAI"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API Keys (optional - some features work without them)
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY')
    
    # Scraping settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1  # seconds
    
    # Cache settings
    CACHE_TIMEOUT = 300  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = 60
    
    # User agent for web scraping
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    # Default settings
    DEFAULT_NEWS_LIMIT = 20
    DEFAULT_STOCK_LIMIT = 10
    
    # Supported news sources
    SUPPORTED_NEWS_SOURCES = [
        'yahoo_finance',
        'marketwatch', 
        'cnbc',
        'morningstar'
    ]
    
    # Supported stock data sources
    SUPPORTED_STOCK_SOURCES = [
        'yahoo_finance',
        'alpha_vantage'
    ]
