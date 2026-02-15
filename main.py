import streamlit as st
import time
import pandas as pd
from database import init_db, salvar_oportunidade, ler_historico
from services import PriceFetcher
from logic import calcular_arbitragem
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA (Deve ser o primeiro comando) ---
st.set_page_config(
    page_title="Bot.byte | Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILIZAÇÃO PROFISSIONAL (CSS) ---
st.markdown("""
<style>
    /* Importando fonte técnica */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    /* Reset Geral */
    .stApp {
        background-color: #0E1117;
        color: #E6E6E6;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Navbar Customizada */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        background-color: #161B22;
        border-bottom: 1px solid #30363D;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    /* Indicador de Status Pulsante */
    .status-dot {
        height: 12px;
        width: 12px;
        background-color: #00FFA3;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #00FFA3;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 163, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 163, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 163, 0); }
    }

    /* Cards de Métricas (KPIs) */
    div[data-testid="stMetric"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 15px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #00FFA3;
        box-shadow: 0 4px 15px rgba(0, 255, 163, 0.1);
    }
    div[data-testid="stMetricValue"] {
        color: #00FFA3 !important;
        font-weight: 700;
    }

    /* Tabela (Dataframe) */
    div[data-testid="stDataFrame"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid #30363D;
    }
    
    /* Botões */
    div.stButton > button {
        background-color: #238636;
        color: white;
        border: 1px solid rgba(240, 246, 252, 0.1);
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #2ea043;
        border-color: #8b949e;
    }
    
    /* Textos Auxiliares */
    .small-text {
        font-size: 12px;
        color: #8b949e;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO ---
init_db()
fetcher = PriceFetcher()

# --- HEADER PERSONALIZADO ---
st.markdown("""
<div class="nav-container">
    <div style="font-size: 24px; font-weight: bold; color: #E6E6E6;">
        ⚡ Bot<span style="color: #00FFA3;">.byte</span> <span style="font-size: 14px; color: #8b949e;">| PRO TERMINAL</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <span style="color: #00FFA3; font-weight: bold; font-size: 14px;">SISTEMA ATIVO</span>
        <div class="status-dot"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR NATIVA (SEM CSS) ---
with st.sidebar:

    st.image("logo.jpeg", width=844)

    st.divider()

    # 2. Gestão Financeira
    st.subheader("💰 Capital Operacional")
    
    investimento_input = st.number_input(
        "Valor do Investimento (USD)",
        min_value=100.0,
        max_value=10000000000.0,
        value=10000.0,
        step=500.0,
        format="%.2f",
        help="Montante usado para calcular o lucro líquido real."
    )

    # 3. Estratégia
    st.subheader("🎯 Configuração de Alvo")
    
    lucro_minimo = st.number_input(
        "Spread Mínimo Desejado (%)",
        min_value=0.01,
        max_value=20.0,
        value=0.15,
        step=0.01,
        format="%.2f"
    )

    # O st.toggle é o botão de "chave" moderno do Streamlit
    ignorar_rede = st.toggle("Ignorar Taxas de Rede (Modo Demo)", value=False)
    
    if ignorar_rede:
        # st.warning cria uma caixa amarela nativa
        st.warning("⚠️ Custos de Blockchain zerados.")

    # 4. Configurações Técnicas (Escondidas no Expander para limpar o visual)
    with st.expander("⚙️ Ajuste Fino de Taxas"):
        st.caption("Taxa média das Exchanges")
        taxa_display = st.slider(
            "Fee (%)",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.01,
            format="%.2f%%"
        )
        taxa_input = taxa_display / 100
        st.info(f"Fator: {taxa_display}% Compra + {taxa_display}% Venda")

    st.divider()

    # 5. Ações de Banco de Dados
    st.subheader("💾 Dados")
    
    # type="primary" deixa o botão vermelho/destacado nativamente
    if st.button("🗑️ Limpar Histórico", type="primary", use_container_width=True):
        import sqlite3
        conn = sqlite3.connect("arbitragem.db")
        c = conn.cursor()
        c.execute("DELETE FROM oportunidades")
        conn.commit()
        conn.close()
        st.toast("Banco de dados limpo!", icon="✅")
        time.sleep(1)
        st.rerun()

    # Rodapé simples usando caption
    st.caption("Bot.byte | 2026")
# --- DASHBOARD (LAYOUT PRINCIPAL) ---

# Top KPI Row
placeholder_metrics = st.empty()

# Main Split
col_main, col_sidebar = st.columns([2.5, 1])

with col_main:
    st.markdown("##### 📡 SCANNER DE MERCADO (LIVE)")
    # Radar de Preços (Grid 4x1)
    placeholder_radar = st.empty()
    
    st.markdown("##### 📈 GRÁFICO DE PERFORMANCE")
    # Gráfico
    placeholder_chart = st.empty()

with col_sidebar:
    st.markdown("##### 📜 HISTÓRICO DE ORDENS")
    placeholder_feed = st.empty()
    
    st.markdown("##### 📊 COMPRAS POR EXCHANGE")
    placeholder_pie = st.empty()

# --- LOOP PRINCIPAL ---
while True:
    # 1. Fetch
    try:
        p_uphold_ask, p_uphold_bid = fetcher.get_uphold()
        p_bin, _ = fetcher.get_binance()
        p_coin, _ = fetcher.get_coinbase()
        p_kucoin, _ = fetcher.get_kucoin()
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        time.sleep(5)
        continue

    dict_precos = {
        "UpHold": p_uphold_ask, 
        "Binance": p_bin,
        "Coinbase": p_coin,
        "Kucoin": p_kucoin
    }

    # 2. Logic (Passando investimento para calcular taxas corretamente)
    oportunidade = calcular_arbitragem(
        dict_precos, 
        investimento=investimento_input, 
        taxa_fee=taxa_input,
        ignorar_rede=ignorar_rede
    )

    # 3. Ler dados históricos
    df_historico = ler_historico()
    
    # KPIs Globais
    total_profit = df_historico['lucro_pct'].sum() if not df_historico.empty else 0.0
    count_trades = len(df_historico)
    
    with placeholder_metrics.container():
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("P&L (Total)", f"{total_profit:.2f}%", delta_color="normal")
        k2.metric("Ordens Executadas", f"{count_trades}")
        k3.metric("Capital Alocado", f"${investimento_input:,.0f}")
        k4.metric("Spread Alvo", f"{lucro_minimo}%")

    # Atualiza Radar
    with placeholder_radar.container():
        # Estilo "Ticker Tape"
        r1, r2, r3, r4 = st.columns(4)
        
        def price_card(col, label, price):
            val = f"${price:,.2f}" if price else "OFFLINE"
            col.metric(label, val)
        
        price_card(r1, "UpHold", p_uphold_ask)
        price_card(r2, "Binance", p_bin)
        price_card(r3, "Coinbase", p_coin)
        price_card(r4, "Kucoin", p_kucoin)

        # Lógica de Oportunidade e Gráfico
        if oportunidade and oportunidade['lucro_pct'] > lucro_minimo:
            # CARD DE ALERTA DE LUCRO (Estilo Terminal)
            st.markdown(f"""
            <div style="background-color: rgba(0, 255, 163, 0.1); border: 1px solid #00FFA3; padding: 15px; border-radius: 5px; margin-top: 10px;">
                <label style="color: #00FFA3; margin:0;">🚀 SINAL DE OPORTUNIDADE DETECTADO</h3>
                <p style="margin:0;">BUY: <b>{oportunidade['comprar_em']}</b> | SELL: <b>{oportunidade['vender_em']}</b></p>
                <label style="color: white; margin:0;">LUCRO: {oportunidade['lucro_pct']:.2f}% <span style="font-size: 16px;">(${oportunidade['lucro_usd']:.2f})</span></h2>
            </div>
            """, unsafe_allow_html=True)
            
            # --- CORREÇÃO DO GRÁFICO (Live Update) ---
            if not df_historico.empty:
                df_visual = df_historico[['lucro_pct']].copy()
            else:
                df_visual = pd.DataFrame(columns=['lucro_pct'])

            # Adiciona o dado atual "na memória" para o gráfico atualizar AGORA
            novo_dado = pd.DataFrame({'lucro_pct': [oportunidade['lucro_pct']]})
            df_chart = pd.concat([df_visual, novo_dado], ignore_index=True)
            df_chart['acumulado'] = df_chart['lucro_pct'].cumsum()
            
            # Plotly Chart Customizado (Verde e Escuro)
            fig_line = px.area(df_chart, y='acumulado', template='plotly_dark')
            fig_line.update_traces(line_color='#00FFA3', fillcolor='rgba(0, 255, 163, 0.1)')
            fig_line.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            placeholder_chart.plotly_chart(fig_line, use_container_width=True, key=f"chart_{time.time()}")

            # Salva no DB
            salvar_oportunidade(
                oportunidade['comprar_em'],
                oportunidade['vender_em'],
                oportunidade['p_compra'],
                oportunidade['p_venda'],
                oportunidade['lucro_pct'],
                oportunidade['lucro_usd']
            )
            time.sleep(2) # Pausa para ver o lucro

        elif oportunidade:
             # Mostra spread negativo ou baixo de forma discreta
            st.markdown(f"""
            <div style="border: 1px dashed #30363D; padding: 10px; border-radius: 5px; margin-top: 10px; color: #8b949e; text-align: center;">
                Buscando... Spread Atual: <span style="color: {'#ff4b4b' if oportunidade['lucro_pct'] < 0 else '#E6E6E6'}">{oportunidade['lucro_pct']:.2f}%</span> (Alvo: {lucro_minimo}%)
            </div>
            """, unsafe_allow_html=True)
            
            # Mostra gráfico estático (histórico) se não tiver nova ordem
            if not df_historico.empty:
                df_chart = df_historico.copy()
                df_chart['acumulado'] = df_chart['lucro_pct'].cumsum()
                fig_line = px.area(df_chart, y='acumulado', template='plotly_dark')
                fig_line.update_traces(line_color='#00FFA3', fillcolor='rgba(0, 255, 163, 0.1)')
                fig_line.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                placeholder_chart.plotly_chart(fig_line, use_container_width=True, key=f"line_chart_{time.time()}")
            else:
                placeholder_chart.info("Aguardando primeira execução para gerar gráfico...")

        else:
            st.warning("Mercado Offline ou Dados Insuficientes")

    # 4. Atualiza Feed Lateral
    with placeholder_feed.container():
        if not df_historico.empty:
            # Tabela Estilizada
            st.dataframe(
                df_historico[['data_hora', 'lucro_pct', 'comprar_em', 'vender_em']].tail(10).iloc[::-1],
                column_config={
                    "data_hora": st.column_config.TextColumn("Data/Hora"),
                    "lucro_pct": st.column_config.NumberColumn("Lucro %", format="%.2f%%"),
                    "comprar_em": "Buy",
                    "vender_em": "Sell"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.text("Sem trades executados ainda.")

    # 5. Atualiza Pizza (Volume)
    with placeholder_pie.container():
        if not df_historico.empty:
            dist = df_historico['comprar_em'].value_counts().reset_index()
            dist.columns = ['Exchange', 'Qtd']
            
            fig_pie = px.pie(dist, values='Qtd', names='Exchange', hole=0.6, template='plotly_dark')
            fig_pie.update_traces(textinfo='percent', marker=dict(colors=['#00FFA3', '#238636', '#0E4429']))
            fig_pie.update_layout(showlegend=False, height=200, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)')
            
            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{time.time()}")

    time.sleep(2)