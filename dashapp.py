import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import glob
import fnmatch
import json
from plotly.subplots import make_subplots

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])

server = app.server

all_files = glob.glob('data_cleaned/*')
all_files.sort()
print(all_files)


# Store dataframes in a dictionary
dfs_dict = {}

for filename in all_files:
    df = pd.read_csv(filename, compression='gzip')
    dfs_dict[filename[13:-7]] = df

print(dfs_dict.keys())

with open('neighbourhoods.geojson') as fp:
    TRT_geo = json.load(fp)

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h")
)

def_click = {'points': [{'curveNumber': 0, 'pointNumber': 122, 'pointIndex': 122,
                         'location': 'Waterfront Communities-The Island', 'z': 1183.66}]}
def_hov = {'points': [{'curveNumber': 0, 'pointNumber': 23, 'pointIndex': 23,
                       'x': '2020 Oct', 'y': 1183.66}]}

github_link = "App source code: [Github](https://github.com/RobinKongNingLo/dash-toronto-airbnb)"

data_source = "Dataset source: [Inside Airbnb](http://insideairbnb.com/get-the-data.html)"

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.A(
                            html.Img(className="logo", src=app.get_asset_url("dash-logo.png")),
                            href="https://dash.plot.ly/",
                        ),
                        html.H2(
                            [
                                "Toronto Airbnb Data App",
                            ],
                            style={"text-align": "left"},
                        ),

                        html.P('Select a feature'),
                        dcc.Dropdown(
                            id='feature_dropdown',
                            options=[
                                {'label': 'Price per Accommodate per Day', 'value': 'price'},
                                {'label': 'Revenue per Accommodate per Month', 'value': 'revenue'},
                                {'label': 'Occupancy per Month', 'value': 'occupancy'}
                            ],
                            value='revenue'),
                        html.H3('About this app'),
                        html.P('Click a neighbourhood from the map to see the data visualization of the neighbourhood, '
                               'click a time from the line chart to see the data visualization at the time. '),
                        html.Div(id="github_link", children=dcc.Markdown(github_link)),
                        html.Div(id="data_set_source", children=dcc.Markdown(data_source)),
                    ],
                    className='pretty_container threehalf columns'
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P("Selected Neighbourhood"),
                                        html.H6(id="neighbourhood_txt"),
                                    ],
                                    className='eight columns pretty_container'
                                ),
                                html.Div(
                                    [
                                        html.P(id="avg_1_txt"),
                                        html.H6(id="avg_1_val"),
                                    ],
                                    className='five columns pretty_container'
                                ),
                                html.Div(
                                    [
                                        html.P(id="avg_2_txt"),
                                        html.H6(id="avg_2_val"),
                                    ],
                                    className='five columns pretty_container'
                                ),
                            ],
                            className='row container-display',
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(id='map_title'),
                                        dcc.Graph(id='map', figure={}, clickData=def_click, config={'displayModeBar': False})
                                    ],
                                    id='mapContainer',
                                    className='seven columns pretty_container'
                                ),
                                html.Div(
                                    [
                                        html.H4(id='box_title'),
                                        dcc.Graph(id='box', figure={}, config={'displayModeBar': False})
                                    ],
                                    id='boxContainer',
                                    className='five columns pretty_container'
                                ),
                            ],
                            className='row container-display',
                        ),
                    ],
                    className='eighthalf columns'
                ),
            ],
            className="row flex-display"
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.H4(id='pie_title'),
                        dcc.Graph(id='pie', figure={}, config={'displayModeBar': False})
                    ],
                    id='pieContainer',
                    className='pretty_container threehalf columns'
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(id='line_title'),
                                dcc.Graph(id='line', figure={}, clickData=def_hov, config={'displayModeBar': False})
                            ],
                            id='lineContainer',
                            className='seven columns pretty_container'
                        ),
                        html.Div(
                            [
                                html.H4(id='bar_title'),
                                dcc.Graph(id='bar', figure={}, config={'displayModeBar': False})
                            ],
                            id='barContainer',
                            className='five columns pretty_container'
                        ),
                    ],
                    className='row container-display eighthalf columns',
                ),
            ],
            className="row flex-display"
        )
    ],
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(
    [Output(component_id='box_title', component_property='children'),
     Output(component_id='line_title', component_property='children'),
     Output(component_id='bar_title', component_property='children'),
     Output(component_id='pie_title', component_property='children')],
    [Input(component_id='feature_dropdown', component_property='value'),
     Input(component_id='line', component_property='clickData')]
)
def update_titles(feature, hover_data):
    [key_1, key_2] = [key for key in dfs_dict.keys() if fnmatch.fnmatch(key, '*' + hover_data['points'][0]['x'][5:])]
    box_title = "Box Plot of " + feature.capitalize() #+ " " + key_1[9:13] + " vs " + key_2[9:]
    line_title = "Line Chart of " + feature.capitalize() + " Nov 2018 to Oct 2020"
    bar_title = "Bar Chart of " + feature.capitalize() #+ " " + key_1[9:13] + " vs " + key_2[9:]
    pie_title = "Number of Each Room Type " #+ key_1[9:13] + " vs " + key_2[9:]
    return box_title, line_title, bar_title, pie_title


