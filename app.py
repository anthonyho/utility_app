#!/usr/bin/env python3
'''
Interactive interface for exploring building-level energy consumption data

Anthony Ho <anthony.ho@energy.ca.gov>
Last updated 8/17/2017
'''


import numpy as np
# import pandas as pd
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
dict_by = {'building_type': 'Building type',
           'cz': 'Climate zone'}
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
# Define radio botton and dropdown menu for "select by"
by_radio = dcc.RadioItems(id='by_radio',
                          options=[{'label': 'Building type',
                                    'value': 'building_type'},
                                   {'label': 'Climate zone', 'value': 'cz'}],
                          value='cz',
                          labelStyle={'display': 'inline-block'})
selection_dropdown = dcc.Dropdown(id='selection_dropdown')
#selection_by_html = html.Div([html.Label('Slice data by:'),
#                              by_radio,
#                              selection_dropdown])
# Define radio botton for statistics to plot
unit_radio = dcc.RadioItems(id='unit_radio',
                            options=[{'label': 'Raw', 'value': 'raw'},
                                     {'label': 'EUI', 'value': 'EUI'}],
                            value='EUI',
                            labelStyle={'display': 'inline-block'})
#unit_html = html.Div([html.Label('Plot data for: (to fix)'),
#                      unit_radio])
# Define radio botton for statistics to plot
stats_radio = dcc.RadioItems(id='stats_radio',
                             options=[{'label': 'Average annual total',
                                       'value': 'avg'},
                                      {'label': 'Trend', 'value': 'fit'}],
                             value='avg',
                             labelStyle={'display': 'inline-block'})
#stats_html = html.Div([html.Label('Statistics:'),
#                       stats_radio])
# Define radio botton for fuel to plot
fuel_radio = dcc.RadioItems(id='fuel_radio',
                            options=[{'label': 'Total', 'value': 'tot'},
                                     {'label': 'Electric', 'value': 'elec'},
                                     {'label': 'Gas', 'value': 'gas'}],
                            value='tot',
                            labelStyle={'display': 'inline-block'})
#fuel_html = html.Div([html.Label('Fuel type:'),
#                      fuel_radio])
# Define radio botton for color in map
color_radio = dcc.RadioItems(id='color_radio',
                             options=[{'label': 'Raw', 'value': 'raw'},
                                      {'label': 'EUI', 'value': 'EUI'},
                                      {'label': 'Climate zone', 'value': 'cz'},
                                      {'label': 'Building type',
                                       'value': 'building_type'}],
                             value='EUI',
                             labelStyle={'display': 'inline-block'})
#color_html = html.Div([html.Label('Color buildings by:'),
#                       color_radio])


left_col_html = html.Div([html.Label('Slice data by:'),
                          by_radio,
                          selection_dropdown,
                          html.Label('Plot data for: (to fix)'),
                          unit_radio,
                          html.Label('Statistics:'),
                          stats_radio,
                          html.Label('Fuel type:'),
                          fuel_radio],
                         style={'width': '48%',
                                'display': 'inline-block'})
right_col_html = html.Div([html.Label('Color buildings by:'),
                           color_radio],
                          style={'width': '48%',
                                 'display': 'inline-block',
                                 'float': 'right'})
control_panel_html = html.Div([left_col_html,
                               right_col_html],
                              style={'borderBottom': 'thin lightgrey solid',
                                     'backgroundColor': 'rgb(250, 250, 250)',
                                     # 'padding': '10px 5px'
                                     })


# Initiate dash and define layout
app = dash.Dash()
app.layout = html.Div([html.Div([dcc.Graph(id='map',
                                           figure=lib.plot_map(bills))],
                                style={'width': '49%',
                                       'display': 'inline-block'}),
                       html.Div([control_panel_html,
                                 dcc.Graph(id='boxplot')],
                                style={'width': '49%',
                                       'display': 'inline-block',
                                       'float': 'right'
                                       })
                       ])
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
               Input('selection_dropdown', 'value'),
               Input('unit_radio', 'value'),
               Input('stats_radio', 'value'),
               Input('fuel_radio', 'value')])
def update_boxplot(by, selection, unit, stats, fuel):
    if by == 'cz':
        order = list_types
    else:
        order = None
    if stats == 'fit':
        value_suffix = '_slope'
    else:
        value_suffix = ''

    value = 'EUI_' + fuel + '_' + stats + '_2009_2015' + value_suffix
    return lib.plot_box(bills,
                        by=by, selection=selection, value=value,
                        order=order)



if __name__ == '__main__':
    app.run_server()