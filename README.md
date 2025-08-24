# SmartWealthAI

A comprehensive financial data analysis and stock recommendation platform that combines web scraping, AI-powered analysis, and real-time streaming data visualization.

## 🚀 Features

### Core Functionality
- **Real-time Stock Data Streaming**: Companies appear as they're discovered with smooth animations
- **Sector-based Company Filtering**: Strict filtering to show only companies from selected sectors
- **Interactive Table Sorting**: Sort by any column (Company, Price, Change, Market Cap, P/E, Volume)
- **Multi-source Data Scraping**: Yahoo Finance, Morningstar, Seeking Alpha, Finviz, CNBC, MarketWatch
- **AI-powered Stock Recommendations**: LLM integration for intelligent analysis
- **Modern React Frontend**: Built with Vite, TypeScript, and Framer Motion

### Data Sources
- **Yahoo Finance**: Stock prices, market data, earnings calendar
- **Morningstar**: Fund analysis, sector performance, ETF data
- **Seeking Alpha**: Stock analysis, earnings reports, dividends
- **Finviz**: Technical analysis, stock screening, insider trading
- **CNBC & MarketWatch**: Financial news and market updates

### AI Integration
- **Local LLM Support**: Microsoft DialoGPT-medium for offline analysis
- **Sector Analysis**: Intelligent sector growth and risk assessment
- **Stock Recommendations**: Multi-factor scoring system
- **Sentiment Analysis**: News sentiment using TextBlob

## 🛠️ Technology Stack

### Backend
- **Python 3.12**: Core application logic
- **Flask**: RESTful API framework
- **BeautifulSoup4 & Selenium**: Web scraping
- **yfinance**: Yahoo Finance data integration
- **Transformers**: Local LLM integration
- **ThreadPoolExecutor**: Concurrent data processing

### Frontend
- **React 18**: User interface
- **TypeScript**: Type safety
- **Vite**: Fast development and building
- **Tailwind CSS**: Styling
- **Framer Motion**: Smooth animations
- **Fetch API**: Real-time streaming

## 📦 Installation

### Prerequisites
- Python 3.12
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd SmartWealthAI

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd SmartWealthSimple/app
pip install -r requirements.txt

# Start the Flask server
python app.py
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd SmartWealthSimple/web

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🎯 Usage

### Getting Started
1. **Start Backend**: Flask server runs on `http://127.0.0.1:5001`
2. **Start Frontend**: Vite dev server runs on `http://localhost:5173`
3. **Navigate to Sectors**: Select sectors to find companies
4. **Watch Streaming**: Companies appear in real-time as they're discovered
5. **Sort Data**: Click column headers to sort the table

### API Endpoints

#### Core Endpoints
- `GET /api/ai/sectors` - Get available sectors
- `POST /api/companies/dynamic` - Get companies with streaming support
- `GET /api/stock/{ticker}` - Get stock information
- `GET /api/news` - Get financial news
- `GET /api/market-movers` - Get market movers

#### AI Endpoints
- `GET /api/ai/sectors/{sector}/subsectors` - Get subsectors for a sector
- `POST /api/ai/recommendations` - Get AI-powered stock recommendations
- `GET /api/ai/analysis/{sector}` - Get sector analysis

#### Data Endpoints
- `GET /api/earnings` - Get earnings calendar
- `GET /api/funds` - Get fund information
- `GET /api/etfs` - Get ETF data
- `GET /api/screening` - Stock screening
- `GET /api/dividends` - Dividend information

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the `SmartWealthSimple/app` directory:

```env
# API Keys (optional for basic functionality)
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# LLM Configuration
LLM_MODEL=microsoft/DialoGPT-medium
LLM_DEVICE=cpu

# Scraping Configuration
SCRAPING_DELAY=1
MAX_CONCURRENT_REQUESTS=5
```

## 📊 Features in Detail

### Real-time Streaming
- Companies appear as they're fetched from multiple sources
- Smooth animations with staggered delays
- Live count updates during loading
- Graceful fallback to regular requests if streaming fails

### Sector Filtering
- Strict filtering ensures only companies from selected sectors are shown
- Removed subsector complexity for simplified user experience
- Multiple sector selection supported
- Real-time validation and error handling

### Table Sorting
- Click any column header to sort
- Visual indicators show current sort field and direction
- Toggle between ascending and descending order
- Maintains sorting during streaming updates

### Error Handling
- Comprehensive error messages
- Graceful fallbacks for failed requests
- Console logging for debugging
- User-friendly error displays

## 🚀 Performance

### Optimizations
- **Concurrent Scraping**: Multiple sources processed simultaneously
- **Streaming Responses**: Real-time data delivery
- **Caching**: Intelligent caching of frequently accessed data
- **Lazy Loading**: Components load only when needed

### Scalability
- **Modular Architecture**: Easy to add new data sources
- **Configurable Limits**: Adjustable request limits and delays
- **Error Recovery**: Automatic retry mechanisms
- **Resource Management**: Efficient memory and CPU usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [Issues](https://github.com/your-repo/issues) page
- Review the API documentation
- Test with the provided examples

## 🔮 Roadmap

### Planned Features
- [ ] Portfolio tracking and analysis
- [ ] Advanced technical indicators
- [ ] Machine learning price predictions
- [ ] Mobile app support
- [ ] Real-time alerts and notifications
- [ ] Social trading features
- [ ] Advanced charting capabilities
- [ ] API rate limiting and authentication

### Performance Improvements
- [ ] Database integration for caching
- [ ] Redis for session management
- [ ] CDN for static assets
- [ ] Load balancing for high traffic
- [ ] Microservices architecture

---

**SmartWealthAI** - Making financial data analysis intelligent and accessible! 🚀📈