@app.callback(
    [Output(component_id='map', component_property='figure'),
     Output(component_id='map_title', component_property='children')],
    [Input(component_id='line', component_property='clickData'),
     Input(component_id='feature_dropdown', component_property='value')]
)
def update_map(hover_data, feature):
    print(hover_data)
    df_feature = dfs_dict[feature]
    dff = df_feature[['neighbourhood_cleansed', 'room_type', hover_data['points'][0]['x']]]
    dff = dff.loc[dff['room_type'] == 'Both']



    fig_map = px.choropleth_mapbox(dff, geojson=TRT_geo,
                                   locations="neighbourhood_cleansed",
                                   featureidkey="properties.neighbourhood",
                                   color=dff[hover_data['points'][0]['x']],
                                   #color_continuous_scale=[(0.00, "#ff000d"), (0.50, "#007a89"), (1.00, "#27408B")],
                                   color_continuous_scale="DarkMint",
                                   mapbox_style="carto-positron",
                                   zoom=9,
                                   center={"lat": 43.722275, "lon": -79.406074},
                                   opacity=0.5,
                                   )

    """
    fig_map = go.Figure(go.Choroplethmapbox(geojson=TRT_geo,
                                            locations=dff.neighbourhood_cleansed,
                                            featureidkey="properties.neighbourhood",
                                            z=dff[hover_data['points'][0]['x']],
                                            marker_opacity=0.5,
                                            colorscale="Viridis",
                                            colorbar=dict(thickness=10, ticklen=0),
                                            marker_line_width=0
                                            ))
    
    fig_map.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=9,
        #marker_opacity=0.5,
        mapbox_center={"lat": 43.722275, "lon": -79.366074},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10),
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1
                    ),
        )
    """
    fig_map.update_coloraxes(
        colorbar_xpad=10,
        colorbar_ypad=10,
        colorbar_x=0,
        colorbar_thickness=20,
        colorbar_title=None
        #showscale=False
    )
    fig_map.update_traces(hovertemplate=None)
    fig_map.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        hoverlabel=dict(
            font_size=12,
            namelength=-1,
            bgcolor="#007a89")
    )
    map_title = "Map Overview of " + feature.capitalize() + " " + hover_data['points'][0]['x']
    return fig_map, map_title


