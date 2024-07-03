import streamlit as st
import numpy as np
import pandas as pd
import requests
import plotly.express as px


# Get data
def get_crypto_data(current_price):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": current_price,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    data = response.json()
    return pd.DataFrame(data)

# Streamlit configuration
st.set_page_config(layout="wide")
st.image("images .jpeg", width=800)
st.title("Crypto Price App")
st.markdown("This app shows the prices of the top 100 cryptocurrencies.")

# Page layout
col1 = st.sidebar


# Current price
current_price = col1.selectbox('Select currency for price', ('usd', 'btc', 'inr', 'eth'))

# Load the dataframe
df = get_crypto_data(current_price)
images = df["image"]
df = df.drop(columns=["image"])

sorted_coins = sorted(df['name'])
selected_coin = col1.multiselect('Cryptocurrency', sorted_coins, sorted_coins)

df_selected_coin = df[df['name'].isin(selected_coin)]

# Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

st.subheader('Price Data of Cryptocurrency')
st.write('Data Dimension: ' + str(df_selected_coin.shape[0]) + ' rows and ' + str(df_selected_coin.shape[1]) + ' columns.')

st.dataframe(df_coins)

# Bar Chart
fig_bar = px.bar(df_coins, x='name', y='current_price', title='Current Price of Selected Cryptocurrencies')
st.plotly_chart(fig_bar)

# Line Chart
fig_line = px.line(df_coins, x='name', y='market_cap', title='Market Cap of Selected Cryptocurrencies')
st.plotly_chart(fig_line)

# Histogram
fig_hist = px.histogram(df_coins, x='name', y='total_volume', title='Total Volume of Selected Cryptocurrencies')
st.plotly_chart(fig_hist)

# Pie Chart
fig_pie = px.pie(
    df_coins, 
    names='name', 
    values='market_cap', 
    title='Market Cap Distribution of Selected Cryptocurrencies',
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_pie.update_traces(textinfo='percent+label', pull=[0.1 if i < 3 else 0 for i in range(len(df_coins))])
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
fig_scatter = px.scatter(df_coins, x='name', y='price_change_percentage_24h', size='market_cap', color='name',
                         title='24h Price Change Percentage vs Market Cap',
                         hover_name='name', size_max=60)
st.plotly_chart(fig_scatter)
