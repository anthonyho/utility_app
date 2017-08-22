# Anthony Ho <anthony.ho@energy.ca.gov>
# Last update 8/21/2017
"""
Python library for interactive webapp
"""

import numpy as np
from scipy import stats
import pandas as pd
import plotly.graph_objs as go
import seaborn as sns


# Define mapbox token
mapbox_token = 'pk.eyJ1IjoiYW50aG9ueWhvIiwiYSI6ImNqNmgxYnhpMDA0ZWoyeXF3N3FldTNwdWIifQ.YX3qN_InNTLbg6twap6Kpg'

# Set default translation dictionary for abbr
terms = {'elec': 'electric',
         'gas': 'gas',
         'tot': 'total'}

# Define default colors for plotly
list_colors = sns.color_palette('Paired', 12)
list_colors_rgb = []
for color in list_colors:
    color_rgb = 'rgb('
    color_rgb += str(color[0] * 255) + ','
    color_rgb += str(color[1] * 255) + ','
    color_rgb += str(color[2] * 255) + ')'
    list_colors_rgb.append(color_rgb)


def to_options(iterables):
    if isinstance(iterables, list):
        return [{'label': item, 'value': item} for item in iterables]
    else:
        return [{'label': iterables[key], 'value': key} for key in iterables]


def get_iloc(clickData):
    return clickData['points'][0]['customdata']


def name_iou(all_iou):
    mapping = {'pge': 'PG&E',
               'sce': 'SCE',
               'scg': 'SCG',
               'sdge': 'SDG&E'}
    return ', '.join([mapping[iou] for iou in all_iou.split(',')])


def read_processed_bills(file, multi_index=True, dtype=None):
    """Function to read processed bills after merging and transformation. Same
    as utilib.read.read_processed_bills()"""
    if multi_index:
        header = [0, 1]
    else:
        header = None

    # Define dtypes for all possible (level 0) columns
    dtype = {'cis': str,
             'kWh': np.float64,
             'kWhOn': np.float64,
             'kWhSemi': np.float64,
             'kWhOff': np.float64,
             'kW': np.float64,
             'kWOn': np.float64,
             'kWSemi': np.float64,
             'billAmnt': np.float64,
             'Therms': np.float64,
             'EUI_elec': np.float64,
             'EUI_gas': np.float64,
             'EUI_tot': np.float64,
             'EUI_tot_mo_avg_2009_2015': np.float64,
             'EUI_tot_mo_avg_2013_2015': np.float64,
             'EUI_elec_mo_avg_2009_2015': np.float64,
             'EUI_elec_mo_avg_2013_2015': np.float64,
             'EUI_gas_mo_avg_2009_2015': np.float64,
             'EUI_gas_mo_avg_2013_2015': np.float64,
             'summary': np.float64}
    # Define all possible (level 1) columns under cis to be converted to float
    col_to_float = ['Longitude', 'Latitude',
                    'year_built', 'year_renovated',
                    'Vacancy %', 'Number Of Stories',
                    'building_area', 'land_area']
    # Define all possible (level 1) columns under cis to be converted to
    # datetime
    col_to_time = ['date_transfer']
    # Define all possible (level 1) columns under cis to be converted to
    # boolean
    col_to_bool = ['range_address_ind']

    # Read file
    df = pd.read_csv(file, header=header, dtype=dtype)

    # Convert (level 1) columns to float
    for col in col_to_float:
        full_col = ('cis', col)
        if full_col in df:
            df.loc[:, full_col] = df.loc[:, full_col].astype(np.float64)
    # Convert (level 1) columns to datetime
    for col in col_to_time:
        full_col = ('cis', col)
        if full_col in df:
            df.loc[:, full_col] = pd.to_datetime(df.loc[:, full_col],
                                                 format='%Y-%m-%d')
    # Convert (level 1) columns to boolean
    for col in col_to_bool:
        full_col = ('cis', col)
        if full_col in df:
            df.loc[:, full_col] = df.loc[:, full_col].astype(bool)

    return df


