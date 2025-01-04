import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Caminho do arquivo (relativo - ajuste se necessário)
diretorio_atual = os.path.dirname(r"C:\\Users\\Administrator\\Documents\\Estudos_Python\\ecommerce_estatistica.csv")
caminho_arquivo = os.path.join(diretorio_atual, "ecommerce_estatistica.csv")

try:
    data = pd.read_csv(caminho_arquivo)
except FileNotFoundError:
    raise FileNotFoundError(f"O arquivo {caminho_arquivo} não foi encontrado. Certifique-se de que '{nome_arquivo_csv}' está no mesmo diretório do script.")
except pd.errors.ParserError:
    raise ValueError(f"Erro ao ler o arquivo CSV. Verifique o formato.")
except Exception as e:
    raise RuntimeError(f"Um erro inesperado ocorreu durante a leitura do arquivo: {e}")

data['Qtd_Vendidos'] = data['Qtd_Vendidos'].str.replace('mil', '000').str.replace(r'\+', '', regex=True)
data['Qtd_Vendidos'] = pd.to_numeric(data['Qtd_Vendidos'], errors='coerce')
data.dropna(subset=['Qtd_Vendidos'], inplace=True) # Tratamento de NaN

app = dash.Dash(__name__)
app.title = "Dashboard de E-commerce"

app.layout = html.Div([
    html.H1("Dashboard de E-commerce", style={"textAlign": "center"}),

    html.Label("Escolha o gráfico para visualizar:"),
    dcc.Dropdown(
        id="graph-selector",
        options=[
            {"label": "Histograma - Notas", "value": "histogram"},
            {"label": "Dispersão - Preço vs Avaliações", "value": "scatter"},
            {"label": "Mapa de Calor - Correlação", "value": "heatmap"},
            {"label": "Barras - Média de Preço por Material", "value": "bar"},
            {"label": "Pizza - Proporção de Vendas por Gênero", "value": "pie"},
            {"label": "Densidade - Preço", "value": "density"},
            {"label": "Regressão - Preço vs Quantidade Vendida", "value": "regression"},
        ],
        value="histogram"
    ),

    dcc.Graph(id="main-graph")
])

@app.callback(
    Output("main-graph", "figure"),
    Input("graph-selector", "value")
)
def update_graph(graph_type):
    if graph_type == "histogram":
        fig = px.histogram(
            data, x="Nota", nbins=15, title="Distribuição de Notas",
            labels={"Nota": "Notas"}, color_discrete_sequence=["skyblue"]
        )
    elif graph_type == "scatter":
        fig = px.scatter(
            data, x="Preço", y="N_Avaliações", color="Marca",
            title="Dispersão: Preço vs Avaliações",
            labels={"Preço": "Preço", "N_Avaliações": "Número de Avaliações"},
            color_continuous_scale="Viridis"
        )
    elif graph_type == "heatmap":
        correlacao = data[['Nota', 'Preço', 'Qtd_Vendidos', 'N_Avaliações']].corr()
        fig = px.imshow(
            correlacao, text_auto=".2f", title="Mapa de Calor - Correlação",
            labels=dict(x="Variáveis", y="Variáveis", color="Correlação"),
            color_continuous_scale=px.colors.diverging.RdBu,
            zmin=-1, zmax=1
        )
        fig.update_layout(coloraxis_showscale=True)

    elif graph_type == "bar":
        media_preco_material = data.groupby('Material')['Preço'].mean().sort_values()
        cores_pastel = ['#b3e2cd', '#fdcdac', '#cbd5e8', '#f4cae4', '#e6f5c9', '#fff2ae', '#f1e2cc']  # Paleta pastel
        fig = px.bar(
        x=media_preco_material.index,
        y=media_preco_material.values,
        title="Média de Preço por Material",
        labels={"y": "Preço Médio", "x": "Material"},
        color=media_preco_material.index, # Define a coluna para atribuir cores diferentes
        color_discrete_sequence=cores_pastel[:len(media_preco_material)] # Ajusta a lista de cores ao número de barras
    )
    elif graph_type == "pie":
        vendas_por_genero = data['Gênero'].value_counts()
        cores_pastel = ['#b3e2cd', '#fdcdac', '#cbd5e8', '#f4cae4', '#e6f5c9', '#fff2ae', '#f1e2cc']
        fig = px.pie(
            names=vendas_por_genero.index, values=vendas_por_genero.values,
            title="Proporção de Vendas por Gênero",
            color_discrete_sequence=cores_pastel[:len(vendas_por_genero)]
        )
    elif graph_type == "density":
        fig = px.density_contour(
            data_frame=data, x="Preço", y="N_Avaliações",
            title="Densidade do Preço vs. Número de Avaliações"
        )
    elif graph_type == "regression":
        try:
            # Tenta converter a coluna "Qtd_Vendidos" para numérica.
            data["Qtd_Vendidos"] = pd.to_numeric(data["Qtd_Vendidos"], errors='coerce')
            # Remove valores nulos gerados pela conversao
            data.dropna(subset=['Qtd_Vendidos'], inplace=True)
        except (ValueError, TypeError) as e:
            print(f"Erro ao converter 'Qtd_Vendidos': {e}")
            return px.scatter(title="Erro: 'Qtd_Vendidos' não pode ser convertido para número")

        cores_pastel = ['#b3e2cd', '#fdcdac', '#cbd5e8', '#f4cae4', '#e6f5c9', '#fff2ae', '#f1e2cc']
        fig = px.scatter(
            data, x="Preço", y="Qtd_Vendidos", trendline="ols",
            title="Regressão: Preço vs Quantidade Vendida",
            labels={"Preço": "Preço", "Qtd_Vendidos": "Quantidade Vendida"},
            color_discrete_sequence=cores_pastel
        )

        fig.update_layout(
            xaxis_title="Preço",  # Redundante, mas para clareza
            yaxis_title="Quantidade Vendida",  # Redundante, mas para clareza
            template="plotly_white"  # Melhora a visualização
        )

        # Adiciona uma legenda mais informativa para a linha de tendencia
        fig.data[1].name = "Tendência Linear"  # Nomeia a linha de tendencia
        fig.data[1].showlegend = True  # Mostra a legenda da linha de tendencia

        return fig
    else:
        fig = go.Figure()

    return fig

if __name__ == "__main__":
    app.run_server(debug=True)