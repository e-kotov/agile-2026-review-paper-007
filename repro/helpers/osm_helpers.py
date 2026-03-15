import numpy as np
import pandas as pd
from shapely import wkt


def dataframe_converter(df):
    for col in df.columns:
        if col in ['tags', 'members', 'nodes']:
            df[col] = df[col].apply(eval)  # convert lists as lists and dicts as dicts
        elif col in ['geom', 'proj_geom']:
            df[col] = df[col].apply(wkt.loads)  # convert string of shapes to shapely WKT
        else:
            continue
    return df


def string_converter(df):
    temp = df.astype(str)
    return temp.str.cat(sep=';')


def string_to_list(df):
    temp = df.str.split(';')
    temp = temp.apply(lambda row: [int(x) for x in row])  # convert to int
    temp = temp.apply(set).apply(list).astype(str)  # get unique values, convert to string
    temp = temp.apply(lambda row: row.replace(', ', ';'))  # convert to correct string
    temp = temp.apply(lambda row: row.replace('[', ''))  # remove brackets
    temp = temp.apply(lambda row: row.replace(']', ''))  # remove brackets
    return temp


def nodes_pairwise_from_string(row):
    """
    converts a string with node IDs (e.g. '3237285785;1860901093;1860901093;483667820;483667820;333740999')
    to a dataframe with one basic segment per row.
    :param row: pandas dataframe (1 rows x _ columns) that has the column 'node_id'
    :return: pandas dataframe (_ rows x 2 columns) 'osm_id1', 'osm_id2'
    """
    # explode node_id string
    dataframe = row.node_id.str.split(';').explode().reset_index()

    # merge dataframe with shifted self
    df_merged = pd.merge(dataframe, dataframe.shift(-1), how='left', left_index=True, right_index=True)

    # remove NaN
    df_merged.dropna(inplace=True)

    # keep only rows where both IDs are not same
    df_merged = df_merged[df_merged.node_id_x != df_merged.node_id_y]

    # rename columns and switch the order! (no direct going back allowed aka turned basic segments)
    df_merged.rename(columns={'node_id_x': 'osm_id2', 'node_id_y': 'osm_id1'}, inplace=True)

    # make sure, both columns are of type int
    df_merged['osm_id1'] = df_merged['osm_id1'].astype(np.int64)
    df_merged['osm_id2'] = df_merged['osm_id2'].astype(np.int64)

    return df_merged[['osm_id1', 'osm_id2']]
