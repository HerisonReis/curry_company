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

#Não encontrei os icons, quando encontrar, fazer para todas as visões, pois os gráficos ficam maiores.
#st.set_page_config( page_title='Visão Empresa', page_icon='', layout='wide' )


#------------------------------------------------
# Funções
#------------------------------------------------
def country_maps( df1 ):
    df_aux05 = (df1.loc[:, ['City','Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                   .groupby(['City','Road_traffic_density'])
                   .median()
                   .reset_index())

    map = folium.Map()
    for index, location_info in df_aux05.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']]).add_to(map)
            
    folium_static( map, width=1024, height=600 )
    
    return None


def order_share_by_week( df1 ):
    #Quantidade de pedidos por semana / Número único de entregadores por semana
    df_aux01 = (df1.loc[:, ['ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .count()
                   .reset_index() )
            
    df_aux02 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                   .groupby('week_of_year')
                   .nunique()
                   .reset_index())

    df_aux4 = pd.merge(df_aux01, df_aux02, how='inner')
    df_aux4['order_by_deliver'] = df_aux4['ID']/df_aux4['Delivery_person_ID']

    fig = px.line(df_aux4, x='week_of_year', y='order_by_deliver')

    return fig

def order_by_week( df1 ):

    #criar a coluna semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux1 = df1.loc[:, ['ID','week_of_year']].groupby('week_of_year').count().reset_index()
    #desenhar gráfico de linhas
    fig = px.line( df_aux1, x='week_of_year', y='ID')
    
    return fig

def traffic_order_city( df1 ):
    df_aux3 = (df1.loc[:,['ID', 'City', 'Road_traffic_density']]
                  .groupby(['City','Road_traffic_density'])
                  .count()
                  .reset_index() )

    fig = px.scatter(df_aux3, x='City', y='Road_traffic_density', size= 'ID', color='City')
                
    return fig


def traffic_order_share( df1 ):
    df_aux2 = (df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby('Road_traffic_density')
                  .count()
                  .reset_index() )

    df_aux2 = df_aux2.loc[df_aux2['Road_traffic_density'] != "NaN", :]

    df_aux2['entregas_perc'] = df_aux2['ID'] / df_aux2['ID'].sum()

    fig = px.pie(df_aux2, values='entregas_perc', names= 'Road_traffic_density')
                
    return fig

def order_metric( df1 ):
    #colunas
    cols = ['ID', 'Order_Date']

    #selecao de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()

    #desenhar o gráfico de linhas - Plotly
    fig = px.bar(df_aux, x='Order_Date', y='ID')
            
    return fig

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

# -------------------------------------- Início da Estrutura lógica do código _________________________________________________
#------------------------------------
# Import dataset
#------------------------------------
df = pd.read_csv( 'dataset/train.csv' )

#------------------------------------
# Limpando os dados
#------------------------------------
df1 = clean_code( df )


    
# =========================================================
# Barra Lateral
# =========================================================

st.header('Marketplace - Visão Cliente')

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

#st.dataframe( df1 )
# =========================================================
# layout no Streamlit
# =========================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric( df1 )
        st.markdown( 'Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )
        

    with st.container():
        col1, col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share( df1 )
            st.header( "Traffic Order Share" )
            st.plotly_chart( fig, use_container_width=True )
                       
            
        with col2:
            fig = traffic_order_city( df1 )
            st.header( "Traffic Order City" )
            st.plotly_chart( fig, use_container_width=True )
                     

with tab2:
    
    with st.container():
        st.markdown("# Order by Week")
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        
    
    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
        
        
        
        
with tab3:
    st.markdown("# Country Maps")    
    country_maps( df1 )
    

        
