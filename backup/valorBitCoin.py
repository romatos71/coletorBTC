import os
import time
import redis
import requests

REDIS_HOST = os.getenv("REDIS_HOST", "valkey-db")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
INTERVALO = int(os.getenv("INTERVALO_SEGUNDOS", 15))

# Conecta ao Valkey
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

print(f"Iniciando coletor. Intervalo: {INTERVALO}s | Destino: {REDIS_HOST}", flush=True)

while True:
    try:
        response = requests.get(API_URL, timeout=10)
        data = response.json()
        if "bitcoin" in data and "usd" in data["bitcoin"]:
            preco = data["bitcoin"]["usd"]
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Salva no Valkey
            client.set("bitcoin:preco", preco)
            client.set("bitcoin:ultima_atualizacao", timestamp)
            
            print(f"[{timestamp}] Preço BTC: $ {preco} USD salvo no Valkey.", flush=True)
    except Exception as e:
        print(f"Erro na execução: {e}", flush=True)
    
    time.sleep(INTERVALO)