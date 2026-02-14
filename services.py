import requests
from kucoin.client import Market

class PriceFetcher:
    def get_uphold(self):
        try:
            url = "https://api.uphold.com/v0/ticker/BTC-USD"
            r = requests.get(url, timeout=2).json()
            return float(r['ask']), float(r['bid']) # Retorna (Preço Compra, Preço Venda)
        except:
            return None, None

    def get_binance(self):
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
            r = requests.get(url, timeout=2).json()
            p = float(r['price'])
            return p, p # Binance spot simples geralmente é preço único na API pública
        except:
            return None, None
            
    def get_coinbase(self):
        try:
            url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
            r = requests.get(url, timeout=2).json()
            p = float(r['data']['amount'])
            return p, p
        except:
            return None, None
        


    def get_kucoin(self, symbol="BTC-USDT"):
        try:
            # Inicializa o cliente de mercado da KuCoin
            client = Market(url='https://api.kucoin.com')
            ticker = client.get_ticker(symbol)
            
            # 'bestAsk' é o preço de venda e 'bestBid' é o de compra
            return float(ticker['bestAsk']), float(ticker['bestBid'])
        except Exception as e:
            # Em caso de erro, retorna None para manter a consistência do seu código
            return None, None
        
# Função para buscar taxa da rede Bitcoin (Mempool) ---
def get_real_network_fee():
    """
    Busca o custo REAL (em BTC) para transferir Bitcoin agora.
    Fonte: API pública Mempool.space
    """
    try:
        # Tenta pegar a taxa prioritária (rápida)
        url = "https://mempool.space/api/v1/fees/recommended"
        response = requests.get(url, timeout=3)
        data = response.json()
        
        sat_per_vbyte = data['fastestFee'] # Ex: 15 sats/vbyte
        
        # Uma transação padrão pesa ~140 vBytes
        tx_cost_sats = sat_per_vbyte * 140
        
        # Converte de Satoshi para Bitcoin
        return tx_cost_sats / 100_000_000
        
    except Exception as e:
        print(f"⚠️ Erro ao buscar taxa de rede: {e}")
        return 0.00015 # Valor padrão conservador (15k sats) para evitar surpresas