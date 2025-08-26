# app/app.py
# Updated for Railway deployment - Root directory: /app
from __future__ import annotations

import os
import re
import time
import threading
import json
from datetime import date, datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from urllib.parse import urlparse

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
from flask import Flask, send_from_directory, render_template, request, jsonify, Response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Note: NLTK data will be handled gracefully by the sentiment analyzer
from scrapers.yahoo_finance_scraper import YahooFinanceScraper
from scrapers.news_scraper import NewsScraper
from scrapers.morningstar_scraper import MorningstarScraper
from scrapers.seeking_alpha_scraper import SeekingAlphaScraper
from scrapers.finviz_scraper import FinvizScraper
from scrapers.data_aggregator import DataAggregator
from ai.sector_analyzer import SectorAnalyzer
from ai.stock_recommender import AIStockRecommender
from stock_scoring import score_stocks

# =========================
# Flask app
# =========================
app = Flask(__name__, static_folder="static", template_folder="templates")
# Configure CORS for production
allowed_origins = [
    "http://127.0.0.1:5001", "http://localhost:5001", 
    "http://127.0.0.1:5002", "http://localhost:5002", 
    "http://localhost:3000", "http://127.0.0.1:3000", 
    "http://localhost:5173", "http://127.0.0.1:5173",
    "https://smart-wealth-simple.vercel.app",  # Your Vercel domain
    "https://smart-wealth-simple-git-main-pratiks-projects.vercel.app"  # Alternative Vercel domain format
]

# Allow all origins in development, specific origins in production
if os.environ.get('FLASK_ENV') == 'production':
    CORS(app, origins=allowed_origins)
else:
    CORS(app, origins=["*"])

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

# =========================
# Constants / Logos
# =========================
CLEARBIT = "https://logo.clearbit.com/"

KNOWN_LOGOS: Dict[str, str] = {
    "AAPL": CLEARBIT + "apple.com",
    "MSFT": CLEARBIT + "microsoft.com",
    "AMZN": CLEARBIT + "amazon.com",
    "GOOGL": CLEARBIT + "abc.xyz",
    "META": CLEARBIT + "meta.com",
    "TSLA": CLEARBIT + "tesla.com",
    "NVDA": CLEARBIT + "nvidia.com",
    "BRK-B": CLEARBIT + "berkshirehathaway.com",
    "BRK.B": CLEARBIT + "berkshirehathaway.com",
    "WMT": CLEARBIT + "walmart.com",
    "XOM": CLEARBIT + "exxonmobil.com",
    "CVX": CLEARBIT + "chevron.com",
    "JPM": CLEARBIT + "jpmorganchase.com",
    "V": CLEARBIT + "visa.com",
    "MA": CLEARBIT + "mastercard.com",
    "UNH": CLEARBIT + "uhc.com",
}

# ========= Your static ~200 universe (from your test) =========
TOP200_TICKERS_RAW = [
    "WMT","AMZN","AAPL","UNH","BRK-B","CVS","XOM","GOOGL","MCK","CNC",
    "COST","JPM","MSFT","CAH","CVX","CI","F","BAC","GM","ELV","C","HD",
    "MPC","KR","PSX","WBA","VZ","T","CMCSA","WFC","GS","TGT","HUM","TSLA",
    "MS","JNJ","ADM","PEP","UPS","FDX","DIS","DELL","LOW","PG","ET","BA",
    "ACI","SYY","RTX","GE","LMT","AXP","CAT","MET","HCA","PGR","IBM","DE",
    "NVDA","COF","MRK","COP","PFE","DAL","SNX","ALL","CSCO","CHTR","ABBV",
    "INTC","TJX","PRU","HPQ","UAL","PFGC","TSN","AAL","NKE","ORCL","EPD",
    "PAA","AIG","KO","DUK","SO","NEE","EXC","D","AEP","SRE","XEL","LUV",
    "NOC","GD","ETN","EMR","ITW","PH","ROK","MMM","SHW","LIN","APD","NUE",
    "STLD","FCX","MOS","CF","KHC","GIS","CL","KMB","HSY","MKC","STZ","DG",
    "DLTR","YUM","CMG","MCD","SBUX","BKNG","MAR","HLT","LVS","WYNN","RCL",
    "NCLH","CCL","EBAY","PYPL","V","MA","SCHW","BK","STT","USB","PNC","TFC",
    "KEY","FITB"
]