def get_group(df, building_type=None, cz=None, other=None):
    """Function to extract group of specific building type and/or climate
    zone and/or other attributes. Same as utilib.plot.get_group()"""
    ind = pd.Series(True, index=df.index)
    if building_type is not None:
        if isinstance(building_type, str):
            building_type = [building_type]
        ind = ind & (df[('cis', 'building_type')].isin(building_type))
    if cz is not None:
        if np.issubdtype(type(cz), np.integer) or isinstance(cz, str):
            cz = [cz]
        cz = [str(item) for item in cz]
        ind = ind & (df[('cis', 'cz')].isin(cz))
    if other is not None:
        for key in other:
            if np.issubdtype(type(other[key]),
                             np.integer) or isinstance(other[key], str):
                value = [other[key]]
            else:
                value = other[key]
            value = [str(item) for item in value]
            ind = ind & df[key].isin(value)
    return df[ind]


def filter_bldg(df, types_tf, cz_tf, iou_tf, fuel=None,
                consumption_range=None, value=None, year_range=None, area_range=None):
    # Make sure types_tf is a list since multi dropmenu could result in str
    if not isinstance(types_tf, list):
        list_types_tf = list(types_tf)
    else:
        list_types_tf = types_tf
    # Filter by building types and cz
    index = (df['cis']['building_type'].isin(list_types_tf) &
             df['cis']['cz'].isin(cz_tf))
    # Filter by iou
    index_iou = pd.Series([False] * len(index))
    for iou in iou_tf:
        index_iou = index_iou | (df['cis']['iou'].str.contains(iou))
    index = index & index_iou
    # Filter by fuel type
    
    return df[index]


def plot_box(df, by, selection, value,
             min_sample_size=5, order=None, xlabel=None):
    """Plot boxplot of value for a particular climate zone or building type"""
    # Extract rows from the specified building types and climate zones
    group = get_group(df, other={('cis', by): selection})
    # Extract relevant rows and columns
    df_pf = group.loc[:, [('cis', 'cz'),
                          ('cis', 'building_type'),
                          ('summary', value)]]
    # Process df for next steps
    df_pf.columns = df_pf.columns.droplevel()
    df_pf = df_pf.dropna()
    df_pf['cz'] = df_pf['cz'].astype(int)

    # Define variable and labels
    if by == 'cz':
        y = 'building_type'
        color = 'rgb(8, 81, 156)'
    elif by == 'building_type':
        y = 'cz'
        color = '#FF851B'

    # Identify building types/climate zones with minimum sample size
    sample_size = df_pf.groupby(y).size()
    ind_pf = sample_size[sample_size > min_sample_size].index
    # Select building types/climate zones with minimum sample size
    df_pf = df_pf[df_pf[y].isin(ind_pf)]

    # Order
    if order is None:
        ind_pf = ind_pf.sort_values()
    else:
        ind_pf = [item for item in order if item in ind_pf]

    # Define label
    if xlabel is None:
        if 'fit' in value:
            xlabel = 'Change in annual EUI from 2009-2015\n(kBtu/ft²/year)'
        elif 'avg' in value:
            xlabel = 'Average annual EUI from 2009-2015 \n(kBtu/ft²)'

    # Plot
    data = []
    for item in reversed(ind_pf):
        item_values = df_pf[df_pf[y] == item][value]
        if by == 'cz':
            name = item
        elif by == 'building_type':
            name = 'CZ ' + str(item)
        curr_box = go.Box(x=item_values,
                          name=name,
                          marker={'color': color})
        data.append(curr_box)
    data = go.Data(data)
    # Set layout
    layout = go.Layout(xaxis={'title': xlabel},
                       margin={'l': 200, 'r': 20, 't': 20, 'b': 40},
                       showlegend=False,
                       paper_bgcolor='#F3F3F3')

    return {'data': data, 'layout': layout}


