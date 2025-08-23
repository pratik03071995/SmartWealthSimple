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

interface SubsectorData {
  sector: string;
  subsectors: string[];
  subsector_count: number;
  last_updated: string;
}

const SectorCompanySelector: React.FC = () => {
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [selectedSectors, setSelectedSectors] = useState<string[]>([]);
  const [availableSubsectors, setAvailableSubsectors] = useState<string[]>([]);
  const [selectedSubsectors, setSelectedSubsectors] = useState<string[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingSubsectors, setLoadingSubsectors] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<'sectors' | 'subsectors' | 'companies'>('sectors');

  // Fetch available sectors on component mount
  useEffect(() => {
    fetchSectors();
  }, []);

  // Fetch subsectors when sectors are selected
  useEffect(() => {
    if (selectedSectors.length > 0) {
      fetchSubsectors();
    } else {
      setAvailableSubsectors([]);
      setSelectedSubsectors([]);
    }
  }, [selectedSectors]);

  const fetchSectors = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5001/api/ai/sectors');
      const data = await response.json();
      setSectors(data.sectors || []);
    } catch (err) {
      setError('Failed to fetch sectors');
    }
  };

  const fetchSubsectors = async () => {
    setLoadingSubsectors(true);
    setError(null);
    
    try {
      const allSubsectors = new Set<string>();
      
      for (const sector of selectedSectors) {
        try {
          const response = await fetch(`http://127.0.0.1:5001/api/ai/sectors/${encodeURIComponent(sector)}/subsectors`);
          const data: SubsectorData = await response.json();
          if (data.subsectors) {
            data.subsectors.forEach(subsector => allSubsectors.add(subsector));
          }
        } catch (err) {
          console.error(`Failed to fetch subsectors for ${sector}:`, err);
        }
      }
      
      setAvailableSubsectors(Array.from(allSubsectors));
    } catch (err) {
      setError('Failed to fetch subsectors');
    } finally {
      setLoadingSubsectors(false);
    }
  };

  const fetchCompanies = async () => {
    if (selectedSectors.length === 0 && selectedSubsectors.length === 0) {
      setError('Please select at least one sector or subsector');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep('companies');

    try {
      const response = await fetch('http://127.0.0.1:5001/api/companies/dynamic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sectors: selectedSectors,
          subsectors: selectedSubsectors,
          limit: 50
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setCompanies(data.companies || []);
      } else {
        setError(data.error || 'Failed to fetch companies');
      }
    } catch (err) {
      setError('Failed to fetch companies');
    } finally {
      setLoading(false);
    }
  };

  const handleSectorToggle = (sectorName: string) => {
    setSelectedSectors(prev => 
      prev.includes(sectorName) 
        ? prev.filter(s => s !== sectorName)
        : [...prev, sectorName]
    );
  };

  const handleSubsectorToggle = (subsectorName: string) => {
    setSelectedSubsectors(prev => 
      prev.includes(subsectorName) 
        ? prev.filter(s => s !== subsectorName)
        : [...prev, subsectorName]
    );
  };

  const handleNextStep = () => {
    if (currentStep === 'sectors' && selectedSectors.length > 0) {
      setCurrentStep('subsectors');
    } else if (currentStep === 'subsectors') {
      fetchCompanies();
    }
  };

  const handleBackStep = () => {
    if (currentStep === 'subsectors') {
      setCurrentStep('sectors');
    } else if (currentStep === 'companies') {
      setCurrentStep('subsectors');
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Sector-Based Company Selector
        </h1>
        <p className="text-gray-600">
          Select sectors and subsectors to find top companies by market cap
        </p>
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
          <div className={`flex items-center ${currentStep === 'subsectors' || currentStep === 'companies' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              currentStep === 'subsectors' ? 'border-blue-600 bg-blue-600 text-white' : 
              currentStep === 'companies' ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Subsectors</span>
          </div>
          <div className="w-8 h-0.5 bg-gray-300"></div>
          <div className={`flex items-center ${currentStep === 'companies' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${
              currentStep === 'companies' ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-300'
            }`}>
              3
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
            <div className="mt-6 text-center">
              <motion.button
                onClick={handleNextStep}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Next: Select Subsectors ({selectedSectors.length} selected)
              </motion.button>
            </div>
          )}
        </motion.div>
      )}

      {/* Step 2: Subsector Selection */}
      {currentStep === 'subsectors' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Step 2: Select Subsectors</h2>
              <button
                onClick={handleBackStep}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                ← Back to Sectors
              </button>
            </div>
            
            {loadingSubsectors ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading subsectors...</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {availableSubsectors.map((subsector) => (
                    <motion.button
                      key={subsector}
                      onClick={() => handleSubsectorToggle(subsector)}
                      className={`p-3 rounded-xl text-left transition-all ${
                        selectedSubsectors.includes(subsector)
                          ? 'bg-green-50 border-2 border-green-200 text-green-900'
                          : 'bg-gray-50 border-2 border-gray-200 text-gray-700 hover:bg-gray-100'
                      }`}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <div className="font-medium">{subsector}</div>
                    </motion.button>
                  ))}
                </div>
                
                <div className="mt-6 text-center">
                  <motion.button
                    onClick={handleNextStep}
                    disabled={selectedSubsectors.length === 0}
                    className={`px-8 py-3 rounded-xl font-semibold ${
                      selectedSubsectors.length === 0
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                    whileHover={selectedSubsectors.length > 0 ? { scale: 1.05 } : {}}
                    whileTap={selectedSubsectors.length > 0 ? { scale: 0.95 } : {}}
                  >
                    {selectedSubsectors.length === 0 
                      ? 'Select at least one subsector'
                      : `Get Top Companies (${selectedSubsectors.length} selected)`
                    }
                  </motion.button>
                </div>
              </>
            )}
          </div>
        </motion.div>
      )}

      {/* Selected Items Display */}
      {(selectedSectors.length > 0 || selectedSubsectors.length > 0) && currentStep !== 'companies' && (
        <div className="bg-blue-50 rounded-2xl p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Selected:</h3>
          <div className="flex flex-wrap gap-2">
            {selectedSectors.map((sector) => (
              <span key={sector} className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm">
                {sector}
              </span>
            ))}
            {selectedSubsectors.map((subsector) => (
              <span key={subsector} className="bg-green-200 text-green-800 px-3 py-1 rounded-full text-sm">
                {subsector}
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
              ← Back to Subsectors
            </button>
          </div>

          {loading ? (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading companies...</p>
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
              <p className="text-gray-600">No companies found. Try selecting different sectors or subsectors.</p>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};

export default SectorCompanySelector;
