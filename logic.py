def calcular_arbitragem(precos, taxa_fee=0.001): # 0.001 = 0.1% de taxa
    """
    Calcula o lucro LÍQUIDO (descontando taxas de compra e venda).
    Requisito: Motor de Spread Líquido.
    """
    # Filtra quem está offline
    validos = {k: v for k, v in precos.items() if v is not None}
    
    if len(validos) < 2:
        return None

    # Identifica menor e maior preço
    exchange_compra = min(validos, key=validos.get)
    exchange_venda = max(validos, key=validos.get)
    
    preco_compra_bruto = validos[exchange_compra]
    preco_venda_bruto = validos[exchange_venda]
    
    # --- A MATEMÁTICA DO SPREAD LÍQUIDO ---
    # 1. Custo total na compra (Preço + Taxa)
    custo_compra = preco_compra_bruto * (1 + taxa_fee)
    
    # 2. Receita total na venda (Preço - Taxa)
    receita_venda = preco_venda_bruto * (1 - taxa_fee)
    
    # 3. Lucro Real (Net Profit)
    lucro_liquido = receita_venda - custo_compra
    lucro_pct = (lucro_liquido / custo_compra) * 100
    
    return {
        "comprar_em": exchange_compra,
        "vender_em": exchange_venda,
        "p_compra": preco_compra_bruto,
        "p_venda": preco_venda_bruto,
        "lucro_usd": lucro_liquido,
        "lucro_pct": lucro_pct
    }