def plot_bldg_full_timetrace(df, i, fuel='all'):
    # Parse building info
    building = df.iloc[i]
    # Define fuel types
    if isinstance(fuel, list):
        list_fuel = fuel
    elif fuel == 'all':
        list_fuel = ['tot', 'gas', 'elec']
    else:
        list_fuel = [fuel]
    # Plot
    data = []
    for fuel in list_fuel:
        # Define colors
        if fuel == 'tot':
            color_i = 2
        elif fuel == 'elec':
            color_i = 4
        elif fuel == 'gas':
            color_i = 0
        # Extract data
        field = 'EUI_' + fuel
        trace = building[field]
        yr_mo = pd.to_datetime(trace.index)
        curr_trace = go.Scatter(x=yr_mo,
                                y=trace,
                                mode='lines',
                                line=dict(color=list_colors_rgb[color_i + 1],
                                          width=4),
                                name=terms[fuel].title())
        data.append(curr_trace)
    data = go.Data(data)
    # Set layout
    layout = go.Layout(xaxis={'title': 'Year'},
                       yaxis={'title': 'Monthly EUI (kBtu/ft²)'},
                       margin={'l': 45, 'r': 0, 't': 0, 'b': 40},
                       showlegend=True,
                       paper_bgcolor='#F3F3F3')
    return {'data': data, 'layout': layout}


def plot_bldg_avg_monthly(df, i, fuel='all', year_range=None):
    """Plot the average monthly EUI of a building by specified fuel types"""
    # Parse building info
    building = df.iloc[i]
    # Define fuel types
    if isinstance(fuel, list):
        list_fuel = fuel
    elif fuel == 'all':
        list_fuel = ['tot', 'gas', 'elec']
    else:
        list_fuel = [fuel]
    # Plot
    data = []
    for fuel in list_fuel:
        # Define colors
        min_alpha = 0.15
        if fuel == 'tot':
            color_i = 2
        elif fuel == 'elec':
            color_i = 4
        elif fuel == 'gas':
            color_i = 0
        # Extract yearly trace of the building and transform to multi-index df
        field = 'EUI_' + fuel
        bldg_all_trace = building[field].copy()
        list_yr_mo = [tuple(yr_mo.split('-'))
                      for yr_mo in bldg_all_trace.index]
        bldg_all_trace.index = pd.MultiIndex.from_tuples(list_yr_mo)
        # Extract the average monthly trace of the building
        if year_range:
            start_year = int(year_range[0])
            end_year = int(year_range[1])
            list_year = [str(year) for year in range(start_year, end_year + 1)]
            field_prefix = str(start_year) + '_' + str(end_year)
            field_avg_mo = field + '_mo_avg_' + field_prefix
        else:
            field_avg_mo = field + '_mo_avg'
        bldg_mean_trace = building[field_avg_mo]
        months = [int(mo) for mo in bldg_mean_trace.index]
        # Plot
        for i, year in enumerate(list_year):
            curr_yr_trace = bldg_all_trace[year]
            alpha = (1 - min_alpha) / len(list_year) * i + min_alpha
            data.append(go.Scatter(x=months,
                                   y=curr_yr_trace,
                                   mode='lines',
                                   line={'color': list_colors_rgb[color_i],
                                         'width': 2},
                                   opacity=alpha,
                                   showlegend=False))
        data.append(go.Scatter(x=months,
                               y=bldg_mean_trace,
                               mode='lines',
                               line={'color': list_colors_rgb[color_i + 1],
                                     'width': 4},
                               name=terms[fuel].title(),
                               showlegend=True))
    data = go.Data(data)
    # Set layout
    layout = go.Layout(xaxis={'title': 'Month',
                              'autotick': False,
                              'dtick': 1},
                       yaxis={'title': 'Average monthly EUI (kBtu/ft²)'},
                       margin={'l': 45, 'r': 0, 't': 0, 'b': 40},
                       paper_bgcolor='#F3F3F3')
    return {'data': data, 'layout': layout}


