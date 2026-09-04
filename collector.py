import time
import json
import requests
from datetime import datetime
import redis

# Conexão com o Redis (local ou via variável de ambiente no OpenShift)
REDIS_URL = "redis://localhost:6379"
r = redis.from_url(REDIS_URL)

API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,brl"

def fetch_and_store():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            btc = data.get("bitcoin", {})
            
            usd_price = btc.get("usd", 0)
            brl_price = btc.get("brl", 0)
            
            now = datetime.now()
            timestamp_ms = int(now.timestamp() * 1000)
            
            # Formato do registro para salvar no Redis
            record = {
                "source": "CoinGecko",
                "timestamp": timestamp_ms,
                "usd": usd_price,
                "brl": brl_price
            }
            
            # Usando Sorted Set (ZADD) onde o score é o timestamp para ordenar o histórico
            r.zadd("bitcoin_history", {json.dumps(record): timestamp_ms})
            print(f"[{now.strftime('%d/%m/%Y %H:%M:%S]')} Coletado -> USD: ${usd_price} | BRL: R${brl_price}")
        else:
            print("Erro ao acessar a API de preços:", response.status_code)
    except Exception as e:
        print("Erro na execução do coletor:", e)

if __name__ == "__main__":
    print("Iniciando coletor de Bitcoin (a cada 5 segundos)...")
    while True:
        fetch_and_store()
        time.sleep(5)