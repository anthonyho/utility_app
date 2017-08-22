#!/usr/bin/env python3
'''
Interactive interface for exploring building-level energy consumption data

Anthony Ho <anthony.ho@energy.ca.gov>
Last updated 8/18/2017
'''


import numpy as np
# import pandas as pd
import dash
# import dash_auth
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# import plotly.graph_objs as go
import argparse
from collections import OrderedDict
import lib


# Define css links
banner_link = 'https://raw.githubusercontent.com/anthonyho/utility_app/master/banner.png'
css_links = ['https://fonts.googleapis.com/css?family=Overpass:300,300i',
             'https://cdn.rawgit.com/plotly/dash-app-stylesheets/dab6f937fd5548cebf4c6dc7e93a10ac438f5efb/dash-technical-charting.css']

# Define names and options
list_types = ['Warehouse', 'Distribution',
              'Office building', 'Medical building',
              'Hospital / convalescent home', 'Hotel / motel',
              'Shopping center', 'Department store / retail outlet',
              'Food store / supermarket', 'Storefront retail',
              'Miscell commercial']
dict_iou = OrderedDict([('pge', 'PG&E'),
                        ('sce', 'SCE'),
                        ('scg', 'SCG'),
                        ('sdge', 'SDG&E')])
dict_fuel1 = OrderedDict([('elec', 'Electric only'),
                          ('gas', 'Gas only'),
                          ('both', 'Both')])
dict_fuel2 = OrderedDict([('tot', 'Total'),
                          ('elec', 'Electric'),
                          ('gas', 'Gas')])
dict_unit = OrderedDict([('raw', 'Raw'),
                         ('EUI', 'EUI')])
dict_stat = OrderedDict([('avg', 'Average annual total'),
                         ('fit', 'Trend')])
list_colorby = ['Building type', 'Climate zone',
                'IOU', 'Fuel type',
                'Consumption', 'Year built', 'Building area']

# Define username and password
# VALID_USERNAME_PASSWORD_PAIRS = [
#     ['hello', 'world']
# ]

# Get options and arguments from command line
description = 'Interactive web app for visualizing building energy data'
parser = argparse.ArgumentParser(description=description)
parser.add_argument('--public', action='store_true',
                    help='run app in public mode')
parser.add_argument('file', help='path to the billing data file')
args = parser.parse_args()
bills_file = args.file
public_mode = args.public

# Read file
bills = lib.read_processed_bills(bills_file)

# Compute names and options that are not defined in the section above
# dynamically
list_cz = [str(cz)
           for cz in np.sort(bills[('cis', 'cz')].unique().astype(int))]

# Initiate dash
app = dash.Dash()
# app = dash.Dash('auth')
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )


# Define app panel components

# Define header
header = html.Div([html.Img(src=banner_link,
                            className='four columns',
                            style={'height': '60',
                                   'width': '200',
                                   'float': 'left',
                                   'position': 'relative'}),
                   html.H1('Whole Building Consumption Browser',
                           className='eight columns',
                           style={'text-align': 'right',
                                  'float': 'right',
                                  'position': 'relative'})],
                  className='row')
# Define filter components
filter_types = dcc.Dropdown(id='filter_types',
                            options=lib.to_options(list_types),
                            value='Office building',
                            multi=True)
filter_cz = dcc.Checklist(id='filter_cz',
                          options=lib.to_options(list_cz),
                          values=list_cz,
                          labelStyle={'display': 'inline-block'})
filter_iou = dcc.Checklist(id='filter_iou',
                           options=lib.to_options(dict_iou),
                           values=list(dict_iou.keys()),
                           labelStyle={'display': 'inline-block'})
filter_fuel = dcc.RadioItems(id='filter_fuel',
                             options=lib.to_options(dict_fuel1),
                             value='both',
                             labelStyle={'display': 'inline-block'})
filter_value = dcc.RangeSlider(id='filter_value',
                               min=0, max=1000, step=0.1,
                               marks={i: str(i)
                                      for i in range(0, 1000) if i % 100 == 0},
                               value=[0, 1000])
filter_year = dcc.RangeSlider(id='filter_year',
                              min=2009, max=2015,
                              marks={i: str(i) for i in range(2009, 2016)},
                              value=[2009, 2015])
filter_area = dcc.RangeSlider(id='filter_area',
                              min=0, max=1000, step=0.1,
                              marks={i: str(i)
                                     for i in range(0, 1000) if i % 100 == 0},
                              value=[0, 1000])

# Define radio botton for color in map
colorby = dcc.RadioItems(id='colorby',
                         options=lib.to_options(list_colorby),
                         value='Consumption',
                         labelStyle={'display': 'inline-block'})

# Define dropdown menu for metric
metric_unit = dcc.Dropdown(id='metric_unit',
                           options=lib.to_options(dict_unit),
                           value='EUI')
metric_fuel = dcc.Dropdown(id='metric_fuel',
                           options=lib.to_options(dict_fuel2),
                           value='tot')
metric_stat = dcc.Dropdown(id='metric_stat',
                           options=lib.to_options(dict_stat),
                           value='avg')

# Define html subcomponents
html_topleft = html.Div([html.H4('Filter buildings by:'),
                         html.Label('Select building type:'),
                         filter_types],
                        className='eight columns')
html_topright = html.Div([html.H4('Color buildings in map by:'),
                          colorby],
                         className='four columns')
