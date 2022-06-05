import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt

# Configurando o ambiente Streamlit
st.set_page_config(page_title='Disposição do estoque', page_icon=':bar_chart:', layout='wide')

# Configurando os dados
dados = pd.read_csv('dados/analise_rack.csv')
dados_curva = pd.read_csv('dados/curva_vlr_qtd.csv')
produtos_tempo = pd.read_csv('dados/produtos_no_tempo.csv')
total_produtos_tempo = pd.read_csv('dados/total_produtos_no_tempo.csv')

# Criando a barra lateral
with st.sidebar:
    st.header('Filtrar')
    #upload = st.file_uploader('Selecione um arquivo "csv"', type= ['csv'])
    #dados=pd.read_csv(upload)
    produto = st.sidebar.text_input('Produto')
    tipo_item = st.sidebar.multiselect('Tipo do item:', options=dados['tipo_item'].unique(),default=dados['tipo_item'].unique())
    tipo_produto = st.sidebar.multiselect('Tipo produto:', options=dados['tipo_produto'].unique(),default=dados['tipo_produto'].unique())
    curva_qtd = st.sidebar.multiselect('Curva qtd:', options=dados['curva_qtd'].unique(),default=dados['curva_qtd'].unique())
    curva_valor = st.sidebar.multiselect('Curva valor:', options=dados['curva_valor'].unique(),default=dados['curva_valor'].unique())
    tipo_estoque = st.sidebar.multiselect('Tipo do estoque:', options=dados['tipo_estoque'].unique(),default=dados['tipo_estoque'].unique())

produto = produto.upper()

# Filtrando o dataframe
if produto == "":
    dados_selecionados = dados.query(
        'tipo_estoque == @tipo_estoque & tipo_item == @tipo_item & tipo_produto == @tipo_produto & curva_valor == @curva_valor& curva_qtd == @curva_qtd'
        )
    dados_selecionados_curva = dados_curva.query(
        'curva_valor == @curva_valor & curva_qtd == @curva_qtd & tipo_item == @tipo_item & tipo_produto == @tipo_produto'
        )
    
    valor_total = dados_selecionados_curva['valor_total'].sum()
    total_produto = dados_selecionados.shape[0]
else:
    dados_selecionados = dados.query(
        'tipo_estoque == @tipo_estoque & tipo_item == @tipo_item & tipo_produto == @tipo_produto & curva_valor == @curva_valor& curva_qtd == @curva_qtd & produto == @produto'
        )
    dados_selecionados_curva = dados_curva.query(
        'Material == @produto & tipo_item == @tipo_item & tipo_produto == @tipo_produto & curva_valor == @curva_valor& curva_qtd == @curva_qtd'
        )
    
    valor_total = dados_selecionados_curva['valor_total'].sum()
    total_produto = dados_selecionados.shape[0]

# Página principal
st.header('Visualização dos racks')

# KPIs
total_livre_005 = int(dados_selecionados.query('tipo_estoque == @tipo_estoque').shape[0])

st.markdown('---')

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Total de UCs: {}'.format(total_produto))
with middle_column:

    st.subheader('Valor total: R$ {:,.0f}'.format(valor_total))

st.markdown('---')

st.markdown('Gráficos')

# Gráfico com plotly
fig_plotly = px.scatter(dados_selecionados, x='label', y='rack_visualizacao', color='rua', height=700, hover_data=['rack_original','Material'], title='Distribuição dos itens por posição no depósito - Racks')
fig_plotly.update_xaxes(title_text='Rua', title_font={'size':14}, autorange="reversed", showgrid=False)
fig_plotly.update_yaxes(title_text='Rack', title_font={'size':14}, autorange="reversed", showgrid=False)

see_scatter_pos = st.expander('Visualizar distribuição das posições do estoque 👉')

with see_scatter_pos:
    st.plotly_chart(fig_plotly, use_container_width=True)

fig_percentual_valor = px.bar(dados_selecionados_curva.sort_values(by='percentual_valor', ascending=False), orientation='h', y='Material', x='percentual_valor',color='curva_valor' , height=700, hover_data=['qtd_total', 'valor_total'], title='Curva de itens')
fig_percentual_valor.update_xaxes(title_text='Material', title_font={'size':14}, showgrid=False)
fig_percentual_valor.update_yaxes(title_text='Percentual', title_font={'size':14}, showgrid=False)

see_scatter_valor = st.expander('Visualizar gráfico de barras por valor em estoque 👉')

with see_scatter_valor:
    st.plotly_chart(fig_percentual_valor, use_container_width=True)

if produto != "":
    analise_item = produtos_tempo.query('produto == @produto')['label_data'].value_counts()
    analise_item = analise_item.to_frame().reset_index()
    analise_item.rename(columns = {'index':'data', 'label_data':'quantidade'}, inplace =True)
    analise_item = analise_item.merge(produtos_tempo, left_on='data', right_on='label_data')
    analise_item = analise_item[['data_x', 'quantidade', 'data_y']]
    analise_item.sort_values(by='data_y', inplace=True)
    fig_percentual_produto_tempo = px.bar(analise_item, x='quantidade', y='data_x', orientation='v', height=700, title='Itens no tempo')
    fig_percentual_produto_tempo.update_xaxes(title_text='Material', title_font={'size':14}, showgrid=False)
    fig_percentual_produto_tempo.update_yaxes(title_text='Percentual', title_font={'size':14}, showgrid=False)

    see_scatter_produto_tempo = st.expander('Visualizar gráfico de barras por valor em estoque 👉')

    with see_scatter_produto_tempo:
        st.plotly_chart(fig_percentual_produto_tempo, use_container_width=True)

st.markdown('---')

st.markdown('Dataframes')
see_dataframe_pos = st.expander('Visualizar o dataframe de posições aqui 👉')
see_dataframe_curva = st.expander('Visualizar o dataframe de valores aqui 👉')
see_total_produtos_tempo = st.expander('Visualizar o dataframe de valores aqui 👉')

with see_dataframe_pos:
    st.dataframe(data=dados_selecionados.reset_index(drop=True))
with see_dataframe_curva:
    st.dataframe(dados_selecionados_curva.reset_index(drop=True))

if produto == "":
    with see_total_produtos_tempo:
        st.dataframe(produtos_tempo.reset_index(drop=True))
else:
    with see_total_produtos_tempo:
        st.write()
        st.dataframe(analise_item.reset_index(drop=True))