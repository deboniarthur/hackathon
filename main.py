import streamlit as st
import time
import pandas as pd
from database import init_db, salvar_oportunidade, ler_historico
from services import PriceFetcher
from logic import calcular_arbitragem

# Configuração da Página
st.set_page_config(page_title="Bot.byte", layout="wide")

# Inicialização
init_db()
fetcher = PriceFetcher()

# --- SIDEBAR (CONFIGURAÇÕES) ---
st.sidebar.image("logo.jpeg", width=130)
st.sidebar.header("⚙️ Configurações do Motor")
taxa_input = st.sidebar.slider("Taxa da Exchange (%)", 0.0, 1.0, 0.1) / 100 # Converte 0.1 para 0.001
lucro_minimo = st.sidebar.number_input("Lucro Mínimo para Execução (%)", 0.1, 5.0, 0.5)
# Coloque isso na barra lateral (st.sidebar)
if st.sidebar.button("🗑️ Limpar Histórico"):
    import sqlite3
    conn = sqlite3.connect("arbitragem.db") # Ou use sua funcao get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM oportunidades")
    conn.commit()
    conn.close()
    st.toast("Histórico limpo com sucesso!", icon="✅")
    time.sleep(1)
    st.rerun() # Recarrega a página sozinho

# --- CABEÇALHO ---
st.title("🎯 Bot.byte")

with st.expander("📟 Logs do Sistema (Terminal)", expanded=False):
    st.code(f"""
    [INFO] Bot iniciado em: {time.strftime('%H:%M:%S')}
    [NETWORK] Conectado a: UpHold, Binance, Coinbase
    [STRATEGY] Buscando spreads > {lucro_minimo}%
    [STATUS] Monitorando...
    """)

# Container de Métricas em Tempo Real (P&L Acumulado)
# Vamos calcular isso somando o banco de dados
df_historico = ler_historico()
if not df_historico.empty:
    lucro_total = df_historico['lucro_pct'].sum() # Simplificação: soma das %
    trades_total = len(df_historico)
else:
    lucro_total = 0.0
    trades_total = 0

# Mostra o P&L no topo como pede o requisito
col_pl1, col_pl2, col_pl3 = st.columns(3)
col_pl1.metric("P&L Acumulado (Simulado)", f"{lucro_total:.2f}%")
col_pl2.metric("Oportunidades Executadas", trades_total)
col_pl3.metric("Taxa Aplicada", f"{taxa_input*100:.2f}%")

st.divider()

# --- LAYOUT PRINCIPAL ---
col_monitor, col_live_feed = st.columns([2, 1])

with col_monitor:
    st.subheader("📡 Radar de Mercado (Tempo Real)")
    placeholder_radar = st.empty()

with col_live_feed:
    st.subheader("📜 Histórico de Ordens")
    placeholder_feed = st.empty()

# --- LOOP PRINCIPAL ---
while True:
    # 1. Coleta Dados
    p_uphold_ask, p_uphold_bid = fetcher.get_uphold()
    p_bin, _ = fetcher.get_binance()
    p_coin, _ = fetcher.get_coinbase()
    p_ku_ask, p_ku_bid = fetcher.get_kucoin()
    
    # Monta dicionário (Usando Ask da Uphold para compra e Bid para venda seria o ideal, 
    # mas para simplificar o MVP usamos o preço base)
    dict_precos = {
        "UpHold": p_uphold_ask,
        "Binance": p_bin,
        "Coinbase": p_coin,
        "KuCoin": p_ku_ask
    }

    # 2. Motor de Cálculo (Com Taxas!)
    oportunidade = calcular_arbitragem(dict_precos, taxa_fee=taxa_input)

    # 3. Atualiza Radar
    with placeholder_radar.container():
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("UpHold", f"${p_uphold_ask:,.2f}" if p_uphold_ask else "Offline")
        c2.metric("Binance", f"${p_bin:,.2f}" if p_bin else "Offline")
        c3.metric("Coinbase", f"${p_coin:,.2f}" if p_coin else "Offline")
        c4.metric("KuCoin", f"${p_ku_ask:,.2f}" if p_ku_ask else "Offline")

        # Se achar oportunidade válida (acima do mínimo configurado)
        if oportunidade and oportunidade['lucro_pct'] > lucro_minimo:
            st.success(f"🚀 OPORTUNIDADE: Compre na {oportunidade['comprar_em']} e venda na {oportunidade['vender_em']}")
            st.metric("Lucro Líquido Estimado", f"{oportunidade['lucro_pct']:.2f}%", f"${oportunidade['lucro_usd']:.2f}")
            st.line_chart([oportunidade['lucro_pct']]) # Gráfico simples para destacar a oportunidade
            # Salva no Banco (Simula Execução)
            salvar_oportunidade(
                oportunidade['comprar_em'],
                oportunidade['vender_em'],
                oportunidade['p_compra'],
                oportunidade['p_venda'],
                oportunidade['lucro_pct']
            )
        elif oportunidade:
            # Mostra o spread atual mesmo que seja negativo ou baixo (para o juiz ver que está calculando)
            st.info(f"Spread Atual: {oportunidade['lucro_pct']:.2f}% (Abaixo do alvo de {lucro_minimo}%)")
        else:
            st.warning("Buscando dados...")

    # 4. Atualiza Tabela Lateral
    df_novo = ler_historico()
    placeholder_feed.dataframe(df_novo[['data_hora', 'lucro_pct', 'comprar_em', 'vender_em']].head(10), hide_index=True)

    time.sleep(3)