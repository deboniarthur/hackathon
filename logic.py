from services import get_real_network_fee

# Taxas reais por exchange (Diferencial técnico para o projeto)
TAXAS_EXCHANGES = {
    'Binance': 0.001,   # 0.1%
    'UpHold': 0.002,    # 0.2%
    'Coinbase': 0.005,  # 0.5%
    'KuCoin': 0.001     # 0.1%
}

def _normalizar_preco(valor):
    """
    Garante que recebemos a tupla (ask, bid). 
    Retorna None para qualquer dado inválido ou zerado, protegendo o motor de cálculo.
    """
    try:
        if isinstance(valor, (list, tuple)) and len(valor) >= 2:
            ask, bid = float(valor[0]), float(valor[1])
            if ask > 0 and bid > 0:
                return ask, bid
        return None
    except (ValueError, TypeError):
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

    # Cenário 1: O sonho (Binance barata, UpHold cara)
    # Lucro bruto seria 1.000 (1%). Com taxas, deve cair para ~0.8%.
    teste_lucro = {'Binance': 100000, 'UpHold': 101000, 'Coinbase': 100500}
    resultado = calcular_arbitragem(teste_lucro, taxa_fee=0.001)
    
    print("\n--- Cenário 1: Esperado Lucro ---")
    if resultado['lucro_pct'] > 0:
        print(f"✅ SUCESSO! Lucro calculado: {resultado['lucro_pct']:.4f}%")
        print(f"Detalhes: Comprar na {resultado['comprar_em']} e vender na {resultado['vender_em']}")
    else:
        print(f"❌ ERRO! Deveria dar lucro. Deu: {resultado['lucro_pct']}%")

    # Cenário 2: O pesadelo das Taxas (Preços iguais)
    # Se comprar e vender a 100k com taxa, você PERDE dinheiro. O código tem que mostrar negativo.
    teste_prejuizo = {'Binance': 100000, 'UpHold': 100000}
    resultado2 = calcular_arbitragem(teste_prejuizo, taxa_fee=0.001)
    
    print("\n--- Cenário 2: Esperado Prejuízo (Taxas) ---")
    if resultado2['lucro_pct'] < 0:
        print(f"✅ SUCESSO! O sistema detectou o custo das taxas: {resultado2['lucro_pct']:.4f}%")
    else:
        print(f"❌ ERRO! Deu lucro onde não devia.")