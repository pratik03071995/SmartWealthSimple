from flask import Flask, send_from_directory, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime, date
import calendar
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import yfinance as yf
from scipy.stats import percentileofscore
from stock_scoring import score_stocks

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/health")
def health():
    return jsonify({"ok": True})

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

@app.get("/api/earnings")
def earnings():
    """Return mock earnings for the requested month (?month=YYYY-MM)."""
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

@app.route("/api/score-stocks", methods=["POST"])
def score_stocks_endpoint():
    """Score a list of stocks using our comprehensive scoring system"""
    try:
        data = request.get_json()
        tickers = data.get('tickers', [])
        manual_inputs = data.get('manual_inputs', {})
        
        if not tickers:
            return jsonify({"error": "No tickers provided"}), 400
        
        # Limit to prevent abuse
        if len(tickers) > 10:
            return jsonify({"error": "Maximum 10 stocks allowed per request"}), 400
        
        # Score the stocks
        results = score_stocks(tickers, manual_inputs)
        
        # Format for frontend
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

# Serve static assets or SPA index.html
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    static_path = os.path.join(app.static_folder, path)
    if path and os.path.exists(static_path):
        return send_from_directory(app.static_folder, path)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
