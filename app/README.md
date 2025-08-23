# SmartWealthAI - Comprehensive Financial Data Scraper & AI-Powered Analysis Platform

A powerful web application that aggregates financial data from multiple sources and provides AI-powered stock recommendations using open-source LLMs.

## 🚀 Features

### 🤖 AI-Powered Stock Recommendations
- **Sector-based analysis** with intelligent subsector selection
- **LLM-powered insights** using open-source language models
- **Multi-factor scoring** combining technical, fundamental, and analyst data
- **Risk-adjusted recommendations** based on user preferences
- **Portfolio optimization** with diversification analysis
- **Long-term growth potential** assessment

### 📊 Comprehensive Stock Data
- **Real-time stock prices** and market data from multiple sources
- **Historical price analysis** with technical indicators
- **Company information** and financial metrics
- **Analyst ratings** and price targets
- **Technical analysis** (RSI, moving averages, volatility, beta)
- **Fundamental analysis** (P/E ratios, market cap, revenue growth)

### 📰 Multi-Source Financial News
- **Aggregated news** from 6+ financial sources
- **Sentiment analysis** of news articles
- **Stock-specific news** filtering
- **News search** functionality across all sources
- **Real-time updates** and trending topics

### 📅 Earnings & Calendar Data
- **Earnings calendar** with estimates and actual results
- **Earnings announcements** and conference call schedules
- **Revenue and EPS estimates** from analysts
- **Earnings surprises** and historical data

### 💼 Portfolio Analysis
- **Portfolio performance** tracking
- **Risk analysis** and metrics calculation
- **Stock comparison** tools
- **Diversification analysis**
- **Performance attribution**

### 🔍 Advanced Screening & Analysis
- **Stock screening** with multiple criteria
- **ETF screening** and analysis
- **Fund analysis** and ratings
- **Insider trading** data
- **Sector performance** tracking

### 📈 Market Intelligence
- **Market movers** (top gainers/losers)
- **Sector performance** analysis
- **Market commentary** and analysis
- **Economic indicators**
- **Trading volume** analysis

## 🗂️ Data Sources

### Primary Sources
- **Yahoo Finance**: Stock prices, company info, financial metrics
- **MarketWatch**: Business news and market updates
- **CNBC**: Financial news and market analysis
- **Morningstar**: Fund analysis, ratings, and research
- **Seeking Alpha**: Stock analysis, earnings data, dividend info
- **Finviz**: Technical analysis, stock screening, insider trading

### AI & LLM Components
- **Open-source LLMs**: Local language models for analysis
- **Sector Analyzer**: Comprehensive sector and subsector analysis
- **Stock Recommender**: AI-powered stock recommendation engine
- **Sentiment Analysis**: News and market sentiment evaluation

### Data Types Available
- **Stock Data**: Prices, volumes, market cap, P/E ratios
- **Technical Indicators**: RSI, moving averages, beta, volatility
- **Fundamental Data**: Revenue, earnings, debt ratios, margins
- **Analyst Ratings**: Price targets, buy/sell recommendations
- **News & Sentiment**: Articles with sentiment analysis
- **Earnings Data**: Estimates, actuals, surprises, dates
- **Dividend Information**: Yields, payout ratios, ex-dates
- **Insider Trading**: Executive transactions and ownership
- **AI Insights**: LLM-generated analysis and recommendations

## 🛠️ Setup Instructions

### 1. Virtual Environment Setup
```bash
# Navigate to your project directory
cd /Users/shubhampal/Documents/SmartwealthAI

# Activate the virtual environment
source venv/bin/activate

# Or use the provided script
./activate_venv.sh
```

### 2. Install Dependencies
```bash
# Install all required packages including AI components
pip install -r SmartWealthSimple/app/requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `SmartWealthSimple/app/` directory:
```bash
# Flask settings
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# Optional API Keys (some features work without them)
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
NEWS_API_KEY=your-news-api-key

# AI/LLM settings
USE_LOCAL_LLM=True
LLM_MODEL_NAME=microsoft/DialoGPT-medium
```

### 4. Run the Application
```bash
# Navigate to the app directory
cd SmartWealthSimple/app

