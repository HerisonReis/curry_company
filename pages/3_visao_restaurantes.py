# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium

# bibliotecas necessárias
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from streamlit_folium import folium_static

#------------------------------------------------
# Funções
#------------------------------------------------

def avg_std_time_on_traffic( df1 ): 
    
    df_aux = (df1.loc[:, ['City','Time_taken(min)', 'Road_traffic_density']]
                 .groupby(['Road_traffic_density','City'])
                 .agg({'Time_taken(min)': ['mean','std']}))
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
            
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                            color='std_time', color_continuous_scale='RdBu',
                            color_continuous_midpoint=np.average(df_aux['std_time'] ) )
        
    return fig


def distance( df1, fig ):
    if fig == False:
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']

        df1['distance'] = df1.loc[:,cols].apply(lambda x:
                        haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
            
        avg_distance = np.round( df1['distance'].mean(), 2 )
        return avg_distance
    
    else:
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']

        df1['distance'] = df1.loc[:,cols].apply(lambda x:
                        haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),
                        (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
            
        avg_distance = df1.loc[:, ['distance' , 'City']].groupby('City').mean().reset_index()
                       
        fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        
        
        return fig
        

def avg_std_time_graph( df1 ):

    df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control',
                             x=df_aux['City'],
                             y=df_aux['avg_time'],
                       error_y=dict( type='data', array=df_aux['std_time'] ) ) )

    fig.update_layout(barmode='group')
        
    return fig



def avg_std_time_delivery( df1, festival, op ):
    """
        Esta função cálcula o tempo médio e o desvio padrão do tempo de entrega.
            Parâmetros:
                Input:
                     - df: Dataframe com os dados necessários para o cálculo
                     - op: Tipo de operação precisa ser calculado
                         'avg_time': Calcula o tempo médio
                         'std_time': Calcula o desvio padrão do tempo
                Output:
                    - df: Dataframe com 2 colunas e 1 linha
            
            """
               
    df_aux = ( df1.loc[:, ['Time_taken(min)', 'Festival']]
                  .groupby('Festival')
                  .agg({'Time_taken(min)': ['mean', 'std']}) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2 )


    return df_aux





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
    
            #limpeza 'NaN ' do Festival
    linhas_vazia = (df1['Festival'] != 'NaN ')
    #df1 = df1.loc[linhas_selecionadas, :].copy()
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

# -------------------------------------- Início da Estrutura lógica do código _________________________________________________
#------------------------------------
# Import dataset
#------------------------------------
df = pd.read_csv( 'train.csv' )

#------------------------------------
# Limpando os dados
#------------------------------------
df1 = clean_code( df )



# =========================================================
# Barra Lateral
# =========================================================

st.header('Marketplace - Visão Restaurantes')

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
    value=pd.datetime(2022, 4, 13 ),
    min_value=pd.datetime(2022, 2, 11 ),
    max_value=pd.datetime(2022, 4, 6 ),
    format='DD-MM-YYYY' )

#st.write( date_slider )
st.markdown( date_slider )
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
with st.container():
    st.title( " Overal Metrics " )
        
    col1, col2, col3 = st.columns( 3 )
    with col1:
            delivery_unique = len (df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric( 'Entregadores' , delivery_unique )
            
    with col2:
        avg_distance = distance( df1, fig=False )
        col2.metric('Distância média', avg_distance)
                
                        
    with col3:
        df_aux = avg_std_time_delivery(df1, 'Yes ', 'avg_time' )
        col3.metric( 'Tempo Médio', df_aux)
        
        
            
            
with st.container():
    st.markdown("""___""")
        
    col1, col2, col3 = st.columns( 3 )

    with col1:
        df_aux = avg_std_time_delivery(df1, 'Yes ', 'std_time' )
        col1.metric( 'STD Entrega', df_aux)
        
                 
    with col2:
        df_aux = avg_std_time_delivery(df1, 'No ', 'std_time' )
        col2.metric( 'Tempo Médio', df_aux)

        
            
    with col3:
        df_aux = avg_std_time_delivery(df1, 'No ', 'std_time' )
        col3.metric( 'STD Entrega', df_aux)
    
    
    
    
    
with st.container():
    st.markdown("""___""")      
    st.title( "tempo Medio de entrega por cidade" )
          
    fig = avg_std_time_graph( df1 )
    st.plotly_chart( fig )
            


        
        
with st.container():
    st.markdown("""___""")
    st.title( "Distribuição do Tempo" )
                    
    fig = distance( df1, fig=True )
    st.plotly_chart( fig )
            
        

        
with st.container():
    st.markdown("""___""")
    st.title( "Distribuição da Distância" )

    df_aux = (df1.loc[:, ['City','Time_taken(min)', 'Type_of_order']]
                 .groupby(['Type_of_order','City'])
                 .agg({'Time_taken(min)': ['mean','std']}))

    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    st.dataframe( df_aux )
        
        
with st.container():
    st.title( "Sunburst" )    
    fig = avg_std_time_on_traffic( df1 )
    st.plotly_chart( fig )