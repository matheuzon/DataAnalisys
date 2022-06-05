import pandas as pd
import os

def concat_tarefas():

    #Definindo o caminho dos arquivos
    path = 'dados/Tarefas/tarefas/'
    #Atribuindo os arquivos da para à uma variável
    arquivos = os.listdir(path)

    lista = []

    for n in range(0,len(arquivos)):
        file = path+arquivos[n]
        print(file)
        locals()['dados%s' %n] = pd.read_excel(
            file,
            usecols=('C:I,M:N,P'),
            names=[
                'tipo_processo',
                'autor',
                'data_criacao',
                'hora_criacao',
                'pd_origem',
                'pd_destino',
                'produto',
                'tipo_estoque',
                'desc_tipo_estoque',
                'uc'
                ],
                dtype={
                    'uc':'string'
                    }
                )
        #locals()['dados%s' %n]['data'] = c_time
        lista.append(locals()['dados%s' %n])

    dados = pd.concat(lista)

    dia_semana = {
    0:'seg',
    1:'ter',
    2:'qua',
    3:'qui',
    4:'sex',
    5:'sab',
    6:'dom',
    }

    dados['dia_semana'] = dados['data_criacao'].dt.weekday
    dados['nome_dia_semana'] = dados['dia_semana'].map(dia_semana)

    dados.to_csv('dados/Tarefas/tarefas_concat.csv', sep=',', index=None)

def curva_abc(mon, mb52, gravacao = False):

    arquivo_mon = mon
    arquivo_mb52 = mb52

    # Para gerar uma pastas com os dados gravados, trocar o valor da variável gravacao para True

    # Cria uma função gravar que pega os dados e faz o processo quanto solicitado

    if gravacao == True:
        import os
        from datetime import datetime

        nova_pasta = 'dados/análises/análise_abc_'+datetime.now().strftime("%d-%m-%Y_%Hh%m")
        arquivo_estoque = 'dados/'+arquivo_mon
        arquivo_mb = 'dados/'+arquivo_mb52
        

        if not os.path.exists(nova_pasta): # se a pasta não existir
            os.makedirs(nova_pasta) # cria a pasta
            destino = nova_pasta+'/'+arquivo_mon
            os.replace(arquivo_estoque,destino) # move o arquivo mon para a pasta criada
            destino = nova_pasta+'/'+arquivo_mb52
            os.replace(arquivo_mb, destino) # move o arquivo mb52 para a pasta criada
            del destino
        del arquivo_mb, arquivo_estoque

    if gravacao == True:
        estoque = pd.read_excel(nova_pasta+'/'+arquivo_mon)
        mb52 = pd.read_excel(nova_pasta+'/'+arquivo_mb52)
    else:
        estoque = pd.read_excel('dados/'+arquivo_mon)
        mb52 = pd.read_excel('dados/'+arquivo_mb52)

    acabados = pd.read_csv('dados/arquivos_base/relacao_acabados.csv', sep=',')

    acabados = acabados['0'].unique()

    lista_acabados = []
    for x in range(0, len(acabados)):
        lista_acabados.append(acabados[x])

    mb52['valor_total'] = mb52['Val.utiliz.livre'] + mb52['Valor verif.qual.'] + mb52['Val.estoque bloq.']
    mb52['qtd_total'] = mb52['Utilização livre'] + mb52['Controle qualidade'] + mb52['Bloqueado']
    mb52['valor_unitario'] = mb52['valor_total'] / mb52['qtd_total']

    tipo_item = {
    'HE':'shrink',
    'HC':'shrink',
    'HA':'shrink',
    'HZ':'shrink',
    'HI':'shrink',
    'SE':'stretch',
    'SA':'stretch',
    'SZ':'stretch',
    'IH':'shrink',
    'IS':'shrink',
    'IZ':'shrink',
    }

    tipo_produto = {
    'HE':'semiacabado',
    'HC':'acabado',
    'HA':'acabado',
    'HZ':'semiacabado',
    'HI':'acabado',
    'SE':'semiacabado',
    'SA':'acabado',
    'SZ':'semiacabado',
    'IH':'acabado',
    'IS':'acabado',
    'IZ':'semiacabado',
    }

    mb52['inicial_item'] = mb52['Material'].str[:2]
    mb52['tipo_item'] = mb52['inicial_item'].map(tipo_item)
    mb52['tipo_produto'] = mb52['inicial_item'].map(tipo_produto)

    mb52.dropna(subset=['tipo_item'], inplace=True)
    mb52.query('tipo_item.isna()')['Material'].unique()

    valor_produto = mb52.groupby('Material')['valor_unitario'].mean().to_frame().round(2)

    dados = mb52[['Material', 'valor_total']]
    dados['grupo'] = mb52['Material'].apply(lambda x: 'Acabado' if x in lista_acabados else 'na')
    dados = dados.query('grupo =="Acabado"')

    grupo_produtos = dados.groupby(by='Material')['valor_total'].sum().to_frame().sort_values(by='valor_total', ascending=False).reset_index()

    grupo_produtos['percentual'] = ((grupo_produtos['valor_total'] / grupo_produtos['valor_total'].sum())*100).round(2)

    grupo_produtos['percentual_acumulado'] = grupo_produtos['percentual'].cumsum()

    grupo_produtos['curva'] = grupo_produtos['percentual_acumulado'].apply(lambda x: 'A' if x <= 20 else 'B' if x <= 50 else 'C')

    curva = (grupo_produtos.groupby(by='curva')['valor_total'].sum()/1000000).to_frame()
    curva['percentual'] = (curva['valor_total'] / curva['valor_total'].sum()*100).round(2)

    # Cria um dataframe com a quantidade total de cada item
    qtd_estoque = mb52.groupby('Material')['qtd_total'].sum().to_frame().sort_values('qtd_total', ascending=False).round(2)

    qtd_estoque['percentual'] = (qtd_estoque['qtd_total'] / qtd_estoque['qtd_total'].sum()*100).round(2)
    qtd_estoque['acumulado'] = qtd_estoque['percentual'].cumsum()

    qtd_estoque['curva'] = qtd_estoque['acumulado'].apply(lambda x: 'A' if x <= 20 else 'B' if x <= 50 else 'C')

    curva_estoque = qtd_estoque.merge(grupo_produtos, left_on='Material', right_on='Material')

    curva_estoque.rename(columns={
        'percentual_x':'percentual_qtd',
        'acumulado':'acumulado_qtd',
        'curva_x':'curva_qtd',
        'percentual_y':'percentual_valor',
        'percentual_acumulado':'acumulado_valor',
        'curva_y':'curva_valor',
    }, inplace=True)

    curva_combinada = curva_estoque[['Material', 'curva_qtd', 'curva_valor']]

    curva_combinada['inicial_item'] = curva_combinada['Material'].str[:2]
    curva_combinada['tipo_item'] = curva_combinada['inicial_item'].map(tipo_item)
    curva_combinada['tipo_produto'] = curva_combinada['inicial_item'].map(tipo_produto)
    curva_combinada.drop(columns=['inicial_item'], inplace=True)

    if gravacao == True:
        curva_combinada.to_csv(nova_pasta+'/curva_combinada.csv', sep=',', index=False)
        texto =  'curva_combinada gerada com gravação'
        return texto
    else:
        curva_combinada.to_csv('dados/curva_combinada.csv', sep=',', index=False)
        texto =  'curva_combinada gerada sem gravação'
        return texto

def analise_posicoes():
    nada = 1