# Remaps / drops (from your test)
REMAP = { "PX":"LIN", "ETP":"ET" }
DROP  = set(["TWTR","SAP","BABA","CNQ","TD","TM","HMC","NSANY","BYDDF"])

def normalize_ticker(t: str) -> Optional[str]:
    if not isinstance(t, str): return None
    t = t.strip().upper()
    t = t.replace(".", "-")                 # Yahoo prefers '-'
    t = REMAP.get(t, t)
    if t in DROP: return None
    t = re.sub(r"[^A-Z0-9\-=]", "", t)
    return t or None

# Clean + dedupe your universe
CLEAN_TICKERS: List[str] = sorted({ nt for t in TOP200_TICKERS_RAW if (nt := normalize_ticker(t)) })

# =========================
# Cache
# =========================
CACHE_LOCK = threading.Lock()
EARNINGS_CACHE: Dict[str, Any] = {
    "events": [],         # [{"ticker","name","date","time","logoUrl","epsEstimate","epsReported","surprisePct"}]
    "meta": {},           # {ticker: {"name": "...", "logoUrl": "..."}}
    "updated_at": 0.0,    # epoch seconds
    "ttl_sec": 6 * 3600,  # 6 hours
}

# =========================
# Helpers matching your test code
# =========================
def first_scalar(x):
    if x is None: return None
    if isinstance(x, dict):            return first_scalar(next(iter(x.values()), None))
    if isinstance(x, (pd.Series, pd.Index, pd.DatetimeIndex)):
        return first_scalar(x[0] if len(x) else None)
    if isinstance(x, (list, tuple, set)):
        return first_scalar(next(iter(x), None))
    return x

def to_ts(x):
    return pd.to_datetime(first_scalar(x), errors="coerce")

def to_num(x):
    return pd.to_numeric(first_scalar(x), errors="coerce")

def _month_window(months_ahead: int = 6) -> tuple[date, date]:
    today = date.today()
    end = today + relativedelta(months=+months_ahead)
    return today, end

def _registered_domain(host: str) -> Optional[str]:
    if not host: return None
    host = host.lower().strip()
    if host.startswith("www."): host = host[4:]
    for pre in ("investor.", "ir."):
        if host.startswith(pre): host = host[len(pre):]
    parts = host.split(":")[0].split(".")
    if len(parts) >= 2: return ".".join(parts[-2:])
    return host

def _domain_from_website(website: Optional[str]) -> Optional[str]:
    if not website or not isinstance(website, str): return None
    w = website.strip()
    if not w: return None
    if not w.startswith("http"): w = "https://" + w
    try:
        parsed = urlparse(w)
        return _registered_domain(parsed.netloc or parsed.path)
    except Exception:
        return None

# =========================
# Meta (name + logo) cache
# =========================
def _get_meta(ticker: str) -> Dict[str, Optional[str]]:
    """
    Resolve company name and logoUrl for ticker (cached).
    Uses KNOWN_LOGOS first, then yfinance get_info().Website -> Clearbit.
    """
    with CACHE_LOCK:
        m = EARNINGS_CACHE["meta"].get(ticker)
        if m: return m

    name = ticker
    logo = KNOWN_LOGOS.get(ticker) or KNOWN_LOGOS.get(ticker.replace("-", "."))

    # If missing, try yfinance info
    if not logo or name == ticker:
        try:
            info = yf.Ticker(ticker).get_info()
            # name
            name = info.get("shortName") or info.get("longName") or name
            # logo
            if not logo:
                website = info.get("website") or info.get("Website")
                domain = _domain_from_website(website)
                if domain:
                    logo = CLEARBIT + domain
        except Exception:
            pass

    meta = {"name": name, "logoUrl": logo}
    with CACHE_LOCK:
        EARNINGS_CACHE["meta"][ticker] = meta
    return meta

