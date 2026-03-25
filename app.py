
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------
# Cria uma página
# -------------------------
st.set_page_config(page_title="Meu App", page_icon="🚀", layout="wide")

# -------------------------
# Cria o título e substítulos da página app
# -------------------------
st.title("App Streamlit publicado via GitHub")
st.caption("Edite `app.py` e faça `git push` para atualizar o app!")

# -------------------------
# Cria dados de exemplo
# -------------------------
@st.cache_data
def carregar_dados():
    dados = [
        {"data":"2025-07-01","unidade":"Hospital A","especialidade":"Clínica Geral","sexo":"F","idade":23,"tempo_espera_min":18,"satisfacao":4,"custo":120.0},
        {"data":"2025-07-01","unidade":"Hospital A","especialidade":"Cardiologia",  "sexo":"M","idade":67,"tempo_espera_min":35,"satisfacao":3,"custo":420.0},
        {"data":"2025-07-02","unidade":"Hospital A","especialidade":"Pediatria",    "sexo":"F","idade":9, "tempo_espera_min":12,"satisfacao":5,"custo":90.0},
        {"data":"2025-07-02","unidade":"Hospital B","especialidade":"Clínica Geral","sexo":"M","idade":41,"tempo_espera_min":22,"satisfacao":4,"custo":150.0},
        {"data":"2025-07-03","unidade":"Hospital B","especialidade":"Cardiologia",  "sexo":"F","idade":72,"tempo_espera_min":40,"satisfacao":3,"custo":500.0},
        {"data":"2025-07-03","unidade":"Hospital A","especialidade":"Ortopedia",    "sexo":"M","idade":35,"tempo_espera_min":28,"satisfacao":4,"custo":260.0},
        {"data":"2025-07-04","unidade":"Hospital A","especialidade":"Dermatologia", "sexo":"F","idade":29,"tempo_espera_min":15,"satisfacao":5,"custo":110.0},
        {"data":"2025-07-04","unidade":"Hospital B","especialidade":"Pediatria",    "sexo":"M","idade":6, "tempo_espera_min":10,"satisfacao":5,"custo":80.0},
        {"data":"2025-07-05","unidade":"Hospital B","especialidade":"Clínica Geral","sexo":"F","idade":53,"tempo_espera_min":26,"satisfacao":4,"custo":140.0},
        {"data":"2025-07-05","unidade":"Hospital A","especialidade":"Ortopedia",    "sexo":"M","idade":47,"tempo_espera_min":33,"satisfacao":3,"custo":300.0},
    ]
    df = pd.DataFrame(dados)
    df["data"] = pd.to_datetime(df["data"])
    return df

df = carregar_dados()

# -------------------------
# Filtros
# -------------------------

with st.sidebar:

    st.subheader("🔎 Filtros")

    # intervalo de datas sugerido pelo min/max do DF
    dmin, dmax = df["data"].min().date(), df["data"].max().date()
    f_data = st.date_input("Período", value=(dmin, dmax), min_value=dmin, max_value=dmax)

    # filtros categóricos (multiselect) com todas as opções pré-selecionadas
    f_unidade = st.multiselect("Unidade",
                               sorted(df["unidade"].unique().tolist()),
                               default=sorted(df["unidade"].unique().tolist()))

    f_esp = st.multiselect("Especialidade",
                           sorted(df["especialidade"].unique().tolist()),
                           default=sorted(df["especialidade"].unique().tolist()))

    f_sexo = st.multiselect("Sexo",
                            sorted(df["sexo"].unique().tolist()),
                            default=sorted(df["sexo"].unique().tolist()))

    # filtros numéricos (sliders com intervalo)
    f_idade = st.slider("Idade",
                        int(df["idade"].min()),
                        int(df["idade"].max()),
                        (int(df["idade"].min()), int(df["idade"].max())))

    f_espera = st.slider("Tempo de espera (min)",
                         int(df["tempo_espera_min"].min()),
                         int(df["tempo_espera_min"].max()),
                         (int(df["tempo_espera_min"].min()), int(df["tempo_espera_min"].max())))

    f_custo = st.slider("Custo (R$)",
                        float(df["custo"].min()),
                        float(df["custo"].max()),
                        (float(df["custo"].min()), float(df["custo"].max())))

# -------------------------
# Aplica filtro
# -------------------------

# Aplica os filtros construindo uma máscara booleana linha a linha.
mask = (
    (df["data"].between(pd.to_datetime(f_data[0]), pd.to_datetime(f_data[1])))
    & (df["unidade"].isin(f_unidade))
    & (df["especialidade"].isin(f_esp))
    & (df["sexo"].isin(f_sexo))
    & (df["idade"].between(f_idade[0], f_idade[1]))
    & (df["tempo_espera_min"].between(f_espera[0], f_espera[1]))
    & (df["custo"].between(f_custo[0], f_custo[1]))
)

# DataFrame filtrado (cópia para evitar avisos do pandas)
df_f = df[mask].copy()

# -------------------------
# KPIs
# -------------------------

c1, c2, c3, c4 = st.columns(4)

#len(): contagem de linhas sobre o filtrado
#mean()/sum(): agregações sobre o filtrado

c1.metric("Atendimentos", len(df_f))
c2.metric("Tempo médio de espera (min)", f"{df_f['tempo_espera_min'].mean():.1f}")
c3.metric("Satisfação média (1–5)", f"{df_f['satisfacao'].mean():.1f}")
c4.metric("Custo total (R$)", f"{df_f['custo'].sum():.2f}")

st.divider()

# -------------------------
# 4) Tabela / Gráfico / Download
# -------------------------

tab1, tab2, tab3 = st.tabs(["📋 Tabela", "📊 Gráfico", "⬇️ Exportar"])

with tab1: # Tabela responsiva com o DF filtrado
    st.dataframe(df_f, use_container_width=True, height=340)

with tab2:

    # Gráfico dinâmico:
    st.subheader("Gráfico por dimensão")

    # o usuário escolhe a dimensão (eixo X)
    dim = st.selectbox("Dimensão", ["especialidade", "unidade", "sexo", "data"])

    # e a métrica (agregação).
    met = st.selectbox("Métrica", ["Atendimentos", "Tempo médio de espera", "Custo total", "Satisfação média"])

    # groupby + size/mean/sum produzem o DataFrame 'agg' para plotar
    if met == "Atendimentos":
        agg = df_f.groupby(dim).size().reset_index(name="valor")
    elif met == "Tempo médio de espera":
        agg = df_f.groupby(dim)["tempo_espera_min"].mean().reset_index(name="valor")
    elif met == "Custo total":
        agg = df_f.groupby(dim)["custo"].sum().reset_index(name="valor")
    else:
        agg = df_f.groupby(dim)["satisfacao"].mean().reset_index(name="valor")

    # se a dimensão for data, faz linha temporal; caso contrário, barras.
    if dim == "data":
        fig = px.line(agg.sort_values(dim), x=dim, y="valor", markers=True)
    else:
        fig = px.bar(agg.sort_values("valor", ascending=False), x=dim, y="valor")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with tab3:

    ## Exporta o DF filtrado como CSV para download.
    st.download_button(
        "Baixar CSV filtrado",
        df_f.to_csv(index=False).encode("utf-8"),
        file_name="dados_saude_filtrados.csv",
        mime="text/csv",
    )

# Rodapé com shapes (linhas, colunas) do DF original e filtrado.
st.caption(f"Shape original: {df.shape} | filtrado: {df_f.shape}")