def _vertline(x_value, color):
    return {'type': 'line',
            'xref': 'x', 'yref': 'paper',
            'x0': x_value, 'x1': x_value,
            'y0': 0, 'y1': 1,
            'line': {'color': color, 'width': 2}}


def _annot(x_value, text, sign):
    return {'x': x_value, 'y': 1,
            'xref': 'x', 'yref': 'paper',
            'text': text,
            'ax': sign * 30, 'ay': -20}


def plot_bldg_hist(df, i, value):
    """Plot histogram of value with line indicating the value of current
    building"""
    # Parse building info
    building = df.iloc[i]
    building_type = building[('cis', 'building_type')]
    cz = str(building[('cis', 'cz')])
    # Extract rows from the specified building types and climate zones
    group = get_group(df, building_type=building_type, cz=cz)
    # Get values
    building_eui = building[value]
    group_eui = group[value]
    group_eui = group_eui[group_eui.notnull()]
    group_eui_mean = group_eui.mean()
    percentile = stats.percentileofscore(group_eui, building_eui)
    # Define xlabel and title
    if 'fit' in value[1]:
        xlabel = 'Change in annual EUI from 2009-2015<br>(kBtu/ft²/year)'
        xlim = None
    elif 'avg' in value[1]:
        xlabel = 'Average annual EUI from 2009-2015<br>(kBtu/ft²)'
        xlim = [0, group_eui.max()]
    # Plot
    data = go.Data([go.Histogram(x=group_eui,
                                 marker={'color': 'rgb(52,152,219)'},
                                 opacity=0.75)])
    # Set layout
    sign = int(building_eui < group_eui_mean) * 2 - 1
    layout = go.Layout(shapes=[_vertline(group_eui_mean, 'rgb(0,0,0)'),
                               _vertline(building_eui, list_colors_rgb[5])],
                       annotations=[_annot(group_eui_mean, 'group mean', sign),
                                    _annot(building_eui,
                                           '{:.1f}%'.format(percentile),
                                           -sign)],
                       xaxis={'title': xlabel,
                              'range': xlim},
                       yaxis={'title': 'Counts'},
                       margin={'l': 50, 'r': 0, 't': 40, 'b': 60},
                       showlegend=False,
                       paper_bgcolor='#F3F3F3')
    return {'data': data, 'layout': layout}


def plot_map(df):
    # Define text when hovering over data point
    EUI_field = ('summary', 'EUI_tot_avg_2009_2015')
    text = df['cis']['address'].str.title() + ', ' + df['cis']['city'].str.title()
    text = text + '<br>' + df['cis']['building_type']
    text = text + '<br>Climate zone ' + df['cis']['cz']
    text = text + df[EUI_field].apply('<br>Avg annual EUI = {:.1f} kBtu/ft²'.format)
    text = text + df['cis']['building_area'].apply('<br>Building area = {:,.0f} ft²'.format)

    # Plot
    data = go.Data([go.Scattermapbox(lat=df['cis']['Latitude'],
                                     lon=df['cis']['Longitude'],
                                     text=text,
                                     hoverinfo='text',
                                     customdata=list(df.index),
                                     mode='markers',
                                     marker=go.Marker(size=6,
                                                      color='rgb(255, 0, 0)',
                                                      opacity=0.6))])
            
    # Set layout
    layout = go.Layout(autosize=True,
                       hovermode='closest',
                       showlegend=False,
                       mapbox=dict(accesstoken=mapbox_token,
                                   bearing=0,
                                   center={'lat': 37.25, 'lon': -120},
                                   pitch=0,
                                   zoom=5.05,
                                   style='streets'),
                       margin={'l': 0, 'r': 0, 't': 0, 'b': 0})

    return {'data': data, 'layout': layout}