@app.callback(
    Output(component_id='line', component_property='figure'),
    [Input(component_id='map', component_property='clickData'),
     Input(component_id='feature_dropdown', component_property='value')]
)
def update_line(click_data, feature):
    print(click_data)
    df_feature = dfs_dict[feature]
    dff_pr_feature = df_feature.loc[
        (df_feature['neighbourhood_cleansed'] == click_data['points'][0]['location']) & (df_feature['room_type'] == 'Private room')]
    dff_eh_feature = df_feature.loc[
        (df_feature['neighbourhood_cleansed'] == click_data['points'][0]['location']) & (df_feature['room_type'] == 'Entire home/apt')]
    dff_pr_feature = dff_pr_feature.transpose()[2:].reset_index()
    dff_pr_feature.columns = ['time', feature]
    dff_eh_feature = dff_eh_feature.transpose()[2:].reset_index()
    dff_eh_feature.columns = ['time', feature]
    fig = go.Figure(go.Scatter(x=dff_pr_feature['time'], y=dff_pr_feature[feature],
                               mode='lines+markers', name='Private Room', marker_color="#ff5a61"))
    fig.add_trace(go.Scatter(x=dff_eh_feature['time'], y=dff_eh_feature[feature],
                             mode='lines+markers', name='Entire Home/Apt', marker_color="#007a89"))
    #fig.update_traces(mode="markers+lines", hovertemplate=None)

    fig.update_layout(
        margin={"r": 0, "t": 0.5, "l": 0, "b": 0},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10),
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1
                    ),
        hovermode="x",
        hoverlabel=dict(
            font_size=12,
            namelength=-1
        )
        )
    return fig


@app.callback(
    Output(component_id='neighbourhood_txt', component_property='children'),
    [Input(component_id='map', component_property='clickData')]
)
def update_neighbourhood_txt(click_data):
    return click_data['points'][0]['location']


@app.callback(
    [Output(component_id='avg_1_txt', component_property='children'),
     Output(component_id='avg_2_txt', component_property='children'),
     Output(component_id='avg_1_val', component_property='children'),
     Output(component_id='avg_2_val', component_property='children')
     ],
    [Input(component_id='line', component_property='clickData'),
     Input(component_id='map', component_property='clickData'),
     Input(component_id='feature_dropdown', component_property='value')]
)
def update_avg_box(hover_data, click_data, feature):
    [key_1, key_2] = [key for key in dfs_dict.keys() if fnmatch.fnmatch(key, '*'+hover_data['points'][0]['x'][5:])]
    txt_1 = key_1[9:] + " Average"
    txt_2 = key_2[9:] + " Average"
    df_feature = dfs_dict[feature]
    val_1 = df_feature.loc[(df_feature['neighbourhood_cleansed'] == click_data['points'][0]['location']) & (df_feature['room_type'] == 'Both')][key_1[9:]]
    val_2 = df_feature.loc[(df_feature['neighbourhood_cleansed'] == click_data['points'][0]['location']) & (df_feature['room_type'] == 'Both')][key_2[9:]]
    val_1 = format(float(val_1), '0,.2f')
    val_2 = format(float(val_2), '0,.2f')
    if feature == 'occupancy':
        val_1 = val_1 + ' Days'
        val_2 = val_2 + ' Days'
    else:
        val_1 = '$' + val_1
        val_2 = '$' + val_2
    return txt_1, txt_2, val_1, val_2


@app.callback(
    Output(component_id='box', component_property='figure'),
    [Input(component_id='line', component_property='clickData'),
     Input(component_id='map', component_property='clickData'),
     Input(component_id='feature_dropdown', component_property='value')]
)
def update_box(hover_data, click_data, feature):
    [key_1, key_2] = [key for key in dfs_dict.keys() if fnmatch.fnmatch(key, '*' + hover_data['points'][0]['x'][5:])]
    df_time_1 = dfs_dict[key_1]
    df_time_2 = dfs_dict[key_2]
    # Column of price in listings tables are called 'price_per_accommodate'
    if feature == 'price':
        feature = 'price_per_accommodate'
    df_time_1 = df_time_1.loc[df_time_1['neighbourhood_cleansed'] == click_data['points'][0]['location']]
    df_time_2 = df_time_2.loc[df_time_2['neighbourhood_cleansed'] == click_data['points'][0]['location']]
    fig = go.Figure(data=[go.Box(x=df_time_1["room_type"], y=df_time_1[feature], name=key_1[9:], marker_color="#ff5a61"),
                          go.Box(x=df_time_2["room_type"], y=df_time_2[feature], name=key_2[9:], marker_color="#007a89")])
    fig.update_layout(
        boxmode='group',  # group together boxes of the different traces for each value of x
        margin={"r": 0, "t": 0.5, "l": 0, "b": 0},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10),
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1,
                    ),
        #yaxis=dict(title='Revenue per Accommodate', title_font_family="Helvetica", zeroline=False),
    )
    fig.update_traces(hovertemplate="%{x} <br>" + feature.capitalize() + ": %{y}")
    return fig


