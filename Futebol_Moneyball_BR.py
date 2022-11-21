import streamlit as st
#import base64
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import operator
import math
#import webbrowser

#########################################################################################################

# Criando a calculadora de distância entre pontos
def Similarity(player_id1, player_id2):
  a = df_knn_posição[(df_knn_posição['player_id'] == player_id1)]
  b = df_knn_posição[(df_knn_posição['player_id'] == player_id2)]

  Valor_performanceA = float(a['Valor_performance'])
  Valor_performanceB = float(b['Valor_performance'])

  Valor_mercadoA = float(a['Valor_mercado'])
  Valor_mercadoB = float(b['Valor_mercado'])
  
  euclidean_dist = math.sqrt((Valor_performanceA-Valor_performanceB)**2 + (Valor_mercadoA-Valor_mercadoB)**2)

  return euclidean_dist


#########################################################################################################

# Criando calculadora de distância apenas para o valor de performance
def Similarity_performance(player_id1, player_id2):
  a = df_knn_posição[(df_knn_posição['player_id'] == player_id1)]
  b = df_knn_posição[(df_knn_posição['player_id'] == player_id2)]

  Valor_performanceA = a['Valor_performance'].iloc[0]
  Valor_performanceB = b['Valor_performance'].iloc[0]
  
  euclidean_dist = math.sqrt((Valor_performanceA-Valor_performanceB)**2)

  return euclidean_dist

#########################################################################################################

# Criando função de recomendação para jogadores de custo-benefísio mais semelhante
def replace_player():

      st.subheader("Tipo de recomendação: Similaridade em custo-benefício")
      st.text("As recomendações apresentadas nesta página apontam quais jogadores mais se \naproximam em custo-benefício ao jogador escolhido.")
      st.markdown("---")    
    
      if name in df_knn_posição['player_name'].tolist() and equipe in df_knn_posição['club_names_tm'].tolist():
        new_player = df_knn_posição[(df_knn_posição['club_names_tm'] == equipe) & df_knn_posição['player_name'].str.contains(name)].iloc[0].to_frame().T
        id_player = new_player['player_id'].iloc[0]
        resposta_grafico = False
        col1, col2 = st.columns(2)
        col1.metric(label="Jogador Escolhido", value= new_player.player_name.values[0])
        col1.write("Clique no botão abaixo para gerar gráfico de jogadores")
        resposta_grafico = col1.button("Gerar gráfico")
        if resposta_grafico == True:
            fig = comp_graph(id_player)
            st.plotly_chart(fig)
#         fig.show()
      
  
        col2.metric(label="Valor de Performance", value=f"€{round(new_player.Valor_performance.values[0], 2) * 1000000:,.2f}")
        col2.metric(label="Valor de Mercado", value=f"€{new_player.Valor_mercado.values[0] * 1000000:,.2f}")
        
        player_id_list = []
        player_name_list = []
        player_club_list = []
        
        def getNeighbors(baseJogador, K):
          distances = []

          for index, player in df_knn_posição.iterrows():
            if player['player_id'] != baseJogador['player_id'].values[0]:
              dist = Similarity(baseJogador['player_id'].values[0], player['player_id'])
              distances.append((player['player_id'], dist, player['player_name'], player['club_names_tm'],
                                player['Valor_performance'], player['Valor_mercado']))
                
          distances.sort(key=operator.itemgetter(1))
          for x in range(5):
            player_id_list.append(distances[x][0])
          
          distances.sort(key=operator.itemgetter(1))
          for x in range(5):
            player_name_list.append(distances[x][2])
            
          distances.sort(key=operator.itemgetter(1))
          for x in range(5):
            player_club_list.append(distances[x][3])
            
          neighbors = []
          
          distances.sort(key=operator.itemgetter(1))
          for x in range(K):
            neighbors.append(distances[x])
          return neighbors
                

        K = 5

        neighbors = getNeighbors(new_player, K)
        st.markdown("---")       
        
        st.write('\nJogadores Recomendados: \n')
        st.write('')
        col_nomes = []
        col_equipe = []
        col_performance = []
        col_custo = []
        for neighbor in neighbors:
            col_nomes.append(neighbor[2])
            col_equipe.append(neighbor[3])
            col_performance.append(round(neighbor[4]*1000000, 2))
            col_custo.append(round(neighbor[5]*1000000, 2))
        df_recomend = pd.DataFrame()
        df_recomend['Nome do jogador'] = col_nomes
        df_recomend['Time'] = col_equipe
        df_recomend['Valor de Performance (€)'] = col_performance
        df_recomend['Valor de mercado (€)'] = col_custo
        df_recomend.index += 1 
        st.dataframe(df_recomend)
        
        
        st.write('')
        jogador_comp_list = [None]
        for jog in player_name_list:
            jogador_comp_list.append(jog)
        jogador_comp = st.selectbox("Selecione um jogador para comparar estatísticas:", player_name_list)
        jogador_clube = player_club_list[player_name_list.index(jogador_comp)]
        
        botão_comparação = False
        for id in player_id_list:
            if id in df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].tolist():
                jogador_escolhido_id = df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].iloc[0]
                comp_table = df_2022[(df_2022['player_id']==id) | (df_2022['player_id']==new_player.player_id.values[0])]
                botão_comparação = st.button('Gerar tabela comparativa')
                if botão_comparação == True:
                    st.dataframe(comp_table.T)

      else:
        st.write("Erro! Verifique o nome do jogador e do time")
      return neighbors