# Run the Flask application
python app.py
```

The application will be available at `http://localhost:5000`

## 🔌 API Endpoints

### 🤖 AI-Powered Recommendations
- `GET /api/ai/sectors` - Get all available sectors for analysis
- `GET /api/ai/sectors/<sector>` - Get detailed sector information
- `GET /api/ai/sectors/<sector>/subsectors` - Get subsectors for a sector
- `POST /api/ai/recommendations` - Get AI-powered stock recommendations
- `POST /api/ai/analysis` - Get LLM-powered sector analysis
- `GET /api/ai/stocks/<sector>/<subsector>` - Get stocks by subsector
- `POST /api/ai/portfolio-analysis` - Analyze portfolio with AI insights

### Stock Data
- `GET /api/stock/<ticker>` - Comprehensive stock data from all sources
- `GET /api/stock/<ticker>/simple` - Basic stock data from Yahoo Finance
- `GET /api/stock/<ticker>/technical` - Technical analysis from Finviz
- `GET /api/stock/<ticker>/analysis` - Analyst ratings and analysis
- `GET /api/stock/<ticker>/news` - Stock-specific news from all sources

### News & Media
- `GET /api/news` - Aggregated financial news from all sources
- `GET /api/news/search?q=<query>` - Search news across all sources
- `GET /api/news?source=<source>&category=<category>` - News from specific source

### Market Data
- `GET /api/market-movers` - Top gainers and losers
- `GET /api/market-overview` - Comprehensive market overview
- `GET /api/sector-performance` - Sector performance data

### Screening & Analysis
- `GET /api/stock-screener` - Stock screening from Finviz
- `GET /api/stock-screener/seeking-alpha` - Stock screening from Seeking Alpha
- `GET /api/etf-screener` - ETF screening from Morningstar
- `GET /api/insider-trading` - Insider trading data

### Portfolio & Earnings
- `POST /api/portfolio/analyze` - Comprehensive portfolio analysis
- `GET /api/earnings-calendar` - Earnings calendar from multiple sources
- `GET /api/earnings/<ticker>` - Earnings data for specific stock
- `GET /api/dividends/<ticker>` - Dividend information

### Source-Specific Data
- `GET /api/sources/yahoo/<ticker>` - Yahoo Finance data only
- `GET /api/sources/finviz/<ticker>` - Finviz data only
- `GET /api/sources/morningstar/<ticker>` - Morningstar data only
- `GET /api/sources/seeking-alpha/<ticker>` - Seeking Alpha data only

### Dashboard
- `GET /api/dashboard` - Comprehensive dashboard data
- `GET /health` - Health check endpoint

## 📊 Usage Examples

### Get AI-Powered Stock Recommendations
```bash
curl -X POST http://localhost:5000/api/ai/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "Technology",
    "subsectors": ["Software & Services", "Semiconductors"],
    "market_cap_preference": "all",
    "risk_tolerance": "medium",
    "investment_horizon": "long_term",
    "max_recommendations": 20
  }'
```

### Get Sector Analysis
```bash
curl -X POST http://localhost:5000/api/ai/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "Healthcare",
    "subsectors": ["Biotechnology", "Medical Devices"],
    "market_cap_preference": "mid_cap"
  }'
```

### Browse Available Sectors
```bash
curl http://localhost:5000/api/ai/sectors
```

### Get Comprehensive Stock Data
```bash
curl http://localhost:5000/api/stock/AAPL
```

### Get News for a Specific Stock
```bash
curl http://localhost:5000/api/stock/AAPL/news?limit=10
```

### Search for News Articles
```bash
curl "http://localhost:5000/api/news/search?q=tesla&limit=10"
```

### Analyze Portfolio with AI
```bash
curl -X POST http://localhost:5000/api/ai/portfolio-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"],
    "risk_tolerance": "medium",
    "investment_horizon": "long_term"
  }'
```

### Get Market Overview
```bash
curl http://localhost:5000/api/market-overview
```

