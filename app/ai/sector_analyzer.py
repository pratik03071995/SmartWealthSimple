import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

# LLM imports
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from sentence_transformers import SentenceTransformer
    import torch
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM packages not available. Install with: pip install transformers torch sentence-transformers")

@dataclass
class Sector:
    name: str
    description: str
    subsectors: List[str]
    growth_potential: str
    risk_level: str
    market_cap_range: str
    key_drivers: List[str]

@dataclass
class StockRecommendation:
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

class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class SectorAnalyzer:
    def __init__(self, use_local_llm: bool = True, model_name: str = "microsoft/DialoGPT-medium"):
        self.use_local_llm = use_local_llm and LLM_AVAILABLE
        self.model_name = model_name
        self.sector_data = self._load_sector_data()
        self.stock_database = self._load_stock_database()
        
        # Initialize LLM components
        if self.use_local_llm:
            self._initialize_llm()
        
        # Sector hierarchy and analysis - Focus on most relevant sectors using Yahoo Finance's exact names
        self.sector_hierarchy = {
            "Technology": {
                "description": "Companies involved in software, hardware, semiconductors, and digital services",
                "subsectors": [
                    "Software & Services",
                    "Hardware & Equipment",
                    "Semiconductors",
                    "Internet Services",
                    "Cloud Computing",
                    "Artificial Intelligence",
                    "Cybersecurity",
                    "Fintech",
                    "E-commerce",
                    "Gaming & Entertainment"
                ],
                "growth_potential": "High",
                "risk_level": "Medium",
                "key_drivers": ["Digital transformation", "AI/ML adoption", "Cloud migration", "Cybersecurity needs"]
            },
            "Healthcare": {
                "description": "Companies in pharmaceuticals, biotechnology, medical devices, and healthcare services",
                "subsectors": [
                    "Pharmaceuticals",
                    "Biotechnology",
                    "Medical Devices",
                    "Healthcare Services",
                    "Health Insurance",
                    "Digital Health",
                    "Telemedicine",
                    "Medical Equipment",
                    "Drug Discovery",
                    "Gene Therapy"
                ],
                "growth_potential": "High",
                "risk_level": "High",
                "key_drivers": ["Aging population", "Medical innovation", "Healthcare digitization", "Personalized medicine"]
            },
            "Financial Services": {
                "description": "Banks, insurance companies, investment firms, and fintech companies",
                "subsectors": [
                    "Commercial Banking",
                    "Investment Banking",
                    "Insurance",
                    "Asset Management",
                    "Fintech",
                    "Payment Processing",
                    "Cryptocurrency",
                    "Real Estate Investment",
                    "Consumer Finance",
                    "Wealth Management"
                ],
                "growth_potential": "Medium",
                "risk_level": "Medium",
                "key_drivers": ["Digital banking", "Fintech innovation", "Wealth management growth", "Insurance demand"]
            },
            "Energy": {
                "description": "Companies involved in oil, gas, renewable energy, and utilities",
                "subsectors": [
                    "Oil & Gas",
                    "Renewable Energy",
                    "Utilities",
                    "Energy Storage",
                    "Electric Vehicles",
                    "Nuclear Energy",
                    "Energy Infrastructure",
                    "Clean Technology",
                    "Energy Trading",
                    "Energy Services"
                ],
                "growth_potential": "Medium",
                "risk_level": "Medium",
                "key_drivers": ["Energy transition", "Renewable adoption", "EV growth", "Energy security"]
            },
            "Utilities": {
                "description": "Electric, gas, and water utility companies",
                "subsectors": [
                    "Electric Utilities",
                    "Gas Utilities", 
                    "Water Utilities",
                    "Multi-Utilities",
                    "Independent Power Producers",
                    "Renewable Energy Utilities",
                    "Nuclear Power",
                    "Energy Distribution",
                    "Energy Transmission",
                    "Energy Storage"
                ],
                "growth_potential": "Low",
                "risk_level": "Low",
                "key_drivers": ["Regulatory environment", "Infrastructure investment", "Energy efficiency", "Grid modernization"]
            },
            "Consumer Cyclical": {  # Yahoo Finance uses "Consumer Cyclical" not "Consumer Discretionary"
                "description": "Companies that sell non-essential goods and services",
                "subsectors": [
                    "Automotive",
                    "Retail",
                    "Restaurants",
                    "Entertainment",
                    "Travel & Leisure",
                    "Luxury Goods",
                    "Home Improvement",
                    "Apparel & Accessories",
                    "Consumer Electronics",
                    "Online Retail"
                ],
                "growth_potential": "Medium",
                "risk_level": "Medium",
                "key_drivers": ["Consumer spending", "E-commerce growth", "Experiential consumption", "Brand loyalty"]
            }
        }
    
    def _initialize_llm(self):
        """Initialize the local LLM model"""
        try:
            print("Initializing local LLM...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Initialize sentence transformer for similarity
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            print("LLM initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize LLM: {e}")
            self.use_local_llm = False
    
    def _load_sector_data(self) -> Dict:
        """Load sector analysis data"""
        return {
            "Technology": {
                "growth_rate": "15-20%",
                "market_cap": "$50B+",
                "key_players": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
                "emerging_trends": ["AI/ML", "Cloud Computing", "Cybersecurity", "IoT"]
            },
            "Healthcare": {
                "growth_rate": "10-15%",
                "market_cap": "$20B+",
                "key_players": ["JNJ", "PFE", "UNH", "ABBV", "TMO"],
                "emerging_trends": ["Biotech", "Digital Health", "Personalized Medicine", "Gene Therapy"]
            },
            "Financial Services": {
                "growth_rate": "8-12%",
                "market_cap": "$30B+",
                "key_players": ["JPM", "BAC", "WFC", "GS", "MS"],
                "emerging_trends": ["Fintech", "Digital Banking", "Cryptocurrency", "AI Trading"]
            }
        }
    
    def _load_stock_database(self) -> Dict:
        """Load comprehensive stock database with sector classifications"""
        return {
            "Technology": {
                "Software & Services": {
                    "large_caps": ["MSFT", "ORCL", "CRM", "ADBE", "INTU"],
                    "mid_caps": ["NOW", "TEAM", "SNOW", "PLTR", "CRWD"],
                    "small_caps": ["ZS", "OKTA", "NET", "DDOG", "MDB"]
                },
                "Hardware & Equipment": {
                    "large_caps": ["AAPL", "HPQ", "DELL", "CSCO", "AVGO"],
                    "mid_caps": ["AMD", "QCOM", "MU", "TXN", "INTC"],
                    "small_caps": ["NVDA", "MRVL", "KLAC", "LRCX", "AMAT"]
                },
                "Semiconductors": {
                    "large_caps": ["NVDA", "INTC", "AMD", "QCOM", "AVGO"],
                    "mid_caps": ["MU", "TXN", "MRVL", "KLAC", "LRCX"],
                    "small_caps": ["AMAT", "ASML", "TSM", "UMC", "SMIC"]
                }
            },
            "Healthcare": {
                "Pharmaceuticals": {
                    "large_caps": ["JNJ", "PFE", "ABBV", "MRK", "BMY"],
                    "mid_caps": ["GILD", "REGN", "VRTX", "BIIB", "AMGN"],
                    "small_caps": ["BMRN", "ALKS", "INCY", "EXEL", "SGEN"]
                },
                "Biotechnology": {
                    "large_caps": ["AMGN", "GILD", "BIIB", "REGN", "VRTX"],
                    "mid_caps": ["MRNA", "BNTX", "CRSP", "EDIT", "BEAM"],
                    "small_caps": ["NTLA", "CRSP", "EDIT", "BEAM", "CRBU"]
                },
                "Medical Devices": {
                    "large_caps": ["JNJ", "TMO", "ABT", "DHR", "BDX"],
                    "mid_caps": ["ISRG", "DXCM", "ALGN", "IDXX", "WAT"],
                    "small_caps": ["MASI", "PEN", "ATRC", "IRTC", "TNDM"]
                }
            },
            "Financial Services": {
                "Commercial Banking": {
                    "large_caps": ["JPM", "BAC", "WFC", "C", "GS"],
                    "mid_caps": ["USB", "PNC", "TFC", "COF", "AXP"],
                    "small_caps": ["KEY", "HBAN", "FITB", "ZION", "CMA"]
                },
                "Investment Banking": {
                    "large_caps": ["GS", "MS", "JPM", "BAC", "C"],
                    "mid_caps": ["SCHW", "ETFC", "AMTD", "LPLA", "RJF"],
                    "small_caps": ["SF", "PIPR", "LAZ", "EVR", "HLI"]
                },
                "Fintech": {
                    "large_caps": ["V", "MA", "PYPL", "SQ", "ADP"],
                    "mid_caps": ["FIS", "FISV", "GPN", "JKHY", "PAYX"],
                    "small_caps": ["AFRM", "UPST", "SOFI", "LC", "OPRT"]
                }
            }
        }
    
    def get_sector_hierarchy(self) -> Dict:
        """Get the complete sector hierarchy with subsectors"""
        return self.sector_hierarchy
    
    def analyze_sector(self, sector_name: str) -> Sector:
        """Analyze a specific sector and return detailed information"""
        if sector_name not in self.sector_hierarchy:
            raise ValueError(f"Sector '{sector_name}' not found")
        
        sector_info = self.sector_hierarchy[sector_name]
        
        return Sector(
            name=sector_name,
            description=sector_info["description"],
            subsectors=sector_info["subsectors"],
            growth_potential=sector_info["growth_potential"],
            risk_level=sector_info["risk_level"],
            market_cap_range=sector_info.get("market_cap", "Varies"),
            key_drivers=sector_info["key_drivers"]
        )
    
    def get_subsectors(self, sector_name: str) -> List[str]:
        """Get all subsectors for a given sector"""
        if sector_name not in self.sector_hierarchy:
            return []
        
        return self.sector_hierarchy[sector_name]["subsectors"]
    
    def get_sector_info(self, sector_name: str) -> Dict:
        """Get detailed information about a specific sector"""
        if sector_name not in self.sector_hierarchy:
            return None
        
        return self.sector_hierarchy[sector_name]
    
    def get_stocks_by_subsector(self, sector: str, subsector: str, market_cap_filter: str = "all") -> List[str]:
        """Get stocks for a specific subsector with market cap filtering"""
        if sector not in self.stock_database or subsector not in self.stock_database[sector]:
            return []
        
        stocks = []
        subsector_data = self.stock_database[sector][subsector]
        
        if market_cap_filter == "all":
            stocks.extend(subsector_data.get("large_caps", []))
            stocks.extend(subsector_data.get("mid_caps", []))
            stocks.extend(subsector_data.get("small_caps", []))
        elif market_cap_filter in subsector_data:
            stocks.extend(subsector_data[market_cap_filter])
        
        return stocks
    
    def generate_llm_analysis(self, sector: str, subsectors: List[str], market_cap_preference: str = "all") -> str:
        """Generate LLM-powered analysis for sector and subsector selection"""
        if not self.use_local_llm:
            return self._generate_fallback_analysis(sector, subsectors, market_cap_preference)
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(sector, subsectors, market_cap_preference)
            
            # Generate response using local LLM
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=1024,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response[len(prompt):]  # Remove the prompt from response
            
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self._generate_fallback_analysis(sector, subsectors, market_cap_preference)
    
    def _create_analysis_prompt(self, sector: str, subsectors: List[str], market_cap_preference: str) -> str:
        """Create a detailed prompt for LLM analysis"""
        prompt = f"""
        Analyze the {sector} sector with focus on the following subsectors: {', '.join(subsectors)}.
        
        Market cap preference: {market_cap_preference}
        
        Please provide:
        1. Growth potential analysis for each subsector
        2. Key investment themes and trends
        3. Risk factors to consider
        4. Recommended stock categories (large cap, mid cap, small cap)
        5. Long-term investment outlook
        
        Focus on identifying companies with strong competitive advantages, innovation potential, and sustainable growth prospects.
        """
        return prompt
    
    def _generate_fallback_analysis(self, sector: str, subsectors: List[str], market_cap_preference: str) -> str:
        """Generate analysis without LLM when not available"""
        analysis = f"""
        SECTOR ANALYSIS: {sector.upper()}
        
        Selected Subsectors: {', '.join(subsectors)}
        Market Cap Preference: {market_cap_preference}
        
        GROWTH POTENTIAL:
        - {sector} sector shows strong growth potential driven by digital transformation
        - Key subsectors offer varying risk-reward profiles
        - Focus on companies with sustainable competitive advantages
        
        INVESTMENT THEMES:
        - Innovation and R&D investment
        - Market leadership and brand strength
        - Scalable business models
        - Strong financial fundamentals
        
        RISK FACTORS:
        - Market volatility and economic cycles
        - Regulatory changes and compliance
        - Competition and disruption
        - Technology obsolescence
        
        RECOMMENDATIONS:
        - Diversify across subsectors
        - Focus on companies with strong balance sheets
        - Consider both growth and value opportunities
        - Monitor industry trends and competitive dynamics
        """
        return analysis
    
    def get_stock_recommendations(self, sector: str, subsectors: List[str], 
                                market_cap_preference: str = "all", 
                                risk_tolerance: str = "medium") -> List[StockRecommendation]:
        """Get intelligent stock recommendations based on sector and subsector analysis"""
        recommendations = []
        
        for subsector in subsectors:
            stocks = self.get_stocks_by_subsector(sector, subsector, market_cap_preference)
            
            for ticker in stocks[:5]:  # Limit to top 5 per subsector
                recommendation = self._create_stock_recommendation(
                    ticker, sector, subsector, risk_tolerance
                )
                if recommendation:
                    recommendations.append(recommendation)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations[:20]  # Return top 20 recommendations
    
    def _create_stock_recommendation(self, ticker: str, sector: str, subsector: str, 
                                   risk_tolerance: str) -> Optional[StockRecommendation]:
        """Create a detailed stock recommendation"""
        try:
            # This would typically fetch real data from your scrapers
            # For now, we'll create a template recommendation
            
            # Determine market cap category
            market_cap = self._get_market_cap_category(ticker)
            
            # Generate recommendation based on sector and subsector
            recommendation_reason = self._generate_recommendation_reason(ticker, sector, subsector)
            
            # Calculate confidence score based on various factors
            confidence_score = self._calculate_confidence_score(ticker, sector, subsector, risk_tolerance)
            
            return StockRecommendation(
                ticker=ticker,
                company_name=self._get_company_name(ticker),
                sector=sector,
                subsector=subsector,
                recommendation_reason=recommendation_reason,
                growth_potential=self._assess_growth_potential(sector, subsector),
                risk_level=self._assess_risk_level(subsector, risk_tolerance),
                market_cap=market_cap,
                current_price=0.0,  # Would be fetched from scraper
                target_price=0.0,   # Would be calculated
                confidence_score=confidence_score,
                key_advantages=self._get_key_advantages(ticker, sector),
                risks=self._get_risks(subsector),
                long_term_outlook=self._get_long_term_outlook(sector, subsector)
            )
        except Exception as e:
            print(f"Error creating recommendation for {ticker}: {e}")
            return None
    
    def _get_market_cap_category(self, ticker: str) -> str:
        """Determine market cap category for a ticker"""
        # This would be determined by actual market cap data
        large_caps = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "JNJ", "JPM", "V", "PG", "UNH"]
        mid_caps = ["AMD", "NVDA", "CRM", "ADBE", "PYPL", "NFLX", "TSLA", "UBER", "LYFT", "ZM"]
        
        if ticker in large_caps:
            return "Large Cap ($50B+)"
        elif ticker in mid_caps:
            return "Mid Cap ($10B-$50B)"
        else:
            return "Small Cap (<$10B)"
    
    def _generate_recommendation_reason(self, ticker: str, sector: str, subsector: str) -> str:
        """Generate a compelling reason for the recommendation"""
        reasons = {
            "Technology": {
                "Software & Services": "Leading position in enterprise software with strong recurring revenue model",
                "Hardware & Equipment": "Innovation leader with strong brand loyalty and ecosystem",
                "Semiconductors": "Critical supplier in high-growth semiconductor market"
            },
            "Healthcare": {
                "Pharmaceuticals": "Strong pipeline of innovative drugs with patent protection",
                "Biotechnology": "Cutting-edge technology with breakthrough potential",
                "Medical Devices": "Innovative medical solutions with regulatory approval"
            },
            "Financial Services": {
                "Commercial Banking": "Strong balance sheet with diversified revenue streams",
                "Investment Banking": "Market leader in M&A and capital markets",
                "Fintech": "Disruptive technology with rapid adoption"
            }
        }
        
        return reasons.get(sector, {}).get(subsector, "Strong fundamentals and growth potential")
    
    def _calculate_confidence_score(self, ticker: str, sector: str, subsector: str, risk_tolerance: str) -> float:
        """Calculate confidence score for recommendation"""
        base_score = 0.7
        
        # Adjust based on sector growth potential
        sector_growth = {"Technology": 0.2, "Healthcare": 0.15, "Financial Services": 0.1}
        base_score += sector_growth.get(sector, 0.05)
        
        # Adjust based on risk tolerance
        risk_adjustments = {"low": -0.1, "medium": 0.0, "high": 0.1}
        base_score += risk_adjustments.get(risk_tolerance.lower(), 0.0)
        
        # Add some randomness for demonstration
        import random
        base_score += random.uniform(-0.1, 0.1)
        
        return min(max(base_score, 0.0), 1.0)
    
    def _get_company_name(self, ticker: str) -> str:
        """Get company name for ticker"""
        names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "NVDA": "NVIDIA Corporation",
            "JNJ": "Johnson & Johnson",
            "JPM": "JPMorgan Chase & Co.",
            "V": "Visa Inc.",
            "PG": "Procter & Gamble Co.",
            "UNH": "UnitedHealth Group Inc."
        }
        return names.get(ticker, f"{ticker} Corporation")
    
    def _assess_growth_potential(self, sector: str, subsector: str) -> str:
        """Assess growth potential for sector/subsector combination"""
        high_growth = ["Technology", "Healthcare"]
        medium_growth = ["Financial Services", "Consumer Cyclical"]
        
        if sector in high_growth:
            return "High (15-25% annual growth potential)"
        elif sector in medium_growth:
            return "Medium (8-15% annual growth potential)"
        else:
            return "Moderate (5-10% annual growth potential)"
    
    def _assess_risk_level(self, subsector: str, risk_tolerance: str) -> str:
        """Assess risk level for subsector"""
        high_risk_subsectors = ["Biotechnology", "Semiconductors", "Fintech"]
        medium_risk_subsectors = ["Software & Services", "Medical Devices", "Investment Banking"]
        
        if subsector in high_risk_subsectors:
            return "High"
        elif subsector in medium_risk_subsectors:
            return "Medium"
        else:
            return "Low"
    
    def _get_key_advantages(self, ticker: str, sector: str) -> List[str]:
        """Get key competitive advantages"""
        advantages = {
            "Technology": ["Strong brand recognition", "Network effects", "High switching costs", "R&D leadership"],
            "Healthcare": ["Patent protection", "Regulatory barriers", "Clinical expertise", "Distribution networks"],
            "Financial Services": ["Scale advantages", "Regulatory compliance", "Customer relationships", "Technology infrastructure"]
        }
        return advantages.get(sector, ["Competitive positioning", "Market leadership", "Innovation capability"])
    
    def _get_risks(self, subsector: str) -> List[str]:
        """Get key risks for subsector"""
        risks = {
            "Software & Services": ["Competition from larger players", "Technology disruption", "Cybersecurity threats"],
            "Biotechnology": ["Clinical trial failures", "Regulatory delays", "Patent expirations"],
            "Semiconductors": ["Cyclical demand", "Technology obsolescence", "Supply chain disruptions"],
            "Fintech": ["Regulatory changes", "Cybersecurity risks", "Competition from incumbents"]
        }
        return risks.get(subsector, ["Market volatility", "Economic downturns", "Competitive pressures"])
    
    def _get_long_term_outlook(self, sector: str, subsector: str) -> str:
        """Get long-term outlook for sector/subsector"""
        outlooks = {
            "Technology": "Strong long-term growth driven by digital transformation and innovation",
            "Healthcare": "Favorable demographics and medical advances support sustained growth",
            "Financial Services": "Digital transformation and fintech innovation create opportunities"
        }
        return outlooks.get(sector, "Positive long-term outlook based on fundamental trends")