# =========================
# Earnings fetch (your calendar-based approach)
# =========================
def _fetch_calendar_for_one(sym: str) -> Dict[str, Any]:
    """
    Return normalized single-row dict for one ticker from Ticker.calendar.
    """
    try:
        cal = yf.Ticker(sym).calendar
        cal_dict = cal.to_dict() if hasattr(cal, "to_dict") else (cal if isinstance(cal, dict) else {})
        return {
            "symbol": sym,
            "earnings_date": to_ts(cal_dict.get("Earnings Date")),
            "eps_avg": to_num(cal_dict.get("Earnings Average")),
            "eps_low": to_num(cal_dict.get("Earnings Low")),
            "eps_high": to_num(cal_dict.get("Earnings High")),
            "error": None
        }
    except Exception as e:
        return {"symbol": sym, "earnings_date": pd.NaT, "eps_avg": pd.NA, "eps_low": pd.NA, "eps_high": pd.NA, "error": str(e)}

def _build_events_from_calendar(months_ahead: int = 6) -> List[Dict[str, Any]]:
    """
    Sequential (safer for Yahoo throttling) build using your tested logic.
    Keeps only FUTURE dates within next `months_ahead`.
    """
    rows = [_fetch_calendar_for_one(sym) for sym in CLEAN_TICKERS]
    df_all = pd.DataFrame(rows)

    # Filter to future dates only
    today = pd.Timestamp.today().normalize()
    df = df_all[df_all["earnings_date"].notna()].copy()
    df = df[df["earnings_date"] >= today].copy()

    # Limit to the next N months
    end_dt = pd.Timestamp((_month_window(months_ahead)[1]).isoformat())
    df = df[df["earnings_date"] <= end_dt].copy()

    # Sort and shape
    df = df.sort_values(["earnings_date", "symbol"]).reset_index(drop=True)
    events: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        tk = str(r["symbol"])
        dt: pd.Timestamp = r["earnings_date"]
        meta = _get_meta(tk)

        events.append({
            "ticker": tk,
            "name": meta["name"] or tk,
            "date": dt.strftime("%Y-%m-%d"),
            "time": None,                         # not provided by calendar reliably
            "logoUrl": meta["logoUrl"],
            "epsEstimate": (float(r["eps_avg"]) if pd.notna(r["eps_avg"]) else None),
            "epsReported": None,
            "surprisePct": None,
        })
    return events

def _ensure_cache(force: bool = False, months_ahead: int = 6):
    with CACHE_LOCK:
        now = time.time()
        ttl = EARNINGS_CACHE.get("ttl_sec", 6*3600)
        if not force and EARNINGS_CACHE["events"] and (now - EARNINGS_CACHE["updated_at"] < ttl):
            return
    # build outside the lock
    events = _build_events_from_calendar(months_ahead=months_ahead)
    with CACHE_LOCK:
        EARNINGS_CACHE["events"] = events
        EARNINGS_CACHE["updated_at"] = time.time()

# =========================
# Health
# =========================
@app.route("/health")
def health():
    return jsonify({"ok": True, "time": datetime.utcnow().isoformat() + "Z"})

# =========================
# Demo recommend endpoint (unchanged)
# =========================
@app.route("/api/recommend", methods=["POST"])
def recommend():
    picks = [
        {
            "ticker": "EXAI",
            "name": "Example AI Chips Co.",
            "thesis": "Differentiated interconnect; capacity scaling; margin expansion.",
            "stats": {"P/E": "—", "Rev 3yr CAGR": "78%", "Gross Margin": "61%", "Moat": "Scale + Ecosystem"},
        },
        {
            "ticker": "EVXP",
            "name": "EverExpand Motors",
            "thesis": "Software-led margins; charging optionality; near FCF+.",
            "stats": {"P/S": "9.2", "Units YoY": "+46%", "Cash": "$7.1B", "Moat": "Vertical integration"},
        },
    ]
    return jsonify(picks)

