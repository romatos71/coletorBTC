import os
import time
import redis
import requests

# Lê as variáveis de ambiente injetadas pelo OpenShift (ou usa padrões)
REDIS_HOST = os.getenv("REDIS_HOST", "valkey-db")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
INTERVALO = int(os.getenv("INTERVALO_SEGUNDOS", 15))

# Conecta ao Valkey/Redis
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

print(
    f"Iniciando coletor de Bitcoin. Intervalo: {INTERVALO}s | Destino:"
    f" {REDIS_HOST}:{REDIS_PORT}"
)

while True:
  try:
    # Busca a cotação atual do Bitcoin
    response = requests.get(API_URL, timeout=10)
    data = response.json()

    if "bitcoin" in data and "usd" in data["bitcoin"]:
      preco = data["bitcoin"]["usd"]
      timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

      # Salva no Valkey
      client.set(f"bitcoin:preco", preco)
      client.set(f"bitcoin:ultima_atualizacao", timestamp)

      print(
          f"[{timestamp}] Preço do Bitcoin obtido com sucesso: $ {preco} USD"
          " salvo no Valkey."
      )
    else:
      print("Erro ao interpretar o JSON da API de cotação.")

  except Exception as e:
    print(f"Erro na execução da rotina: {e}")

  # Aguarda o parâmetro configurado antes da próxima coleta
  time.sleep(INTERVALO)