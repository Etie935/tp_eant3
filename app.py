import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input,Output,State
import dash_table
import pandas as pd
from datetime import date
import plotly.express as px
#import numpy as np
import folium 
import json
import requests
from bs4 import BeautifulSoup


#EVGJ=json.loads(requests.get("https://cdn.buenosaires.gob.ar/datosabiertos/datasets/secretaria-de-desarrollo-urbano/espacios-verdes/espacio-verde-publico.geojson").text)

#metrobus2=json.loads(requests.get("https://cdn.buenosaires.gob.ar/datosabiertos/datasets/metrobus/recorrido-de-metrobus.geojson").text)

#subtes2=json.loads(requests.get("https://cdn.buenosaires.gob.ar/datosabiertos/datasets/subte-estaciones/subte_lineas.geojson").text)

subterraneos = pd.read_csv('https://raw.githubusercontent.com/Etie935/Movilidad/main/estaciones-de-subte%20(1).csv', sep=',')

estaciones_metro=pd.read_csv('https://raw.githubusercontent.com/Etie935/Movilidad/main/estaciones-de-metrobus.csv', sep=',')

#estaciones_metro['WKT']=estaciones_metro['WKT'].apply(wkt.loads)

metrobus = estaciones_metro[['WKT','ID','NOMBRE','METROBUS']]

EV2=pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSYlWKbAAgTztOZm7PmhCNAuM3BLCORHNfJEKmiGNbRieL-TVtBx9hfaBMv2bVLGaSHfrw2Oa_SoukJ/pub?output=csv",sep=',')




#grafico ev/prop
EV2.COMUNA[(EV2['COMUNA']==0) & (EV2['clasificac'].str.contains("PARQUE", na=False))]=1
EV2.COMUNA[(EV2['COMUNA']==0)]=8
ev_area = pd.DataFrame({'area' : EV2.groupby(['BARRIO'])['area'].sum()}).reset_index() 
prop = pd.read_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQ3eGbDe7NfdHvtbut0lcTNRxRzbn_UfmNCm9h5DyKfRTBQ3pUwgGgsraeB2WY-TYYvlxwA7NQxv_tI/pub?output=csv",sep=';', error_bad_lines=False)
precio_ev_barrio = ev_area.merge(prop, left_on='BARRIO', right_on='barrio')
precio_ev_barrio["comuna"] = precio_ev_barrio.comuna.astype("category")
df_ev = precio_ev_barrio.sort_values('comuna', ascending=True)

figura1 = px.scatter(df_ev, x="precio_prom", y="area", color="comuna", hover_data=['barrio'],
                 labels={
                     
                     "precio_prom": "Precio Promedio del m2 (USD)" ,
                     "area": "Área de Espacio Verde Público"
                 },
                title="Precio promedio según área verde en la comuna")


#propiedades
df_prop=pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vRzwQsqjwFPZXeXiwVkLFhwwHqbdptFCkhYEL8yJgBFjSOolnpmOgLtShfakV1uf_LnOh1-Cq6O8uyk/pub?output=csv',sep=",")
temp=df_prop.groupby(['año','ambientes','barrio'],as_index=False).precio_prom.mean()

prop =px.bar(data_frame=temp,x='barrio',y='precio_prom', 
           color='ambientes',
           animation_frame='año',
           animation_group='barrio',
           barmode='group')

df=df_ev

########### Initiate the app
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = ['https://codepen.io/saisubrahmanyamjanapati/pen/WNNOYLZ.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
#app.title=tabtitle

response = 'https://drive.google.com/file/d/1BwXBDKhby2vf56hLB5VP8hAlX3ZWFAuV'
#soup=BeautifulSoup(open(response,encoding='utf-8'),'html.parser')

########### Set up the layout
app.layout = html.Div([
    html.H1('Precio de las propiedades en CABA: Cuál es el factor que más influye?'), 
        dcc.Tabs
    ([
        dcc.Tab(id='Tab1', label='Introducción',  children=
                [dcc.Markdown('''
                  A la hora de elegir un lugar para vivir, muchos factores influencian nuestra decisión. 
                  Es posible que nos guiemos por buscar en la zona en la que crecimos, o la que nos queda más cerca del trabajo. 
                  El precio suele ser un factor clave, tanto a la hora de comprar como de elegir un alquiler, 
                  pero a su vez el mismo se ve influenciado por otras cuestiones, que no siempre resultan claras, 
                  y que muchas veces dificultan la elección al presentar disyuntivas.
                  En este trabajo, realizado en el marco del curso Python Data Analytics de la Escuela Argentina de Nuevas Tecnologías [(EANT) ](https://eant.tech/escuela-de-ciencias-de-datos) 
                  y utilizando los [datos abiertos del Gobierno de la Ciudad de Buenos Aires](https://data.buenosaires.gob.ar/), 
                  proponemos que dos de los factores que influencian el valor de las propiedades de dos y tres ambientes de la Ciudad Autónoma de Buenos Aires 
                  son los medios de transporte disponibles y el fácil acceso a espacios verdes públicos como parques y plazas.
                  ''')]),
        dcc.Tab(id='Tab3', label='Gráficos',  children=[


            dcc.Dropdown(
                    id="drop_ev_amb",
                    value=df.ambientes.unique()[0],
                    options=[
                        {"label": col, "value": col} for col in df.ambientes.unique()
                    ]
                ),
            dcc.Graph(id='graph_1',figure=figura1),
            dcc.Graph(id='graph_2',figure=prop)

        ]), 
            
        dcc.Tab(id='Tab2', label='Mapa', children=[html.Iframe(id='map',srcDoc=open('mapa.html','r').read(),width='50%',height='600')]),
    
        dcc.Tab(id='Tab4', label='Conclusiones', children=[html.P("texto conclusiones")])
    ])

        
]) 

@app.callback(
    Output(component_id='graph_1', component_property='figure'),
    [Input(component_id='drop_ev_amb', component_property='value')]
)


def update_fig(selected_value):
    
    figura1 = px.scatter(df[df['ambientes'].isin(selected_value)],
                     x='precio_prom', 
                     y='area', 
                     color='comuna',
                     color_discrete_map=color_discrete_map,
                     hover_name='barrio')

    return figura1




if __name__ == '__main__':
    app.run_server()
