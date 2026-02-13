import requests

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