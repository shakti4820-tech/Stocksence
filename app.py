import streamlit as st
import numpy as np
import logging
import os
import urllib.parse
import json
from datetime import datetime, timedelta
import pytz

# Core Data Libraries
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Attempt to load AI / ML libraries gracefully
try:
    from sklearn.ensemble import RandomForestRegressor
    from textblob import TextBlob
    HAS_AI_LIBS = True
except ImportError:
    HAS_AI_LIBS = False

# -----------------------------------------------------------------------------
# Configuration & Production Logging
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="StockSense Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup Logging for Monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ProTradeApp")

# -----------------------------------------------------------------------------
# Authentication & Session State Management
# -----------------------------------------------------------------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_user(username, user_data):
    users = load_users()
    users[username] = user_data
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Fallback credentials if environment variables aren't set
ADMIN_USER = os.getenv("APP_USERNAME", "admin")
ADMIN_PASS = os.getenv("APP_PASSWORD", "securepassword123")

if not st.session_state['authenticated']:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔒 Secure Access</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #8B949E;'>Login or register to access the trading terminal.</p>",
            unsafe_allow_html=True
        )
        
        tab1, tab2 = st.tabs(["Login", "Register Stock Account"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Authenticate", use_container_width=True)
                
                if submit:
                    users = load_users()
                    if (username == ADMIN_USER and password == ADMIN_PASS) or (username in users and users[username]['password'] == password):
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        logger.info(f"Successful login for user: {username}")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Access denied.")
                        logger.warning(f"Failed login attempt for username: {username}")
                        
        with tab2:
            with st.form("register_form"):
                st.markdown("#### Personal Information")
                reg_fullname = st.text_input("Full Legal Name *")
                reg_dob = st.date_input("Date of Birth *", value=datetime(1990, 1, 1), min_value=datetime(1900, 1, 1))
                reg_ssn = st.text_input("Social Security Number (Last 4 Digits) *", max_chars=4, type="password")
                
                st.markdown("#### Contact Information")
                reg_email = st.text_input("Email Address *")
                reg_phone = st.text_input("Phone Number")
                reg_address = st.text_area("Residential Address *")
                
                st.markdown("#### Financial Profile")
                reg_employment = st.selectbox("Employment Status *", ["Employed", "Self-Employed", "Unemployed", "Retired", "Student"])
                reg_income = st.selectbox("Annual Income *", ["Under $25,000", "$25,000 - $50,000", "$50,000 - $100,000", "$100,000 - $250,000", "Over $250,000"])
                
                st.markdown("#### Account Credentials")
                reg_username = st.text_input("Choose Username *")
                reg_password = st.text_input("Choose Password *", type="password")
                reg_confirm_password = st.text_input("Confirm Password *", type="password")
                
                st.markdown("<small style='color: #8B949E;'>* Required fields</small>", unsafe_allow_html=True)
                
                register_submit = st.form_submit_button("Create Account", use_container_width=True)
                
                if register_submit:
                    if not all([reg_fullname, reg_email, reg_username, reg_password, reg_confirm_password, reg_ssn, reg_address]):
                        st.error("Please fill in all required fields.")
                    elif reg_password != reg_confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        users = load_users()
                        if reg_username in users or reg_username == ADMIN_USER:
                            st.error("Username already exists. Please choose another one.")
                        else:
                            save_user(reg_username, {
                                "fullname": reg_fullname,
                                "dob": str(reg_dob),
                                "email": reg_email,
                                "phone": reg_phone,
                                "address": reg_address,
                                "employment": reg_employment,
                                "income": reg_income,
                                "password": reg_password,
                                "registration_date": datetime.now().isoformat()
                            })
                            st.success("Account created successfully! Please switch to the Login tab to access your account.")
                            logger.info(f"New stock account registered: {reg_username}")
                            
    st.stop()  # Halt execution until authenticated

# -----------------------------------------------------------------------------
# Custom CSS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #E6EDF3; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #30363D; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-size: 15px; font-weight: 500; color: #8B949E; }
    .stTabs [aria-selected="true"] { color: #FFFFFF !important; border-bottom: 2px solid #FF4B4B !important; }
    div[data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    .sidebar-header { color: #FFFFFF; font-weight: 600; font-size: 1.1rem; margin-top: 1rem; margin-bottom: 0.5rem; }
    hr { border-color: #30363D; }
    div[data-testid="metric-container"] {
        background: #1C2128;
        border: 1px solid #30363D;
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-testid="stMetricLabel"] p { color: #8B949E !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem !important; }
    /* Show the main menu and header */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Backend API, Technicals, & Caching
# -----------------------------------------------------------------------------
def get_market_status():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    is_open = False
    if now.weekday() < 5:
        if now.hour > 9 or (now.hour == 9 and now.minute >= 30):
            if now.hour < 16:
                is_open = True
    status_text = "MARKET OPEN" if is_open else "MARKET CLOSED"
    color = "#92FE9D" if is_open else "#FF4B4B"
    circle = "🟢" if is_open else "🔴"
    return is_open, f"{circle} {status_text} | {now.strftime('%Y-%m-%d %H:%M EST')}", color

@st.cache_data(ttl=300)
def fetch_top_movers():
    tickers = "NVDA TSLA AMD COIN"
    try:
        df = yf.download(tickers, period="5d", interval="1d", progress=False)
        if 'Close' in df:
            close_df = df['Close'].dropna(how='all')
            if len(close_df) >= 2:
                prev_close = close_df.iloc[-2]
                current = close_df.iloc[-1]
                pct_change = ((current - prev_close) / prev_close) * 100
                movers = []
                for ticker in pct_change.index:
                    val = float(pct_change[ticker])
                    movers.append((ticker, val))
                return movers
    except Exception as e:
        logger.error(f"Error fetching top movers: {e}")
    return [("NVDA", 0.0), ("TSLA", 0.0), ("AMD", 0.0), ("COIN", 0.0)]

@st.cache_data(ttl=300)
def fetch_stock_data(ticker, period="1y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        if df.empty:
            return None
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        
        if 'Date' not in df.columns and 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'Date'})
            
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema_12 - ema_26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        std_dev = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['SMA_20'] + (std_dev * 2)
        df['BB_Lower'] = df['SMA_20'] - (std_dev * 2)
        
        logger.info(f"Successfully fetched and processed data for {ticker}")
        return df
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        st.error("Error fetching market data. Please check logs.")
        return None

@st.cache_data(ttl=3600)
def fetch_company_info(ticker):
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

@st.cache_data(ttl=1800)
def fetch_market_news(ticker):
    try:
        return yf.Ticker(ticker).news[:10]
    except Exception:
        return []

def get_company_logo_urls(website_url, ticker):
    domain = None
    if website_url and isinstance(website_url, str):
        try:
            domain = urllib.parse.urlparse(website_url).netloc.replace('www.', '')
        except Exception:
            pass
            
    if not domain:
        # Fallback to guessing the domain if yfinance doesn't provide the website
        domain = f"{ticker.lower()}.com"
        
    primary_logo = f"https://logo.clearbit.com/{domain}?size=200"
    fallback_logo = f"https://s2.googleusercontent.com/s2/favicons?domain={domain}&sz=128"
    return primary_logo, fallback_logo

# -----------------------------------------------------------------------------
# AI & Quant Models
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def analyze_news_sentiment(news_list):
    if not HAS_AI_LIBS or not news_list:
        return 0.0
        
    sentiments = []
    for article in news_list:
        title = article.get('title', '')
        if title:
            blob = TextBlob(title)
            sentiments.append(blob.sentiment.polarity)
            
    if not sentiments:
        return 0.0
        
    return sum(sentiments) / len(sentiments)

@st.cache_data(ttl=300)
def predict_future_prices(df, days_ahead=7):
    if df is None or not HAS_AI_LIBS or len(df) < 30:
        return None
        
    data = df['Close'].values
    X, y = [], []
    window = 10
    
    for i in range(len(data) - window):
        X.append(data[i : i+window])
        y.append(data[i+window])
        
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    last_sequence = list(data[-window:])
    predictions = []
    for _ in range(days_ahead):
        pred = model.predict([last_sequence])[0]
        predictions.append(pred)
        last_sequence.append(pred)
        last_sequence.pop(0)
        
    return predictions

def calculate_risk_metrics(df):
    if df is None or df.empty:
        return 0.0, 0.0, 0.0
        
    df['Daily_Return'] = df['Close'].pct_change()
    ann_volatility = df['Daily_Return'].std() * np.sqrt(252)
    
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    
    if start_price > 0 and len(df) > 0:
        ann_return = (end_price / start_price) ** (252 / len(df)) - 1
    else:
        ann_return = 0.0
        
    sharpe = (ann_return - 0.04) / ann_volatility if ann_volatility > 0 else 0.0
    
    roll_max = df['Close'].cummax()
    drawdown = df['Close'] / roll_max - 1.0
    max_drawdown = drawdown.min()
    
    return ann_volatility, sharpe, max_drawdown

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color: #FFFFFF; font-weight: 800; display: flex; align-items: center; gap: 10px;'><span style='color: #4C6EF5;'>🟦</span> StockSense</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8B949E; margin-bottom: 20px; font-size: 14px;'>Welcome back, <strong>Shakti Singh</strong>! 👋</p>", unsafe_allow_html=True)
    
    ticker = st.text_input("🔍 Ticker Symbol", "AAPL", help="Enter a valid stock ticker symbol").upper()
    
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📋 My Watchlist", expanded=True):
        if 'watchlist' not in st.session_state:
            st.session_state['watchlist'] = []
            
        wl_input = st.text_input("Add symbol", placeholder="e.g. NVDA", label_visibility="collapsed")
        if st.button("➕ Add to Watchlist", use_container_width=True):
            if wl_input and wl_input.upper() not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(wl_input.upper())
                st.rerun()
                
        if not st.session_state['watchlist']:
            st.markdown("<small style='color: #8B949E;'>No symbols added yet.</small>", unsafe_allow_html=True)
        else:
            for sym in st.session_state['watchlist']:
                col1, col2 = st.columns([0.8, 0.2])
                col1.markdown(f"**{sym}**")
                if col2.button("✖", key=f"del_{sym}"):
                    st.session_state['watchlist'].remove(sym)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    time_period = st.selectbox("📅 Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=0)
    
    st.markdown("<div class='sidebar-header'>Technical Indicators</div>", unsafe_allow_html=True)
    show_sma20 = st.checkbox("SMA 20", value=True)
    show_sma50 = st.checkbox("SMA 50", value=False)
    show_bb = st.checkbox("Bollinger Bands", value=False)
    show_rsi = st.checkbox("RSI", value=False)
    
    st.markdown("---")
    st.markdown("<small style='color: #8B949E;'>Data powered by Yahoo Finance · Free tier</small><br>", unsafe_allow_html=True)
    st.markdown("<small style='color: #8B949E;'>Refresh page to update quotes</small>", unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("Logout", use_container_width=True):
        st.session_state['authenticated'] = False
        logger.info("User logged out.")
        st.rerun()

# Fetch Data
with st.spinner("Analyzing market data..."):
    df = fetch_stock_data(ticker, period=time_period)
    info = fetch_company_info(ticker)
    news = fetch_market_news(ticker)

if df is None or df.empty:
    st.warning(f"⚠️ Could not fetch data for {ticker}. Please ensure the symbol is correct.")
    st.stop()

# -----------------------------------------------------------------------------
# Main View
# -----------------------------------------------------------------------------
st.markdown("<h1 style='font-size: 2.5rem; font-weight: 800; margin-bottom: 0;'>StockSense</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Single Stock Analysis", "Portfolio / Comparison", "Latest News"])

# Single Stock Analysis Tab
with tab1:
    primary_logo, fallback_logo = get_company_logo_urls(info.get('website'), ticker)
    
    company_name = info.get('shortName', ticker)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    # Header with Logo
    html_content = f"""
    <div style="display: flex; align-items: center; gap: 20px; margin-top: 20px; margin-bottom: 20px;">
        <img src="{primary_logo}" onerror="this.onerror=null; this.src='{fallback_logo}';" 
             style="height: 60px; width: 60px; border-radius: 50%; background-color: white; padding: 5px; object-fit: contain;">
        <div>
            <h2 style="margin: 0; padding: 0; font-weight: 700; font-size: 2rem; color: #FFFFFF;">{company_name}</h2>
            <p style="margin: 0; color: #8B949E; font-size: 14px;">{sector} | {industry}</p>
        </div>
    </div>
    <hr style="border-color: #30363D; margin-top: 0; margin-bottom: 20px;">
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Market Overview Stats
    current_price = float(df['Close'].iloc[-1])
    prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
    pct_change = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0.0
    day_high = float(df['High'].iloc[-1])
    day_low = float(df['Low'].iloc[-1])
    volume = int(df['Volume'].iloc[-1])
    
    change_color = "#FF4B4B" if pct_change < 0 else "#92FE9D"
    change_bg = "rgba(255, 75, 75, 0.1)" if pct_change < 0 else "rgba(146, 254, 157, 0.1)"
    arrow = "↓" if pct_change < 0 else "↑"
    
    st.markdown("<h4 style='color: #8B949E; margin-top: 10px; margin-bottom: 20px; font-size: 12px; letter-spacing: 1.5px; font-weight: 700;'>MARKET OVERVIEW</h4>", unsafe_allow_html=True)
    
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<p style='color: #8B949E; font-size: 13px; margin-bottom: 0;'>💰 Current Price</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 1.8rem; margin-top: 0; margin-bottom: 8px;'>${current_price:.2f}</h2>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: {change_color}; font-weight: 700; background-color: {change_bg}; padding: 4px 8px; border-radius: 4px; font-size: 12px; display: inline-block;'>{arrow} {abs(current_price-prev_close):.2f} ({pct_change:.2f}%)</span>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<p style='color: #8B949E; font-size: 13px; margin-bottom: 0;'>📈 Day High</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 1.8rem; margin-top: 0;'>${day_high:.2f}</h2>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<p style='color: #8B949E; font-size: 13px; margin-bottom: 0;'>📉 Day Low</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 1.8rem; margin-top: 0;'>${day_low:.2f}</h2>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<p style='color: #8B949E; font-size: 13px; margin-bottom: 0;'>📊 Volume</p>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='font-size: 1.8rem; margin-top: 0;'>{volume:,}</h2>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"### Historical Price ({time_period})")
    
    # Chart with specific indicators enabled via sidebar
    fig = go.Figure()
    
    # Main price trace
    fig.add_trace(go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price'
    ))
    
    # Dynamic overlays
    if show_sma20:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], line=dict(color='#00C9FF', width=1.5), name='SMA 20'))
    if show_sma50:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], line=dict(color='#FF4B4B', width=1.5), name='SMA 50'))
    if show_bb:
        fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Upper'], line=dict(color='rgba(255,255,255,0.2)', width=1), name='BB Upper'))
        fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_Lower'], line=dict(color='rgba(255,255,255,0.2)', width=1), fill='tonexty', fillcolor='rgba(255,255,255,0.05)', name='BB Lower'))
    
    fig.update_layout(
        template="plotly_dark", 
        height=500, 
        margin=dict(l=0, r=0, t=10, b=0), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        xaxis_rangeslider_visible=False, 
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])
    st.plotly_chart(fig, use_container_width=True)

    if show_rsi:
        st.markdown("#### RSI (14)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line=dict(color='#E1C16E', width=1.5), name='RSI'))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(template="plotly_dark", height=200, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_rsi, use_container_width=True)

# Portfolio / Comparison Tab
with tab2:
    st.markdown("### 🤖 AI Quantitative Analysis & Portfolio Modeling")
    if not HAS_AI_LIBS:
        st.error("⚠️ **AI Modules Missing:** Install scikit-learn and textblob to view AI Insights.")
    else:
        sentiment_score = analyze_news_sentiment(news)
        ann_volatility, sharpe, max_drawdown = calculate_risk_metrics(df)
        preds = predict_future_prices(df, days_ahead=7)
        
        signal_score = 0
        signal_score += 1 if df['RSI'].iloc[-1] < 40 else (-1 if df['RSI'].iloc[-1] > 60 else 0)
        signal_score += 1 if df['MACD'].iloc[-1] > df['MACD_Signal'].iloc[-1] else -1
        signal_score += 1 if sentiment_score > 0.05 else (-1 if sentiment_score < -0.05 else 0)
        signal_score += 1 if df['Close'].iloc[-1] > df['SMA_50'].iloc[-1] else -1
        
        if signal_score >= 2:
            overall_signal, sig_color = "🟢 STRONG BUY", "#92FE9D"
        elif signal_score == 1:
            overall_signal, sig_color = "🟢 ACCUMULATE", "#00C9FF"
        elif signal_score == 0:
            overall_signal, sig_color = "🟡 HOLD", "#E1C16E"
        elif signal_score == -1:
            overall_signal, sig_color = "🔴 REDUCE", "#FF7675"
        else:
            overall_signal, sig_color = "🔴 STRONG SELL", "#FF4B4B"

        st.markdown(f"#### Consensus Signal: <span style='color:{sig_color}'>{overall_signal}</span>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sent_label = "Bullish" if sentiment_score > 0 else "Bearish" if sentiment_score < 0 else "Neutral"
            st.metric("NLP Sentiment Polarity", f"{sentiment_score:.2f}", delta=sent_label)
        with col2:
            st.metric("Annual Volatility", f"{ann_volatility*100:.1f}%")
        with col3:
            st.metric("Sharpe Ratio", f"{sharpe:.2f}", delta="Good" if sharpe > 1 else "Poor")

        st.markdown("---")
        st.markdown("#### 🔮 7-Day Machine Learning Forecast")
        if preds:
            last_date = df['Date'].iloc[-1]
            future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
            fig2 = go.Figure()
            recent_df = df.tail(30)
            fig2.add_trace(go.Scatter(x=recent_df['Date'], y=recent_df['Close'], mode='lines', name='Historical', line=dict(color='#00C9FF', width=2)))
            pred_x = [last_date] + future_dates
            pred_y = [recent_df['Close'].iloc[-1]] + preds
            fig2.add_trace(go.Scatter(x=pred_x, y=pred_y, mode='lines+markers', name='ML Prediction', line=dict(color='#D473D4', width=2, dash='dash')))
            fig2.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig2, use_container_width=True)

# Latest News Tab
with tab3:
    st.markdown("### 📰 Latest Market News")
    if not news:
        st.info("No recent news found.")
    else:
        for article in news:
            with st.container():
                title = article.get('title', 'No Title')
                link = article.get('link', '#')
                publisher = article.get('publisher', 'Unknown')
                pub_time = article.get('providerPublishTime')
                
                st.markdown(f"#### [{title}]({link})")
                date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d %H:%M') if pub_time else "Unknown"
                st.markdown(f"*{publisher} - {date_str}*")
                st.markdown("<hr style='border-color: #30363D; margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)