### Screen Stocks
```bash
curl "http://localhost:5000/api/stock-screener?market_cap_min=1000000000&pe_ratio_max=20"
```

### Get Technical Analysis
```bash
curl http://localhost:5000/api/stock/AAPL/technical
```

## 🌐 Web Interface

The application includes a modern web interface built with React/TypeScript. The frontend is located in the `web/` directory and provides:

- **AI-powered stock recommendations** with sector analysis
- **Real-time dashboard** with market data
- **Stock search** and detailed analysis
- **News feed** with sentiment indicators
- **Portfolio tracking** and analysis
- **Earnings calendar** with notifications
- **Market movers** and sector performance
- **Stock screening** tools
- **Technical charts** and indicators

## 🏗️ Project Structure

```
SmartWealthSimple/app/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── scrapers/            # Data scraping modules
│   ├── __init__.py
│   ├── yahoo_finance.py # Yahoo Finance scraper
│   ├── news_scraper.py  # News aggregation scraper
│   ├── morningstar_scraper.py # Morningstar scraper
│   ├── seeking_alpha_scraper.py # Seeking Alpha scraper
│   ├── finviz_scraper.py # Finviz scraper
│   └── data_aggregator.py # Data aggregation and processing
├── ai/                  # AI and LLM components
│   ├── __init__.py
│   ├── sector_analyzer.py # Sector analysis with LLM
│   └── stock_recommender.py # AI stock recommendation engine
├── templates/           # HTML templates
├── static/             # Static assets
├── test_scrapers.py    # Test script for all scrapers
├── test_ai_system.py   # Test script for AI components
└── README.md          # This file
```

## 🔧 Development

### Testing

Run the comprehensive test suites:
```bash
# Test scrapers
cd SmartWealthSimple/app
python test_scrapers.py

# Test AI system
python test_ai_system.py
```

### Adding New Data Sources

1. Create a new scraper class in the `scrapers/` directory
2. Implement the required methods following the existing pattern
3. Add the scraper to the `DataAggregator` class
4. Update the main Flask application with new endpoints
5. Add tests to `test_scrapers.py`

### Adding New AI Features

1. Create new AI components in the `ai/` directory
2. Implement LLM integration following the existing pattern
3. Add new endpoints to the Flask application
4. Update the AI recommender with new scoring methods
5. Add tests to `test_ai_system.py`

### Error Handling

The application includes comprehensive error handling:
- **Network timeouts** and automatic retries
- **Rate limiting** to respect API limits
- **Graceful degradation** when sources are unavailable
- **Detailed error logging** and reporting
- **Fallback data sources** when primary sources fail
- **LLM fallback** when local models are unavailable

### Performance Optimization

- **Concurrent scraping** using ThreadPoolExecutor
- **Caching** of frequently requested data
- **Request batching** to minimize API calls
- **Data deduplication** for news articles
- **Lazy loading** of heavy data
- **LLM model caching** for faster inference

## ⚖️ Legal Notice

This application is for **educational and personal use only**. Please respect the terms of service of the data sources you're scraping from. Consider implementing:

- **Proper rate limiting** to avoid overwhelming external services
- **Caching mechanisms** to reduce server load
- **User agent headers** that identify your application
- **Respect for robots.txt** files
- **Attribution** to data sources where appropriate

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. Check the test results: `python test_scrapers.py` and `python test_ai_system.py`
2. Verify your internet connection
3. Check if the target websites are accessible
4. Review the error logs in the console
5. Open an issue with detailed error information

## 🎯 Roadmap

- [ ] Add more data sources (Bloomberg, Reuters, etc.)
- [ ] Implement real-time data streaming
- [ ] Add machine learning predictions
- [ ] Create mobile app
- [ ] Add user authentication and portfolios
- [ ] Implement advanced charting
- [ ] Add options and futures data
- [ ] Create API rate limiting and authentication
- [ ] Enhance LLM models with fine-tuning
- [ ] Add natural language query interface
- [ ] Implement portfolio rebalancing recommendations
- [ ] Add ESG and sustainability analysis
