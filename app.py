import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Salários Área de Dados",
    page_icon="📊",
    layout="wide",
)


# --- 2. CARREGAMENTO DOS DADOS (COM CACHE) ---
@st.cache_data
def carregar_dados():
    url = "https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv"
    df = pd.read_csv(url)
    return df


df = carregar_dados()

# --- 3. BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros")

# Campo de Busca por Texto
busca_cargo = st.sidebar.text_input(
    "🎯 Buscar cargo específico", "", help="Ex: Data Scientist, Analyst..."
)

# Filtros de Seleção
anos_disponiveis = sorted(df["ano"].unique())
anos_selecionados = st.sidebar.multiselect(
    "Anos", anos_disponiveis, default=anos_disponiveis
)

senioridades_disponiveis = sorted(df["senioridade"].unique())
senioridades_selecionadas = st.sidebar.multiselect(
    "Senioridade", senioridades_disponiveis, default=senioridades_disponiveis
)

# --- 4. FILTRAGEM DOS DADOS ---
df_filtrado = df[
    (df["ano"].isin(anos_selecionados))
    & (df["senioridade"].isin(senioridades_selecionadas))
]

# Aplica a busca por texto apenas se algo for digitado
if busca_cargo:
    df_filtrado = df_filtrado[
        df_filtrado["cargo"].str.contains(busca_cargo, case=False)
    ]

# --- 5. TÍTULO E MÉTRICAS ---
st.title("🎲 Dashboard: Mercado Global de Dados")
st.markdown(f"Exibindo **{len(df_filtrado)}** registros encontrados.")

st.markdown("---")
if not df_filtrado.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Salário Médio", f"${df_filtrado['usd'].mean():,.0f}")
    col2.metric("Salário Máximo", f"${df_filtrado['usd'].max():,.0f}")
    col3.metric("Total de Registros", f"{len(df_filtrado):,}")

    cargo_frequente = (
        df_filtrado["cargo"].mode()[0]
        if not df_filtrado["cargo"].mode().empty
        else "N/A"
    )
    col4.metric("Cargo mais Frequente", cargo_frequente)
else:
    st.error("⚠️ Nenhum dado encontrado para os filtros selecionados.")

# --- 6. GRÁFICOS PRINCIPAIS (LINHA 1) ---
st.markdown("---")
col_esq, col_dir = st.columns(2)

if not df_filtrado.empty:
    with col_esq:
        # Gráfico de Barras - Top 10 Cargos
        top_cargos = (
            df_filtrado.groupby("cargo")["usd"]
            .mean()
            .nlargest(10)
            .sort_values(ascending=True)
            .reset_index()
        )
        fig_bar = px.bar(
            top_cargos,
            x="usd",
            y="cargo",
            orientation="h",
            title="Top 10 Cargos por Média Salarial",
            color="usd",
            color_continuous_scale="Viridis",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_dir:
        # Gráfico de Distribuição - Histograma
        fig_hist = px.histogram(
            df_filtrado,
            x="usd",
            nbins=20,
            title="Distribuição Salarial (USD)",
            color_discrete_sequence=["#00CC96"],
        )
        st.plotly_chart(fig_hist, use_container_width=True)

# --- 7. GRÁFICOS (LINHA 2) ---
st.markdown("---")
col_mapa, col_box = st.columns([1.2, 0.8])  # Mapa um pouco maior que o boxplot

if not df_filtrado.empty:
    with col_mapa:
        # Mapa Mundi
        media_pais = df_filtrado.groupby("residencia_iso3")["usd"].mean().reset_index()
        fig_mapa = px.choropleth(
            media_pais,
            locations="residencia_iso3",
            color="usd",
            color_continuous_scale="Blues",
            title="Média Salarial por País",
        )
        st.plotly_chart(fig_mapa, use_container_width=True)

    with col_box:
        # Boxplot LEVE (Apenas outliers para não travar o PC)
        fig_box = px.box(
            df_filtrado,
            x="senioridade",
            y="usd",
            color="senioridade",
            title="Variação por Senioridade",
            category_orders={"senioridade": ["Junior", "Pleno", "Senior", "Expert"]},
            points="outliers",
        )  # Essencial para performance
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# --- 8. RODAPÉ E DADOS ---
st.markdown("---")
with st.expander("📄 Ver base de dados completa"):
    st.dataframe(df_filtrado)