html_lowerleft = html.Div([html.Div([html.Label('Select climate zone:'),
                                     html.Div([filter_cz],
                                              style={'margin-bottom': '10'}),
                                     html.Label('Select IOU:'),
                                     html.Div([filter_iou],
                                              style={'margin-bottom': '10'}),
                                     html.Label('Select fuel type:'),
                                     html.Div([filter_fuel],
                                              style={'margin-bottom': '0'})],
                                    className='three columns'),
                           html.Div([html.Label('Consumption range:'),
                                     html.Div([filter_value],
                                              style={'margin-bottom': '35'}),
                                     html.Label('Year built:'),
                                     html.Div([filter_year],
                                              style={'margin-bottom': '35'}),
                                     html.Label('Building area:'),
                                     html.Div([filter_area],
                                              style={'margin-bottom': '35'})],
                                    className='five columns')])
html_lowerright = html.Div([html.H4('Define consumption metric:'),
                            html.Label('Unit:'),
                            metric_unit,
                            html.Label('Fuel:'),
                            metric_fuel,
                            html.Label('Statistics:'),
                            metric_stat],
                           className='four columns')
html_map = html.Div([dcc.Graph(id='map',
                               style={'max-height': '400',
                                      'height': '40vh'})],
                    className='five columns')
html_boxplot = html.Div([dcc.Graph(id='boxplot',
                                   style={'max-height': '400',
                                          'height': '40vh'})],
                        className='seven columns')
html_bldg_info = html.Div([html.H4('Current building info:'),
                           html.Div(id='building_info')],
                          className='four columns')
html_fulltrace = html.Div([dcc.Graph(id='fulltrace',
                                     style={'max-height': '300',
                                            'height': '30vh'})],
                          className='eight columns')

# Define app layout
app.layout = html.Div([header,
                       html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
                       html.Div(html.H2('Step 1: Browse buildings'),
                                className='row',
                                style={'margin-bottom': '5'}),
                       html.Div([html_topleft,
                                 html_topright],
                                className='row',
                                style={'margin-bottom': '10'}),
                       html.Div([html_lowerleft,
                                 html_lowerright],
                                className='row',
                                style={'margin-bottom': '10'}),
                       html.Div([html_map,
                                 html_boxplot],
                                className='row',
                                style={'margin-bottom': '10'}),
                       html.Hr(style={'margin': '0', 'margin-bottom': '5'}),
                       html.Div(html.H2('Step 2: Examine individual building'),
                                className='row',
                                style={'margin-bottom': '5'}),
                       html.Div([html_bldg_info,
                                 html_fulltrace],
                                className='row',
                                style={'margin-bottom': '10'})],
                      style={'width': '85%',
                             'max-width': '1200',
                             'margin-left': 'auto',
                             'margin-right': 'auto',
                             'font-family': 'overpass',
                             'background-color': '#F3F3F3',
                             'padding': '40',
                             'padding-top': '20',
                             'padding-bottom': '20'})


#app.css.append_css({"external_url": css_link})
for css in css_links:
    app.css.append_css({"external_url": css})


@app.callback(Output('map', 'figure'),
              [Input('filter_iou', 'values')])
def update_map(tmp):
    return lib.plot_map(bills)


@app.callback(Output('building_info', 'children'),
              [Input('map', 'clickData')])
def update_building_info(clickData):
    # Get current building
    bldg = bills.iloc[lib.get_iloc(clickData)]
    # Define field of variables
    EUI_field = ('summary', 'EUI_tot_avg_2009_2015')
    trend_field = ('summary', 'EUI_tot_fit_2009_2015_slope')
    area_field = ('cis', 'building_area')
    address = (bldg['cis']['address'].title() + ', ' +
               bldg['cis']['city'].title() + ', CA ' + bldg['cis']['zip'])
    link_map = 'https://www.google.com/maps/place/' + address.replace(' ', '+')
    # Define text
    p = []
    p.append('**Address:**  [' + address + '](' + link_map + ')')
    p.append('**Building type:**  ' + bldg['cis']['building_type'])
    p.append('**Climate zone:**  ' + bldg['cis']['cz'])
    p.append('**6-year average annual EUI:**  {:.1f} kBTU/ft2'.format(bldg[EUI_field]))
    p.append('**Change in annual EUI over 6 years:**  {:.1f} kBTU/ft2/year'.format(bldg[trend_field]))
    p.append('**Floor area:**  {:,.0f} ft2'.format(bldg[area_field]))
    return [dcc.Markdown(item) for item in p]


@app.callback(Output('fulltrace', 'figure'),
              [Input('map', 'clickData')])
def update_fulltrace(clickData):
    return lib.plot_bldg_full_timetrace(bills.iloc[lib.get_iloc(clickData)])


@app.callback(Output('boxplot', 'figure'),
              [Input('filter_types', 'value'),
               Input('filter_cz', 'values'),
               Input('filter_iou', 'values'),
               Input('filter_fuel', 'value'),
               Input('filter_value', 'value'),
               Input('filter_year', 'value'),
               Input('filter_area', 'value'),
               Input('colorby', 'value'),
               Input('metric_unit', 'value'),
               Input('metric_fuel', 'value'),
               Input('metric_stat', 'value')])
def update_boxplot(tmp, tmp2, tmp3, tmp4, t5, t6, t7, t8, t9, t10, t11):
    by = 'cz'
    selection = '3'
    unit = 'EUI'
    stats = 'avg'
    fuel = ''
    if by == 'cz':
        order = list_types
    else:
        order = None
    if stats == 'fit':
        value_suffix = '_slope'
    else:
        value_suffix = ''
    by = 'cz'
    selection = '3'
    stats = 'avg'
    fuel = 'tot'

    value = 'EUI_' + fuel + '_' + stats + '_2009_2015' + value_suffix
    return lib.plot_box(bills,
                        by=by, selection=selection, value=value,
                        order=order)


if __name__ == '__main__':
    if public_mode:
        app.run_server(host='0.0.0.0')
    else:
        app.run_server()
    