# Anthony Ho <anthony.ho@energy.ca.gov>
# Last update 8/18/2017
"""
Python library for interactive webapp
"""

import numpy as np
import pandas as pd
import plotly.graph_objs as go
from collections import OrderedDict


mapbox_token = 'pk.eyJ1IjoiYW50aG9ueWhvIiwiYSI6ImNqNmgxYnhpMDA0ZWoyeXF3N3FldTNwdWIifQ.YX3qN_InNTLbg6twap6Kpg'


def to_options(iterables):
    if isinstance(iterables, list):
        return [{'label': item, 'value': item} for item in iterables]
    else:
        return [{'label': iterables[key], 'value': key} for key in iterables]


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
            xlabel = 'Change in annual EUI from 2009-2015\n(kBtu/ft2/year)'
        elif 'avg' in value:
            xlabel = 'Average annual EUI from 2009-2015 \n(kBtu/ft2)'

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
                       #height=400,
                       showlegend=False)

    return {'data': data, 'layout': layout}


def plot_map(df, by=None, color_dict=None):
    # Define text when hovering over data point
    EUI_field = ('summary', 'EUI_tot_avg_2009_2015')
    text = df['cis']['address'].str.title() + ', ' + df['cis']['city'].str.title()
    text = text + '<br>' + df['cis']['building_type']
    text = text + '<br>Climate zone ' + df['cis']['cz']
    text = text + df[EUI_field].apply('<br>Avg annual EUI = {:.1f} kBTU/ft2'.format)
    text = text + df['cis']['building_area'].apply('<br>Floor area = {:.0f} ft2'.format)
    # Plot
    data = go.Data([go.Scattermapbox(lat=df['cis']['Latitude'],
                                     lon=df['cis']['Longitude'],
                                     text=text,
                                     hoverinfo='text',
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
                       margin={'l': 20, 'r': 20, 't': 20, 'b': 20},
                       height=640)

    return {'data': data, 'layout': layout}
