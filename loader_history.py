import json
import time
from datetime import datetime, timedelta
import requests
import redis

# Conexão com o Redis
REDIS_URL = "redis://localhost:6379"
r = redis.from_url(REDIS_URL)

# CoinGecko API para histórico de mercado (últimos 45 dias)
# Pegamos em USD e BRL
API_HISTORY_URL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=45&interval=daily"

def load_historical_data():
    try:
        print("Buscando dados históricos de 45 dias...")
        response = requests.get(API_HISTORY_URL, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            prices_usd = data.get("prices", [])
            
            # Para o BRL, podemos buscar em paralelo ou estimar/fazer outra chamada. 
            # Vamos buscar o histórico em BRL também para manter a precisão:
            API_HISTORY_BRL = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=brl&days=45&interval=daily"
            response_brl = requests.get(API_HISTORY_BRL, timeout=15)
            prices_brl = response_brl.json().get("prices", []) if response_brl.status_code == 200 else []

            # Mapeia os preços por timestamp aproximado do dia
            brl_dict = {item[0]: item[1] for item in prices_brl}

            pipe = r.pipeline()
            count = 0

            for item in prices_usd:
                timestamp_ms = int(item[0])
                usd_price = item[1]
                brl_price = brl_dict.get(item[0], usd_price * 5.0) # Fallback de conversão caso falhe

                record = {
                    "source": "CoinGecko-History",
                    "timestamp": timestamp_ms,
                    "usd": usd_price,
                    "brl": brl_price
                }

                # Adiciona no Sorted Set do Redis
                pipe.zadd("bitcoin_history", {json.dumps(record): timestamp_ms})
                count += 1

            pipe.execute()
            print(f"Sucesso! {count} registros históricos de 45 dias injetados no Redis.")
        else:
            print("Erro ao buscar histórico da API:", response.status_code)
    except Exception as e:
        print("Erro ao carregar histórico:", e)

if __name__ == "__main__":
    load_historical_data()