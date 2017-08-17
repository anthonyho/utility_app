#!/usr/bin/env python3
'''
Interactive interface for exploring building-level energy consumption data

Anthony Ho <anthony.ho@energy.ca.gov>
Last updated 8/16/2017
'''


import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import lib


# Read file
bills_file = '../EDA/processed_data/bills_building_eui_all_add_pf.csv'
bills = lib.read_processed_bills(bills_file)


# Define climate zones and types
list_cz = [str(cz)
           for cz in np.sort(bills[('cis', 'cz')].unique().astype(int))]
list_types = ['Warehouse', 'Distribution',
              'Office building', 'Medical building',
              'Hospital / convalescent home',
              'Hotel / motel',
              'Shopping center', 'Department store / retail outlet',
              'Food store / supermarket', 'Storefront retail',
              'Miscell commercial']


# Define app components
type_dropdown = dcc.Dropdown(id='building_type',
                             options=[{'label': bldg_type, 'value': bldg_type}
                                      for bldg_type in list_types],
                             value='Office building')
type_html = html.Div(type_dropdown,
                     style={'width': '48%',
                            'display': 'inline-block'})

cz_dropdown = dcc.Dropdown(id='climate_zone',
                           options=[{'label': 'Climate zone ' + cz,
                                     'value': cz}
                                    for cz in list_cz],
                           value='Office building')
cz_html = html.Div(cz_dropdown,
                   style={'width': '48%',
                          'float': 'right',
                          'display': 'inline-block'})


# Initiate dash and define layout
app = dash.Dash()


app.layout = html.Div([html.Div([type_html, cz_html]),
                       dcc.Graph(id='boxplot')])


@app.callback(Output('boxplot', 'figure'),
              [Input('climate_zone', 'value')])
def update_boxplot(cz):
    return lib.plot_box(bills, by='cz', selection=cz, value='EUI_tot_avg_2009_2015',
                 order=list_types)    

if __name__ == '__main__':
    app.run_server()