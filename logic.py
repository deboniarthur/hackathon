from services import get_real_network_fee

# Taxas reais por exchange 
TAXAS_EXCHANGES = {
    'Binance': 0.001,   # 0.1%
    'UpHold': 0.00,     # cobra no spread 
    'Coinbase': 0.006,  # 0.6%
    'KuCoin': 0.001     # 0.1%
}

def _normalizar_preco(valor):
    try:
        # Se vier lista/tupla (padrão correto das APIs: [ask, bid])
        if isinstance(valor, (list, tuple)) and len(valor) >= 2:
            ask, bid = float(valor[0]), float(valor[1])
            if ask > 0 and bid > 0:
                return ask, bid
        
        # Se vier apenas um número (float/int), simula spread minúsculo para não quebrar
        elif isinstance(valor, (int, float)) and valor > 0:
            return float(valor), float(valor) * 0.999 
            
        return None
    except:
        return None

def calcular_arbitragem(precos_brutos, investimento=100.0, taxa_fee=0.0, ignorar_rede=False):
    """
    Calcula o lucro LÍQUIDO.
    Se ignorar_rede=True, ZERA TODAS AS TAXAS (Modo Demo/God Mode).
    """
    validos = {}
    for exch, p in precos_brutos.items():
        dados_limpos = _normalizar_preco(p)
        if dados_limpos:
            validos[exch] = dados_limpos
    
    if len(validos) < 2:
        return None

    # Identifica o par de execução
    exch_compra = min(validos, key=lambda x: validos[x][0])
    exch_venda = max(validos, key=lambda x: validos[x][1])
    
    if exch_compra == exch_venda:
        return None
    
    p_compra_ask = validos[exch_compra][0]
    p_venda_bid = validos[exch_venda][1]

    if ignorar_rede:
        # MODO DEMO: Zera TUDO para garantir lucro (ideal para simular)
        fee_compra = 0.0
        fee_venda = 0.0
        taxa_rede_btc = 0.0
    else:
        # MODO REAL: Usa as taxas reais do dicionário ou do input
        fee_compra = TAXAS_EXCHANGES.get(exch_compra, taxa_fee)
        fee_venda = TAXAS_EXCHANGES.get(exch_venda, taxa_fee)
        taxa_rede_btc = get_real_network_fee()

    # --- CÁLCULO FINANCEIRO ---
    
    # 1. Compra (desconta fee se houver)
    qtd_btc_comprada = (investimento * (1 - fee_compra)) / p_compra_ask
    
    # 2. Transfere (desconta rede se houver)
    qtd_btc_liquida = qtd_btc_comprada - taxa_rede_btc
    
    if qtd_btc_liquida <= 0: 
        return {
            "comprar_em": exch_compra,
            "vender_em": exch_venda,
            "lucro_pct": -100.0,
            "lucro_usd": -investimento,
            "p_compra": p_compra_ask,
            "p_venda": p_venda_bid
        }

    # 3. Venda (desconta fee se houver)
    valor_final_usd = (qtd_btc_liquida * p_venda_bid) * (1 - fee_venda)
    
    lucro_usd = valor_final_usd - investimento
    lucro_pct = (lucro_usd / investimento) * 100

    return {
        "comprar_em": exch_compra,
        "vender_em": exch_venda,
        "p_compra": p_compra_ask,
        "p_venda": p_venda_bid,
        "lucro_usd": round(lucro_usd, 2),
        "lucro_pct": round(lucro_pct, 4),
        "taxa_rede_usd": round(taxa_rede_btc * p_compra_ask, 2)
    }

# --- ÁREA DE TESTES (terminal)
if __name__ == "__main__":
    print("🛠 RODANDO TESTES DO MOTOR DE LÓGICA...")

    # Cenário de Teste 
    teste_lucro = {
        'Binance': (100000, 99990), 
        'UpHold': (102000, 101500)
    }
    
    # Simula chamada do main (com ignorar_rede=False e True)
    print("\n--- Teste 1: Com Taxas de Rede (Realista) ---")
    res1 = calcular_arbitragem(teste_lucro, investimento=10000, ignorar_rede=False)
    if res1: print(f"Resultado: {res1['lucro_pct']}% (USD {res1['lucro_usd']})")

    print("\n--- Teste 2: Modo Demo (Sem Taxas de Rede) ---")
    res2 = calcular_arbitragem(teste_lucro, investimento=10000, ignorar_rede=True)
    if res2: print(f"Resultado: {res2['lucro_pct']}% (USD {res2['lucro_usd']})")