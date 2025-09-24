# 📈 Stock Screener Dashboard

A modern, interactive web application for screening stocks based on technical and fundamental analysis criteria.

![Dashboard Screenshot](https://via.placeholder.com/800x400?text=Stock+Screener+Dashboard)

## 🌟 Features

- **Interactive Filtering**: Adjust P/E ratios, price ranges, market cap, and technical indicators
- **Real-time Analysis**: Live progress tracking during stock screening
- **Visual Charts**: Sector distribution, RSI histograms, and candlestick price charts
- **Export Capabilities**: Download results as CSV for further analysis
- **Modern UI**: Responsive design with gradient styling and smooth interactions

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Stock-Picks
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the dashboard**
   ```bash
   streamlit run dashboard.py
   ```

5. **Access the app** at `http://localhost:8501`

## 🌐 Deployment Options

### Option 1: Streamlit Community Cloud (FREE & EASIEST)

1. **Push code to GitHub**
2. **Visit** [share.streamlit.io](https://share.streamlit.io)
3. **Connect your GitHub repo**
4. **Deploy instantly** - Get a public URL like `https://your-app.streamlit.app`

### Option 2: Railway (FREE Tier Available)

1. **Visit** [railway.app](https://railway.app)
2. **Connect GitHub repo**
3. **Deploy automatically** with the included `Procfile`
4. **Get custom domain** like `https://your-app.railway.app`

### Option 3: Render (FREE Tier Available)

1. **Visit** [render.com](https://render.com)
2. **Create new Web Service**
3. **Connect GitHub repo**
4. **Uses** `render.yaml` configuration automatically

### Option 4: Docker Deployment

```bash
# Build the image
docker build -t stock-screener .

# Run the container
docker run -p 8501:8501 stock-screener
```

### Option 5: Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
```

## 📊 How It Works

1. **Set Criteria**: Use the sidebar to configure screening parameters
2. **Run Analysis**: Click "Run Stock Screening" to analyze S&P 500 stocks
3. **View Results**: Explore results through interactive charts and tables
4. **Export Data**: Download findings for further analysis
5. **Analyze Stocks**: Click on individual stocks for detailed charts

## ⚙️ Configuration

### Screening Criteria

- **Fundamental Filters**: P/E ratio, price, market cap, beta
- **Technical Filters**: Moving averages, RSI, momentum indicators
- **Volume Analysis**: Average trading volume requirements
- **Sentiment Data**: Optional Finviz web scraping for additional metrics

### Data Sources

- **Yahoo Finance**: Primary source for stock data and financials
- **Finviz**: Optional sentiment and institutional ownership data

## 🔒 Security & Rate Limiting

The application includes:
- Rate limiting to prevent API abuse
- Error handling for network failures
- No API keys required for basic functionality
- Graceful degradation when external services are unavailable

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly, Altair
- **Data Sources**: yfinance, BeautifulSoup for web scraping
- **Deployment**: Docker, Streamlit Cloud, Railway, Render

## 📈 Sample Screening Results

The dashboard will display stocks that meet your criteria with:
- Current price and P/E ratio
- Market capitalization
- Technical indicators (RSI, moving averages)
- Sector classification
- Momentum indicators
- Suggested stop-loss levels

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Live Demo

Access the live dashboard at: [Your Deployment URL]

---

**Built with ❤️ using Streamlit** | **Data powered by Yahoo Finance**