#########################################################################################################


# Criando função de recomendação para jogadores com performance mais semelhante
def performance_substitute():

  st.subheader("Tipo de recomendação: Similaridade em performance")
  st.text("As recomendações apresentadas nesta página apontam quais jogadores possuem as \nperformances mais similares à do jogador escolhido.")
  st.markdown("---")    
    
  if name in df_knn_posição['player_name'].tolist() and equipe in df_knn_posição['club_names_tm'].tolist():
    new_player = df_knn_posição[(df_knn_posição['club_names_tm'] == equipe) & df_knn_posição['player_name'].str.contains(name)].iloc[0].to_frame().T
    id_player = new_player['player_id'].iloc[0]
    col1, col2 = st.columns(2)
    col1.metric(label="Jogador Escolhido", value= new_player.player_name.values[0])
    col1.write("Clique no botão abaixo para gerar gráfico de jogadores")
    resposta_grafico = col1.button("Gerar gráfico")
    if resposta_grafico == True:
        fig = comp_graph(id_player)
        st.plotly_chart(fig)
#         fig.show()
        
    col2.metric(label="Valor de Performance", value=f"€{round(new_player.Valor_performance.values[0], 2) * 1000000:,.2f}")
    col2.metric(label="Valor de Mercado", value=f"€{new_player.Valor_mercado.values[0] * 1000000:,.2f}")

    player_id_list = []
    player_name_list = []
    player_club_list = []
  
    def getNeighbors(baseJogador, K):
      distances = []

      for index, player in df_knn_posição.iterrows():
        if player['player_id'] != baseJogador['player_id'].values[0]:
          dist = Similarity_performance(baseJogador['player_id'].values[0], player['player_id'])
          distances.append((player['player_id'], dist, player['player_name'], player['club_names_tm'],
                            player['Valor_performance'], player['Valor_mercado'],
                            player['Valor_performance'] / player['Valor_mercado']))
      
      distances.sort(key=operator.itemgetter(1))
      for x in range(5):
        player_id_list.append(distances[x][0])
          
      distances.sort(key=operator.itemgetter(1))
      for x in range(5):
        player_name_list.append(distances[x][2])
            
      distances.sort(key=operator.itemgetter(1))
      for x in range(5):
        player_club_list.append(distances[x][3])
    
      distances.sort(key=operator.itemgetter(1))
      neighbors = []

      for x in range(K):
        neighbors.append(distances[x])
      return neighbors

    K = 5

    neighbors = getNeighbors(new_player, K)
    st.markdown("---")
      
        
    st.write('\nJogadores Recomendados: \n')
    st.write('')
    col_nomes = []
    col_equipe = []
    col_performance = []
    col_custo = []
    for neighbor in neighbors:
        col_nomes.append(neighbor[2])
        col_equipe.append(neighbor[3])
        col_performance.append(round(neighbor[4]*1000000, 2))
        col_custo.append(round(neighbor[5]*1000000, 2))
    df_recomend = pd.DataFrame()
    df_recomend['Nome do jogador'] = col_nomes
    df_recomend['Time'] = col_equipe
    df_recomend['Valor de Performance (€)'] = col_performance
    df_recomend['Valor de mercado (€)'] = col_custo
    df_recomend.index += 1 
    st.dataframe(df_recomend)
    
    
    jogador_comp_list = [None]
    for jog in player_name_list:
        jogador_comp_list.append(jog)
    jogador_comp = st.selectbox("Selecione um jogador para comparar estatísticas:", player_name_list)
    jogador_clube = player_club_list[player_name_list.index(jogador_comp)]
      
    botão_comparação = False
    for id in player_id_list:
        if id in df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].tolist():
            jogador_escolhido_id = df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].iloc[0]
            comp_table = df_2022[(df_2022['player_id']==id) | (df_2022['player_id']==new_player.player_id.values[0])]
            botão_comparação = st.button('Gerar tabela comparativa')
            if botão_comparação == True:
                st.dataframe(comp_table.T)
  
  else:
    st.write("Erro! Verifique o nome do jogador e do time")
  return neighbors

