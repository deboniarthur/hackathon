def calcular_arbitragem(precos):
    """
    Recebe um dicionário: {'UpHold': 98000, 'Binance': 97500}
    Retorna a melhor oportunidade ou None
    """
    # Filtra quem está None (offline)
    validos = {k: v for k, v in precos.items() if v is not None}
    
    if len(validos) < 2:
        return None

    barato_nome = min(validos, key=validos.get)
    caro_nome = max(validos, key=validos.get)
    
    p_barato = validos[barato_nome]
    p_caro = validos[caro_nome]
    
    lucro = ((p_caro - p_barato) / p_barato) * 100
    
    return {
        "comprar": barato_nome,
        "vender": caro_nome,
        "p_compra": p_barato,
        "p_venda": p_caro,
        "lucro": lucro
    }