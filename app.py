import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard - Indústria Calçadista", page_icon="👞", layout="wide")
st.title("👞 Dashboard de Produção e Vendas")
st.markdown("Visão executiva do faturamento e status do chão de fábrica.")

# 2. Carregando os Dados (O @st.cache_data faz o app carregar super rápido)
@st.cache_data
def carregar_dados():
    df = pd.read_excel('dados_fabrica_calcados.xlsx')
    
    # Criando as colunas financeiras usando a base do Pandas
    df['Faturamento'] = df['Preco_Venda_Par'] * df['Quantidade_Pares']
    df['Custo_Total'] = df['Custo_Material_Par'] * df['Quantidade_Pares']
    df['Lucro'] = df['Faturamento'] - df['Custo_Total']
    
    # Ajustando a data para extrair apenas Mês e Ano
    df['Mes_Ano'] = df['Data_Venda'].dt.to_period('M').astype(str)
    
    # Ordenando cronologicamente
    df = df.sort_values(by='Data_Venda')
    return df

df = carregar_dados()

# 3. Barra Lateral (Filtros Interativos)
st.sidebar.header("⚙️ Filtros do Dashboard")
modelo_selecionado = st.sidebar.multiselect(
    "Selecione o(s) Modelo(s):",
    options=df['Modelo'].unique(),
    default=df['Modelo'].unique()
)

status_selecionado = st.sidebar.multiselect(
    "Status de Produção:",
    options=df['Status_Producao'].unique(),
    default=df['Status_Producao'].unique()
)

# Aplicando os filtros no DataFrame principal
df_filtrado = df[(df['Modelo'].isin(modelo_selecionado)) & (df['Status_Producao'].isin(status_selecionado))]

# 4. KPIs (Indicadores Principais)
st.subheader("Resumo Financeiro e de Produção")
col1, col2, col3, col4 = st.columns(4)

faturamento_total = df_filtrado['Faturamento'].sum()
lucro_total = df_filtrado['Lucro'].sum()
margem_lucro = (lucro_total / faturamento_total) * 100 if faturamento_total > 0 else 0
pares_produzidos = df_filtrado['Quantidade_Pares'].sum()

# Formatando os números para o padrão brasileiro
col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
col2.metric("Lucro Total", f"R$ {lucro_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
col3.metric("Margem de Lucro", f"{margem_lucro:.1f}%")
col4.metric("Pares Produzidos", f"{pares_produzidos:,}".replace(',', '.'))

st.markdown("---")

# 5. Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Faturamento Mensal")
    # Agrupando os dados por mês para o gráfico de linha
    df_mensal = df_filtrado.groupby('Mes_Ano')['Faturamento'].sum().reset_index()
    fig_linha = px.line(df_mensal, x='Mes_Ano', y='Faturamento', markers=True)
    fig_linha.update_layout(xaxis_title="Mês/Ano", yaxis_title="Faturamento (R$)")
    st.plotly_chart(fig_linha, use_container_width=True)

with col_graf2:
    st.subheader("Lucro por Modelo")
    # Agrupando para ver qual modelo traz mais dinheiro real para a empresa
    df_modelo = df_filtrado.groupby('Modelo')['Lucro'].sum().reset_index()
    fig_barras = px.bar(df_modelo, x='Modelo', y='Lucro', color='Modelo')
    fig_barras.update_layout(xaxis_title="Modelo de Calçado", yaxis_title="Lucro Total (R$)")
    st.plotly_chart(fig_barras, use_container_width=True)

# Gráfico Inferior Pegando a Tela Toda
st.subheader("Status do Chão de Fábrica")
df_status = df_filtrado.groupby('Status_Producao')['Quantidade_Pares'].sum().reset_index()
fig_pizza = px.pie(df_status, values='Quantidade_Pares', names='Status_Producao', hole=0.4)
st.plotly_chart(fig_pizza, use_container_width=True)