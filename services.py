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