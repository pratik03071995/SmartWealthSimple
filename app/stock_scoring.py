"""
Stock Scoring System for Financial Advisory
Based on 12 comprehensive criteria groups with weighted scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
import yfinance as yf
from scipy.stats import percentileofscore
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class StockScorer:
    """
    Comprehensive stock scoring system based on financial advisor criteria
    """
    
    def __init__(self):
        self.criteria_weights = {
            'business_fundamentals': 0.35,
            'competitive_advantage': 0.15,
            'management_quality': 0.10,
            'industry_attributes': 0.10,
            'valuation_metrics': 0.10,
            'growth_catalysts': 0.05,
            'risks_red_flags': -0.10,  # Penalty
            'macro_sensitivity': 0.05,
            'market_sentiment': 0.05,
            'vendors_supply_chain': 0.03,
            'innovation_rd': 0.07,
            'global_trends_alignment': 0.05
        }
        
        self.sub_criteria_weights = {
            'business_fundamentals': {
                'revenue_cagr_5y': 0.10,
                'eps_growth_5y': 0.07,
                'margins_trend': 0.06,
                'roe_roce': 0.06,
                'free_cash_flow': 0.06
            }
        }
    
    def get_financial_data(self, ticker: str) -> Dict:
        """
        Fetch financial data using yfinance
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            return {
                'info': info,
                'financials': financials,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'history': stock.history(period="5y")
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return {}
    
    def calculate_cagr(self, start_value: float, end_value: float, years: int) -> float:
        """Calculate Compound Annual Growth Rate"""
        if start_value <= 0 or end_value <= 0 or years <= 0:
            return 0
        return ((end_value / start_value) ** (1/years) - 1) * 100
    
    def safe_divide(self, numerator: float, denominator: float) -> float:
        """Safe division with zero handling"""
        return numerator / denominator if denominator != 0 else 0
    
    def normalize_score(self, value: float, min_val: float, max_val: float, reverse: bool = False) -> float:
        """Normalize score to 0-100 scale"""
        if max_val == min_val:
            return 50
        
        normalized = (value - min_val) / (max_val - min_val) * 100
        if reverse:
            normalized = 100 - normalized
        
        return max(0, min(100, normalized))
    
    def score_business_fundamentals(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score business fundamentals (35% weight)
        """
        scores = {}
        details = {}
        
        try:
            financials = data.get('financials', pd.DataFrame())
            info = data.get('info', {})
            
            # Revenue CAGR (5y) - 10% (try multiple revenue field names)
            revenue_found = False
            revenue_alternatives = ['Total Revenue', 'Revenue', 'Net Revenue', 'Total Revenues', 'Operating Revenue']
            
            for revenue_field in revenue_alternatives:
                if not financials.empty and revenue_field in financials.index:
                    revenues = financials.loc[revenue_field].dropna()
                    if len(revenues) >= 2:
                        start_revenue = revenues.iloc[-1]
                        end_revenue = revenues.iloc[0]
                        years = len(revenues) - 1
                        revenue_cagr = self.calculate_cagr(start_revenue, end_revenue, years)
                        scores['revenue_cagr'] = self.normalize_score(revenue_cagr, 0, 30)
                        details['revenue_cagr'] = f"{revenue_cagr:.1f}% (from {revenue_field})"
                        revenue_found = True
                        break
            
            if not revenue_found:
                # Fallback to info revenue growth if available
                revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
                if revenue_growth > 0:
                    scores['revenue_cagr'] = self.normalize_score(revenue_growth, 0, 30)
                    details['revenue_cagr'] = f"{revenue_growth:.1f}% (1yr growth fallback)"
                else:
                    scores['revenue_cagr'] = 50
                    details['revenue_cagr'] = "N/A"
            
            # EPS Growth (5y) - 7%
            eps_growth = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
            scores['eps_growth'] = self.normalize_score(eps_growth, -20, 50)
            details['eps_growth'] = f"{eps_growth:.1f}%"
            
            # Margins (Gross & Operating trend) - 6%
            gross_margin = info.get('grossMargins', 0) * 100 if info.get('grossMargins') else 0
            operating_margin = info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0
            avg_margin = (gross_margin + operating_margin) / 2
            scores['margins'] = self.normalize_score(avg_margin, 0, 50)
            details['margins'] = f"Gross: {gross_margin:.1f}%, Operating: {operating_margin:.1f}%"
            
            # ROE & ROCE - 6% (try multiple field names for ROCE)
            roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
            
            # Try multiple ROCE alternatives
            roce_raw = (
                info.get('returnOnCapital') or 
                info.get('returnOnInvestedCapital') or 
                info.get('returnOnAssets') or 0
            )
            roce = roce_raw * 100 if roce_raw else 0
            
            avg_return = (roe + roce) / 2
            scores['roe_roce'] = self.normalize_score(avg_return, 0, 30)
            details['roe_roce'] = f"ROE: {roe:.1f}%, ROCE: {roce:.1f}%"
            
            # Free Cash Flow Generation - 6%
            fcf = info.get('freeCashflow', 0)
            market_cap = info.get('marketCap', 1)
            fcf_yield = (fcf / market_cap * 100) if market_cap > 0 else 0
            scores['fcf'] = self.normalize_score(fcf_yield, -5, 15)
            details['fcf'] = f"FCF Yield: {fcf_yield:.1f}%"
            
        except Exception as e:
            print(f"Error in business fundamentals scoring: {e}")
            scores = {k: 50 for k in ['revenue_cagr', 'eps_growth', 'margins', 'roe_roce', 'fcf']}
            details = {k: "Error" for k in scores.keys()}
        
        # Weighted average
        weights = [0.10, 0.07, 0.06, 0.06, 0.06]
        total_weight = sum(weights)
        weighted_score = sum(scores[k] * w for k, w in zip(scores.keys(), weights)) / total_weight
        
        return weighted_score, details
    
    def score_competitive_advantage(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score competitive advantage/moat (15% weight)
        Note: This requires manual inputs for qualitative assessment
        """
        details = {}
        
        if manual_inputs and 'competitive_advantage' in manual_inputs:
            # Manual scoring based on patents, IP, switching costs, scale, brand
            moat_score = manual_inputs['competitive_advantage'].get('moat_strength', 50)
            details['moat_assessment'] = manual_inputs['competitive_advantage'].get('description', 'Manual assessment required')
        else:
            # Basic approximation using market position metrics
            info = data.get('info', {})
            market_cap = info.get('marketCap', 0)
            
            # Larger companies often have stronger moats
            if market_cap > 100e9:  # >$100B
                moat_score = 80
            elif market_cap > 10e9:  # >$10B
                moat_score = 65
            elif market_cap > 1e9:   # >$1B
                moat_score = 50
            else:
                moat_score = 35
            
            details['moat_assessment'] = f"Market cap based assessment: ${market_cap/1e9:.1f}B"
        
        return moat_score, details
    
    def score_management_quality(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score management quality (10% weight)
        """
        details = {}
        
        if manual_inputs and 'management_quality' in manual_inputs:
            score = manual_inputs['management_quality'].get('score', 50)
            details['assessment'] = manual_inputs['management_quality'].get('description', 'Manual assessment')
        else:
            # Basic metrics from available data
            info = data.get('info', {})
            
            # Insider ownership - try multiple field names
            insider_ownership = (
                info.get('heldPercentInsiders', 0) or 
                info.get('heldByInsiders', 0) or 0
            ) * 100
            
            # Company age (approximation) - try multiple field names
            founded_year = (
                info.get('foundedYear') or 
                info.get('incorporatedYear') or 
                info.get('foundingDate') or 2000
            )
            company_age = datetime.now().year - founded_year
            
            # Scoring based on available metrics
            insider_score = self.normalize_score(insider_ownership, 0, 20)
            age_score = self.normalize_score(company_age, 0, 50)
            
            score = (insider_score + age_score) / 2
            details['assessment'] = f"Insider ownership: {insider_ownership:.1f}%, Age: {company_age} years"
        
        return score, details
    
    def score_industry_attributes(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score industry attributes (10% weight)
        """
        details = {}
        
        if manual_inputs and 'industry_attributes' in manual_inputs:
            score = manual_inputs['industry_attributes'].get('score', 50)
            details['assessment'] = manual_inputs['industry_attributes'].get('description', 'Manual assessment')
        else:
            info = data.get('info', {})
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # High-growth sectors scoring
            growth_sectors = ['Technology', 'Healthcare', 'Consumer Cyclical', 'Communication Services']
            growth_industries = ['Semiconductors', 'Software', 'Biotechnology', 'Electric Vehicles', 'Renewable Energy']
            
            sector_score = 70 if sector in growth_sectors else 40
            industry_score = 80 if any(gi in industry for gi in growth_industries) else 45
            
            score = (sector_score + industry_score) / 2
            details['assessment'] = f"Sector: {sector}, Industry: {industry}"
        
        return score, details
    
    def score_valuation_metrics(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score valuation metrics (10% weight)
        """
        details = {}
        info = data.get('info', {})
        
        try:
            # P/E Ratio
            pe_ratio = info.get('trailingPE', 0)
            pe_score = self.normalize_score(pe_ratio, 5, 30, reverse=True) if pe_ratio > 0 else 50
            
            # PEG Ratio - try multiple field names
            peg_ratio = (
                info.get('pegRatio') or 
                info.get('trailingPegRatio') or 
                info.get('forwardPegRatio') or 0
            )
            peg_score = self.normalize_score(peg_ratio, 0.5, 2.0, reverse=True) if peg_ratio > 0 else 50
            
            # EV/EBITDA
            ev_ebitda = info.get('enterpriseToEbitda', 0)
            ev_score = self.normalize_score(ev_ebitda, 5, 25, reverse=True) if ev_ebitda > 0 else 50
            
            # Price to Book
            pb_ratio = info.get('priceToBook', 0)
            pb_score = self.normalize_score(pb_ratio, 1, 5, reverse=True) if pb_ratio > 0 else 50
            
            valuation_score = (pe_score + peg_score + ev_score + pb_score) / 4
            
            details['valuation'] = f"P/E: {pe_ratio:.1f}, PEG: {peg_ratio:.2f}, EV/EBITDA: {ev_ebitda:.1f}, P/B: {pb_ratio:.2f}"
            
        except Exception as e:
            print(f"Error in valuation scoring: {e}")
            valuation_score = 50
            details['valuation'] = "Error in calculation"
        
        return valuation_score, details
    
    def score_growth_catalysts(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score growth catalysts (5% weight)
        """
        details = {}
        
        if manual_inputs and 'growth_catalysts' in manual_inputs:
            score = manual_inputs['growth_catalysts'].get('score', 50)
            details['catalysts'] = manual_inputs['growth_catalysts'].get('description', 'Manual assessment')
        else:
            # Basic approximation using growth metrics
            info = data.get('info', {})
            revenue_growth = info.get('revenueGrowth', 0) * 100
            
            if revenue_growth > 20:
                score = 80
            elif revenue_growth > 10:
                score = 65
            elif revenue_growth > 0:
                score = 50
            else:
                score = 30
            
            details['catalysts'] = f"Revenue growth: {revenue_growth:.1f}%"
        
        return score, details
    
    def score_risks_red_flags(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score risks and red flags (-10% penalty)
        """
        details = {}
        info = data.get('info', {})
        
        try:
            # Debt to Equity
            debt_to_equity = info.get('debtToEquity', 0)
            debt_penalty = max(0, (debt_to_equity - 50) * 0.5) if debt_to_equity > 50 else 0
            
            # Current Ratio (liquidity)
            current_ratio = info.get('currentRatio', 1)
            liquidity_penalty = max(0, (1.5 - current_ratio) * 20) if current_ratio < 1.5 else 0
            
            # Profit margins (negative margins are red flags)
            profit_margin = info.get('profitMargins', 0) * 100
            margin_penalty = max(0, -profit_margin * 2) if profit_margin < 0 else 0
            
            total_penalty = min(100, debt_penalty + liquidity_penalty + margin_penalty)
            risk_score = 100 - total_penalty
            
            details['risks'] = f"Debt/Equity: {debt_to_equity:.1f}, Current Ratio: {current_ratio:.2f}, Profit Margin: {profit_margin:.1f}%"
            
        except Exception as e:
            print(f"Error in risk scoring: {e}")
            risk_score = 70  # Conservative score
            details['risks'] = "Error in calculation"
        
        return risk_score, details
    
    def score_macro_sensitivity(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score macro sensitivity (5% weight)
        """
        details = {}
        info = data.get('info', {})
        
        # Beta as proxy for market sensitivity
        beta = info.get('beta', 1)
        
        # Lower beta = less sensitivity = higher score for stability
        if beta < 0.8:
            score = 80
        elif beta < 1.2:
            score = 60
        elif beta < 1.5:
            score = 40
        else:
            score = 20
        
        details['macro_sensitivity'] = f"Beta: {beta:.2f}"
        
        return score, details
    
    def score_market_sentiment(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score market sentiment (5% weight)
        """
        details = {}
        info = data.get('info', {})
        
        try:
            # Institutional ownership - try multiple field names
            institutional_ownership = (
                info.get('heldPercentInstitutions', 0) or 
                info.get('heldByInstitutions', 0) or 0
            ) * 100
            
            # Analyst recommendations
            recommendation = info.get('recommendationMean', 3)  # 1=Strong Buy, 5=Strong Sell
            
            # Scoring
            institutional_score = self.normalize_score(institutional_ownership, 30, 80)
            recommendation_score = self.normalize_score(recommendation, 1, 5, reverse=True)
            
            sentiment_score = (institutional_score + recommendation_score) / 2
            
            details['sentiment'] = f"Institutional: {institutional_ownership:.1f}%, Recommendation: {recommendation:.1f}"
            
        except Exception as e:
            print(f"Error in sentiment scoring: {e}")
            sentiment_score = 50
            details['sentiment'] = "Error in calculation"
        
        return sentiment_score, details
    
    def score_vendors_supply_chain(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score vendors/supply chain (3% weight)
        """
        details = {}
        
        if manual_inputs and 'supply_chain' in manual_inputs:
            score = manual_inputs['supply_chain'].get('score', 50)
            details['supply_chain'] = manual_inputs['supply_chain'].get('description', 'Manual assessment')
        else:
            # Basic approximation
            info = data.get('info', {})
            sector = info.get('sector', '')
            
            # Technology and manufacturing sectors typically have complex supply chains
            if sector in ['Technology', 'Consumer Cyclical', 'Industrials']:
                score = 60
            else:
                score = 50
            
            details['supply_chain'] = f"Sector-based assessment: {sector}"
        
        return score, details
    
    def score_innovation_rd(self, data: Dict) -> Tuple[float, Dict]:
        """
        Score innovation & R&D (7% weight)
        """
        details = {}
        info = data.get('info', {})
        
        try:
            # Employee count as proxy for talent
            employees = info.get('fullTimeEmployees', 0)
            
            # Technology sector gets higher innovation score
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # Base score from sector/industry
            if sector == 'Technology' or 'Software' in industry or 'Semiconductor' in industry:
                base_score = 70
            elif sector in ['Healthcare', 'Communication Services']:
                base_score = 60
            else:
                base_score = 40
            
            # Adjust based on company size (larger companies often have more R&D)
            if employees > 10000:
                size_bonus = 20
            elif employees > 1000:
                size_bonus = 10
            else:
                size_bonus = 0
            
            innovation_score = min(100, base_score + size_bonus)
            
            details['innovation'] = f"Sector: {sector}, Employees: {employees:,}"
            
        except Exception as e:
            print(f"Error in innovation scoring: {e}")
            innovation_score = 50
            details['innovation'] = "Error in calculation"
        
        return innovation_score, details
    
    def score_global_trends_alignment(self, data: Dict, manual_inputs: Dict = None) -> Tuple[float, Dict]:
        """
        Score global trends alignment (5% weight)
        """
        details = {}
        
        if manual_inputs and 'global_trends' in manual_inputs:
            score = manual_inputs['global_trends'].get('score', 50)
            details['trends'] = manual_inputs['global_trends'].get('description', 'Manual assessment')
        else:
            info = data.get('info', {})
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            business_summary = info.get('longBusinessSummary', '').lower()
            
            # Keywords for mega-trends
            ai_keywords = ['artificial intelligence', 'ai', 'machine learning', 'neural']
            ev_keywords = ['electric vehicle', 'ev', 'battery', 'automotive']
            clean_energy_keywords = ['renewable', 'solar', 'wind', 'clean energy', 'green']
            cloud_keywords = ['cloud', 'saas', 'software as a service', 'data center']
            
            trend_score = 30  # Base score
            
            # Check for trend alignment
            for keywords in [ai_keywords, ev_keywords, clean_energy_keywords, cloud_keywords]:
                if any(keyword in business_summary for keyword in keywords):
                    trend_score += 15
            
            # Sector bonuses
            if sector in ['Technology', 'Consumer Cyclical']:
                trend_score += 10
            
            trend_score = min(100, trend_score)
            
            details['trends'] = f"Sector: {sector}, Trend keywords found in business summary"
        
        return trend_score, details
    
    def calculate_total_score(self, ticker: str, manual_inputs: Dict = None) -> Dict:
        """
        Calculate total weighted score for a stock
        """
        # Fetch financial data
        data = self.get_financial_data(ticker)
        
        if not data:
            return {
                'ticker': ticker,
                'total_score': 0,
                'error': 'Failed to fetch data',
                'breakdown': {}
            }
        
        # Calculate scores for each criteria
        scores = {}
        details = {}
        
        # 1. Business Fundamentals (35%)
        score, detail = self.score_business_fundamentals(data)
        scores['business_fundamentals'] = score
        details['business_fundamentals'] = detail
        
        # 2. Competitive Advantage (15%)
        score, detail = self.score_competitive_advantage(data, manual_inputs)
        scores['competitive_advantage'] = score
        details['competitive_advantage'] = detail
        
        # 3. Management Quality (10%)
        score, detail = self.score_management_quality(data, manual_inputs)
        scores['management_quality'] = score
        details['management_quality'] = detail
        
        # 4. Industry Attributes (10%)
        score, detail = self.score_industry_attributes(data, manual_inputs)
        scores['industry_attributes'] = score
        details['industry_attributes'] = detail
        
        # 5. Valuation Metrics (10%)
        score, detail = self.score_valuation_metrics(data)
        scores['valuation_metrics'] = score
        details['valuation_metrics'] = detail
        
        # 6. Growth Catalysts (5%)
        score, detail = self.score_growth_catalysts(data, manual_inputs)
        scores['growth_catalysts'] = score
        details['growth_catalysts'] = detail
        
        # 7. Risks & Red Flags (-10%)
        score, detail = self.score_risks_red_flags(data)
        scores['risks_red_flags'] = score
        details['risks_red_flags'] = detail
        
        # 8. Macro Sensitivity (5%)
        score, detail = self.score_macro_sensitivity(data)
        scores['macro_sensitivity'] = score
        details['macro_sensitivity'] = detail
        
        # 9. Market Sentiment (5%)
        score, detail = self.score_market_sentiment(data)
        scores['market_sentiment'] = score
        details['market_sentiment'] = detail
        
        # 10. Vendors/Supply Chain (3%)
        score, detail = self.score_vendors_supply_chain(data, manual_inputs)
        scores['vendors_supply_chain'] = score
        details['vendors_supply_chain'] = detail
        
        # 11. Innovation & R&D (7%)
        score, detail = self.score_innovation_rd(data)
        scores['innovation_rd'] = score
        details['innovation_rd'] = detail
        
        # 12. Global Trends Alignment (5%)
        score, detail = self.score_global_trends_alignment(data, manual_inputs)
        scores['global_trends_alignment'] = score
        details['global_trends_alignment'] = detail
        
        # Calculate weighted total score
        total_score = 0
        for criteria, weight in self.criteria_weights.items():
            if criteria in scores:
                total_score += scores[criteria] * abs(weight)  # Use absolute weight for calculation
        
        # Apply risk penalty
        if 'risks_red_flags' in scores:
            risk_penalty = (100 - scores['risks_red_flags']) * 0.10
            total_score -= risk_penalty
        
        # Ensure score is between 0 and 100
        total_score = max(0, min(100, total_score))
        
        return {
            'ticker': ticker,
            'total_score': round(total_score, 2),
            'grade': self.get_grade(total_score),
            'scores': scores,
            'details': details,
            'weights': self.criteria_weights,
            'company_info': {
                'name': data.get('info', {}).get('longName', ticker),
                'sector': data.get('info', {}).get('sector', 'N/A'),
                'industry': data.get('info', {}).get('industry', 'N/A'),
                'market_cap': data.get('info', {}).get('marketCap', 0)
            }
        }
    
    def get_grade(self, score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        elif score >= 45:
            return 'D+'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def score_stock_list(self, tickers: List[str], manual_inputs: Dict = None) -> List[Dict]:
        """
        Score a list of stocks and return ranked results
        """
        results = []
        
        for ticker in tickers:
            print(f"Scoring {ticker}...")
            result = self.calculate_total_score(ticker, manual_inputs)
            results.append(result)
        
        # Sort by total score (descending)
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        return results


# Example usage function
def score_stocks(tickers: List[str], manual_inputs: Dict = None) -> List[Dict]:
    """
    Main function to score a list of stocks
    
    Args:
        tickers: List of stock ticker symbols
        manual_inputs: Optional dictionary with manual assessments for qualitative criteria
                      Format: {
                          'TICKER': {
                              'competitive_advantage': {'moat_strength': 80, 'description': 'Strong patents'},
                              'management_quality': {'score': 75, 'description': 'Founder-led'},
                              'industry_attributes': {'score': 85, 'description': 'AI growth sector'},
                              'growth_catalysts': {'score': 70, 'description': 'New product launch'},
                              'supply_chain': {'score': 60, 'description': 'Diversified suppliers'},
                              'global_trends': {'score': 90, 'description': 'Strong AI alignment'}
                          }
                      }
    
    Returns:
        List of dictionaries with scores and analysis for each stock
    """
    scorer = StockScorer()
    return scorer.score_stock_list(tickers, manual_inputs)


if __name__ == "__main__":
    # Example usage
    test_tickers = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN']
    
    # Example manual inputs (optional)
    manual_inputs = {
        'NVDA': {
            'competitive_advantage': {'moat_strength': 90, 'description': 'CUDA ecosystem and AI chip dominance'},
            'management_quality': {'score': 85, 'description': 'Strong leadership under Jensen Huang'},
            'industry_attributes': {'score': 95, 'description': 'AI semiconductor leader'},
            'global_trends': {'score': 95, 'description': 'Perfect AI alignment'}
        }
    }
    
    results = score_stocks(test_tickers, manual_inputs)
    
    print("\n=== STOCK SCORING RESULTS ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['ticker']} - {result['company_info']['name']}")
        print(f"   Total Score: {result['total_score']} ({result['grade']})")
        print(f"   Sector: {result['company_info']['sector']}")
        print(f"   Market Cap: ${result['company_info']['market_cap']/1e9:.1f}B")
