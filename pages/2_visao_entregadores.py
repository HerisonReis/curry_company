# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium

# bibliotecas necessárias
import streamlit as st
import pandas as pd
from PIL import Image
from streamlit_folium import folium_static
from datetime import datetime

#------------------------------------------------
# Funções
#------------------------------------------------



def top_delivers( df1, top_asc ):
                
    df2 = (df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
              .reset_index() )

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index( drop=True )
                
    return df3


def clean_code( df1 ):
    """ Está função tema a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """""

    # Remover espaços da string

    df1.loc[0:, 'ID'] = df1.loc[0:, 'ID'].str.strip()
    df1.loc[0:,'Delivery_person_ID'] = df1.loc[0:, 'Delivery_person_ID'].str.strip()
    df1.loc[0: , 'Road_traffic_density'] = df1.loc[0: , 'Road_traffic_density'].str.strip()
    df1.loc[0: , 'Type_of_order'] = df1.loc[0: , 'Type_of_order'].str.strip()
    df1.loc[0: , 'Type_of_vehicle'] = df1.loc[0: , 'Type_of_vehicle'].str.strip()
    df1.loc[0: , 'City'] = df1.loc[0: , 'City'].str.strip()

    # Excluir linhas com a idade dos entregadores vazias
    # (conceito de seleção condicional)

    linhas_vazia = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazia, :]

    linhas_vazia = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazia, :]

    linhas_vazia = df1['Type_of_order'] != 'NaN'
    df1 = df1.loc[linhas_vazia, :]

    linhas_vazia = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazia, :]
    

    # Conversão de texto para numero
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # Conversão de texto para decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para Data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y')

    # Remover as linhas da coluna multiple_deliveries que tenham o conteudo 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Road_traffic_density'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['City'] != 'NaN'
    df1 = df1.loc[linhas_vazias, :]

    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)


    # Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)


    return df1


# Import dataset

df = pd.read_csv( 'dataset/train.csv' )

# Cleaning dataset
df1 = clean_code( df )



# =========================================================
# Barra Lateral
# =========================================================

st.header('Marketplace - Visão Entregadores')

#image_path = 'logo_cds.jpg'
#image = Image.open( image_path)
image = Image.open( 'logo_cds.jpg')
st.sidebar.image( image, width=120 )

st.sidebar.markdown ('# Cury Company')
st.sidebar.markdown ('## Fastest Delivery in Town')
st.sidebar.markdown ("""___""")

st.sidebar.markdown( '## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13 ),
    min_value=datetime(2022, 2, 11 ),
    max_value=datetime(2022, 4, 6 ),
    format='DD-MM-YYYY' )

st.write( date_slider )
#MOSTRAR QUE O DATE_SLIDER NÃO ESTÁ MODIFICANDO
st.sidebar.markdown ("""___""")


traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
                       ['Low', 'Medium', 'High', 'Jam'],
                       default='Low' )


st.sidebar.markdown ("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Condições do Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


# =========================================================
# layout no Streamlit
# =========================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''])

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns(4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', maior_idade )

        
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', menor_idade )
        
        with col3:
             # A melhor condicao de veiculos
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )

        
        with col4:
             # A pior condicao de veiculos
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric( 'Pior condição', pior_condicao )
    
    with st.container():
        st.markdown ("""___""")
        st.title( 'Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( '#### Avaliacao medias por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                             .groupby('Delivery_person_ID')
                                             .mean()
                                             .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )


        
        with col2:
            st.markdown( '#### Avaliacao media por transito' )
            
            df_avg_std_rating_by_traffic = (df1.loc[:,['Road_traffic_density','Delivery_person_Ratings',]]
                                               .groupby('Road_traffic_density')
                                               .agg( {'Delivery_person_Ratings':['mean', 'std'] }) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean','delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

            st.dataframe( df_avg_std_rating_by_traffic )
            
            st.markdown( '#### Avaliacao media por clima' )
            
            df_avg_std_rating_by_weathers_condition = (df1.loc[:,['Weatherconditions','Delivery_person_Ratings']]
                                                          .groupby('Weatherconditions')
                                                          .agg( {'Delivery_person_Ratings':['mean', 'std'] }) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_weathers_condition.columns = ['condition_mean','condition_std']

            # reset do index
            df_avg_std_rating_by_weathers_condition = df_avg_std_rating_by_weathers_condition.reset_index()

            st.dataframe( df_avg_std_rating_by_weathers_condition )
        
    
    with st.container():
        st.markdown ("""___""")
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown( '#### Top entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=True)
            st.dataframe( df3 )
        
        with col2:
            st.markdown( '#### Top entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=False)
            st.dataframe( df3 )
            
            
            
            
            
        
