import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    page_title="Dashboard de Cancelamentos de Clientes",
    page_icon="📉",
    layout="wide",
)


# --- Carregamento dos dados ---
df = pd.read_csv("cancelamentos.csv")

# --- Limpeza de dados ---
df = df.drop(columns="CustomerID", errors="ignore")
df = df.dropna()

# --- Mapeia valores para Sim/Não e cria coluna cancelou_label ---
mapa_cancelou = {1: "Sim", 0: "Não", True: "Sim", False: "Não"}
df["cancelou_label"] = df["cancelou"].map(mapa_cancelou)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro: Cancelou
cancelou_opcoes = df['cancelou_label'].unique()
cancelou_sel = st.sidebar.multiselect("Status do Cliente", cancelou_opcoes, default=cancelou_opcoes)

# Aplica o filtro
df = df[df["cancelou_label"].isin(cancelou_sel)]

# Filtro: Sexo
sexo_opcoes = df['sexo'].unique()
sexo_sel = st.sidebar.multiselect("Sexo", sexo_opcoes, default=sexo_opcoes)

# Filtro: Idade
idade_min, idade_max = int(df['idade'].min()), int(df['idade'].max())
idade_sel = st.sidebar.slider("Idade", idade_min, idade_max, (idade_min, idade_max))

# Filtro: Frequência de uso
freq_min, freq_max = int(df['frequencia_uso'].min()), int(df['frequencia_uso'].max())
freq_sel = st.sidebar.slider("Frequência de Uso", freq_min, freq_max, (freq_min, freq_max))

# Filtro: Ligações Call Center
call_min, call_max = int(df['ligacoes_callcenter'].min()), int(df['ligacoes_callcenter'].max())
call_sel = st.sidebar.slider("Nº de Ligações Call Center", call_min, call_max, (call_min, call_max))

# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['cancelou_label'].isin(cancelou_sel)) &
    (df['sexo'].isin(sexo_sel)) &
    (df['idade'].between(idade_sel[0], idade_sel[1])) &
    (df['frequencia_uso'].between(freq_sel[0], freq_sel[1])) &
    (df['ligacoes_callcenter'].between(call_sel[0], call_sel[1]))
]

# Criar coluna categórica de "Sim/Não"
df_filtrado["cancelou_label"] = df_filtrado["cancelou"].map({0: "Não", 1: "Sim"})

# --- Conteúdo Principal ---
st.title("📉 Dashboard de Cancelamentos de Clientes")
st.markdown("Analise o comportamento dos cancelamentos e entenda os fatores que influenciam a saída dos clientes.")

# --- KPIs ---
st.subheader("📊 Métricas Gerais")

if not df_filtrado.empty:
    total_clientes = df_filtrado.shape[0]
    total_cancelados = df_filtrado[df_filtrado["cancelou"] == 1].shape[0]
    perc_cancelados = total_cancelados / total_clientes * 100
else:
    total_clientes, total_cancelados, perc_cancelados = 0, 0, 0

col1, col2, col3 = st.columns(3)
col1.metric("Total de Clientes", f"{total_clientes:,}")
col2.metric("Cancelamentos", f"{total_cancelados:,}")
col3.metric("% Cancelados", f"{perc_cancelados:.1f}%")

st.markdown("---")

# --- Gráficos ---
st.subheader("📈 Análises Visuais")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        graf_status = df_filtrado["cancelou_label"].value_counts(normalize=True).reset_index()
        graf_status.columns = ["Status", "Proporção"]
        fig1 = px.pie(
            graf_status,
            names="Status",
            values="Proporção",
            title="Proporção de Clientes Ativos x Cancelados",
            hole=0.5
        )
        st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    if not df_filtrado.empty:
        fig2 = px.histogram(
            df_filtrado,
            x="sexo",
            color="cancelou_label",
            barmode="group",
            title="Cancelamentos por Sexo"
        )
        st.plotly_chart(fig2, use_container_width=True)

# --- Gráficos para todas as colunas ---
st.subheader("🔍 Impacto das Variáveis no Cancelamento")

for coluna in df_filtrado.columns:
    if coluna not in ["cancelou", "cancelou_label"]:
        fig = px.histogram(
            df_filtrado,
            x=coluna,
            color="cancelou_label",
            text_auto=True,
            barmode="group",
            title=f"Distribuição de {coluna} por Cancelamento"
        )
        st.plotly_chart(fig, use_container_width=True)

# --- Tabela de Dados ---
st.subheader("📑 Dados Detalhados")
st.dataframe(df_filtrado)
