#!/usr/bin/env python3
'''
Interactive interface for exploring building-level energy consumption data

Anthony Ho <anthony.ho@energy.ca.gov>
Last updated 8/17/2017
'''


import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# import plotly.graph_objs as go
import lib


# Read file
bills_file = '../EDA/processed_data/bills_building_eui_all_add_pf.csv'
bills = lib.read_processed_bills(bills_file)
css_link = 'https://codepen.io/chriddyp/pen/bWLwgP.css'


# Define climate zones and types
dict_by = {'Select by building type': 'building_type',
           'Select by climate zone': 'cz'}
list_types = ['Warehouse', 'Distribution',
              'Office building', 'Medical building',
              'Hospital / convalescent home',
              'Hotel / motel',
              'Shopping center', 'Department store / retail outlet',
              'Food store / supermarket', 'Storefront retail',
              'Miscell commercial']
list_cz = [str(cz)
           for cz in np.sort(bills[('cis', 'cz')].unique().astype(int))]


# Define app components
# Radio botton for "select by"
by_radio = dcc.RadioItems(id='by_radio',
                          options=[{'label': label, 'value': dict_by[label]}
                                  for label in dict_by],
                          value='building_type',
                          labelStyle={'display': 'inline-block'})
by_html = html.Div(by_radio) #,
                   #style={'width': '48%',
                   #       'display': 'inline-block'})
# Dropdown list for selection
selection_dropdown = dcc.Dropdown(id='selection_dropdown')
selection_html = html.Div(selection_dropdown) #,
                          #style={'width': '48%',
                          #       'display': 'inline-block'})


# Dropdown list for building types
#type_dropdown = dcc.Dropdown(id='building_type',
#                             options=[{'label': bldg_type, 'value': bldg_type}
#                                      for bldg_type in list_types],
#                             value='Office building')
#type_html = html.Div(type_dropdown,
#                     style={'width': '48%',
#                            'display': 'inline-block'})
# Dropdown list for climate zones
#cz_dropdown = dcc.Dropdown(id='climate_zone',
#                           options=[{'label': 'Climate zone ' + cz,
#                                     'value': cz}
#                                    for cz in list_cz],
#                           value='3')
#cz_html = html.Div(cz_dropdown,
#                   style={'width': '48%',
#                          'float': 'right',
#                          'display': 'inline-block'})


# Initiate dash and define layout
app = dash.Dash()
app.layout = html.Div([html.Div([by_html,
                                 selection_html],
                                style={'width': '48%',
                                       'display': 'inline-block'}),
                       html.Div([dcc.Graph(id='boxplot')],
                                style={'width': '48%'})])
app.css.append_css({"external_url": css_link})


@app.callback(Output('selection_dropdown', 'options'),
              [Input('by_radio', 'value')])
def update_selection_options(by):
    if by == 'building_type':
        return [{'label': bldg_type, 'value': bldg_type}
                for bldg_type in list_types]
    elif by == 'cz':
        return [{'label': 'Climate zone ' + cz, 'value': cz} for cz in list_cz]


@app.callback(Output('selection_dropdown', 'value'),
              [Input('by_radio', 'value')])
def update_selection_value(by):
    if by == 'building_type':
        return 'Office building'
    elif by == 'cz':
        return '3'


@app.callback(Output('boxplot', 'figure'),
              [Input('by_radio', 'value'),
               Input('selection_dropdown', 'value')])
def update_boxplot(by, selection):
    if by == 'cz':
        order = list_types
    else:
        order = None
    return lib.plot_box(bills,
                        by=by, selection=selection, value='EUI_tot_avg_2009_2015',
                        order=order)



#@app.callback(Output('boxplot', 'figure'),
#              [Input('climate_zone', 'value')])
#def update_boxplot(cz):
#    return lib.plot_box(bills, by='cz', selection=cz, value='EUI_tot_avg_2009_2015',
#                 order=list_types)    

if __name__ == '__main__':
    app.run_server()