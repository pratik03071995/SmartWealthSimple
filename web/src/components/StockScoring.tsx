import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, TrendingUp, Info, CheckCircle, AlertCircle } from 'lucide-react';
import { useCompanies } from '../context/CompaniesContext';

interface Company {
  ticker: string;
  name: string;
  current_price: number;
  price_change_pct: number;
  market_cap: number;
  pe_ratio: number;
  sector: string;
  industry: string;
  volume: number;
  avg_volume: number;
}

interface ScoringResult {
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
    
    const spaceAbove = rect.top;
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

const StockScoring: React.FC = () => {
  const { companies, hasCompanies } = useCompanies();
  const [selectedTickers, setSelectedTickers] = useState<string[]>([]);
  const [scoringResults, setScoringResults] = useState<ScoringResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [expandedStocks, setExpandedStocks] = useState<Set<string>>(new Set());

  const handleTickerToggle = (ticker: string) => {
    setSelectedTickers(prev => 
      prev.includes(ticker) 
        ? prev.filter(t => t !== ticker)
        : [...prev, ticker]
    );
  };

  const toggleStockExpansion = (ticker: string) => {
    setExpandedStocks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(ticker)) {
        newSet.delete(ticker);
      } else {
        newSet.add(ticker);
      }
      return newSet;
    });
  };

  const handleScoreStocks = async () => {
    if (selectedTickers.length === 0) {
      setError('Please select at least one stock to score');
      return;
    }

    setLoading(true);
    setError(null);

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

      const results = await response.json();
      setScoringResults(results);
      setShowResults(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to score stocks');
    } finally {
      setLoading(false);
    }
  };

  const getCriteriaTooltip = (criteria: string, score: number, weight: number, details: any) => {
    const criteriaInfo: Record<string, string> = {
      'business_fundamentals': '📊 Business Fundamentals (35%)\nRevenue growth, margins, ROE, cash flow',
      'competitive_advantage': '🛡️ Competitive Advantage (15%)\nMarket position, moats, brand strength',
      'management_quality': '👥 Management Quality (10%)\nLeadership, insider ownership, track record',
      'industry_attributes': '🏭 Industry Attributes (10%)\nGrowth potential, sector dynamics',
      'valuation_metrics': '💰 Valuation Metrics (10%)\nP/E, PEG, EV/EBITDA, P/B ratios',
      'growth_catalysts': '🚀 Growth Catalysts (5%)\nRevenue growth, expansion opportunities',
      'risks_red_flags': '⚠️ Risks & Red Flags (-10%)\nDebt, liquidity, negative margins',
      'macro_sensitivity': '🌍 Macro Sensitivity (5%)\nBeta, market correlation',
      'market_sentiment': '📈 Market Sentiment (5%)\nInstitutional ownership, analyst ratings',
      'vendors_supply_chain': '🔗 Supply Chain (3%)\nVendor relationships, supply chain strength',
      'innovation_rd': '🔬 Innovation & R&D (7%)\nTechnology focus, employee talent',
      'global_trends_alignment': '🌐 Global Trends (5%)\nAI, EV, clean energy alignment'
    };

    const info = criteriaInfo[criteria] || criteria;
    const detailText = details ? `\n\nDetails: ${JSON.stringify(details, null, 2)}` : '';
    
    return `${info}\n\nScore: ${score.toFixed(1)}/100\nWeight: ${(weight * 100).toFixed(1)}%${detailText}`;
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toLocaleString()}`;
  };

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600';
    if (grade.startsWith('B')) return 'text-blue-600';
    if (grade.startsWith('C')) return 'text-yellow-600';
    if (grade.startsWith('D')) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Stock Scoring Analysis
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Select stocks from the companies table below to analyze them using our comprehensive 12-criteria scoring system
          </p>
        </div>

        {/* No Companies Message */}
        {!hasCompanies && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-12 text-center"
          >
            <div className="text-gray-400 mb-4">
              <BarChart3 size={64} className="mx-auto" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Companies Available</h3>
            <p className="text-gray-600">
              Please go to the Sector Company Selector page first to load companies, then return here to score them.
            </p>
          </motion.div>
        )}

        {/* Companies Table */}
        {hasCompanies && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-gray-900">
                Available Companies ({companies.length})
              </h2>
              <div className="text-sm text-gray-500">
                {selectedTickers.length} selected
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Select</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-900">Company</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Price</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Change</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Market Cap</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">P/E</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-900">Sector</th>
                  </tr>
                </thead>
                <tbody>
                  {companies.map((company) => (
                    <motion.tr
                      key={company.ticker}
                      className="border-b border-gray-100 hover:bg-gray-50"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                    >
                      <td className="py-3 px-4">
                        <input
                          type="checkbox"
                          checked={selectedTickers.includes(company.ticker)}
                          onChange={() => handleTickerToggle(company.ticker)}
                          className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                      </td>
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-semibold text-gray-900">{company.ticker}</div>
                          <div className="text-sm text-gray-500">{company.name}</div>
                        </div>
                      </td>
                      <td className="text-right py-3 px-4 font-semibold text-gray-900">
                        ${company.current_price.toFixed(2)}
                      </td>
                      <td className={`text-right py-3 px-4 font-semibold ${
                        company.price_change_pct >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {company.price_change_pct >= 0 ? '+' : ''}{company.price_change_pct.toFixed(2)}%
                      </td>
                      <td className="text-right py-3 px-4 text-gray-700">
                        {formatMarketCap(company.market_cap)}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-700">
                        {company.pe_ratio > 0 ? company.pe_ratio.toFixed(1) : 'N/A'}
                      </td>
                      <td className="text-right py-3 px-4 text-gray-700">
                        {company.sector}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>

            {selectedTickers.length > 0 && (
              <div className="mt-6 text-center">
                <motion.button
                  onClick={handleScoreStocks}
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-semibold text-lg"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Analyzing Stocks...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <BarChart3 className="w-5 h-5" />
                      <span>Analyze Selected Stocks ({selectedTickers.length})</span>
                    </div>
                  )}
                </motion.button>
              </div>
            )}
          </motion.div>
        )}

        {/* No Companies Message */}
        {companies.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center"
          >
            <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Companies Available
            </h3>
            <p className="text-gray-600">
              Please go to the Sector Company Selector page first to load companies, then return here to score them.
            </p>
          </motion.div>
        )}

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 border border-red-200 rounded-xl p-4"
          >
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </motion.div>
        )}

        {/* Scoring Results */}
        {showResults && scoringResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Scoring Results
              </h2>
              <p className="text-gray-600">
                Comprehensive analysis of {scoringResults.length} stocks using 12 criteria
              </p>
            </div>

                         {/* Quick Stats */}
             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
               {scoringResults.slice(0, 3).map((result, index) => (
                 <motion.div
                   key={result.ticker}
                   initial={{ opacity: 0, y: 20 }}
                   animate={{ opacity: 1, y: 0 }}
                   transition={{ delay: index * 0.1 }}
                   className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
                   onClick={() => toggleStockExpansion(result.ticker)}
                 >
                   <div className="text-center">
                     <div className="text-2xl font-bold text-gray-900 mb-2">
                       {result.ticker}
                     </div>
                     <div className="text-lg text-gray-600 mb-2">
                       {result.name}
                     </div>
                     <div className={`text-4xl font-bold mb-2 ${getGradeColor(result.grade)}`}>
                       {result.grade}
                     </div>
                     <div className="text-2xl font-semibold text-blue-600">
                       {result.totalScore.toFixed(1)}
                     </div>
                     <div className="text-sm text-gray-500">
                       {result.sector} • {result.industry}
                     </div>
                     <div className="mt-3 text-sm text-blue-600 font-medium">
                       {expandedStocks.has(result.ticker) ? 'Click to collapse' : 'Click to expand'}
                     </div>
                   </div>
                 </motion.div>
               ))}
             </div>

                         {/* Detailed Breakdown */}
             <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
               <h3 className="text-xl font-semibold text-gray-900 mb-6">
                 Detailed Breakdown
               </h3>
               
               {scoringResults.map((result, resultIndex) => (
                 <div key={result.ticker} className="mb-6 last:mb-0">
                   {/* Stock Header - Clickable to expand/collapse */}
                   <div 
                     className="border-b border-gray-200 pb-4 mb-4 cursor-pointer hover:bg-gray-50 p-3 rounded-lg transition-colors"
                     onClick={() => toggleStockExpansion(result.ticker)}
                   >
                     <div className="flex items-center justify-between">
                       <div>
                         <h4 className="text-lg font-semibold text-gray-900 mb-2">
                           {result.ticker} - {result.name}
                         </h4>
                         <div className="flex items-center space-x-4 text-sm text-gray-600">
                           <span>Total Score: <span className="font-semibold">{result.totalScore.toFixed(1)}</span></span>
                           <span>Grade: <span className={`font-semibold ${getGradeColor(result.grade)}`}>{result.grade}</span></span>
                           <span>Sector: {result.sector}</span>
                         </div>
                       </div>
                       <div className="text-blue-600 font-medium">
                         {expandedStocks.has(result.ticker) ? '▼ Collapse' : '▶ Expand'}
                       </div>
                     </div>
                   </div>

                   {/* Detailed Scores - Only show when expanded */}
                   {expandedStocks.has(result.ticker) && (
                     <motion.div
                       initial={{ opacity: 0, height: 0 }}
                       animate={{ opacity: 1, height: 'auto' }}
                       exit={{ opacity: 0, height: 0 }}
                       transition={{ duration: 0.3 }}
                       className="space-y-3"
                     >
                       {Object.entries(result.scores).map(([criteria, score]) => {
                         const weight = result.weights[criteria] || 0;
                         const details = result.details[criteria] || {};
                         const tooltipContent = getCriteriaTooltip(criteria, score, weight, details);
                         
                         return (
                           <div key={criteria} className="w-full block">
                             <div className="flex items-center justify-between mb-2">
                               <div className="flex items-center space-x-2">
                                 <Tooltip content={tooltipContent}>
                                   <Info className="w-4 h-4 text-gray-500 cursor-help" />
                                 </Tooltip>
                                 <span className="font-medium text-gray-700 capitalize">
                                   {criteria.replace(/_/g, ' ')}
                                 </span>
                               </div>
                               <div className="flex items-center space-x-3">
                                 <span className="text-sm text-gray-600">
                                   {(weight * 100).toFixed(1)}%
                                 </span>
                                 <span className="font-semibold text-gray-900">
                                   {score.toFixed(1)}
                                 </span>
                               </div>
                             </div>
                             
                             <div className="w-full bg-gray-200 rounded-full h-3">
                               <motion.div
                                 className="bg-blue-600 h-3 rounded-full"
                                 initial={{ width: 0 }}
                                 animate={{ width: `${score}%` }}
                                 transition={{ duration: 0.8, delay: resultIndex * 0.1 }}
                               />
                             </div>
                           </div>
                         );
                       })}
                     </motion.div>
                   )}
                 </div>
               ))}
             </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default StockScoring;
