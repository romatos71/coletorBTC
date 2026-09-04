import time
from datetime import datetime
import redis
import requests
import streamlit as st
import pandas as pd

# Conexão com o Redis usando o nome correto fornecido
REDIS_HOST = "dbredis-matos"
REDIS_PORT = 6379

@st.cache_resource
def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

r = get_redis_client()

# Função para popular histórico de 1 mes se estiver vazio
def init_historical_data():
    if not r.exists("btc_history"):
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json().get("prices", [])
                for timestamp, price in data:
                    dt = datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    r.zadd("btc_history", {f"{dt}:{price}": timestamp})
        except Exception:
            pass

init_historical_data()

st.title("Monitor de Bitcoin - OpenShift Sandbox")

# Coleta de dados atuais (USD e BRL)
def get_current_btc():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,brl"
        res = requests.get(url, timeout=5).json()
        return res["bitcoin"]["usd"], res["bitcoin"]["brl"]
    except:
        return 0.0, 0.0

usd_price, brl_price = get_current_btc()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.subheader(f"Dados Atuais ({now})")
col1, col2 = st.columns(2)
col1.metric("Valor em Dólar (USD)", f"${usd_price:,.2f}")
col2.metric("Valor em Reais (BRL)", f"R$ {brl_price:,.2f}")

# Caixa de diálogo para multiplicação
st.markdown("---")
st.subheader("Calculadora de Conversão")
multiplicador = st.number_input("Insira a quantidade de Bitcoin para multiplicar:", min_value=0.0, value=1.0, step=0.1)
total_usd = usd_price * multiplicador
total_brl = brl_price * multiplicador
st.success(f"Total em Dólar: **$ {total_usd:,.2f}** | Total em Reais: **R$ {total_brl:,.2f}**")

# Gráfico de evolução (Último mês)
st.markdown("---")
st.subheader("Evolução do Bitcoin (Último Mês)")
raw_history = r.zrange("btc_history", 0, -1)
chart_data = []
for item in raw_history:
    parts = item.split(":")
    if len(parts) >= 2:
        chart_data.append({"Data": parts[0], "Preço USD": float(parts[1])})

if chart_data:
    df = pd.DataFrame(chart_data)
    df["Data"] = pd.to_datetime(df["Data"])
    df = df.set_index("Data")
    st.line_chart(df)

# Atualização a cada 5 segundos
time.sleep(5)
st.rerun()