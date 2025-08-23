import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from dataclasses import dataclass, asdict

from .sector_analyzer import SectorAnalyzer, StockRecommendation, Sector
from scrapers.yahoo_finance import YahooFinanceScraper
from scrapers.finviz_scraper import FinvizScraper
from scrapers.seeking_alpha_scraper import SeekingAlphaScraper

@dataclass
class EnhancedStockRecommendation:
    ticker: str
    company_name: str
    sector: str
    subsector: str
    recommendation_reason: str
    growth_potential: str
    risk_level: str
    market_cap: str
    current_price: float
    target_price: float
    confidence_score: float
    key_advantages: List[str]
    risks: List[str]
    long_term_outlook: str
    # Enhanced fields
    technical_score: float
    fundamental_score: float
    analyst_rating: str
    dividend_yield: float
    pe_ratio: float
    debt_to_equity: float
    revenue_growth: float
    earnings_growth: float
    beta: float
    rsi: float
    moving_averages: Dict[str, float]
    price_momentum: str
    volume_trend: str
    institutional_ownership: float
    insider_ownership: float
    short_interest: float
    earnings_date: str
    next_earnings_estimate: float
    revenue_estimate: float
    sector_rank: int
    subsector_rank: int
    overall_rank: int

class AIStockRecommender:
    def __init__(self):
        self.sector_analyzer = SectorAnalyzer()
        self.yahoo_scraper = YahooFinanceScraper()
        self.finviz_scraper = FinvizScraper()
        self.seeking_alpha_scraper = SeekingAlphaScraper()
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Scoring weights
        self.scoring_weights = {
            'technical': 0.25,
            'fundamental': 0.35,
            'analyst_sentiment': 0.20,
            'sector_growth': 0.15,
            'risk_adjustment': 0.05
        }
    
    def get_intelligent_recommendations(self, 
                                      sector: str, 
                                      subsectors: List[str],
                                      market_cap_preference: str = "all",
                                      risk_tolerance: str = "medium",
                                      investment_horizon: str = "long_term",
                                      max_recommendations: int = 20) -> Dict:
        """
        Get intelligent stock recommendations based on comprehensive analysis
        """
        try:
            # Step 1: Get base recommendations from sector analyzer
            base_recommendations = self.sector_analyzer.get_stock_recommendations(
                sector, subsectors, market_cap_preference, risk_tolerance
            )
            
            # Step 2: Enhance with real-time data
            enhanced_recommendations = []
            
            with self.executor as executor:
                # Submit tasks for data enhancement
                futures = []
                for rec in base_recommendations[:max_recommendations]:
                    future = executor.submit(
                        self._enhance_recommendation_with_data, 
                        rec, sector, subsectors
                    )
                    futures.append(future)
                
                # Collect results
                for future in futures:
                    try:
                        enhanced_rec = future.result(timeout=30)
                        if enhanced_rec:
                            enhanced_recommendations.append(enhanced_rec)
                    except Exception as e:
                        print(f"Error enhancing recommendation: {e}")
                        continue
            
            # Step 3: Rank and score recommendations
            ranked_recommendations = self._rank_recommendations(
                enhanced_recommendations, investment_horizon
            )
            
            # Step 4: Generate LLM analysis
            llm_analysis = self.sector_analyzer.generate_llm_analysis(
                sector, subsectors, market_cap_preference
            )
            
            # Step 5: Create comprehensive response
            response = {
                'sector': sector,
                'subsectors': subsectors,
                'market_cap_preference': market_cap_preference,
                'risk_tolerance': risk_tolerance,
                'investment_horizon': investment_horizon,
                'total_recommendations': len(ranked_recommendations),
                'recommendations': [asdict(rec) for rec in ranked_recommendations],
                'sector_analysis': llm_analysis,
                'summary': self._generate_summary(ranked_recommendations),
                'risk_analysis': self._analyze_portfolio_risk(ranked_recommendations),
                'diversification_analysis': self._analyze_diversification(ranked_recommendations),
                'generated_at': datetime.now().isoformat()
            }
            
            return response
            
        except Exception as e:
            return {
                'error': str(e),
                'sector': sector,
                'subsectors': subsectors,
                'recommendations': [],
                'generated_at': datetime.now().isoformat()
            }
    
    def _enhance_recommendation_with_data(self, 
                                        base_rec: StockRecommendation, 
                                        sector: str, 
                                        subsectors: List[str]) -> Optional[EnhancedStockRecommendation]:
        """Enhance base recommendation with real-time market data"""
        try:
            ticker = base_rec.ticker
            
            # Get real-time data from multiple sources
            yahoo_data = self._get_yahoo_data(ticker)
            finviz_data = self._get_finviz_data(ticker)
            seeking_alpha_data = self._get_seeking_alpha_data(ticker)
            
            # Calculate scores
            technical_score = self._calculate_technical_score(finviz_data, yahoo_data)
            fundamental_score = self._calculate_fundamental_score(yahoo_data, finviz_data)
            analyst_score = self._calculate_analyst_score(seeking_alpha_data)
            
            # Calculate overall score
            overall_score = (
                technical_score * self.scoring_weights['technical'] +
                fundamental_score * self.scoring_weights['fundamental'] +
                analyst_score * self.scoring_weights['analyst_sentiment']
            )
            
            # Create enhanced recommendation
            enhanced_rec = EnhancedStockRecommendation(
                ticker=base_rec.ticker,
                company_name=base_rec.company_name,
                sector=base_rec.sector,
                subsector=base_rec.subsector,
                recommendation_reason=base_rec.recommendation_reason,
                growth_potential=base_rec.growth_potential,
                risk_level=base_rec.risk_level,
                market_cap=base_rec.market_cap,
                current_price=yahoo_data.get('current_price', 0.0),
                target_price=seeking_alpha_data.get('price_target', 0.0),
                confidence_score=overall_score,
                key_advantages=base_rec.key_advantages,
                risks=base_rec.risks,
                long_term_outlook=base_rec.long_term_outlook,
                technical_score=technical_score,
                fundamental_score=fundamental_score,
                analyst_rating=seeking_alpha_data.get('quant_rating', 'N/A'),
                dividend_yield=yahoo_data.get('dividend_yield', 0.0),
                pe_ratio=yahoo_data.get('pe_ratio', 0.0),
                debt_to_equity=finviz_data.get('debt_to_equity', 0.0),
                revenue_growth=yahoo_data.get('revenue_growth', 0.0),
                earnings_growth=yahoo_data.get('earnings_growth', 0.0),
                beta=finviz_data.get('beta', 1.0),
                rsi=finviz_data.get('rsi_14', 50.0),
                moving_averages=self._get_moving_averages(finviz_data),
                price_momentum=self._calculate_momentum(yahoo_data),
                volume_trend=self._analyze_volume_trend(yahoo_data),
                institutional_ownership=finviz_data.get('institutional_ownership', 0.0),
                insider_ownership=finviz_data.get('insider_ownership', 0.0),
                short_interest=finviz_data.get('short_float', 0.0),
                earnings_date=seeking_alpha_data.get('next_earnings_date', 'N/A'),
                next_earnings_estimate=seeking_alpha_data.get('eps_estimate', 0.0),
                revenue_estimate=seeking_alpha_data.get('revenue_estimate', 0.0),
                sector_rank=0,  # Will be set during ranking
                subsector_rank=0,  # Will be set during ranking
                overall_rank=0  # Will be set during ranking
            )
            
            return enhanced_rec
            
        except Exception as e:
            print(f"Error enhancing recommendation for {base_rec.ticker}: {e}")
            return None
    
    def _get_yahoo_data(self, ticker: str) -> Dict:
        """Get Yahoo Finance data for a ticker"""
        try:
            return self.yahoo_scraper.get_stock_info(ticker)
        except Exception as e:
            print(f"Error getting Yahoo data for {ticker}: {e}")
            return {}
    
    def _get_finviz_data(self, ticker: str) -> Dict:
        """Get Finviz data for a ticker"""
        try:
            overview = self.finviz_scraper.get_stock_overview(ticker)
            technical = self.finviz_scraper.get_technical_analysis(ticker)
            return {**overview, **technical}
        except Exception as e:
            print(f"Error getting Finviz data for {ticker}: {e}")
            return {}
    
    def _get_seeking_alpha_data(self, ticker: str) -> Dict:
        """Get Seeking Alpha data for a ticker"""
        try:
            analysis = self.seeking_alpha_scraper.get_stock_analysis(ticker)
            earnings = self.seeking_alpha_scraper.get_earnings_data(ticker)
            return {**analysis, **earnings}
        except Exception as e:
            print(f"Error getting Seeking Alpha data for {ticker}: {e}")
            return {}
    
    def _calculate_technical_score(self, finviz_data: Dict, yahoo_data: Dict) -> float:
        """Calculate technical analysis score"""
        score = 0.5  # Base score
        
        try:
            # RSI analysis
            rsi = finviz_data.get('rsi_14', 50)
            if 30 <= rsi <= 70:
                score += 0.2
            elif 40 <= rsi <= 60:
                score += 0.3
            
            # Moving averages
            current_price = yahoo_data.get('current_price', 0)
            sma_20 = finviz_data.get('sma_20', 0)
            sma_50 = finviz_data.get('sma_50', 0)
            
            if current_price > sma_20 > sma_50:
                score += 0.2
            elif current_price > sma_20:
                score += 0.1
            
            # Volume trend
            volume = yahoo_data.get('volume', 0)
            avg_volume = yahoo_data.get('avg_volume', 0)
            if volume > avg_volume * 1.2:
                score += 0.1
            
            # Beta analysis
            beta = finviz_data.get('beta', 1.0)
            if 0.8 <= beta <= 1.2:
                score += 0.1
            
        except Exception as e:
            print(f"Error calculating technical score: {e}")
        
        return min(score, 1.0)
    
    def _calculate_fundamental_score(self, yahoo_data: Dict, finviz_data: Dict) -> float:
        """Calculate fundamental analysis score"""
        score = 0.5  # Base score
        
        try:
            # P/E ratio analysis
            pe_ratio = yahoo_data.get('pe_ratio', 0)
            if 0 < pe_ratio < 25:
                score += 0.2
            elif 0 < pe_ratio < 15:
                score += 0.3
            
            # Debt to equity
            debt_to_equity = finviz_data.get('debt_to_equity', 0)
            if debt_to_equity < 0.5:
                score += 0.2
            elif debt_to_equity < 1.0:
                score += 0.1
            
            # Revenue growth
            revenue_growth = yahoo_data.get('revenue_growth', 0)
            if revenue_growth > 0.1:
                score += 0.2
            elif revenue_growth > 0.05:
                score += 0.1
            
            # Earnings growth
            earnings_growth = yahoo_data.get('earnings_growth', 0)
            if earnings_growth > 0.1:
                score += 0.2
            elif earnings_growth > 0.05:
                score += 0.1
            
            # Dividend yield (bonus for income stocks)
            dividend_yield = yahoo_data.get('dividend_yield', 0)
            if 0.02 <= dividend_yield <= 0.06:
                score += 0.1
            
        except Exception as e:
            print(f"Error calculating fundamental score: {e}")
        
        return min(score, 1.0)
    
    def _calculate_analyst_score(self, seeking_alpha_data: Dict) -> float:
        """Calculate analyst sentiment score"""
        score = 0.5  # Base score
        
        try:
            # Quant rating
            quant_rating = seeking_alpha_data.get('quant_rating', '')
            if 'Strong Buy' in quant_rating or 'Buy' in quant_rating:
                score += 0.3
            elif 'Hold' in quant_rating:
                score += 0.1
            
            # Author rating
            author_rating = seeking_alpha_data.get('author_rating', '')
            if 'Strong Buy' in author_rating or 'Buy' in author_rating:
                score += 0.2
            
            # Wall Street rating
            ws_rating = seeking_alpha_data.get('wall_street_rating', '')
            if 'Strong Buy' in ws_rating or 'Buy' in ws_rating:
                score += 0.2
            
        except Exception as e:
            print(f"Error calculating analyst score: {e}")
        
        return min(score, 1.0)
    
    def _get_moving_averages(self, finviz_data: Dict) -> Dict[str, float]:
        """Extract moving averages from Finviz data"""
        return {
            'sma_20': finviz_data.get('sma_20', 0.0),
            'sma_50': finviz_data.get('sma_50', 0.0),
            'sma_200': finviz_data.get('sma_200', 0.0),
            'ema_20': finviz_data.get('ema_20', 0.0),
            'ema_50': finviz_data.get('ema_50', 0.0)
        }
    
    def _calculate_momentum(self, yahoo_data: Dict) -> str:
        """Calculate price momentum"""
        try:
            price_change = yahoo_data.get('price_change', 0)
            if price_change > 0.05:
                return "Strong Positive"
            elif price_change > 0.02:
                return "Positive"
            elif price_change > -0.02:
                return "Neutral"
            elif price_change > -0.05:
                return "Negative"
            else:
                return "Strong Negative"
        except:
            return "Unknown"
    
    def _analyze_volume_trend(self, yahoo_data: Dict) -> str:
        """Analyze volume trend"""
        try:
            volume = yahoo_data.get('volume', 0)
            avg_volume = yahoo_data.get('avg_volume', 0)
            
            if avg_volume == 0:
                return "Unknown"
            
            ratio = volume / avg_volume
            if ratio > 1.5:
                return "High Volume"
            elif ratio > 1.2:
                return "Above Average"
            elif ratio > 0.8:
                return "Average"
            else:
                return "Below Average"
        except:
            return "Unknown"
    
    def _rank_recommendations(self, 
                            recommendations: List[EnhancedStockRecommendation], 
                            investment_horizon: str) -> List[EnhancedStockRecommendation]:
        """Rank recommendations based on investment horizon"""
        if not recommendations:
            return []
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Assign ranks
        for i, rec in enumerate(recommendations):
            rec.overall_rank = i + 1
            
            # Calculate sector and subsector ranks
            sector_recs = [r for r in recommendations if r.sector == rec.sector]
            subsector_recs = [r for r in recommendations if r.subsector == rec.subsector]
            
            rec.sector_rank = sector_recs.index(rec) + 1
            rec.subsector_rank = subsector_recs.index(rec) + 1
        
        return recommendations
    
    def _generate_summary(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Generate summary statistics for recommendations"""
        if not recommendations:
            return {}
        
        return {
            'total_recommendations': len(recommendations),
            'average_confidence_score': np.mean([r.confidence_score for r in recommendations]),
            'average_technical_score': np.mean([r.technical_score for r in recommendations]),
            'average_fundamental_score': np.mean([r.fundamental_score for r in recommendations]),
            'sector_distribution': self._get_sector_distribution(recommendations),
            'market_cap_distribution': self._get_market_cap_distribution(recommendations),
            'risk_distribution': self._get_risk_distribution(recommendations),
            'top_picks': [r.ticker for r in recommendations[:5]]
        }
    
    def _get_sector_distribution(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Get distribution of recommendations by sector"""
        distribution = {}
        for rec in recommendations:
            sector = rec.sector
            distribution[sector] = distribution.get(sector, 0) + 1
        return distribution
    
    def _get_market_cap_distribution(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Get distribution of recommendations by market cap"""
        distribution = {}
        for rec in recommendations:
            market_cap = rec.market_cap
            distribution[market_cap] = distribution.get(market_cap, 0) + 1
        return distribution
    
    def _get_risk_distribution(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Get distribution of recommendations by risk level"""
        distribution = {}
        for rec in recommendations:
            risk = rec.risk_level
            distribution[risk] = distribution.get(risk, 0) + 1
        return distribution
    
    def _analyze_portfolio_risk(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Analyze portfolio risk characteristics"""
        if not recommendations:
            return {}
        
        return {
            'average_beta': np.mean([r.beta for r in recommendations if r.beta > 0]),
            'average_pe_ratio': np.mean([r.pe_ratio for r in recommendations if r.pe_ratio > 0]),
            'average_debt_to_equity': np.mean([r.debt_to_equity for r in recommendations if r.debt_to_equity > 0]),
            'average_dividend_yield': np.mean([r.dividend_yield for r in recommendations if r.dividend_yield > 0]),
            'risk_score': self._calculate_portfolio_risk_score(recommendations)
        }
    
    def _calculate_portfolio_risk_score(self, recommendations: List[EnhancedStockRecommendation]) -> float:
        """Calculate overall portfolio risk score"""
        if not recommendations:
            return 0.0
        
        risk_scores = []
        for rec in recommendations:
            # Base risk score
            base_risk = {'Low': 0.2, 'Medium': 0.5, 'High': 0.8}.get(rec.risk_level, 0.5)
            
            # Adjust for beta
            beta_adjustment = (rec.beta - 1.0) * 0.1 if rec.beta > 0 else 0
            
            # Adjust for debt
            debt_adjustment = rec.debt_to_equity * 0.1 if rec.debt_to_equity > 0 else 0
            
            risk_score = base_risk + beta_adjustment + debt_adjustment
            risk_scores.append(min(max(risk_score, 0.0), 1.0))
        
        return np.mean(risk_scores)
    
    def _analyze_diversification(self, recommendations: List[EnhancedStockRecommendation]) -> Dict:
        """Analyze portfolio diversification"""
        if not recommendations:
            return {}
        
        sectors = [r.sector for r in recommendations]
        subsectors = [r.subsector for r in recommendations]
        market_caps = [r.market_cap for r in recommendations]
        
        return {
            'sector_diversification': len(set(sectors)) / len(sectors) if sectors else 0,
            'subsector_diversification': len(set(subsectors)) / len(subsectors) if subsectors else 0,
            'market_cap_diversification': len(set(market_caps)) / len(market_caps) if market_caps else 0,
            'concentration_risk': self._calculate_concentration_risk(recommendations)
        }
    
    def _calculate_concentration_risk(self, recommendations: List[EnhancedStockRecommendation]) -> float:
        """Calculate concentration risk (0 = well diversified, 1 = highly concentrated)"""
        if not recommendations:
            return 0.0
        
        # Calculate Herfindahl-Hirschman Index for sectors
        sector_counts = {}
        for rec in recommendations:
            sector_counts[rec.sector] = sector_counts.get(rec.sector, 0) + 1
        
        total = len(recommendations)
        hhi = sum((count / total) ** 2 for count in sector_counts.values())
        
        # Normalize to 0-1 scale
        return min(hhi, 1.0)
