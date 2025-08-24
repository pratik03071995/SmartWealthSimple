# app/app.py
from __future__ import annotations

import os
import re
import time
import threading
from datetime import date, datetime, timedelta
from typing import List, Tuple, Dict, Any, Optional
from urllib.parse import urlparse

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta
from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS

# =========================
# Flask app
# =========================
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

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

# =========================
# Serve SPA
# =========================
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
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
    app.run(port=5000, debug=True)
