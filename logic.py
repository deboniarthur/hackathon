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