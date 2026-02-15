import sqlite3
from datetime import datetime

DB_NAME = "arbitragem.db"

def init_db():
    """Cria a tabela se não existir"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS oportunidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TEXT,
            comprar_em TEXT,
            vender_em TEXT,
            preco_compra REAL,
            preco_venda REAL,
            lucro_pct REAL,
            lucro_usd REAL
        )
    ''')
    conn.commit()
    conn.close()

def salvar_oportunidade(compra, venda, p_compra, p_venda, lucro, lucro_usd):
    """Registra uma oportunidade lucrativa"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO oportunidades (data_hora, comprar_em, vender_em, preco_compra, preco_venda, lucro_pct, lucro_usd) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (data_atual, compra, venda, p_compra, p_venda, lucro, lucro_usd))
    conn.commit()
    conn.close()

def ler_historico():
    """Lê as últimas oportunidades para mostrar na tela"""
    conn = sqlite3.connect(DB_NAME)
    import pandas as pd
    df = pd.read_sql_query("SELECT * FROM oportunidades ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df