# =========================
# Monthly endpoint (same signature)
# =========================
@app.get("/api/earnings")
def earnings_month():
    """
    Returns earnings events for the requested month (?month=YYYY-MM)
    from the cached window (default 6 months).
    Optional: ?force=1 to rebuild cache now.
    """
    force = request.args.get("force") == "1"
    _ensure_cache(force=force, months_ahead=6)

    month_str = request.args.get("month")  # e.g. "2025-09"
    if month_str:
        try:
            y, m = map(int, month_str.split("-"))
        except Exception:
            today = date.today()
            y, m = today.year, today.month
    else:
        today = date.today()
        y, m = today.year, today.month

    with CACHE_LOCK:
        src = list(EARNINGS_CACHE["events"])

    out = []
    for ev in src:
        try:
            yy, mm, _dd = map(int, ev["date"].split("-"))
            if yy == y and mm == m:
                out.append(ev)
        except Exception:
            continue

    out.sort(key=lambda e: (e["date"], e["ticker"]))
    return jsonify(out)

# =========================
# Weekly endpoint (same signature)
# =========================
@app.get("/api/earnings_week")
def earnings_week():
    """
    Returns earnings events for a 7-day window starting at ?start=YYYY-MM-DD.
    Optional: ?force=1 to rebuild cache now.
    """
    force = request.args.get("force") == "1"
    _ensure_cache(force=force, months_ahead=6)

    start_str = request.args.get("start")
    if start_str:
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
        except Exception:
            start = date.today()
    else:
        today = date.today()
        days_since_sun = (today.weekday() + 1) % 7  # Mon=0..Sun=6 -> days since Sunday
        start = today - timedelta(days=days_since_sun)

    end = start + timedelta(days=6)

    with CACHE_LOCK:
        src = list(EARNINGS_CACHE["events"])

    out = []
    for ev in src:
        try:
            d = datetime.strptime(ev["date"], "%Y-%m-%d").date()
            if start <= d <= end:
                out.append(ev)
        except Exception:
            continue

    out.sort(key=lambda e: (e["date"], e["ticker"]))
    return jsonify(out)

# =========================
# Top companies + logos (from your static list)
# =========================
@app.get("/api/top_companies")
def top_companies():
    # ensure meta gets filled lazily once
    for tk in CLEAN_TICKERS[:200]:
        _get_meta(tk)
    with CACHE_LOCK:
        out = [
            {"ticker": tk, "name": EARNINGS_CACHE["meta"].get(tk, {}).get("name") or tk,
             "logoUrl": EARNINGS_CACHE["meta"].get(tk, {}).get("logoUrl") or KNOWN_LOGOS.get(tk)}
            for tk in CLEAN_TICKERS[:200]
        ]
    return jsonify(out)

