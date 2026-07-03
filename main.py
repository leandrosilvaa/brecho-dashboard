import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from streamlit_gsheets import GSheetsConnection
import gspread

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Brechó Que Mimo Kids", page_icon="🧸", layout="wide")

# Cores do Logo para usar nos gráficos
PALETA_CORES = ["#E6007E", "#FFCC00", "#00A8E8", "#6BBF59", "#FF6B35"]

# 2. CONFIGURAÇÃO DO BANCO DE DADOS (GOOGLE SHEETS)
# Cria a conexão nativa com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. CONFIGURAÇÃO DO BANCO DE DADOS (GOOGLE SHEETS)
import gspread

# Cria a conexão nativa com o Google Sheets (usada para LER os dados rapidamente)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_PLANILHA = st.secrets["connections"]["gsheets"]["spreadsheet"]

def carregar_dados():
    try:
        # ttl=0 limpa o cache para sempre trazer os dados mais recentes do celular
        df = conn.read(ttl=0)
        if df.empty or "Produto" not in df.columns:
            return pd.DataFrame(columns=["Produto", "Categoria", "Tamanho", "Data", "Forma de Pagamento", "Preço Unitário", "Quantidade", "Total"])
        
        # Garantir tratamento de data correto
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        return df
    except Exception:
        return pd.DataFrame(columns=["Produto", "Categoria", "Tamanho", "Data", "Forma de Pagamento", "Preço Unitário", "Quantidade", "Total"])

def salvar_dados_via_gspread(nova_linha_dict):
    try:
        # Conecta de forma pública na planilha que está como "Qualquer pessoa com o link pode editar"
        gc = gspread.public()
        sh = gc.open_by_url(URL_PLANILHA)
        ws = sh.get_worksheet(0) # Abre a primeira aba
        
        # Transforma o dicionário em uma lista ordenada para o Google Sheets
        valores = [
            nova_linha_dict["Produto"],
            nova_linha_dict["Categoria"],
            nova_linha_dict["Tamanho"],
            str(nova_linha_dict["Data"]),
            nova_linha_dict["Forma de Pagamento"],
            float(nova_linha_dict["Preço Unitário"]),
            int(nova_linha_dict["Quantidade"]),
            float(nova_linha_dict["Total"])
        ]
        
        # Adiciona a nova linha no final da planilha instantaneamente sem precisar de chaves secretas!
        ws.append_row(valores)
        st.cache_data.clear()  # Limpa o cache do Streamlit
    except Exception as e:
        st.error(f"Erro ao salvar dados no Google Sheets: {e}")


df_vendas = carregar_dados()

