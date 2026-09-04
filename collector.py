import os
import time
import requests
import redis

# Configurações de conexão vindas das variáveis de ambiente do OpenShift
REDIS_URL = os.getenv('REDIS_URL', 'redis://dbredis-matos:6379')
INTERVALO = int(os.getenv('INTERVALO_SEGUNDOS', '30'))

# Conecta ao Redis
client = redis.Redis.from_url(REDIS_URL)

print(f"Iniciando coletor de Bitcoin. Conectado ao Redis em: {REDIS_URL}")

def buscar_preco_bitcoin():
    try:
        # Usando a API pública da CoinGecko para pegar o preço em USD e BRL
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,brl"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'bitcoin' in data:
            timestamp = int(time.time() * 1000) # Milissegundos para o gráfico
            registro = {
                "timestamp": timestamp,
                "usd": data['bitcoin']['usd'],
                "brl": data['bitcoin']['brl']
            }
            return registro
    except Exception as e:
        print(f"Erro ao buscar preço da API: {e}")
    return None

# Loop principal de coleta
while True:
    dados = buscar_preco_bitcoin()
    if dados:
        import json
        payload = json.dumps(dados)
        # Adiciona na lista ordenada do Redis (ZADD)
        client.zadd('bitcoin_history', {payload: dados['timestamp']})
        # Opcional: Mantém apenas os últimos 1000 registros para não lotar o Redis
        client.zremrangebyrank('bitcoin_history', 0, -1001)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Preço salvo: USD {dados['usd']} | BRL {dados['brl']}")
    
    time.sleep(INTERVALO)