#########################################################################################################


# Criando função de recomendação para jogadores com performance mais semelhante e custo benefício mais atraente
def interesting_options():

  st.subheader("Tipo de recomendação: Outras recomendações")
  st.text("Este tipo de recomendação mais inusitado mensura a diferença de custo-benefício \nentre todos os jogadores e o jogador escolhido e ranqueia quais destes jogadores \napresentam a melhor relação entre performance e custo-benefício.")
  st.markdown("---")    
    
  if name in df_knn_posição['player_name'].tolist() and equipe in df_knn_posição['club_names_tm'].tolist():
    new_player = df_knn_posição[(df_knn_posição['club_names_tm'] == equipe) & df_knn_posição['player_name'].str.contains(name)].iloc[0].to_frame().T
    id_player = new_player['player_id'].iloc[0]
    col1, col2 = st.columns(2)
    col1.metric(label="Jogador Escolhido", value= new_player.player_name.values[0])
    col1.write("Clique no botão abaixo para gerar gráfico de jogadores")
    resposta_grafico = col1.button("Gerar gráfico")
    if resposta_grafico == True:
        fig = comp_graph(id_player)
        st.plotly_chart(fig)
#         fig.show()
        
    col2.metric(label="Valor de Performance", value=f"€{round(new_player.Valor_performance.values[0], 2) * 1000000:,.2f}")
    col2.metric(label="Valor de Mercado", value=f"€{new_player.Valor_mercado.values[0] * 1000000:,.2f}")

    player_id_list = []
    player_name_list = []
    player_club_list = []
  
    def getNeighbors(baseJogador, K):
      distances = []

      for index, player in df_knn_posição.iterrows():
        if player['player_id'] != baseJogador['player_id'].values[0]:
          dist = Similarity_performance(baseJogador['player_id'].values[0], player['player_id'])
          distances.append((player['player_id'], dist, player['player_name'], player['club_names_tm'],
                            player['Valor_performance'], player['Valor_mercado'],
                            dist / (player['Valor_performance']**2 / player['Valor_mercado'])))
      
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_id_list.append(distances[x][0])
          
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_name_list.append(distances[x][2])
            
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_club_list.append(distances[x][3])
    
      distances.sort(key=operator.itemgetter(6))
      neighbors = []

      for x in range(K):
        neighbors.append(distances[x])
      return neighbors

    K = 5

    neighbors = getNeighbors(new_player, K)
    st.markdown("---")
      
        
    st.write('\nJogadores Recomendados: \n')
    st.write('')
    col_nomes = []
    col_equipe = []
    col_performance = []
    col_custo = []
    for neighbor in neighbors:
        col_nomes.append(neighbor[2])
        col_equipe.append(neighbor[3])
        col_performance.append(round(neighbor[4]*1000000, 2))
        col_custo.append(round(neighbor[5]*1000000, 2))
    df_recomend = pd.DataFrame()
    df_recomend['Nome do jogador'] = col_nomes
    df_recomend['Time'] = col_equipe
    df_recomend['Valor de Performance (€)'] = col_performance
    df_recomend['Valor de mercado (€)'] = col_custo
    df_recomend.index += 1 
    st.dataframe(df_recomend)
    
    
    jogador_comp_list = [None]
    for jog in player_name_list:
        jogador_comp_list.append(jog)
    jogador_comp = st.selectbox("Selecione um jogador para comparar estatísticas:", player_name_list)
    jogador_clube = player_club_list[player_name_list.index(jogador_comp)]
      
    botão_comparação = False
    for id in player_id_list:
        if id in df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].tolist():
            jogador_escolhido_id = df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].iloc[0]
            comp_table = df_2022[(df_2022['player_id']==id) | (df_2022['player_id']==new_player.player_id.values[0])]
            botão_comparação = st.button('Gerar tabela comparativa')
            if botão_comparação == True:
                st.dataframe(comp_table.T)
  
  else:
    st.write("Erro! Verifique o nome do jogador e do time")
  return neighbors


