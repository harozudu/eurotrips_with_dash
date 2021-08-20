# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 10:14:42 2021

@author: HZU
"""
import pandas as pd
import geopandas

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output

###############################################################################
# Use 3 decimal places in output display
pd.set_option("display.precision", 3)
# Don't wrap repr(DataFrame) across additional lines
pd.set_option("display.expand_frame_repr", False)
# Set max rows displayed in output to 25
pd.set_option("display.max_rows", 15)
###############################################################################
"""
Data is coming from:
    https://ourairports.com/comments.html
"""
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### ---------------- Importing and cleaning data -----------------------------

airports = pd.read_csv('eu-airports.csv', sep=',')
airports = airports.groupby('type').get_group('large_airport')
location_airports_europe = geopandas.GeoDataFrame(airports, geometry=geopandas.points_from_xy(airports.longitude_deg, airports.latitude_deg))

airports_routes = pd.read_csv('AirportsRoutes_V_2.csv', sep=',')

#To search countries
all_countries = airports[['country_name']].drop_duplicates()
all_countries = all_countries.sort_values('country_name')

fig1 = px.scatter_mapbox(location_airports_europe,
                        lat = location_airports_europe.geometry.y,
                        lon = location_airports_europe.geometry.x,
                        hover_name=(location_airports_europe['municipality']+": "+location_airports_europe['name']),
                        title = 'Airports in europe',
                        zoom = 3,
                        )
fig1.update_layout(mapbox_style="open-street-map",
                   title=dict(x=0.5),
                   # margin=dict(l=550, r=20, t=60, b=20),
                   margin=dict(l=20, r=20, t=40, b=20),
                   paper_bgcolor="LightSteelblue"
                   )


airports_world_routes = airports_routes.groupby('id_from').count().sort_values(by='id_go', ascending=False).head(10)

airports_world_routes = airports_world_routes.rename(columns={'id_go':'number_of_flight_routes'})
airports_world_routes['airport_name'] = airports_world_routes.index
airports_world_routes = airports_world_routes[['airport_name','number_of_flight_routes']]
airports_world_routes.iloc[0,0] = 'Jackson Atlanta International Airport'
airports_world_routes.iloc[1,0] = 'O Hare International Airport'
airports_world_routes.iloc[2,0] = 'Beijing Capital International Airport'
airports_world_routes.iloc[3,0] = 'London Heathrow Airport'
airports_world_routes.iloc[4,0] = 'Amsterdam Airport Schiphol'
airports_world_routes.iloc[5,0] = 'Charles De Gaulle International Airport'
airports_world_routes.iloc[6,0] = 'Los Angeles International Airport'
airports_world_routes.iloc[7,0] = 'Dallas/Fort Worth International Airport'
airports_world_routes.iloc[8,0] = 'John F. Kennedy International Airport'
airports_world_routes.iloc[9,0] = 'Frankfurt am Main Airport'

#These are the airports with the most flights within Europe:
most_flights_wt_europe = airports_routes.loc[airports_routes['id_from'].isin(airports.iata_code)].groupby('id_from').count().sort_values(by='id_go', ascending=False).head(10)
most_flights_wt_europe['iata_code'] = most_flights_wt_europe.index
most_flights_wt_europe = most_flights_wt_europe.reset_index(drop=True)
names = airports.name[airports['iata_code'].isin(most_flights_wt_europe['iata_code'])]
names = pd.DataFrame(names)
names = names.reset_index(drop=True)
most_flights_wt_europe['airport_name'] = names
most_flights_wt_europe = most_flights_wt_europe.rename(columns={'id_go':'number_of_flight_routes'})
most_flights_wt_europe = most_flights_wt_europe.drop(['iata_code'], axis=1)
most_flights_wt_europe = most_flights_wt_europe[['airport_name','number_of_flight_routes']]



### --------------------------------------------------------------------------
### -------------------------- App layout ------------------------------------
app.layout = html.Div(#style={'backgroundColor': colors['background']},
                      children=[

    html.H1("Eurotrips with Dash", style={'text-align': 'center'}),
    html.Br(),
    
    html.Div([
        html.Div([        
            html.Label("The data displayed on this page comes from:",style={'fontSize': 20}),
            html.Label("https://ourairports.com/",style={'fontSize': 20}),
            html.Label("https://openflights.org/data.html",style={'fontSize': 20}),
            html.Label("This page has been created to offer information on the location of airports in Europe, the airports to which each of them is connected.",style={'fontSize': 20}),
            html.Label("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        ],style={
            "width" : '100%', 
            'display' : 'inline-block', 
            'paddingLeft' : 50, 
            'paddingRight' : 10,
            'boxSizing' : 'border-box',}
        ),
    ]),
    
    html.Br(),
    html.Br(),
    html.Br(),
        
    html.Div([
        html.Div([
            html.Div('In the world these are the ten airports with most flight routes:', style={'fontSize': 18}),
            html.Br(),
            dash_table.DataTable(
                id='table_airports_world',
                columns=[{"name": i, "id": i} for i in airports_world_routes.columns],
                data=airports_world_routes.to_dict('records'),
                )
        ],style={
            "width" : '50%', 
            'display' : 'inline-block', 
            'paddingLeft' : 50, 
            'paddingRight' : 10,
            'boxSizing' : 'border-box',}
        ),
        
        html.Div([
            html.Div('In Europe these are the ten airports with most flight routes:', style={'fontSize': 18}),
            html.Br(),            
            dash_table.DataTable(
                id='table_airports_europe',
                columns=[{"name": i, "id": i} for i in most_flights_wt_europe.columns],
                data=most_flights_wt_europe.to_dict('records'),
                )
        ],style={
            "width" : '50%', 
            'display' : 'inline-block', 
            'paddingLeft' : 50, 
            'paddingRight' : 10,
            'boxSizing' : 'border-box',}
        )
    ]),

    html.Br(),
    html.Br(),            
    html.Br(),

    html.Div([
            html.Div([

                    html.Label(f"The total number of big airports in Europe is: {len(airports)}", style={'fontSize': 18}),                

            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),
                
            html.Div([

                    html.Label(f"The number of flight routes in the world is: {len(airports_routes)}", style={'fontSize': 18})

            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),

            html.Div([

                    html.Label(f"The total number of flights within Europe is: {len(airports_routes.loc[airports_routes['id_go'].isin(airports.iata_code)])}", style={'fontSize': 18}),

            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),

            html.Br(),
            html.Br(),
            html.Br(),
            
    ]
    ),

    html.Div([
            html.Div([
                # id='output_container',
                # children=[
                    # html.Label('Please select a country:'),html.Br(),
                    html.Label('Please select a country:', style={'fontSize': 18}),
                    dcc.Dropdown(id="slct_country", 
                        options=[{'label':name, 'value':name} for name in all_countries['country_name']],
                                 # value=list(all_countries.iloc[1,0]),
                                 style={'width': "100%", 'display': '100%', 'verticalAlign': 'center'}
                                 ),
                    html.Label('Please select an airport:', style={'fontSize': 18}),
                    dcc.Dropdown(id="slct_city",
                                 style={'width': "100%", 'verticalAlign': 'middle', 'display': 'True'}
                                 ),
                # ], style={"width": "30%"},
            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),

            html.Div([

                    html.Label("The airport:", style={'fontSize': 18}),
                    # html.Label(id="text_airport_name", style={'fontSize': 18}),
                    html.Div(id="text_airport_name"),
                    html.Label("Has a total of flight connections of:", style={'fontSize': 18}),                    
                    # html.Label(id="text_fligths_connections", style={'fontSize': 18}),
                    html.Div(id="text_fligths_connections")

            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),          

            html.Div([

                    #html.Label("The airport with more flight routes within Europe is:", style={'fontSize': 18}),
                    #html.Label("Josep Tarradellas Barcelona-El Prat Airport with 321", style={'fontSize': 18}),

            ],style={
                "width" : '33%', 
                'display' : 'inline-block', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            ),                    
                
    ]),     
                
    html.Br(),
    html.Br(),            
    html.Br(),
                
            html.Div([    
                html.Div([
                    html.Div(
                    dcc.Graph(id='airports_map1', figure=fig1, style={'height':'700px'}),
                    )
                ])
            ],style={
                "width" : '70%', 
                'display' : 'center', 
                'paddingLeft' : 50, 
                'paddingRight' : 10,
                'boxSizing' : 'border-box',}
            )

])

# -----------------------------------------------------------------------------
# ---------- Connect the Plotly graphs with Dash Components -------------------

@app.callback(
    Output(component_id="slct_city", component_property='options'),
    Input(component_id="slct_country", component_property="value")
    )

def display_cities(value):
    if value == None:
        raise dash.exceptions.PreventUpdate
    else:
        all_cities = airports.loc[airports['country_name'] == value]
        all_cities = all_cities[['municipality', 'name']]
        all_cities = all_cities['municipality']+" :"+all_cities['name']
        all_cities_list = all_cities.values.tolist()

        return [{'label':name, 'value':name} for name in all_cities_list]



@app.callback(
    Output(component_id='airports_map1', component_property='figure'),
    # Output(component_id="text_airport_name", component_property='value'),
    # Output(component_id="text_fligths_connections", component_property='value'),
    Output(component_id="text_airport_name", component_property='children'),
    Output(component_id="text_fligths_connections", component_property='children'),

    [Input(component_id='slct_city', component_property='value')]
    )

def draw_map(value):

    if value == None:
        raise dash.exceptions.PreventUpdate
    else:
        name_airport = value.split(':')[1]
        home_aiport = airports.loc[airports['name'] == name_airport]
        from_home_to = airports_routes.loc[airports_routes['id_from'] == home_aiport.iloc[0,16]]
        data = airports.loc[airports['iata_code'].isin(from_home_to.id_go)]
        location_conected_airports = geopandas.GeoDataFrame(data, geometry=geopandas.points_from_xy(data.longitude_deg, data.latitude_deg))
        
        fig = px.scatter_mapbox(location_conected_airports,
                  lat=location_conected_airports.geometry.y,
                  lon=location_conected_airports.geometry.x,
                  hover_name="name",
                  title='From '+name_airport+' you can travel to the airports on the map',
                  
                  color = 'name',
                  
                  zoom=3,)
        
        fig.update_layout(mapbox_style="open-street-map",
                   title=dict(x=0.5),
                   margin=dict(l=20, r=20, t=40, b=20),
                   paper_bgcolor="LightSteelblue"
                   )

        return fig, name_airport, len(data)


  


if __name__ == '__main__':
    app.run_server(debug=True)