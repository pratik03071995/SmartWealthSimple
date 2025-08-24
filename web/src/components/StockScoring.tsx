import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  TrendingUp, 
  Award, 
  BarChart3, 
  AlertTriangle, 
  Loader, 
  Plus, 
  X,
  ChevronDown,
  ChevronUp,
  Info,
  HelpCircle
} from 'lucide-react';

interface StockScore {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  marketCap: number;
  totalScore: number;
  grade: string;
  scores: Record<string, number>;
  details: Record<string, any>;
  weights: Record<string, number>;
}

// Tooltip Component
function Tooltip({ children, content, className = "" }: { 
  children: React.ReactNode; 
  content: string;
  className?: string;
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: true, left: '50%' });

  const handleMouseEnter = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;
    
    // Check if tooltip would go off screen
    const spaceAbove = rect.top;
    const spaceBelow = viewportHeight - rect.bottom;
    const spaceLeft = rect.left;
    const spaceRight = viewportWidth - rect.right;
    
    setPosition({
      top: spaceAbove > 150, // Show above if enough space
      left: spaceRight < 200 ? '85%' : spaceLeft < 200 ? '15%' : '50%'
    });
    setIsVisible(true);
  };

  return (
    <div 
      className={`relative ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, y: position.top ? -10 : 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: position.top ? -10 : 10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`absolute z-50 ${position.top ? 'bottom-full mb-2' : 'top-full mt-2'} px-3 py-2 bg-slate-800 text-white text-xs rounded-lg shadow-xl max-w-xs whitespace-pre-line border border-slate-600`}
            style={{ left: position.left, transform: 'translateX(-50%)' }}
          >
            {content}
            <div className={`absolute ${position.top ? 'top-full' : 'bottom-full'} left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 ${position.top ? 'border-t-4 border-transparent border-t-slate-800' : 'border-b-4 border-transparent border-b-slate-800'}`}></div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function StockScoring() {
  const [inputTicker, setInputTicker] = useState('');
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['NVDA', 'AAPL', 'MSFT']);
  const [results, setResults] = useState<StockScore[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  const addTicker = () => {
    const ticker = inputTicker.trim().toUpperCase();
    if (ticker && !selectedTickers.includes(ticker)) {
      setSelectedTickers([...selectedTickers, ticker]);
      setInputTicker('');
    }
  };

  const removeTicker = (ticker: string) => {
    setSelectedTickers(selectedTickers.filter(t => t !== ticker));
  };

  const scoreStocks = async () => {
    if (selectedTickers.length === 0) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/score-stocks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tickers: selectedTickers,
          manual_inputs: {}
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to score stocks');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'from-emerald-400 to-green-500';
    if (grade.startsWith('B')) return 'from-blue-400 to-cyan-500';
    if (grade.startsWith('C')) return 'from-yellow-400 to-orange-500';
    if (grade.startsWith('D')) return 'from-orange-500 to-red-500';
    return 'from-red-500 to-red-600';
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(1)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(1)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(1)}M`;
    return `$${marketCap.toLocaleString()}`;
  };

  const getCriteriaDisplayName = (key: string) => {
    const names: Record<string, string> = {
      business_fundamentals: 'Business Fundamentals',
      competitive_advantage: 'Competitive Advantage',
      management_quality: 'Management Quality',
      industry_attributes: 'Industry Attributes',
      valuation_metrics: 'Valuation Metrics',
      growth_catalysts: 'Growth Catalysts',
      risks_red_flags: 'Risk Assessment',
      macro_sensitivity: 'Macro Sensitivity',
      market_sentiment: 'Market Sentiment',
      vendors_supply_chain: 'Supply Chain',
      innovation_rd: 'Innovation & R&D',
      global_trends_alignment: 'Global Trends'
    };
    return names[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getCriteriaTooltip = (key: string, details: any, score: number) => {
    const detailData = details[key] || {};
    
    switch (key) {
      case 'business_fundamentals':
        return `💼 Business Performance (35% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `Revenue Growth: ${detailData.revenue_cagr || 'N/A'}\n` +
               `Profit Growth: ${detailData.eps_growth || 'N/A'}\n` +
               `Margins: ${detailData.margins || 'N/A'}`;
      
      case 'competitive_advantage':
        return `🏰 Competitive Moat (15% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.moat_assessment || 'Market position assessment'}\n\n` +
               `How protected is the company from competitors?`;
      
      case 'management_quality':
        return `👥 Leadership Quality (10% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.assessment || 'Management assessment'}\n\n` +
               `Are the executives competent and aligned?`;
      
      case 'industry_attributes':
        return `🏭 Industry Growth (10% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.assessment || 'Industry evaluation'}\n\n` +
               `Is the company in a growing sector?`;
      
      case 'valuation_metrics':
        return `💲 Fair Pricing (10% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.valuation || 'Price ratios'}\n\n` +
               `Are you paying a reasonable price?`;
      
      case 'growth_catalysts':
        return `🚀 Growth Drivers (5% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.catalysts || 'Growth potential'}\n\n` +
               `What could drive future growth?`;
      
      case 'risks_red_flags':
        return `⚠️ Risk Factors (-10% penalty)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.risks || 'Risk analysis'}\n\n` +
               `Financial or operational red flags`;
      
      case 'macro_sensitivity':
        return `🌍 Market Volatility (5% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.macro_sensitivity || 'Beta analysis'}\n\n` +
               `How much does it swing with the market?`;
      
      case 'market_sentiment':
        return `🧠 Professional Opinion (5% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.sentiment || 'Institutional data'}\n\n` +
               `What do big investors think?`;
      
      case 'vendors_supply_chain':
        return `🔗 Supply Chain (3% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.supply_chain || 'Operational resilience'}\n\n` +
               `Can they handle supply disruptions?`;
      
      case 'innovation_rd':
        return `💡 Innovation Ability (7% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.innovation || 'R&D metrics'}\n\n` +
               `How innovative is the company?`;
      
      case 'global_trends_alignment':
        return `🌟 Trend Alignment (5% weight)\nScore: ${score.toFixed(1)}/100\n\n` +
               `${detailData.trends || 'Mega-trend analysis'}\n\n` +
               `Riding AI, EV, cloud, or IoT trends?`;
      
      default:
        return `📊 ${getCriteriaDisplayName(key)}\nScore: ${score.toFixed(1)}/100`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-6 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <BarChart3 className="text-white" size={24} />
            </div>
            <h1 className="text-3xl font-bold text-slate-900">Stock Scoring System</h1>
          </div>
          <p className="text-slate-600 text-lg">
            Comprehensive analysis based on 12 financial criteria with weighted scoring
          </p>
          <div className="mt-4 flex items-center gap-4 text-sm text-slate-500">
            <span className="flex items-center gap-1">
              <HelpCircle size={16} />
              Hover over any score for detailed explanation
            </span>
            <span>•</span>
            <span>💯 90+ = Excellent</span>
            <span>•</span>
            <span>🟢 70+ = Good</span>
            <span>•</span>
            <span>🟡 50+ = Average</span>
            <span>•</span>
            <span>🔴 &lt;50 = Poor</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stock Input Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6 mb-8"
        >
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Search size={20} />
            Select Stocks to Analyze
          </h2>
          
          {/* Add Ticker Input */}
          <div className="flex gap-3 mb-4">
            <input
              type="text"
              value={inputTicker}
              onChange={(e) => setInputTicker(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && addTicker()}
              placeholder="Enter ticker symbol (e.g., NVDA)"
              className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              onClick={addTicker}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-200 flex items-center gap-2"
            >
              <Plus size={20} />
              Add
            </button>
          </div>

          {/* Selected Tickers */}
          <div className="flex flex-wrap gap-2 mb-4">
            {selectedTickers.map((ticker) => (
              <motion.span
                key={ticker}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-slate-100 text-slate-700 px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {ticker}
                <button
                  onClick={() => removeTicker(ticker)}
                  className="text-slate-500 hover:text-red-500 transition-colors"
                >
                  <X size={14} />
                </button>
              </motion.span>
            ))}
          </div>

          {/* Analyze Button */}
          <button
            onClick={scoreStocks}
            disabled={loading || selectedTickers.length === 0}
            className="w-full py-4 bg-gradient-to-r from-emerald-500 to-blue-600 text-white rounded-lg font-semibold text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={20} />
                Analyzing Stocks...
              </>
            ) : (
              <>
                <TrendingUp size={20} />
                Analyze {selectedTickers.length} Stock{selectedTickers.length !== 1 ? 's' : ''}
              </>
            )}
          </button>

          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700"
            >
              <AlertTriangle size={20} />
              {error}
            </motion.div>
          )}
        </motion.div>

        {/* Results Section */}
        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              <div className="flex items-center gap-2 mb-6">
                <Award className="text-emerald-500" size={24} />
                <h2 className="text-2xl font-bold text-slate-900">Analysis Results</h2>
                <span className="text-sm text-slate-500">({results.length} stocks)</span>
              </div>

              {results.map((stock, index) => (
                <motion.div
                  key={stock.ticker}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden"
                >
                  {/* Stock Header */}
                  <div className="p-6 border-b border-slate-100">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                          {stock.ticker.charAt(0)}
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-slate-900">{stock.ticker}</h3>
                          <p className="text-slate-600">{stock.name}</p>
                          <div className="flex items-center gap-4 mt-1 text-sm text-slate-500">
                            <span>{stock.sector}</span>
                            <span>•</span>
                            <span>{formatMarketCap(stock.marketCap)}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Score Badge */}
                      <div className="text-right">
                        <div className={`inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r ${getGradeColor(stock.grade)} text-white font-bold text-lg shadow-lg`}>
                          {stock.grade}
                        </div>
                        <div className="text-2xl font-bold text-slate-900 mt-2">
                          {stock.totalScore.toFixed(1)}/100
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Stats */}
                  <div className="p-4 bg-slate-50 border-b border-slate-100">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(stock.scores)
                        .sort(([,a], [,b]) => b - a)
                        .slice(0, 4)
                        .map(([criteria, score]) => (
                          <Tooltip
                            key={criteria}
                            content={getCriteriaTooltip(criteria, stock.details, score)}
                            className="text-center"
                          >
                            <div className="cursor-help hover:bg-white hover:shadow-sm rounded-lg p-2 transition-all duration-200">
                              <div className="text-sm text-slate-600 mb-1 flex items-center justify-center gap-1">
                                {getCriteriaDisplayName(criteria)}
                                <HelpCircle size={12} className="text-slate-400" />
                              </div>
                              <div className="text-lg font-semibold text-slate-900">
                                {score.toFixed(1)}
                              </div>
                            </div>
                          </Tooltip>
                        ))}
                    </div>
                  </div>

                  {/* Expandable Details */}
                  <div className="p-4">
                    <button
                      onClick={() => setExpandedCard(
                        expandedCard === stock.ticker ? null : stock.ticker
                      )}
                      className="w-full flex items-center justify-between py-2 text-left"
                    >
                      <span className="font-medium text-slate-700">
                        View Detailed Breakdown
                      </span>
                      {expandedCard === stock.ticker ? (
                        <ChevronUp className="text-slate-400" size={20} />
                      ) : (
                        <ChevronDown className="text-slate-400" size={20} />
                      )}
                    </button>

                    <AnimatePresence>
                      {expandedCard === stock.ticker && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          className="mt-4 space-y-3"
                        >
                          <div className="space-y-2">
                            {Object.entries(stock.scores).map(([criteria, score]) => {
                              const weight = stock.weights[criteria] || 0;
                              const isRisk = criteria === 'risks_red_flags';
                              
                              return (
                                <div key={criteria} className="w-full">
                                  <Tooltip
                                    content={getCriteriaTooltip(criteria, stock.details, score)}
                                    className="w-full block"
                                  >
                                    <div className="w-full border border-slate-200 rounded-lg p-4 hover:border-slate-300 hover:shadow-sm transition-all duration-200 cursor-help">
                                      <div className="flex items-center justify-between mb-3">
                                        <span className="font-medium text-slate-700 flex items-center gap-2">
                                          {getCriteriaDisplayName(criteria)}
                                          <Info size={14} className="text-slate-400" />
                                        </span>
                                        <div className="flex items-center gap-3">
                                          <span className="text-sm text-slate-500 bg-slate-100 px-2 py-1 rounded">
                                            {isRisk ? '-' : ''}{Math.abs(weight * 100).toFixed(0)}%
                                          </span>
                                          <span className="font-bold text-lg text-slate-900">
                                            {score.toFixed(1)}
                                          </span>
                                        </div>
                                      </div>
                                      
                                      {/* Progress Bar */}
                                      <div className="w-full bg-slate-200 rounded-full h-3">
                                        <div
                                          className={`h-3 rounded-full transition-all duration-500 ${
                                            score >= 80 ? 'bg-emerald-500' :
                                            score >= 60 ? 'bg-blue-500' :
                                            score >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                                          }`}
                                          style={{ width: `${score}%` }}
                                        />
                                      </div>
                                    </div>
                                  </Tooltip>
                                </div>
                              );
                            })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
