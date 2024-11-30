import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objs as go
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Enhanced data fetching with comprehensive error handling and retry mechanism
def get_crypto_data(current_price):
    def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504, 429)
    ):
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    try:
        # Create a retry-enabled session
        session = requests_retry_session()
        
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": current_price,
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": False
        }
        
        # Add delay to prevent rate limiting
        time.sleep(1)
        
        # Make the request with longer timeout
        response = session.get(url, params=params, timeout=10)
        
        # Raise exception for bad responses
        response.raise_for_status()
        
        # Parse and return data
        data = response.json()
        return pd.DataFrame(data)
    
    except requests.exceptions.RequestException as e:
        # Detailed error handling
        if isinstance(e, requests.exceptions.HTTPError):
            if e.response.status_code == 429:
                st.error("""
                ### 🚨 Rate Limit Exceeded
                You've hit the CoinGecko API rate limit. Solutions:
                - Wait a few minutes before refreshing
                - Use a different API or get a pro API key
                - Reduce the number of requests
                """)
            else:
                st.error(f"HTTP Error: {e}")
        elif isinstance(e, requests.exceptions.ConnectionError):
            st.error("""
            ### 🌐 Connection Error
            - Unable to connect to CoinGecko API
            - Check your internet connection
            - The service might be temporarily unavailable
            """)
        elif isinstance(e, requests.exceptions.Timeout):
            st.error("""
            ### ⏰ Request Timeout
            - The request to CoinGecko took too long
            - Try again later or check your internet speed
            """)
        else:
            st.error(f"Unexpected error occurred: {e}")
        
        return pd.DataFrame()

# Fallback data function
def get_fallback_crypto_data():
    fallback_data = {
        'name': ['Bitcoin', 'Ethereum', 'Tether', 'BNB', 'Solana'],
        'current_price': [50000, 3000, 1, 300, 100],
        'market_cap': [1000000000000, 500000000000, 80000000000, 50000000000, 30000000000],
        'total_volume': [30000000000, 20000000000, 50000000000, 5000000000, 3000000000],
        'price_change_percentage_24h': [2.5, -1.2, 0.1, 1.5, -0.8]
    }
    return pd.DataFrame(fallback_data)

# Improved Streamlit configuration
st.set_page_config(page_title="Crypto Price Tracker", layout="wide", page_icon=":chart_with_upwards_trend:")

# Title and description
st.title("🚀 Cryptocurrency Price Tracker")
st.markdown("Real-time analysis of top 100 cryptocurrencies")

# Add a warning about potential API limitations
st.warning("""
⚠️ Due to API rate limits, you might experience occasional data fetch issues. 
If data doesn't load, please:
- Wait a few minutes
- Refresh the page
- Try a different currency
""")

# Improved sidebar layout
with st.sidebar:
    st.header("🔧 Cryptocurrency Analysis")
    
    # Currency selection with more options
    current_price = st.selectbox('Select Price Currency', 
        ['usd', 'btc', 'inr', 'eth', 'eur', 'jpy'], 
        index=0
    )

    # Attempt to load data with fallback
    df = get_crypto_data(current_price)
    
    # Use fallback data if primary fetch fails
    if df.empty:
        st.warning("Using fallback data due to API issues")
        df = get_fallback_crypto_data()

    # Enhanced coin selection
    sorted_coins = sorted(df['name'])
    selected_coin = st.multiselect(
        'Select Cryptocurrencies', 
        sorted_coins, 
        default=sorted_coins[:10]  # Default to top 10 coins
    )

    # Number of coins to display
    num_coin = st.slider('Display Top N Coins', 1, 100, 10)

# Filter selected coins
df_selected_coin = df[df['name'].isin(selected_coin)].head(num_coin)

# Display data summary
st.subheader('Cryptocurrency Data Overview')
st.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

# Display dataframe
st.dataframe(df_selected_coin)

# Bar Chart
fig_bar = px.bar(df_selected_coin, x='name', y='current_price', title='Current Price of Selected Cryptocurrencies')
st.plotly_chart(fig_bar)

# Line Chart
fig_line = px.line(df_selected_coin, x='name', y='market_cap', title='Market Cap of Selected Cryptocurrencies')
st.plotly_chart(fig_line)

# Histogram
fig_hist = px.histogram(df_selected_coin, x='name', y='total_volume', title='Total Volume of Selected Cryptocurrencies')
st.plotly_chart(fig_hist)

# Pie Chart
fig_pie = px.pie(
    df_selected_coin, 
    names='name', 
    values='market_cap', 
    title='Market Cap Distribution of Selected Cryptocurrencies',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_pie.update_traces(textinfo='percent+label', pull=[0.1 if i < 3 else 0 for i in range(len(df_selected_coin))])
fig_pie.update_layout(
    showlegend=True,
    legend=dict(
        title="Cryptocurrencies",
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.05
    )
)
st.plotly_chart(fig_pie)

# Scatter Plot
fig_scatter = px.scatter(df_selected_coin, x='name', y='price_change_percentage_24h', size='market_cap', color='name',
                         title='24h Price Change Percentage vs Market Cap',
                         hover_name='name', size_max=60)
st.plotly_chart(fig_scatter)