# 3. ESTILIZAÇÃO PERSONALIZADA AVANÇADA (100% Responsivo para Telemóvel)
st.markdown(f"""
    <style>
    .main .block-container {{ padding-top: 1.5rem; }}
    h1 {{ color: #E6007E !important; font-weight: 800; font-size: 28px; }}
    h2, h3, h4 {{ color: #00A8E8 !important; font-weight: 700; }}
    
    /* Cards de Indicadores */
    .card {{
        background: white;
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid #f0f0f0;
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.3s ease;
    }}
    .card-pink {{ border-top: 5px solid #E6007E; }}
    .card-blue {{ border-top: 5px solid #00A8E8; }}
    .card-green {{ border-top: 5px solid #6BBF59; }}
    
    .card-title {{ font-size: 14px; color: #888888; font-weight: 600; text-transform: uppercase; }}
    .card-value {{ font-size: 26px; font-weight: 800; color: #2D3748; margin-top: 6px; }}
    
    /* Painel de Visualização do Valor Total */
    .live-total-box {{
        background-color: #f6fff5;
        border: 2px dashed #6BBF59;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. SIDEBAR (MENU LATERAL)
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.markdown("<h1 style='text-align: center; font-size: 80px; margin: 0; padding: 0;'>🧸</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<h2 style='text-align: center; color: #E6007E; font-size: 22px; margin-top: -10px; margin-bottom: 20px;'>Que Mimo Kids</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

aba = st.sidebar.radio("Navegação", ["📊 Dashboard de Vendas", "🛍️ Registrar Nova Venda"])

# 5. ABA: DASHBOARD
if aba == "📊 Dashboard de Vendas":
    st.title("📊 Painel de Indicadores")
    
    if df_vendas.empty:
        st.info("Nenhuma venda registada ainda no Google Sheets. Vá ao menu 'Registrar Nova Venda' para começar!")
    else:
        # --- FILTROS TEMPORAIS ---
        st.markdown("### 📅 Filtrar Período de Visualização")
        col_filtro1, col_filtro2 = st.columns([1, 2])
        
        today = date.today()
        
        with col_filtro1:
            opcao_periodo = st.selectbox(
                "Mostrar dados de:",
                ["Hoje", "Este Mês", "Tudo Acumulado", "Período Personalizado"],
                index=1
            )
        
        if opcao_periodo == "Hoje":
            df_filtrado = df_vendas[df_vendas['Data'] == today]
        elif opcao_periodo == "Este Mês":
            df_filtrado = df_vendas[df_vendas['Data'].apply(lambda x: x.year == today.year and x.month == today.month)]
        elif opcao_periodo == "Tudo Acumulado":
            df_filtrado = df_vendas
        elif opcao_periodo == "Período Personalizado":
            with col_filtro2:
                intervalo_datas = st.date_input("Escolha o início e fim:", [today, today])
                if len(intervalo_datas) == 2:
                    data_inicio, data_fim = intervalo_datas
                    df_filtrado = df_vendas[(df_vendas['Data'] >= data_inicio) & (df_vendas['Data'] <= data_fim)]
                else:
                    df_filtrado = df_vendas[df_vendas['Data'] == intervalo_datas[0]]

        st.markdown("---")

        if df_filtrado.empty:
            st.warning(f"⚠️ Nenhuma venda registada para o período selecionado: '{opcao_periodo}'.")
        else:
            faturamento_total = df_filtrado["Total"].sum()
            total_vendas = len(df_filtrado)
            ticket_medio = faturamento_total / total_vendas if total_vendas > 0 else 0
            
            pagamentos = df_filtrado.groupby("Forma de Pagamento")["Total"].sum().to_dict()
            pix_total = pagamentos.get("Pix", 0)
            credito_total = pagamentos.get("Crédito", 0)
            dinheiro_total = pagamentos.get("Dinheiro", 0)

            # Layout adaptável para colunas
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="card card-pink"><div class="card-title">💰 Faturamento ({opcao_periodo})</div><div class="card-value">R$ {faturamento_total:,.2f}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="card card-blue"><div class="card-title">📦 Peças Vendidas</div><div class="card-value">{int(df_filtrado["Quantidade"].sum())}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="card card-green"><div class="card-title">📈 Ticket Médio</div><div class="card-value">R$ {ticket_medio:,.2f}</div></div>', unsafe_allow_html=True)

            st.markdown("<h3 style='margin-top: 25px;'>💵 Meios de Pagamento</h3>", unsafe_allow_html=True)
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                st.markdown(f'<div class="card" style="border-top: 5px solid #6BBF59"><div class="card-title">📱 Total Pix</div><div class="card-value" style="color: #6BBF59;">R$ {pix_total:,.2f}</div></div>', unsafe_allow_html=True)
            with col_p2:
                st.markdown(f'<div class="card" style="border-top: 5px solid #00A8E8"><div class="card-title">💳 Total Crédito</div><div class="card-value" style="color: #00A8E8;">R$ {credito_total:,.2f}</div></div>', unsafe_allow_html=True)
            with col_p3:
                st.markdown(f'<div class="card" style="border-top: 5px solid #FF6B35"><div class="card-title">💵 Total Dinheiro</div><div class="card-value" style="color: #FF6B35;">R$ {dinheiro_total:,.2f}</div></div>', unsafe_allow_html=True)

            st.markdown("---")
            
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("#### 📅 Evolução Diária das Vendas")
                df_diario = df_filtrado.groupby("Data")["Total"].sum().reset_index().sort_values(by="Data")
                fig_dia = px.bar(df_diario, x="Data", y="Total", color_discrete_sequence=[PALETA_CORES[2]])
                fig_dia.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_dia, use_container_width=True)

            with col_g2:
                st.markdown("#### 👕 Vendas por Categoria")
                df_cat = df_filtrado.groupby("Categoria")["Total"].sum().reset_index()
                fig_cat = px.pie(df_cat, values="Total", names="Categoria", color_discrete_sequence=PALETA_CORES)
                fig_cat.update_traces(textposition='inside', textinfo='percent+label')
                fig_cat.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_cat, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 📜 Histórico de Transações do Período")
            st.dataframe(df_filtrado.sort_index(ascending=False), use_container_width=True)

# 6. ABA: FORMULÁRIO DE CADASTRO DE VENDA
elif aba == "🛍️ Registrar Nova Venda":
    st.title("🛍️ Lançar Nova Venda")
    st.markdown("Preencha os campos abaixo para registar o produto vendido.")
    
    bg_container = st.container(border=True)
    
    with bg_container:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            produto = st.text_input("Nome do Produto", placeholder="Ex: Conjunto Moletom Tigre")
            categoria = st.selectbox("Categoria", ["Camisas", "Blusas", "Brinquedos", "Conjuntos", "Vestidos", "Calças / Bermudas", "Calçados", "Acessórios"])
            tamanho = st.selectbox("Tamanho", ["RN", "P", "M", "G", "GG", "1 Ano", "2 Anos", "3 a 4 Anos", "5 a 6 Anos", "Outro"])
        
        with col_f2:
            data_venda = st.date_input("Data da Venda", value=date.today())
            forma_pagamento = st.selectbox("Forma de Pagamento", ["Pix", "Crédito", "Dinheiro"])
            preco_unitario = st.number_input("Preço Unitário (R$)", min_value=0.0, step=0.50, format="%.2f")
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
        
        total_item = preco_unitario * quantidade
        
        st.markdown(f"""
            <div class="live-total-box">
                <span style="color: #555; font-weight: bold; font-size: 14px; text-transform: uppercase;">💰 VALOR TOTAL DESTA VENDA</span><br>
                <span style="color: #6BBF59; font-size: 32px; font-weight: 800;">R$ {total_item:,.2f}</span>
            </div>
        """, unsafe_allow_html=True)
        
        botao_salvar = st.button("Confirmar e Registrar Venda", use_container_width=True, type="primary")
        
        if botao_salvar:
            if produto == "" or preco_unitario == 0:
                st.error("Por favor, preencha o nome do produto e o valor da peça!")
            else:
                dados_venda = {
                    "Produto": produto,
                    "Categoria": categoria,
                    "Tamanho": tamanho,
                    "Data": data_venda,
                    "Forma de Pagamento": forma_pagamento,
                    "Preço Unitário": preco_unitario,
                    "Quantidade": quantidade,
                    "Total": total_item
                }
                
               # df_atual = carregar_dados()
               # df_atualizado = pd.concat([df_atual, nova_venda], ignore_index=True)
               # salvar_dados(df_atualizado)
                # CHAMA A FUNÇÃO NOVA QUE ADICIONAMOS VIA GSPREAD
                salvar_dados_via_gspread(dados_venda)
                
                st.success("✅ Venda realizada com sucesso!")
                st.balloons()
                st.rerun()