# --- Add this to app/app.py ---
@app.get("/api/earnings_detail")
def earnings_detail():
    """
    Per-ticker detail for the modal bubble.
    Returns last reported EPS (and surprise%), upcoming EPS estimate, plus short history.
    """
    ticker = request.args.get("ticker", "").strip()
    if not ticker:
        return jsonify({"error": "missing ticker"}), 400

    tkr = normalize_ticker(ticker) or ticker.upper()
    try:
        meta = _get_meta(tkr)  # name + logoUrl (cached)
    except Exception:
        meta = {"name": tkr, "logoUrl": KNOWN_LOGOS.get(tkr)}

    out = {
        "ticker": tkr,
        "name": meta.get("name") or tkr,
        "logoUrl": meta.get("logoUrl"),
        "last": None,
        "next": None,
        "history": [],
    }

    try:
        t = yf.Ticker(tkr)

        # (1) Next earnings + EPS range via calendar
        cal = t.calendar
        cal_dict = cal.to_dict() if hasattr(cal, "to_dict") else (cal if isinstance(cal, dict) else {})
        next_dt = to_ts(cal_dict.get("Earnings Date"))
        if pd.notna(next_dt):
            out["next"] = {
                "date": next_dt.strftime("%Y-%m-%d"),
                "time": None,  # yfinance calendar rarely includes a reliable BMO/AMC
                "epsEstimate": (float(to_num(cal_dict.get("Earnings Average"))) 
                                if pd.notna(to_num(cal_dict.get("Earnings Average"))) else None),
                "low": (float(to_num(cal_dict.get("Earnings Low"))) 
                        if pd.notna(to_num(cal_dict.get("Earnings Low"))) else None),
                "high": (float(to_num(cal_dict.get("Earnings High"))) 
                         if pd.notna(to_num(cal_dict.get("Earnings High"))) else None),
            }

        # (2) Rich history (reported/estimate/surprise/time) via get_earnings_dates
        df = None
        try:
            df = t.get_earnings_dates(limit=16)
        except Exception:
            df = None

        today = pd.Timestamp.today().normalize()
        if isinstance(df, pd.DataFrame) and not df.empty:
            rows = []
            for idx, sr in df.iterrows():
                dt = sr["Earnings Date"] if "Earnings Date" in df.columns else idx
                if pd.isna(dt):
                    continue
                dt = dt if isinstance(dt, pd.Timestamp) else pd.to_datetime(dt, errors="coerce")
                if pd.isna(dt):
                    continue
                def g(key_alt1, key_alt2=None):
                    if key_alt1 in sr: return sr[key_alt1]
                    if key_alt2 and key_alt2 in sr: return sr[key_alt2]
                    return None
                rows.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "time": (str(g("Time", "Time (ET)")).upper() 
                             if g("Time", "Time (ET)") is not None and pd.notna(g("Time", "Time (ET)")) else None),
                    "epsEstimate": (float(g("EPS Estimate")) if g("EPS Estimate") is not None and pd.notna(g("EPS Estimate")) else None),
                    "epsReported": (float(g("Reported EPS")) if g("Reported EPS") is not None and pd.notna(g("Reported EPS")) else None),
                    "surprisePct": (float(str(g("Surprise(%)") if "Surprise(%)" in sr else g("Surprise %")).replace("%",""))
                                   if (g("Surprise(%)") is not None or g("Surprise %") is not None) and pd.notna(g("Surprise(%)") if "Surprise(%)" in sr else g("Surprise %"))
                                   else None),
                })

            # sort newest→oldest
            rows.sort(key=lambda r: r["date"], reverse=True)
            out["history"] = rows[:8]  # keep last ~8 points

            # last past quarter
            past = [r for r in rows if pd.to_datetime(r["date"]) <= today]
            if past:
                out["last"] = past[0]

            # ensure "next" is present even if calendar missing: find first future row
            if out["next"] is None:
                future = [r for r in rows if pd.to_datetime(r["date"]) >= today]
                if future:
                    out["next"] = {
                        "date": future[-1]["date"],  # earliest future
                        "time": future[-1]["time"],
                        "epsEstimate": future[-1]["epsEstimate"],
                        "low": None, "high": None
                    }

    except Exception:
        pass

    return jsonify(out)

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
        sector_info = sector_analyzer.get_sector_info(sector_name)
        if not sector_info:
            return jsonify({"error": f"Sector '{sector_name}' not found"}), 404
        
        return jsonify({
            'sector': sector_name,
            'info': sector_info,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/sectors/<sector_name>/subsectors")
def get_sector_subsectors(sector_name):
    """Get all subsectors for a specific sector"""
    try:
        subsectors = sector_analyzer.get_subsectors(sector_name)
        if subsectors is None:
            return jsonify({"error": f"Sector '{sector_name}' not found"}), 404
        
        return jsonify({
            'sector': sector_name,
            'subsectors': subsectors,
            'subsector_count': len(subsectors),
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/recommend", methods=["POST"])
def get_ai_recommendations():
    """Get AI-powered stock recommendations based on sector analysis"""
    try:
        data = request.get_json()
        sectors = data.get('sectors', [])
        subsectors = data.get('subsectors', [])
        risk_tolerance = data.get('risk_tolerance', 'medium')
        investment_horizon = data.get('investment_horizon', 'medium')
        
        if not sectors and not subsectors:
            return jsonify({"error": "At least one sector or subsector must be specified"}), 400
        
        recommendations = ai_recommender.get_recommendations(
            sectors=sectors,
            subsectors=subsectors,
            risk_tolerance=risk_tolerance,
            investment_horizon=investment_horizon
        )
        
        return jsonify({
            'recommendations': recommendations,
            'filters': {
                'sectors': sectors,
                'subsectors': subsectors,
                'risk_tolerance': risk_tolerance,
                'investment_horizon': investment_horizon
            },
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== DYNAMIC COMPANY FETCHING ENDPOINTS =====
@app.route("/api/companies/dynamic", methods=["POST"])
def get_companies_dynamic():
    """Get companies dynamically based on sector/subsector using Yahoo Finance screeners with streaming response"""
    try:
        data = request.get_json()
        sectors = data.get('sectors', [])
        subsectors = data.get('subsectors', [])
        limit = data.get('limit', 50)
        streaming = data.get('streaming', True)  # Default to streaming
        
        if not sectors and not subsectors:
            return jsonify({"error": "At least one sector or subsector must be specified"}), 400
        
        if streaming:
            # Return streaming response
            def generate():
                try:
                    # Send initial status
                    yield f"data: {json.dumps({'status': 'started', 'message': 'Starting company discovery...'})}\n\n"
                    
                    # Create a generator that yields companies as they're processed
                    def company_generator():
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
                            
                            # Consumer Cyclical subsectors - Use consumer-specific screeners
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
                                        sector_tickers = yahoo_scraper._scrape_screener_tickers(screener_urls[sector])
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
                                        subsector_tickers = yahoo_scraper._scrape_screener_tickers(industry_screener_urls[subsector])
                                        print(f"Found {len(subsector_tickers)} tickers for {subsector}")
                                        all_tickers.update(subsector_tickers)
                                    except Exception as e:
                                        print(f"Error scraping {subsector}: {e}")
                                        continue
                                else:
                                    try:
                                        print(f"Trying general approach for subsector: {subsector}")
                                        general_tickers = yahoo_scraper._scrape_industry_tickers(subsector.lower())
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
                                    fallback_tickers = yahoo_scraper._scrape_screener_tickers(url)
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
                                additional_tickers = yahoo_scraper._get_additional_tickers_from_sources(sector)
                                all_tickers.update(additional_tickers)
                                print(f"Added {len(additional_tickers)} additional tickers for {sector}")
                            
                        if subsectors:
                            for subsector in subsectors:
                                additional_tickers = yahoo_scraper._get_additional_tickers_from_sources(subsector)
                                all_tickers.update(additional_tickers)
                                print(f"Added {len(additional_tickers)} additional tickers for {subsector}")
                            
                        print(f"Total unique tickers found: {len(all_tickers)}")
                        
                        # Get stock data for collected tickers with streaming
                        ticker_list = list(all_tickers)[:limit * 30]  # Process even more tickers to ensure we get enough valid companies
                        processed_count = 0
                        valid_companies_count = 0
                        
                        print(f"Processing {len(ticker_list)} tickers to find {limit} companies...")
                        print(f"Total unique tickers found: {len(all_tickers)}")
                        
                        for ticker in ticker_list:
                            try:
                                stock_data = yahoo_scraper.get_stock_info(ticker)
                                # Be less restrictive - accept companies with any market cap > 0
                                if 'error' not in stock_data and stock_data.get('market_cap', 0) > 0:
                                    # More lenient sector filtering - include companies that match or are closely related
                                    if sectors and stock_data.get('sector'):
                                        stock_sector = stock_data.get('sector', '').lower()
                                        requested_sectors = [s.lower() for s in sectors]
                                        
                                        sector_match = False
                                        for requested_sector in requested_sectors:
                                            # More flexible matching - check for partial matches and related sectors
                                            if (requested_sector in stock_sector or 
                                                stock_sector in requested_sector or
                                                yahoo_scraper._sectors_are_related(requested_sector, stock_sector)):
                                                sector_match = True
                                                break
                                        
                                        # If no sector match, still include the company but log it
                                        if not sector_match:
                                            print(f"Warning: Including {ticker} with sector '{stock_data.get('sector')}' despite not matching requested sectors: {sectors}")
                                            # Don't skip - include anyway for now
                                    else:
                                        # No sector filtering requested, include all
                                        pass
                                    
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
                                    
                                    # companies.append(company_data) # No longer append to local list, yield directly
                                    processed_count += 1
                                    valid_companies_count += 1
                                    
                                    print(f"Added company {valid_companies_count}: {ticker} - ${company_data['current_price']:.2f} ({stock_data.get('sector', 'Unknown')})")
                                    
                                    # Yield the company data for streaming
                                    yield company_data
                                    
                                    # Stop if we've reached the limit
                                    if valid_companies_count >= limit:
                                        print(f"Reached limit of {limit} companies, stopping processing")
                                        break
                                        
                            except Exception as e:
                                print(f"Error getting data for {ticker}: {e}")
                                continue  # Skip tickers that fail
                        
                        print(f"Total valid companies found: {valid_companies_count}")
                    
                    # Process companies and yield them as they're found
                    companies_found = []
                    for company in company_generator():
                        companies_found.append(company)
                        yield f"data: {json.dumps({'status': 'progress', 'company': company, 'index': len(companies_found), 'total': limit})}\n\n"
                    
                    # Send completion status
                    yield f"data: {json.dumps({'status': 'completed', 'companies': companies_found, 'total': len(companies_found)})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        else:
            # Return regular response
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

# =========================
# AI Sectors Endpoint
# =========================
@app.route("/api/ai/sectors", methods=["GET"])
def get_sectors():
    """Get available sectors for analysis"""
    sectors = [
        {
            "name": "Technology",
            "description": "Software, hardware, semiconductors, and digital services",
            "growth_potential": "High",
            "risk_level": "Medium",
            "subsector_count": 10,
            "key_drivers": ["Digital transformation", "AI/ML adoption", "Cloud migration"]
        },
        {
            "name": "Healthcare",
            "description": "Pharmaceuticals, biotechnology, medical devices",
            "growth_potential": "High",
            "risk_level": "High",
            "subsector_count": 8,
            "key_drivers": ["Aging population", "Medical innovation", "Healthcare digitization"]
        },
        {
            "name": "Financial Services",
            "description": "Banks, insurance, fintech, and investment services",
            "growth_potential": "Medium",
            "risk_level": "Medium",
            "subsector_count": 6,
            "key_drivers": ["Digital banking", "Regulatory changes", "Interest rate environment"]
        },
        {
            "name": "Consumer Discretionary",
            "description": "Retail, automotive, entertainment, and luxury goods",
            "growth_potential": "Medium",
            "risk_level": "Medium",
            "subsector_count": 7,
            "key_drivers": ["Consumer spending", "E-commerce growth", "Brand loyalty"]
        },
        {
            "name": "Energy",
            "description": "Oil & gas, renewable energy, and utilities",
            "growth_potential": "Low",
            "risk_level": "High",
            "subsector_count": 5,
            "key_drivers": ["Energy transition", "Geopolitical factors", "Climate policies"]
        }
    ]
    return jsonify({"sectors": sectors})



# =========================
# Stock Scoring Endpoint
# =========================
@app.route("/api/score-stocks", methods=["POST"])
def score_stocks_endpoint():
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        manual_inputs = data.get('manual_inputs', {})
        
        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400
        
        if len(tickers) > 10:
            return jsonify({"error": "Maximum 10 stocks allowed per request"}), 400
        
        results = score_stocks(tickers, manual_inputs)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "ticker": result["ticker"],
                "name": result["company_info"]["name"],
                "sector": result["company_info"]["sector"],
                "industry": result["company_info"]["industry"],
                "marketCap": result["company_info"]["market_cap"],
                "totalScore": result["total_score"],
                "grade": result["grade"],
                "scores": result["scores"],
                "details": result["details"],
                "weights": result["weights"]
            })
        
        return jsonify(formatted_results)
        
    except Exception as e:
        return jsonify({"error": f"Scoring error: {str(e)}"}), 500

# =========================
# Serve SPA
# =========================
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    # Don't serve frontend for API routes
    if path.startswith("api/"):
        return jsonify({"error": "API endpoint not found"}), 404
    
    # Don't serve frontend for docs route
    if path.startswith("docs"):
        return jsonify({"error": "Documentation endpoint not found"}), 404
    
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return send_from_directory(app.static_folder, path)
    return render_template("index.html")

# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    def _warm():
        try:
            _ensure_cache(force=True)
        except Exception:
            pass
    threading.Thread(target=_warm, daemon=True).start()
    app.run(port=5000, debug=True, host='0.0.0.0')