#########################################################################################################


# Criando função de recomendação com melhor custo benefício
def best_performance_and_cost_benefit():

  st.subheader("Tipo de recomendação: Melhor custo-benefício")
  st.text("As recomendações apresentadas nesta página apontam quais jogadores possuem os \nmelhores custos-benefícios para esta posição.")
  st.markdown("---")    
    
  if name in df_knn_posição['player_name'].tolist() and equipe in df_knn_posição['club_names_tm'].tolist():
    new_player = df_knn_posição[(df_knn_posição['club_names_tm'] == equipe) & df_knn_posição['player_name'].str.contains(name)].iloc[0].to_frame().T
    id_player = new_player['player_id'].iloc[0]
    col1, col2 = st.columns(2)
    col1.metric(label="Jogador Escolhido", value= new_player.player_name.values[0])
    col1.write("Clique no botão abaixo para gerar gráfico de jogadores")
    resposta_grafico = col1.button("Gerar gráfico")
    if resposta_grafico == True:
        fig = comp_graph(id_player)
        st.plotly_chart(fig)
#         fig.show()

    col2.metric(label="Valor de Performance", value=f"€{round(new_player.Valor_performance.values[0], 2) * 1000000:,.2f}")
    col2.metric(label="Valor de Mercado", value=f"€{new_player.Valor_mercado.values[0] * 1000000:,.2f}")

    player_id_list = []
    player_name_list = []
    player_club_list = []
  
    def getNeighbors(baseJogador, K):
      distances = []

      for index, player in df_knn_posição.iterrows():
        if player['player_id'] != baseJogador['player_id'].values[0] and (player["Valor_performance"]/player["Valor_mercado"]) > 1:
          dist = Similarity(baseJogador['player_id'].values[0], player['player_id'])
          distances.append((player['player_id'], dist, player['player_name'], player['club_names_tm'],
                            player['Valor_performance'], player['Valor_mercado'],
                            1/player['Valor_performance']))
      
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_id_list.append(distances[x][0])
          
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_name_list.append(distances[x][2])
            
      distances.sort(key=operator.itemgetter(6))
      for x in range(5):
        player_club_list.append(distances[x][3])
    
      distances.sort(key=operator.itemgetter(6))
      neighbors = []

      for x in range(K):
        neighbors.append(distances[x])
      return neighbors

    K = 5

    neighbors = getNeighbors(new_player, K)
    st.markdown("---")
      
        
    st.write('\nJogadores Recomendados: \n')
    st.write('')
    col_nomes = []
    col_equipe = []
    col_performance = []
    col_custo = []
    for neighbor in neighbors:
        col_nomes.append(neighbor[2])
        col_equipe.append(neighbor[3])
        col_performance.append(round(neighbor[4]*1000000, 2))
        col_custo.append(round(neighbor[5]*1000000, 2))
    df_recomend = pd.DataFrame()
    df_recomend['Nome do jogador'] = col_nomes
    df_recomend['Time'] = col_equipe
    df_recomend['Valor de Performance (€)'] = col_performance
    df_recomend['Valor de mercado (€)'] = col_custo
    df_recomend.index += 1 
    st.dataframe(df_recomend)
    
    
    jogador_comp_list = [None]
    for jog in player_name_list:
        jogador_comp_list.append(jog)
    jogador_comp = st.selectbox("Selecione um jogador para comparar estatísticas:", player_name_list)
    jogador_clube = player_club_list[player_name_list.index(jogador_comp)]
      
    botão_comparação = False
    for id in player_id_list:
        if id in df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].tolist():
            jogador_escolhido_id = df_knn_posição[(df_knn_posição['club_names_tm']==jogador_clube) & (df_knn_posição['player_name']==jogador_comp)]['player_id'].iloc[0]
            comp_table = df_2022[(df_2022['player_id']==id) | (df_2022['player_id']==new_player.player_id.values[0])]
            botão_comparação = st.button('Gerar tabela comparativa')
            if botão_comparação == True:
                st.dataframe(comp_table.T)
  
  else:
    st.write("Erro! Verifique o nome do jogador e do time")
  return neighbors

