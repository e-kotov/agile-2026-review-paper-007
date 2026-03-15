import os
import pickle
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from shapely import from_wkt

from constants.speeds import car_speed_default, car_speed_multiplier
from constants.transition_costs import *
from constants.categories import length_bins
from constants.feasibility_filters import *


def to_p_file(graph, name):
    pickle.dump(graph, open(f'{name}.p', "wb"))
    return True


def from_p_file(name):
    g = pickle.load(open(f'{name}.p', "rb"))
    return g


def save_plt(graph, name):
    nx.draw(graph)
    plt.savefig(name)


def show_plt(graph):
    nx.draw(graph)
    plt.show()


def get_commons(arr1, arr2):
    common_list = list(set(arr1).intersection(set(arr2)))
    return common_list


def get_namespace(namespace, return_inverted=False):
    namespaces = {'walk': '000000',
                  'car': '990099',
                  'car_twoway': '990099',
                  'bike': '880088',
                  'bus': '770077',
                  'bus_day': '770077',
                  'bus_night': '770077',
                  'tram': '660066',
                  'subway': '550055',
                  'train': '440044',
                  'child': '220022',
                  'parent': '110011'}

    namespaces_inverted = {'000000': 'walk',
                           '990099': 'car',
                           '880088': 'bike',
                           '770077': 'bus',
                           '660066': 'tram',
                           '550055': 'subway',
                           '440044': 'train',
                           '220022': 'child',
                           '110011': 'parent'}

    if namespace in namespaces.keys():
        return namespaces[namespace]
    elif namespace in namespaces.values():
        if return_inverted:
            return namespaces_inverted[namespace]
        else:
            return namespace
    else:
        raise KeyError(f'OSM namespace {namespace} not available in namespaces')


def generate_node_id(osm_id, mode, postfix=None):
    # node ID format: (6 digit namespace)_osm-id_(4 digit postfix)
    namespace_id = get_namespace(mode)

    if postfix is None:
        return '_'.join([namespace_id, str(check_type(osm_id, (int, str)))])
    else:
        return '_'.join([namespace_id, str(check_type(osm_id, (int, str))), str(check_type(postfix, (int, str)))])

def extract_node_id(node_id, mode=list):
    if mode == list:
        return node_id.split('_')
    elif mode == dict:
        vals = node_id.split('_')
        if len(vals) == 2:
            return {'namespace': vals[0], 'osm_id': vals[1]}
        elif len(vals) == 3:
            return {'namespace': vals[0], 'osm_id': vals[1], 'bus_id': vals[2]}


def wkt_to_geom(geom, type=str):
    geom_ = from_wkt(check_type(geom, type), on_invalid='warn')
    if geom_ is None:
        print(f'Warning! Converted geometry {geom} could not be converted to shapely Object.')
        return None
    else:
        return geom_


def check_type(var, ctypes):
    """
    check the type of variable and return it if True
    type: type, or tuple of types
    else raise an error
    """
    if isinstance(var, ctypes):
        return var
    else:
        raise TypeError(f'Only {ctypes} allowed for object {var}')


def compute_transition_costs(from_mode, to_mode):
    if from_mode in ['car', 'car_twoway']:
        # cost needed to find parking space
        transition_time = car_parking_time
        transition_length = car_speed_default * car_speed_multiplier * transition_time * (1000 / 60)  # from km/h to m/min
    elif to_mode in ['car', 'car_twoway']:
        # cost needed to reach the parked car
        transition_time = car_reach_time
        transition_length = car_reach_length
    elif to_mode in ['bike']:
        # cost needed to reach the parked bike
        transition_time = bike_reach_length
        transition_length = bike_reach_length
    elif to_mode in ['bus', 'bus_day', 'bus_night']:
        # waiting for bus
        transition_time = bus_waiting_time
        transition_length = 0
    elif to_mode == 'tram':
        # waiting for tram
        transition_time = tram_waiting_time
        transition_length = 0
    elif to_mode == 'subway':
        # waiting for subway
        transition_time = subway_waiting_time
        transition_length = 0
    elif to_mode == 'train':
        # waiting for train
        transition_time = train_waiting_time
        transition_length = 0
    else:
        # if no case applies, no transition costs
        transition_length, transition_time = 0, 0
    return transition_length, transition_time


def to_csv(res, pt):
    for i in res:
        df = pd.DataFrame(res[i])
        df.to_csv(pt + str(i) + '.csv', index=False)


def to_csv_individual(res, pt):
    for key in res.keys():
        for i in res[key]:
            df = pd.DataFrame(res[key][i])
            df.to_csv(pt + str(key) + '_' + str(i) + '.csv', index=False)


def array_to_dict(arr):
    res = {}
    for i in arr:
        res[str(i[0]) + '-' + str(i[1])] = []
    return res


