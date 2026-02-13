import streamlit as st
import time
from database import init_db, salvar_oportunidade, ler_historico
from services import PriceFetcher
from logic import calcular_arbitragem

# Configuração Inicial
st.set_page_config(page_title="UpHold ArbBot", layout="wide")
init_db() # Garante que o banco existe
fetcher = PriceFetcher()

st.title("🚀 UpHold Arbitrage Scanner")

# Layout de Colunas
col_precos, col_historico = st.columns([2, 1])

with col_precos:
    st.subheader("Mercado em Tempo Real")
    placeholder_metricas = st.empty()
    placeholder_alerta = st.empty()

with col_historico:
    st.subheader("Histórico de Oportunidades")
    placeholder_tabela = st.empty()

# Loop Infinito
while True:
    # 1. Coleta
    p_up_ask, _ = fetcher.get_uphold()
    p_bin, _ = fetcher.get_binance()
    p_coin, _ = fetcher.get_coinbase()
    
    dict_precos = {
        "UpHold": p_up_ask,
        "Binance": p_bin,
        "Coinbase": p_coin
    }

    # 2. Lógica
    oportunidade = calcular_arbitragem(dict_precos)

    # 3. Atualização Visual
    with placeholder_metricas.container():
        c1, c2, c3 = st.columns(3)
        c1.metric("UpHold", f"${p_up_ask:,.2f}" if p_up_ask else "Offline")
        c2.metric("Binance", f"${p_bin:,.2f}" if p_bin else "Offline")
        c3.metric("Coinbase", f"${p_coin:,.2f}" if p_coin else "Offline")

    # 4. Decisão e Banco de Dados
    if oportunidade and oportunidade['lucro'] > 0.5: # Só avisa se lucro > 0.5%
        msg = f"LUCRO: {oportunidade['lucro']:.2f}% | Compre na {oportunidade['comprar']} e venda na {oportunidade['vender']}"
        placeholder_alerta.success(f"🚨 {msg}")
        
        # Salva no SQLite
        salvar_oportunidade(
            oportunidade['comprar'],
            oportunidade['vender'],
            oportunidade['p_compra'],
            oportunidade['p_venda'],
            oportunidade['lucro']
        )
    else:
        placeholder_alerta.info("🔍 Monitorando spreads...")

    # 5. Atualiza Tabela de Histórico
    df = ler_historico()
    placeholder_tabela.dataframe(df, hide_index=True)

    time.sleep(3)






