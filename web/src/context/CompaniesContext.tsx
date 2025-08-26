import React, { createContext, useContext, useState, ReactNode } from 'react';

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

interface CompaniesContextType {
  companies: Company[];
  setCompanies: (companies: Company[]) => void;
  addCompany: (company: Company) => void;
  clearCompanies: () => void;
  hasCompanies: boolean;
}

const CompaniesContext = createContext<CompaniesContextType | undefined>(undefined);

export const CompaniesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [companies, setCompanies] = useState<Company[]>([]);

  const addCompany = (company: Company) => {
    setCompanies(prev => {
      // Avoid duplicates based on ticker
      if (prev.some(c => c.ticker === company.ticker)) {
        return prev;
      }
      return [...prev, company];
    });
  };

  const clearCompanies = () => {
    setCompanies([]);
  };

  const hasCompanies = companies.length > 0;

  return (
    <CompaniesContext.Provider value={{ 
      companies, 
      setCompanies, 
      addCompany, 
      clearCompanies, 
      hasCompanies 
    }}>
      {children}
    </CompaniesContext.Provider>
  );
};

export const useCompanies = () => {
  const context = useContext(CompaniesContext);
  if (!context) {
    throw new Error('useCompanies must be used within a CompaniesProvider');
  }
  return context;
};