#########################################################################################################

# Criando o gráfico geral de performance x custo da posição selecionada
def comp_graph(player_id) :
  fig = go.Figure(px.scatter(df_knn_posição, x='Valor_mercado', y='Valor_performance', hover_data=['player_name', 'club_names_tm']))

  fig = fig.add_trace(
      go.Scatter(
          x=df_knn_posição['Valor_performance'],
          y=df_knn_posição['Valor_performance'],
          name="Custo/performance = 1"
      ))


  df_player_filter = df_knn_posição[(df_knn_posição['player_id'] == player_id)]

  valor_performance = []
  valor_mercado = []
  valor_performance.append(df_player_filter['Valor_performance'].iloc[0])
  valor_mercado.append(df_player_filter['Valor_mercado'].iloc[0].tolist())
  player_name = df_player_filter['player_name'].iloc[0]

  fig.add_trace(go.Scatter( x = valor_mercado , y = valor_performance , name = player_name, hoverinfo = 'skip' ,opacity = 0.5 ,marker=dict(
            color='LightSkyBlue',
            size=20,
            line=dict(
                color='MediumPurple',
                width=2
            )
        )))

#   fig.update_layout(legend=dict(
#     yanchor="bottom",
#     y=0.01,
#     xanchor="right",
#     x=0.99
#     ))
   
  return fig
  
#########################################################################################################

# Títulos, explicações e chamando arquivos csv
st.title("Granabola")


#df usado nas ferramentas de distância entre pontos
df_knn = pd.read_csv(r'C:\Users\User\TERA - Python Exercises\Project TERA\df_knn.csv')

#df usado na tabela comparativa de estatísticas da interface
df_2022 = pd.read_csv(r'C:\Users\User\TERA - Python Exercises\Project TERA\df_2022.csv')
df_2022.set_index('player_name', inplace=True)
df_2022.drop(['Unnamed: 0', 'player_firstname', 'player_lastname', 'player_injured',
              'statistics_league_season', 'statistics_games_position', 'statistics_games_rating',
              'statistics_games_captain', 'statistics_substitutes_in', 'statistics_substitutes_out',
              'statistics_substitutes_bench', 'full_player_name', 'club_names_tm', 'tm_player_value'],
             axis=1, inplace=True)

#########################################################################################################

#Renomeando colunas da tabela comparativa
df_2022.rename(columns={"player_birth_date": "Data de nascimento", "player_height": "Altura", "player_weight": "Peso",
                        "statistics_games_appearances": "Nº de jogos", "statistics_games_lineups": "Jogos como titular",
                        "statistics_games_minutes": "Minutos jogados", "statistics_shots_total": "Finalizações",
                        "statistics_shots_on": "Finalizações no gol", "statistics_goals_total": "Gols",
                        "statistics_goals_conceded": "Gols sofridos", "statistics_goals_assists": "Assistências",
                        "statistics_goals_saves": "Defesas", "statistics_passes_total": "Total de passes",
                        "statistics_passes_key": "Passes-chave", "statistics_passes_accuracy": "Acurácia dos passes",
                        "statistics_tackles_total": "Embates defensivos", "statistics_tackles_blocks": "Bloqueios",
                        "statistics_tackles_interceptions": "Interceptações", "statistics_duels_total": "Total de duelos",
                        "statistics_duels_won": "Duelos ganhos", "statistics_dribbles_attempts": "Tentativas de dribles",
                        "statistics_dribbles_success": "Dribles concluídos", "statistics_fouls_drawn": "Faltas recebidas",
                        "statistics_fouls_committed": "Faltas cometidas", "statistics_cards_yellow": "Cartões amarelos",
                        "statistics_cards_yellowred": "Segundo amarelo", "statistics_cards_red": "Cartões vermelhos",
                        "statistics_penalty_won": "Pênaltis recebidos", "statistics_penalty_committed": "Pênaltis cometidos",
                        "statistics_penalty_scored": "Pênaltis convertidos", "statistics_penalty_missed": "Pênaltis perdidos",
                        "statistics_penalty_saved": "Pênaltis defendidos", "statistics_games_appearances": "Paticipação em jogos"},
                        inplace=True)

