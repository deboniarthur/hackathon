from services import get_real_network_fee

# Taxas reais por exchange (Diferencial técnico para o projeto)
TAXAS_EXCHANGES = {
    'Binance': 0.001,   # 0.1%
    'UpHold': 0.00,    # cobra no spread 
    'Coinbase': 0.006,  # 0.6   %
    'KuCoin': 0.001     # 0.1%
}

def _normalizar_preco(valor):
    try:
        if isinstance(valor, (list, tuple)) and len(valor) >= 2:
            ask, bid = float(valor[0]), float(valor[1])
            if ask > 0 and bid > 0:
                return ask, bid
        # Se for apenas um número, simula spread zero para o teste não quebrar
        elif isinstance(valor, (int, float)) and valor > 0:
            return float(valor), float(valor)
        return None
    except:
        return None

def calcular_arbitragem(precos_brutos, investimento=100.0): 
    """
    Calcula o lucro LÍQUIDO (descontando taxas de compra e venda).
    Requisito: Motor de Spread Líquido.
    """
    validos = {}
    for exch, p in precos_brutos.items():
        dados_limpos = _normalizar_preco(p)
        if dados_limpos:
            validos[exch] = dados_limpos
    
    if len(validos) < 2:
        return None

    # 2. Identifica o par de execução: Menor ASK (compra) e Maior BID (venda)
    exch_compra = min(validos, key=lambda x: validos[x][0])
    exch_venda = max(validos, key=lambda x: validos[x][1])
    
    p_compra_ask = validos[exch_compra][0]
    p_venda_bid = validos[exch_venda][1]

    fee_compra = TAXAS_EXCHANGES.get(exch_compra, 0.001)
    fee_venda = TAXAS_EXCHANGES.get(exch_venda, 0.002)

    # Busca o custo da rede apurado via API no services.py com fallback integrado
    taxa_rede_btc = get_real_network_fee()

    # 4. Cálculo do Funil Financeiro Líquido (Net Spread)
    # Passo A: Compra na origem (Desconta taxa de trade)
    qtd_btc_comprada = (investimento * (1 - fee_compra)) / p_compra_ask
    
    # Passo B: Transferência entre carteiras (Abate o custo fixo da rede)
    qtd_btc_liquida = qtd_btc_comprada - taxa_rede_btc
    
    # Se as taxas de rede forem maiores que o saldo em BTC, a operação é inviável
    if qtd_btc_liquida <= 0: 
        return None 

    # Passo C: Venda no destino (Desconta taxa de trade final)
    valor_final_usd = (qtd_btc_liquida * p_venda_bid) * (1 - fee_venda)
    
    lucro_usd = valor_final_usd - investimento
    lucro_pct = (lucro_usd / investimento) * 100

    return {
        "comprar_em": exch_compra,
        "vender_em": exch_venda,
        "p_compra_ask": p_compra_ask,
        "p_venda_bid": p_venda_bid,
        "lucro_usd": round(lucro_usd, 2),
        "lucro_pct": round(lucro_pct, 4),
        "taxa_rede_usd": round(taxa_rede_btc * p_compra_ask, 2)
    }
# ... (seu código da função calcular_arbitragem fica acima) ...

# --- ÁREA DE TESTES 
if __name__ == "__main__":
    print("🛠 RODANDO TESTES DO MOTOR DE LÓGICA...")

    # Cenário de Teste ajustado para tuplas (Ask, Bid)
    teste_lucro = {
        'Binance': (100000, 99990), 
        'UpHold': (102000, 101500)
    }
    
    resultado = calcular_arbitragem(teste_lucro, investimento=500)
    
    if resultado:
        print(f"\n✅ SUCESSO! Lucro: {resultado['lucro_pct']}%")
        print(f"💰 Lucro em USD: ${resultado['lucro_usd']}")
        print(f"⛽ Taxa de Rede: ${resultado['taxa_rede_usd']}")
    else:
        print("\n❌ Operação Inviável (Taxas muito altas ou erro nos dados)")