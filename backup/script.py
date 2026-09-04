from datetime import datetime
from zoneinfo import ZoneInfo
import os
import time
import redis
import requests

REDIS_HOST = os.getenv("REDIS_HOST", "valkey-db")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
INTERVALO = int(os.getenv("INTERVALO_SEGUNDOS", 15))

client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,brl"

print(f"Iniciando coletor (USD/BRL). Intervalo: {INTERVALO}s | Destino: {REDIS_HOST}", flush=True)

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        if "bitcoin" in data:
            preco_usd = data["bitcoin"]["usd"]
            preco_brl = data["bitcoin"]["brl"]
            
            # Gera a data/hora ajustada para o fuso horário do Brasil (São Paulo)
            timestamp = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")
            
            client.set("bitcoin:preco_usd", preco_usd)
            client.set("bitcoin:preco_brl", preco_brl)
            client.set("bitcoin:ultima_atualizacao", timestamp)
            
            print(f"[{timestamp}] BTC Salvo -> USD: $ {preco_usd} | BRL: R$ {preco_brl}", flush=True)
    except Exception as e:
        print(f"Erro na execução: {e}", flush=True)
    
    time.sleep(INTERVALO)