#########################################################################################################

# Criando a seleção de posição do jogador avaliado

posição = 0
posições_opções = ['Goleiros', 'Defensores', 'Meio-campistas', 'Atacantes']
posição_dropbox = st.sidebar.selectbox("Selecione a posição de interesse:", posições_opções)
for i in df_knn['statistics_games_position'].unique():
    if posição_dropbox == 'Goleiros':
        posição = 'Goalkeeper'
    elif posição_dropbox == 'Defensores':
        posição = 'Defender'
    elif posição_dropbox == 'Meio-campistas':
        posição = 'Midfielder'
    elif posição_dropbox == 'Atacantes':
        posição = 'Attacker'
df_knn_posição = df_knn[(df_knn['statistics_games_position'] == posição)]


    
#########################################################################################################

list_e = [None]
if posição_dropbox != None:
    for i in sorted(df_knn_posição['club_names_tm'].unique()):
        list_e.append(i)
else:
    list_e = [None]
equipe = st.sidebar.selectbox("Selecione o time de interesse:", list_e)

list_n = [None]
if equipe != [None]:
    for i in sorted(df_knn_posição[(
        df_knn_posição['club_names_tm'] == equipe)]['player_name'].unique()):
        list_n.append(i)
else:
    list_n = [None]
name = st.sidebar.selectbox("Selecione o jogador de referência:", list_n)

list_r = [None]
if name != None:
    list_r = [None, 'Similaridade em custo-benefício', 'Melhor custo-benefício', 
          'Similaridade em performance', 'Outras recomendações']
else:
    list_r = [None]
recomendação = st.sidebar.selectbox("Selecione o tipo de recomendação de interesse:", list_r)  
if recomendação != None:
    if recomendação == 'Similaridade em custo-benefício':
        replace_player()
        st.markdown("![Alt Text](https://thumbs.gfycat.com/FaintCarefreeComet-size_restricted.gif)")
    elif recomendação == 'Similaridade em performance':
        performance_substitute()
        st.markdown("![Alt Text](https://media1.giphy.com/media/YPKAxM2qNEElwJFjqi/giphy.gif)")
    elif recomendação == 'Melhor custo-benefício':
        best_performance_and_cost_benefit()
        st.markdown("![Alt Text](https://i.pinimg.com/originals/b8/ad/39/b8ad39323eb66f7c0e95ccd79571b06e.gif)")
    elif recomendação == 'Outras recomendações':
        interesting_options()
        st.markdown("![Alt Text](https://media.giphy.com/media/8rEVtjWcJoNI5miInv/giphy.gif)")
else:
    st.subheader("O Moneyball versão brasileira Herbert Richers")
    st.text("Este app identifica eventuais oportunidades de negócio no futebol brasileiro.")
    st.markdown("![Alt Text](https://i.gifer.com/CbnC.gif)")
    st.text("Instruções:")
    st.text("1. Utilize o menu do lado esquerdo para selecionar um jogador como referência.")
    st.text("2. Selecione o tipo de recomendação desejada.")
    st.text("3. O aplicativo abrirá a página de recomendação.")
    st.text("4. Gere o gráfico de pontos e a tabela de performance comparativa entre\n jogadores para uma melhor análise.")
#     botão_saber_mais = False
#     new = 2
#     botão_saber_mais = st.button('Saber Mais')
#     if botão_saber_mais == True:
#         webbrowser.open('https://medium.com/@lucasbn17/granabola-o-moneyball-brasileiro-bfea29363fbe',new=new)
#         botão_saber_mais = False
