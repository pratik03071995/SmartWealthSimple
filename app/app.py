from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import os
from datetime import datetime, date
import calendar
import json
from scrapers.yahoo_finance import YahooFinanceScraper
from scrapers.news_scraper import NewsScraper
from scrapers.morningstar_scraper import MorningstarScraper
from scrapers.seeking_alpha_scraper import SeekingAlphaScraper
from scrapers.finviz_scraper import FinvizScraper
from scrapers.data_aggregator import DataAggregator
from ai.sector_analyzer import SectorAnalyzer
from ai.stock_recommender import AIStockRecommender

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Swagger UI configuration
SWAGGER_URL = '/docs'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "SmartWealthAI API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Initialize scrapers
yahoo_scraper = YahooFinanceScraper()
news_scraper = NewsScraper()
morningstar_scraper = MorningstarScraper()
seeking_alpha_scraper = SeekingAlphaScraper()
finviz_scraper = FinvizScraper()
data_aggregator = DataAggregator()

# Initialize AI components
sector_analyzer = SectorAnalyzer()
ai_recommender = AIStockRecommender()

@app.route("/health")
def health():
    return jsonify({"ok": True, "timestamp": datetime.now().isoformat()})

# ===== AI-POWERED RECOMMENDATION ENDPOINTS =====
@app.route("/api/ai/sectors")
def get_available_sectors():
    """Get all available sectors for analysis"""
    try:
        sector_hierarchy = sector_analyzer.get_sector_hierarchy()
        sectors = []
        
        for sector_name, sector_info in sector_hierarchy.items():
            sectors.append({
                'name': sector_name,
                'description': sector_info['description'],
                'growth_potential': sector_info['growth_potential'],
                'risk_level': sector_info['risk_level'],
                'subsector_count': len(sector_info['subsectors']),
                'key_drivers': sector_info['key_drivers']
            })
        
        return jsonify({
            'sectors': sectors,
            'total_sectors': len(sectors),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/sectors/<sector_name>")
def get_sector_details(sector_name):
    """Get detailed information about a specific sector"""
    try:
        sector = sector_analyzer.analyze_sector(sector_name)
        return jsonify({
            'sector': {
                'name': sector.name,
                'description': sector.description,
                'subsectors': sector.subsectors,
                'growth_potential': sector.growth_potential,
                'risk_level': sector.risk_level,
                'market_cap_range': sector.market_cap_range,
                'key_drivers': sector.key_drivers
            },
            'last_updated': datetime.now().isoformat()
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/sectors/<sector_name>/subsectors")
def get_sector_subsectors(sector_name):
    """Get all subsectors for a specific sector"""
    try:
        subsectors = sector_analyzer.get_subsectors(sector_name)
        return jsonify({
            'sector': sector_name,
            'subsectors': subsectors,
            'subsector_count': len(subsectors),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/companies/dynamic", methods=["POST"])
def get_companies_dynamic():
    """Get companies dynamically based on sector/subsector using Yahoo Finance screeners"""
    try:
        data = request.get_json()
        sectors = data.get('sectors', [])
        subsectors = data.get('subsectors', [])
        limit = data.get('limit', 50)
        
        if not sectors and not subsectors:
            return jsonify({"error": "At least one sector or subsector must be specified"}), 400
        
        # Get companies dynamically from Yahoo Finance
        companies = yahoo_scraper.get_companies_dynamic(
            sectors=sectors, 
            subsectors=subsectors, 
            limit=limit
        )
        
        return jsonify({
            'sectors': sectors,
            'subsectors': subsectors,
            'companies': companies,
            'company_count': len(companies),
            'limit': limit,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/recommendations", methods=["POST"])
def get_ai_recommendations():
    """Get AI-powered stock recommendations based on sector and subsector selection"""
    try:
        data = request.get_json()
        
        # Required parameters
        sector = data.get('sector')
        subsectors = data.get('subsectors', [])
        
        if not sector:
            return jsonify({"error": "Sector is required"}), 400
        
        # Optional parameters
        market_cap_preference = data.get('market_cap_preference', 'all')
        risk_tolerance = data.get('risk_tolerance', 'medium')
        investment_horizon = data.get('investment_horizon', 'long_term')
        max_recommendations = data.get('max_recommendations', 20)
        
        # Validate sector
        if sector not in sector_analyzer.get_sector_hierarchy():
            return jsonify({"error": f"Invalid sector: {sector}"}), 400
        
        # Validate subsectors
        valid_subsectors = sector_analyzer.get_subsectors(sector)
        if subsectors:
            invalid_subsectors = [sub for sub in subsectors if sub not in valid_subsectors]
            if invalid_subsectors:
                return jsonify({"error": f"Invalid subsectors: {invalid_subsectors}"}), 400
        else:
            # If no subsectors specified, use all
            subsectors = valid_subsectors
        
        # Get AI recommendations
        recommendations = ai_recommender.get_intelligent_recommendations(
            sector=sector,
            subsectors=subsectors,
            market_cap_preference=market_cap_preference,
            risk_tolerance=risk_tolerance,
            investment_horizon=investment_horizon,
            max_recommendations=max_recommendations
        )
        
        return jsonify(recommendations)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/analysis", methods=["POST"])
def get_sector_analysis():
    """Get LLM-powered sector analysis"""
    try:
        data = request.get_json()
        
        sector = data.get('sector')
        subsectors = data.get('subsectors', [])
        market_cap_preference = data.get('market_cap_preference', 'all')
        
        if not sector:
            return jsonify({"error": "Sector is required"}), 400
        
        # Generate LLM analysis
        analysis = sector_analyzer.generate_llm_analysis(
            sector, subsectors, market_cap_preference
        )
        
        return jsonify({
            'sector': sector,
            'subsectors': subsectors,
            'market_cap_preference': market_cap_preference,
            'analysis': analysis,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/stocks/<sector>/<subsector>")
def get_stocks_by_subsector(sector, subsector):
    """Get stocks for a specific subsector"""
    try:
        market_cap_filter = request.args.get('market_cap', 'all')
        stocks = sector_analyzer.get_stocks_by_subsector(sector, subsector, market_cap_filter)
        
        return jsonify({
            'sector': sector,
            'subsector': subsector,
            'market_cap_filter': market_cap_filter,
            'stocks': stocks,
            'stock_count': len(stocks),
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/companies/by-sector", methods=["POST"])
def get_companies_by_sector():
    """Get top 50 companies by market cap for selected sectors and subsectors"""
    try:
        data = request.get_json()
        sectors = data.get('sectors', [])
        subsectors = data.get('subsectors', [])
        limit = data.get('limit', 50)
        
        if not sectors and not subsectors:
            return jsonify({"error": "At least one sector or subsector must be specified"}), 400
        
        # Get companies dynamically from Yahoo Finance
        companies = yahoo_scraper.get_companies_dynamic(
            sectors=sectors, 
            subsectors=subsectors, 
            limit=limit
        )
        
        return jsonify({
            'sectors': sectors,
            'subsectors': subsectors,
            'companies': companies,
            'company_count': len(companies),
            'limit': limit,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/portfolio-analysis", methods=["POST"])
def analyze_portfolio_with_ai():
    """Analyze a portfolio with AI-powered insights"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        risk_tolerance = data.get('risk_tolerance', 'medium')
        investment_horizon = data.get('investment_horizon', 'long_term')
        
        if not tickers:
            return jsonify({"error": "Tickers are required"}), 400
        
        # Get portfolio data
        portfolio_data = data_aggregator.get_portfolio_analysis(tickers)
        
        # Add AI analysis
        sector_distribution = {}
        subsector_distribution = {}
        
        for stock in portfolio_data.get('stocks', []):
            sector = stock.get('sources', {}).get('yahoo_finance', {}).get('sector', 'Unknown')
            subsector = stock.get('sources', {}).get('yahoo_finance', {}).get('industry', 'Unknown')
            
            sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
            subsector_distribution[subsector] = subsector_distribution.get(subsector, 0) + 1
        
        # Generate AI insights
        ai_insights = {
            'sector_diversification': len(sector_distribution) / len(tickers) if tickers else 0,
            'subsector_diversification': len(subsector_distribution) / len(tickers) if tickers else 0,
            'sector_distribution': sector_distribution,
            'subsector_distribution': subsector_distribution,
            'risk_assessment': {
                'risk_tolerance': risk_tolerance,
                'portfolio_risk_score': portfolio_data.get('metrics', {}).get('avg_volatility', 0),
                'recommendations': []
            }
        }
        
        # Add risk recommendations
        if ai_insights['sector_diversification'] < 0.3:
            ai_insights['risk_assessment']['recommendations'].append(
                "Consider diversifying across more sectors to reduce concentration risk"
            )
        
        if portfolio_data.get('metrics', {}).get('avg_volatility', 0) > 0.3:
            ai_insights['risk_assessment']['recommendations'].append(
                "Portfolio shows high volatility - consider adding defensive stocks"
            )
        
        # Combine data
        response = {
            'portfolio_data': portfolio_data,
            'ai_insights': ai_insights,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== COMPREHENSIVE STOCK DATA =====
@app.route("/api/stock/<ticker>")
def get_stock_info(ticker):
    """Get comprehensive stock information from all sources"""
    try:
        comprehensive_data = data_aggregator.get_comprehensive_stock_data(ticker.upper())
        return jsonify(comprehensive_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock/<ticker>/simple")
def get_simple_stock_info(ticker):
    """Get basic stock information from Yahoo Finance"""
    try:
        stock_data = yahoo_scraper.get_stock_info(ticker.upper())
        return jsonify(stock_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock/<ticker>/technical")
def get_technical_analysis(ticker):
    """Get technical analysis data from Finviz"""
    try:
        technical_data = finviz_scraper.get_technical_analysis(ticker.upper())
        return jsonify(technical_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock/<ticker>/analysis")
def get_stock_analysis(ticker):
    """Get stock analysis from Morningstar and Seeking Alpha"""
    try:
        with data_aggregator.executor as executor:
            morningstar_future = executor.submit(morningstar_scraper.get_stock_analysis, ticker.upper())
            seeking_alpha_future = executor.submit(seeking_alpha_scraper.get_stock_analysis, ticker.upper())
            
            morningstar_data = morningstar_future.result()
            seeking_alpha_data = seeking_alpha_future.result()
        
        analysis_data = {
            'ticker': ticker.upper(),
            'morningstar': morningstar_data,
            'seeking_alpha': seeking_alpha_data,
            'last_updated': datetime.now().isoformat()
        }
        return jsonify(analysis_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== NEWS ENDPOINTS =====
@app.route("/api/stock/<ticker>/news")
def get_stock_news(ticker):
    """Get news for a specific stock from all sources"""
    try:
        limit = request.args.get('limit', 20, type=int)
        news_data = data_aggregator.get_comprehensive_news(ticker.upper(), limit=limit)
        return jsonify(news_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/news")
def get_news():
    """Get aggregated financial news from all sources"""
    try:
        source = request.args.get('source', 'all')
        limit = request.args.get('limit', 20, type=int)
        category = request.args.get('category', 'general')
        
        if source == 'yahoo':
            news_data = news_scraper.get_yahoo_finance_news(category=category, limit=limit)
        elif source == 'marketwatch':
            news_data = news_scraper.get_marketwatch_news(limit=limit)
        elif source == 'cnbc':
            news_data = news_scraper.get_cnbc_news(limit=limit)
        elif source == 'morningstar':
            news_data = morningstar_scraper.get_market_news(limit=limit)
        elif source == 'seeking_alpha':
            news_data = seeking_alpha_scraper.get_market_news(category=category, limit=limit)
        elif source == 'finviz':
            news_data = finviz_scraper.get_news(limit=limit)
        else:
            news_data = data_aggregator.get_comprehensive_news(limit=limit)
        
        return jsonify(news_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/news/search")
def search_news():
    """Search for news articles across all sources"""
    try:
        query = request.args.get('q', '')
        sources = request.args.get('sources', '').split(',') if request.args.get('sources') else None
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
        
        search_results = news_scraper.search_news(query, sources=sources, limit=limit)
        return jsonify(search_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== MARKET DATA =====
@app.route("/api/market-movers")
def get_market_movers():
    """Get top gainers and losers from Yahoo Finance"""
    try:
        movers = yahoo_scraper.get_market_movers()
        return jsonify(movers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/market-overview")
def get_market_overview():
    """Get comprehensive market overview from all sources"""
    try:
        market_data = data_aggregator.get_market_overview()
        return jsonify(market_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sector-performance")
def get_sector_performance():
    """Get sector performance from Morningstar"""
    try:
        sector_data = morningstar_scraper.get_sector_performance()
        return jsonify(sector_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== FUNDS AND ETFs =====
@app.route("/api/fund/<fund_symbol>")
def get_fund_info(fund_symbol):
    """Get fund information from Morningstar"""
    try:
        fund_data = morningstar_scraper.get_fund_info(fund_symbol.upper())
        return jsonify(fund_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/etf-screener")
def get_etf_screener():
    """Get ETF screener data from Morningstar"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', 20, type=int)
        etf_data = morningstar_scraper.get_etf_screener(category=category, limit=limit)
        return jsonify(etf_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== STOCK SCREENING =====
@app.route("/api/stock-screener")
def get_stock_screener():
    """Get stock screener results from Finviz"""
    try:
        filters = request.args.to_dict()
        limit = request.args.get('limit', 50, type=int)
        
        # Remove non-filter parameters
        filters.pop('limit', None)
        
        screener_data = finviz_scraper.get_stock_screener(filters=filters, limit=limit)
        return jsonify(screener_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock-screener/seeking-alpha")
def get_seeking_alpha_screener():
    """Get stock screener results from Seeking Alpha"""
    try:
        criteria = request.args.to_dict()
        limit = request.args.get('limit', 20, type=int)
        
        # Remove non-criteria parameters
        criteria.pop('limit', None)
        
        screener_data = seeking_alpha_scraper.get_stock_screener(criteria=criteria, limit=limit)
        return jsonify(screener_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== EARNINGS DATA =====
@app.route("/api/earnings")
def earnings():
    """Return earnings calendar for the requested month (?month=YYYY-MM)."""
    month_str = request.args.get("month")  # e.g. "2025-09"
    try:
        year, month = map(int, month_str.split("-")) if month_str else (date.today().year, date.today().month)
    except Exception:
        year, month = date.today().year, date.today().month

    # last day of the month
    _, last_day = calendar.monthrange(year, month)

    def clamp_day(d):
        return min(max(1, d), last_day)

    # demo schedule (adjust to real data later)
    rows = [
        ("TSLA", "Tesla, Inc.", clamp_day(5),  "16:00", "https://logo.clearbit.com/tesla.com"),
        ("NVDA", "NVIDIA Corporation", clamp_day(12), "16:00", "https://logo.clearbit.com/nvidia.com"),
        ("AAPL", "Apple Inc.", clamp_day(15), "16:00", "https://logo.clearbit.com/apple.com"),
        ("GOOGL","Alphabet Inc.", clamp_day(22), "16:00", "https://logo.clearbit.com/abc.xyz"),
        ("AMZN", "Amazon.com, Inc.", clamp_day(26), "16:00", "https://logo.clearbit.com/amazon.com"),
    ]
    out = []
    for tkr, name, day, tm, logo in rows:
        ds = f"{year:04d}-{month:02d}-{day:02d}"
        out.append({"ticker": tkr, "name": name, "date": ds, "time": tm, "logoUrl": logo})
    return jsonify(out)

@app.route("/api/earnings-calendar")
def get_earnings_calendar():
    """Get earnings calendar from multiple sources"""
    try:
        date_str = request.args.get('date')
        earnings_data = data_aggregator.get_earnings_calendar(date=date_str)
        return jsonify(earnings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/earnings/<ticker>")
def get_stock_earnings(ticker):
    """Get earnings data for a specific stock from Seeking Alpha"""
    try:
        earnings_data = seeking_alpha_scraper.get_earnings_data(ticker.upper())
        return jsonify(earnings_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== DIVIDEND DATA =====
@app.route("/api/dividends/<ticker>")
def get_dividend_data(ticker):
    """Get dividend information from Seeking Alpha"""
    try:
        dividend_data = seeking_alpha_scraper.get_dividend_data(ticker.upper())
        return jsonify(dividend_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== INSIDER TRADING =====
@app.route("/api/insider-trading")
def get_insider_trading():
    """Get insider trading data from Finviz"""
    try:
        ticker = request.args.get('ticker')
        limit = request.args.get('limit', 20, type=int)
        insider_data = finviz_scraper.get_insider_trading(ticker=ticker, limit=limit)
        return jsonify(insider_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== PORTFOLIO ANALYSIS =====
@app.route("/api/portfolio/analyze", methods=["POST"])
def analyze_portfolio():
    """Analyze a portfolio of stocks using all data sources"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        
        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400
        
        portfolio_data = data_aggregator.get_portfolio_analysis(tickers)
        return jsonify(portfolio_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== DASHBOARD =====
@app.route("/api/dashboard")
def get_dashboard_data():
    """Get comprehensive dashboard data from all sources"""
    try:
        dashboard_data = data_aggregator.get_market_overview()
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== LEGACY ENDPOINTS =====
@app.route("/api/recommend", methods=["POST"])
def recommend():
    # Demo picks
    picks = [
        {
            "ticker": "EXAI",
            "name": "Example AI Chips Co.",
            "thesis": "Differentiated interconnect; capacity scaling; margin expansion.",
            "stats": {"P/E":"—","Rev 3yr CAGR":"78%","Gross Margin":"61%","Moat":"Scale + Ecosystem"}
        },
        {
            "ticker":"EVXP",
            "name":"EverExpand Motors",
            "thesis":"Software-led margins; charging optionality; near FCF+.",
            "stats":{"P/S":"9.2","Units YoY":"+46%","Cash":"$7.1B","Moat":"Vertical integration"}
        }
    ]
    return jsonify(picks)

# ===== SOURCE-SPECIFIC ENDPOINTS =====
@app.route("/api/sources/yahoo/<ticker>")
def get_yahoo_data(ticker):
    """Get data specifically from Yahoo Finance"""
    try:
        stock_data = yahoo_scraper.get_stock_info(ticker.upper())
        news_data = yahoo_scraper.get_stock_news(ticker.upper(), limit=5)
        
        return jsonify({
            'stock': stock_data,
            'news': news_data,
            'source': 'Yahoo Finance',
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sources/finviz/<ticker>")
def get_finviz_data(ticker):
    """Get data specifically from Finviz"""
    try:
        overview_data = finviz_scraper.get_stock_overview(ticker.upper())
        technical_data = finviz_scraper.get_technical_analysis(ticker.upper())
        news_data = finviz_scraper.get_news(ticker.upper(), limit=5)
        
        return jsonify({
            'overview': overview_data,
            'technical': technical_data,
            'news': news_data,
            'source': 'Finviz',
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sources/morningstar/<ticker>")
def get_morningstar_data(ticker):
    """Get data specifically from Morningstar"""
    try:
        analysis_data = morningstar_scraper.get_stock_analysis(ticker.upper())
        news_data = morningstar_scraper.get_market_news(limit=5)
        
        return jsonify({
            'analysis': analysis_data,
            'news': news_data,
            'source': 'Morningstar',
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sources/seeking-alpha/<ticker>")
def get_seeking_alpha_data(ticker):
    """Get data specifically from Seeking Alpha"""
    try:
        analysis_data = seeking_alpha_scraper.get_stock_analysis(ticker.upper())
        earnings_data = seeking_alpha_scraper.get_earnings_data(ticker.upper())
        dividend_data = seeking_alpha_scraper.get_dividend_data(ticker.upper())
        news_data = seeking_alpha_scraper.get_stock_news(ticker.upper(), limit=5)
        
        return jsonify({
            'analysis': analysis_data,
            'earnings': earnings_data,
            'dividends': dividend_data,
            'news': news_data,
            'source': 'Seeking Alpha',
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve static assets or SPA index.html
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return send_from_directory(app.static_folder, path)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5001, debug=True, host='0.0.0.0')