@app.callback(
    Output(component_id='pie', component_property='figure'),
    [Input(component_id='line', component_property='clickData'),
     Input(component_id='map', component_property='clickData')]
)
def update_pie(hover_data, click_data):
    df_count = dfs_dict['count']
    df_count = df_count.loc[(df_count['neighbourhood_cleansed'] == click_data['points'][0]['location'])
                            & (df_count['room_type'] != 'Both')]
    [key_1, key_2] = [key for key in dfs_dict.keys() if fnmatch.fnmatch(key, '*' + hover_data['points'][0]['x'][5:])]
    fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=[key_1[9:], key_2[9:]])
    fig.add_trace(go.Pie(labels=df_count['room_type'], values=df_count[key_1[9:]], name=key_1[9:],
                         textinfo='value', insidetextorientation='radial'), 1, 1)
    fig.add_trace(go.Pie(labels=df_count['room_type'], values=df_count[key_2[9:]], name=key_2[9:],
                         textinfo='value', insidetextorientation='radial'), 1, 2)
    fig.update_traces(hole=.3, marker=dict(colors=['#007a89', '#ff5a61']), hovertemplate="%{label}: <br>Number: %{value} </br>Percentage: %{percent}")
    fig.update_layout(  # group together boxes of the different traces for each value of x
        margin={"r": 15.5, "t": 0, "l": 15.5, "b": 15.5},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10),
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1,
                    ),
        annotations=[{'font': {'size': 12},
                      'y': -0.1},
                     {'font': {'size': 12},
                      'y': -0.1}
                     ]
        #annotations=[dict(text=key_1[9:], x=0.14, y=-0.1, font_size=12, showarrow=False),
                     #dict(text=key_2[9:], x=0.87, y=-0.1, font_size=12, showarrow=False)]
    )
    return fig


@app.callback(
    Output(component_id='bar', component_property='figure'),
    [Input(component_id='line', component_property='clickData'),
     Input(component_id='map', component_property='clickData'),
     Input(component_id='feature_dropdown', component_property='value')]
)
def update_bar(hover_data, click_data, feature):
    [key_1, key_2] = [key for key in dfs_dict.keys() if fnmatch.fnmatch(key, '*' + hover_data['points'][0]['x'][5:])]
    df_feature = dfs_dict[feature]
    df_feature = df_feature.loc[(df_feature['neighbourhood_cleansed'] == click_data['points'][0]['location'])
                                & (df_feature['room_type'] != 'Both')]
    fig = go.Figure(data=[go.Bar(name=key_1[9:], x=df_feature['room_type'], y=df_feature[key_1[9:]], marker_color="#ff5a61"),
                          go.Bar(name=key_2[9:], x=df_feature['room_type'], y=df_feature[key_2[9:]], marker_color="#007a89")])
    fig.update_traces(hovertemplate="%{x} <br>" + feature.capitalize() + ": %{y}")
    fig.update_layout(
        boxmode='group',  # group together boxes of the different traces for each value of x
        margin={"r": 0, "t": 0.5, "l": 0, "b": 0},
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        legend=dict(font=dict(size=10),
                    orientation="h",
                    yanchor="bottom",
                    y=1,
                    xanchor="right",
                    x=1,
                    ),
        # yaxis=dict(title='Revenue per Accommodate', title_font_family="Helvetica", zeroline=False),
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
