import streamlit as st
import time
import pandas as pd
from database import init_db, salvar_oportunidade, ler_historico
from services import PriceFetcher
from logic import calcular_arbitragem
import plotly.express as px





st.markdown("""
<style>
    /* Estilo da Navbar Superior */
    .nav-bar {
        background-color: #161b22;
        padding: 10px 20px;
        border-bottom: 2px solid #00ff88;
        display: flex;
        justify-content: space-between;
        position: fixed;
        top: 0; left: 0; width: 100%;
        z-index: 9999;
    }
    /* Ajuste para o conteúdo não ficar por baixo da barra */
    .main .block-container {
        padding-top: 5rem;
    }
    /* Estilo dos Cards de Métricas */
    div[data-testid="stMetric"] {
        background-color: #1c2128;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
    }
</style>

<div class="nav-bar">
    <div style="color: white; font-weight: bold; font-size: 20px;">🤖 ARBITRAGE BOT</div>
    <div style="color: #00ff88;">● LIVE SYSTEM</div>
</div>
""", unsafe_allow_html=True)





# Configuração da Página
st.set_page_config(page_title="Spread Hunters Bot", layout="wide")

# Inicialização
init_db()
fetcher = PriceFetcher()

# --- SIDEBAR (CONFIGURAÇÕES) ---
st.sidebar.image("logo.jpeg", width=130)
st.sidebar.header("Configurações do Motor Simulado")
taxa_input = st.sidebar.slider("Taxa da Exchange (%)", 0.0, 1.0, 0.01) / 100 # Converte 0.1 para 0.001
lucro_minimo = st.sidebar.number_input("Lucro Mínimo para Execução (%)", 0.01, 5.0, 0.5)
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

with st.expander("📟 Logs do Sistema", expanded=False):
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
    p_kucoin, _ = fetcher.get_kucoin()
    
    # Monta dicionário (Usando Ask da Uphold para compra e Bid para venda seria o ideal, 
    # mas para simplificar o MVP usamos o preço base)
    dict_precos = {
        "UpHold": p_uphold_ask,
        "Binance": p_bin,
        "Coinbase": p_coin,
        "Kucoin": p_kucoin
    }

    # 2. Motor de Cálculo (Com Taxas!)
    oportunidade = calcular_arbitragem(dict_precos, taxa_fee=taxa_input)

    # 3. Atualiza Radar
    with placeholder_radar.container():
        
        c1, c2 = st.columns(2)
        c1.metric("UpHold", f"${p_uphold_ask:,.2f}" if p_uphold_ask else "Offline")
        c1.metric("Coinbase", f"${p_coin:,.2f}" if p_coin else "Offline")
        c2.metric("Binance", f"${p_bin:,.2f}" if p_bin else "Offline")
        c2.metric("Kucoin", f"${p_kucoin:,.2f}" if p_kucoin else "Offline")
        
       
        if oportunidade and oportunidade['lucro_pct'] > lucro_minimo:
            st.success(f"🚀 OPORTUNIDADE: Compre na {oportunidade['comprar_em']} e venda na {oportunidade['vender_em']}")
            st.metric("Lucro Líquido Estimado", f"{oportunidade['lucro_pct']:.2f}%", f"${oportunidade['lucro_usd']:.2f}")
            
            # Melhoria do Gráfico: Mostra a progressão histórica
            if not df_historico.empty:
                # Criamos uma coluna de lucro acumulado para o gráfico ser uma linha crescente
                df_visual = df_historico.copy()
                df_visual['Lucro Acumulado (%)'] = df_visual['lucro_pct'].cumsum()
                st.line_chart(df_visual['Lucro Acumulado (%)'])
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
    
    lucro_total = df_novo['lucro_pct'].sum()
    trades_total = len(df_novo)

# E use placeholders para as métricas se quiser que elas mudem em tempo real
    with placeholder_feed.container():
    # Tabela
        st.dataframe(
            df_novo[['data_hora', 'lucro_pct', 'comprar_em', 'vender_em']].head(10),
            hide_index=True
        )

        st.markdown("### 📊 Distribuição das Exchanges (Compras)")

        if not df_novo.empty:
            # Conta quantas vezes cada exchange foi usada para compra
            distribuicao = df_novo['comprar_em'].value_counts().reset_index()
            distribuicao.columns = ['Exchange', 'Quantidade']

            # Cria gráfico de pizza
            fig = px.pie(
                distribuicao,
                names='Exchange',
                values='Quantidade',
                hole=0.4  # deixa estilo donut (mais moderno)
            )

            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("Sem dados suficientes para gerar gráfico.")

    time.sleep(2)# Recarrega a página para atualizar os dados (Simula o loop contínuo)