import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

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

interface SectorData {
  name: string;
  description: string;
  growth_potential: string;
  risk_level: string;
  subsector_count: number;
  key_drivers: string[];
}

type SortField = 'ticker' | 'name' | 'current_price' | 'price_change_pct' | 'market_cap' | 'pe_ratio' | 'volume';
type SortDirection = 'asc' | 'desc';

const SectorCompanySelector: React.FC = () => {
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'sectors' | 'companies'>('sectors');
  const [sortField, setSortField] = useState<SortField>('market_cap');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Fetch available sectors on component mount
  useEffect(() => {
    fetchSectors();
  }, []);

  // Monitor companies state changes
  useEffect(() => {
    // Companies state updated
  }, [companies]);

  const fetchSectors = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/ai/sectors');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.sectors && Array.isArray(data.sectors)) {
        setSectors(data.sectors);
      } else {
        console.error('Invalid sectors data format:', data);
        setError('Invalid sectors data format');
      }
    } catch (err) {
      console.error('Sectors fetch error:', err);
      setError('Failed to fetch sectors');
    }
  };

  const fetchCompanies = async () => {
    if (selectedSectors.length === 0) {
      setError('Please select at least one sector');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep('companies');
    setCompanies([]); // Clear previous companies

    console.log('Fetching companies for sectors:', selectedSectors);

    try {
      const response = await fetch('http://127.0.0.1:5001/api/companies/dynamic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sectors: selectedSectors,
          limit: 50,
          streaming: true // Enable streaming
        }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        setError(errorData.error || 'Failed to fetch companies');
        setLoading(false);
        return;
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (reader) {
        try {
          while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            
            // Keep the last line in buffer if it's incomplete
            buffer = lines.pop() || '';
            
            for (const line of lines) {
              if (line.trim() && line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.status === 'started') {
                    console.log('Started:', data.message);
                  } else if (data.status === 'progress' && data.company) {
                    // Add company to the list as it's received - simplified approach
                    setCompanies(prev => {
                      const newCompanies = [...prev, data.company];
                      return [...newCompanies];
                    });
                  } else if (data.status === 'completed') {
                    setLoading(false);
                    return;
                  } else if (data.status === 'error') {
                    setError(data.error);
                    setLoading(false);
                    return;
                  }
                } catch (parseError) {
                  console.error('Error parsing streaming data:', parseError, 'Line:', line);
                }
              }
            }
          }
        } catch (streamError) {
          console.error('Streaming error:', streamError);
          setError('Streaming failed, falling back to regular request');
          
          // Fallback to non-streaming request
          const fallbackResponse = await fetch('http://127.0.0.1:5001/api/companies/dynamic', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              sectors: selectedSectors,
              limit: 50,
              streaming: false
            }),
          });
          
          if (fallbackResponse.ok) {
            const data = await fallbackResponse.json();
            if (data.companies && Array.isArray(data.companies)) {
              setCompanies(sortCompanies(data.companies, sortField, sortDirection));
            }
          } else {
            setError('Failed to fetch companies');
          }
        }
      } else {
        // Fallback to regular response if streaming not supported
        const data = await response.json();
        if (data.companies && Array.isArray(data.companies)) {
          setCompanies(sortCompanies(data.companies, sortField, sortDirection));
        } else {
          setError('Invalid response format from server');
        }
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Failed to fetch companies');
    } finally {
      setLoading(false);
    }
  };

  const sortCompanies = (companies: Company[], field: SortField, direction: SortDirection): Company[] => {
    return [...companies].sort((a, b) => {
      let aValue: any = a[field];
      let bValue: any = b[field];
      
      // Handle string comparison
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      // Handle numeric comparison
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        if (direction === 'asc') {
          return aValue - bValue;
        } else {
          return bValue - aValue;
        }
      }
      
      // Handle string comparison
      if (direction === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    });
  };

  const handleSort = (field: SortField) => {
    const newDirection = sortField === field && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortField(field);
    setSortDirection(newDirection);
    setCompanies(prev => sortCompanies(prev, field, newDirection));
  };

  const handleSectorToggle = (sectorName: string) => {
    setSelectedSectors(prev => 
      prev.includes(sectorName) 
        ? prev.filter(s => s !== sectorName)
        : [...prev, sectorName]
    );
  };

  const handleNextStep = () => {
    if (currentStep === 'sectors' && selectedSectors.length > 0) {
      fetchCompanies();
    }
  };

  const handleBackStep = () => {
    if (currentStep === 'companies') {
      setCurrentStep('sectors');
    }
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) return `$${(marketCap / 1e12).toFixed(2)}T`;
    if (marketCap >= 1e9) return `$${(marketCap / 1e9).toFixed(2)}B`;
    if (marketCap >= 1e6) return `$${(marketCap / 1e6).toFixed(2)}M`;
    return `$${marketCap.toLocaleString()}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e9) return `${(volume / 1e9).toFixed(2)}B`;
    if (volume >= 1e6) return `${(volume / 1e6).toFixed(2)}M`;
    return volume.toLocaleString();
  };

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) return '↕️';
    return sortDirection === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Sector-Based Company Selector
        </h1>
        <p className="text-gray-600 mb-4">
          Select sectors to find top companies by market cap
        </p>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 max-w-2xl mx-auto">
          <p className="text-blue-800 text-sm">
            <strong>How to use:</strong> Select one or more sectors below, then click "Get Companies Now" to see the top companies by market cap. 
          </p>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-center mb-6">
        <div className="flex items-center space-x-4">
          <div className={`flex items-center ${currentStep === 'sectors' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              currentStep === 'sectors' ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              1
            </div>
            <span className="ml-2 font-medium">Sectors</span>
          </div>
          <div className="w-8 h-0.5 bg-gray-300"></div>
          <div className={`flex items-center ${currentStep === 'companies' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              currentStep === 'companies' ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Companies</span>
          </div>
        </div>
      </div>

      {/* Step 1: Sector Selection */}
      {currentStep === 'sectors' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6"
        >
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Step 1: Select Sectors</h2>
          <p className="text-gray-600 mb-4">Choose one or more sectors to find top companies by market cap</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {sectors.map((sector) => (
              <motion.button
                key={sector.name}
                onClick={() => handleSectorToggle(sector.name)}
                className={`p-3 rounded-xl text-left transition-all ${
                  selectedSectors.includes(sector.name)
                    ? 'bg-blue-50 border-2 border-blue-200 text-blue-900'
                    : 'bg-gray-50 border-2 border-gray-200 text-gray-700 hover:bg-gray-100'
                }`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="font-medium">{sector.name}</div>
                <div className="text-sm text-gray-500 mt-1">
                  {sector.subsector_count} subsectors
                </div>
              </motion.button>
            ))}
          </div>
          
          {selectedSectors.length > 0 && (
            <div className="mt-6 text-center space-y-3">
              <motion.button
                onClick={handleNextStep}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Next: Get Companies ({selectedSectors.length} selected)
              </motion.button>
            </div>
          )}
        </motion.div>
      )}

      {/* Selected Items Display */}
      {selectedSectors.length > 0 && currentStep !== 'companies' && (
        <div className="bg-blue-50 rounded-2xl p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Selected:</h3>
          <div className="flex flex-wrap gap-2">
            {selectedSectors.map((sector) => (
              <span key={sector} className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                {sector}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Step 3: Companies Display */}
      {currentStep === 'companies' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">Step 3: Top Companies</h2>
            <button
              onClick={handleBackStep}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Back to Sectors
            </button>
          </div>

          {loading ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  Loading Companies... {companies.length > 0 && `(${companies.length} found so far)`}
                </h3>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              </div>
              
              {/* Always show companies if they exist, even during loading */}
              {companies.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Company</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-900">Price</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-900">Change</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-900">Market Cap</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-900">P/E</th>
                        <th className="text-right py-3 px-4 font-semibold text-gray-900">Volume</th>
                      </tr>
                    </thead>
                    <tbody>
                      {companies.map((company, index) => (
                        <motion.tr
                          key={`${company.ticker}-${index}`}
                          className="border-b border-gray-100"
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                        >
                          <td className="py-3 px-4">
                            <div>
                              <div className="font-semibold text-gray-900">{company.ticker}</div>
                              <div className="text-sm text-gray-500">{company.name}</div>
                              <div className="text-xs text-gray-400">{company.sector} • {company.industry}</div>
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
                            {formatVolume(company.volume)}
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              
              {/* Show spinner only if no companies yet */}
              {companies.length === 0 && (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-4 text-gray-600">Fetching companies...</p>
                </div>
              )}
            </div>
          ) : companies.length > 0 ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Top Companies ({companies.length})
              </h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th 
                        className="text-left py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('ticker')}
                      >
                        <div className="flex items-center">
                          Company {getSortIcon('ticker')}
                        </div>
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('current_price')}
                      >
                        <div className="flex items-center justify-end">
                          Price {getSortIcon('current_price')}
                        </div>
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('price_change_pct')}
                      >
                        <div className="flex items-center justify-end">
                          Change {getSortIcon('price_change_pct')}
                        </div>
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('market_cap')}
                      >
                        <div className="flex items-center justify-end">
                          Market Cap {getSortIcon('market_cap')}
                        </div>
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('pe_ratio')}
                      >
                        <div className="flex items-center justify-end">
                          P/E {getSortIcon('pe_ratio')}
                        </div>
                      </th>
                      <th 
                        className="text-right py-3 px-4 font-semibold text-gray-900 cursor-pointer hover:bg-gray-50"
                        onClick={() => handleSort('volume')}
                      >
                        <div className="flex items-center justify-end">
                          Volume {getSortIcon('volume')}
                        </div>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {companies.map((company, index) => (
                      <motion.tr
                        key={company.ticker}
                        className="border-b border-gray-100 hover:bg-gray-50"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                      >
                        <td className="py-3 px-4">
                          <div>
                            <div className="font-semibold text-gray-900">{company.ticker}</div>
                            <div className="text-sm text-gray-500">{company.name}</div>
                            <div className="text-xs text-gray-400">{company.sector} • {company.industry}</div>
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
                          {formatVolume(company.volume)}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
              <p className="text-gray-600">No companies found. Try selecting different sectors.</p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default SectorCompanySelector;