def save_to_dict_separately(res, category, weight, route_number, sum_length, sum_time,
                            osm_ids, modes, lengths, times):
    """
    Stores route data (including OSM IDs, modes, lengths, and times) in a dictionary under a specific weight category

    Args:
    res (dict): dictionary where results are stored
    category (str): string representing the length category (e.g., 'lower-upper')
    weight (str): weight attribute (e.g., 'time') for which the data is stored
    route_number (int): identifier of the current route
    sum_length (float): total length of the route
    sum_time (float): total time of the route
    osm_ids (list): A list of OSM IDs for the route's edges
    modes (list): list of transportation modes for the route's edges
    lengths (list): list of individual lengths for each edge
    times (list): list of individual times for each edge

    Returns:
        res (dict): The updated dictionary with the route data
    """
    tmp = {
        'route_nr': route_number,
        'osm_ids_for_' + str(weight): ';'.join(osm_ids),
        'modes_for_' + str(weight): ';'.join(modes),
        'lengths_for_' + str(weight): ';'.join(lengths),
        'times_for_' + str(weight): ';'.join(times),
        'sum_length_for_' + str(weight): sum_length,
        'sum_time_for_' + str(weight): sum_time,
    }
    res[weight][category].append(tmp)
    return res


def merge_and_filter(path, weights):
    # kicked_out_path = os.path.join(path, "kicked_out_routes")
    # os.makedirs(kicked_out_path, exist_ok=True)

    for weight in weights:
        for category in length_bins:
            cat = str(category[0]) + '-' + str(category[1])
            pt_out = os.path.join(path, f"{weight}_{cat}.csv")

            # Check if files of this length category exist
            files = os.listdir(path)
            if cat not in str(files):
                continue

            # Read routing data
            data = pd.read_csv(pt_out)

            # Sort data
            merged_data = data.sort_values(by='route_nr')
            merged_data.reset_index(inplace=True, drop=True)

            # Filter merged routes by mode sequences
            filtered_data = filter_by_modes(merged_data, weight)

            # Filter routes by allowed thresholds and store back to file
            data_ok, data_not_ok, not_ok_info = filter_by_conditions(filtered_data, weight)

            # Save accepted routes back to the original file
            data_ok.to_csv(pt_out, index=False)

            # Save failed routes and information
            if not data_not_ok.empty:
                # Save failed routes
                # failed_routes_file = os.path.join(kicked_out_path, f"{weight}_{cat}_kicked_out.csv")
                # data_not_ok.to_csv(failed_routes_file, index=False)

                # Save reasons for failure
                # reasons_file = os.path.join(kicked_out_path, f"{weight}_{cat}_failure_info.csv")
                # pd.DataFrame(not_ok_info).to_csv(reasons_file, index=False)
                print("Check Filtering")


def filter_by_conditions(data, weight):
    ix_ok = []
    ix_not_ok = []
    not_ok_info = []  # To store information about failed criteria

    for ind, r in data.iterrows():
        temp = pd.DataFrame()
        for col in data.columns:
            temp[col] = [split_by_semicolon(r[col])]
        walk_lengths, bike_lengths, car_lengths, transition_count = [], [], [], 0
        for ix, mode in enumerate(temp[f"modes_for_{weight}"][0]):
            if mode == "walk":
                walk_lengths.append(temp[f"lengths_for_{weight}"][0][ix])
            elif mode == "bike":
                bike_lengths.append(temp[f"lengths_for_{weight}"][0][ix])
            elif mode == "car":
                car_lengths.append(temp[f"lengths_for_{weight}"][0][ix])
            elif mode == "transition":
                transition_count += 1

        # Check
        walk_diff = sum(walk_lengths) - feasibility_filter_walk
        bike_diff = sum(bike_lengths) - feasibility_filter_bike
        transition_diff = transition_count - feasibility_filter_transitions
        # if transition_diff > 0 :
            # print(transition_diff)
        car_diff = feasibility_filter_car - sum(car_lengths) if len(car_lengths) > 0 else None

        # track failed criteria
        failed_criteria = {}
        if walk_diff > 0:
            failed_criteria["walk"] = walk_diff
        if bike_diff > 0:
            failed_criteria["bike"] = bike_diff
        if transition_diff > 0:
            failed_criteria["transitions"] = transition_diff
        if car_diff is not None and car_diff > 0:
            failed_criteria["car"] = car_diff

        if not failed_criteria:  # all criteria satisfied
            ix_ok.append(ind)
        else:
            ix_not_ok.append(ind)
            not_ok_info.append(
                {
                    "route_nr": r["route_nr"],
                    **failed_criteria,  #  all failed criteria with their differences
                }
            )

    data_ok = data[data.index.isin(ix_ok)]
    data_ok.reset_index(inplace=True, drop=True)

    data_not_ok = data[data.index.isin(ix_not_ok)]
    data_not_ok.reset_index(inplace=True, drop=True)

    return data_ok, data_not_ok, not_ok_info


def filter_by_modes(data, w):
    # kick out routes that include unrealistic mode sequences (due to the specific structure of the multi-graph)
    indices = []
    for r_id in data.route_nr.unique():
        data_r = data[data.route_nr == r_id]
        for ind, p in data_r.iterrows():
            if 'parent;fake' in p['modes_for_' + w] \
                    or 'fake;parent' in p['modes_for_' + w]:

                indices.append(ind)
    data_filtered = data[~data.index.isin(indices)]

    # drop possible duplicates
    data_out = data_filtered.drop_duplicates()
    data_out.reset_index(inplace=True, drop=True)
    return data_out


def split_by_semicolon(string):
    try:
        splitted = string.split(';')
        try:
            splitted_float = [float(x) for x in splitted]
            return splitted_float
        except ValueError:
            return splitted
    except AttributeError:
        return string

    
    
    
    
