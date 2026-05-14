# 📈 StockSense Terminal + NSE India Clone

A full-stack financial analytics platform built with **Python / Streamlit** and a standalone **NSE India Clone** in pure HTML/JS.

---

## 🚀 Projects Included

### 1. ⚡ StockSense Terminal (`venv/Scripts/app.py`)
A professional AI-powered stock analysis dashboard.

**Features:**
- 🔐 Secure Login & Stock Account Registration
- 📊 Real-time candlestick charts with technical indicators (SMA, RSI, MACD, Bollinger Bands)
- 🤖 AI Quantitative Analysis with NLP Sentiment scoring
- 🔮 7-Day Machine Learning Price Forecast (RandomForest)
- 📰 Latest Market News feed
- 📋 Personal Watchlist management

**Stack:** Python · Streamlit · yfinance · Plotly · scikit-learn · TextBlob

---

### 2. 🏛️ NSE India Clone (`nse-clone.html`)
A pixel-perfect, interactive clone of the National Stock Exchange of India website.

**Features:**
- 📡 Live ticker marquee with simulated real-time price updates
- 📈 NIFTY 50 index chart (Chart.js)
- 🟢 Top Gainers / 🔴 Top Losers tables
- 📋 Full Equity Market data table (14 NIFTY 50 stocks)
- 📊 Stock Detail view with Order Book depth
- 🔗 Option Chain page (Derivatives)
- ⭐ Watchlist (persisted via localStorage)

**Stack:** HTML · Vue 3 · TailwindCSS · Chart.js · Font Awesome

---

## 🛠️ Setup & Run

### StockSense Terminal
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run venv/Scripts/app.py
```
Open: http://localhost:8501  
**Default Login:** `admin` / `securepassword123`

### NSE India Clone
Simply open `nse-clone.html` in any modern browser — no server required!

---

## 📦 Dependencies
See `requirements.txt`:
- streamlit >= 1.32.0
- pandas >= 2.2.0
- numpy >= 1.26.0
- yfinance >= 0.2.37
- plotly >= 5.19.0
- scikit-learn >= 1.4.1
- textblob >= 0.18.0

---

## 📸 Screenshots
**StockSense Terminal** — Dark-themed professional trading terminal  
**NSE Clone** — Light-themed exchange interface with live-simulated data

---

## ⚠️ Disclaimer
This project uses simulated/publicly available market data for educational purposes only. Not financial advice.

---

Made with ❤️ by **Shakti Singh**
