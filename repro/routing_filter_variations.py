import random
import sys
import time
import multiprocessing as mp
import pdb
from helpers.feasibility_dijkstra import my_all_shortest_paths
from helpers.routing_helpers import add_parent_child_edges
from constants.categories import number_of_routes, length_bins
from helpers.multigraph_helpers import *

import config

random.seed(0)
MAXINT = sys.maxsize

_all = number_of_routes
cn = length_bins



def get_data_from_edge(graph, edge, weight):
    """
    Function retrieves data from a given edge in a graph.
    
    Args:
        graph: networkx.MultiGraph / the multigraph
        edge: a tuple(start_node, end_node) / an edge between 2 nodes
        weight: str / the optimization weight
        
    Returns: 
        final_data (dict): dictionary representing the edge data of the selected edge.
    """
    
    edge_data = graph[edge[0]][edge[1]]
    if len(edge_data) == 1:
        return edge_data[0]
    else:
        final_data = edge_data[0]
        for idx in edge_data:
            if edge_data[idx][weight] < final_data[weight]:
                final_data = edge_data[idx]
        return final_data


def sum_time_length_labels(datas):
    """
    Function calculating the total time and length from a list of edge data
    
    Args: 
        datas: a list of dictionaries (containing edge attributes)
    Returns:
        _time (float): total time (sum of all 'time' attributes).
        _length (float): total length (sum of all 'length' attributes).
        osm_ids (list): list of OSM ids ('osm_ids' attribute) for the edges.
        modes (list): list of transportation modes ('label' attribute) for the edges.
        lengths (list): list of individual lengths ('length' attribute) for each edge.
        times (list):list of individual times ('time' attribute) for each edge.
    """
    _time = 0
    _length = 0
    osm_ids = []
    modes = []
    lengths = []
    times = []
    for i in datas:
        osm_ids.append(str(i['osm_ids']))
        modes.append(str(i['label']))
        lengths.append(str(i['length']))
        times.append(str(i['time']))
        _length += i['length']
        _time += i['time']
    return _time, _length,osm_ids,modes,lengths,times


def get_shortest_path(graph, _from, _to, _weight, filters_within=False):
    """
    Calculation of the shortest path between 2 nodes in a Multigraph based on a speicied weight
    
    Args:
        graph:  networkx.MultiGraph / the multigraph
        _from: the starting node 
        _to: the ending node 
        _weight: the cost function for the routing algorithm
        filters_within: (bool, optional) . If True a custom path generator (my_all_shortest_paths) is used, allowing for filtering conditions during the shortest path search. If False, the standard networkx.all_shortest_paths is used.
    
    Returns:
        all_datas(list of list): list of paths, where each path is represented as a list of edge data dictionaries.
    
    """
    try:
        if filters_within:
            # filter conditions included in the shortest path computation
            sp_generator = my_all_shortest_paths(graph, _from, _to, weight=_weight)
        else:
            # networkx all shortest paths
            sp_generator = nx.all_shortest_paths(graph, _from, _to, weight=_weight)
        all_datas = []
        
        # Convert the generator to a list to work with it more easily
        all_paths = list(sp_generator)

        # If weight is 'length', limit the paths to 2
        if _weight == 'length':
            all_paths = all_paths[:2] 
        
        for sp in all_paths: 
            pathGraph = nx.path_graph(sp)
            arr = pathGraph.edges
            datas = []
            for i in arr:
                data = get_data_from_edge(graph, i, _weight)
                if data is None:
                    print(i, 'wtf?')
                    continue
                datas.append(data)
            all_datas.append(datas)
        return all_datas
    except:
        return None


def shortest_path_computation(ODs, graph_path, graph, weights, out_path):
    """
    Computes the shortest paths for multiple origin-destination pairs using a multi-modal transportation network graph.
    
    Args: 
        ODs(pandas.DataFrame): DataFrame containing a chunk of origin-destination pairs(each row represents an OD pair)
        graph_path: (str) path to folder containing graph
        graph: (str) name of graph to be loaded
        weights: (list of str) list of weights to be used in shortest path computation
        out_path: (str) path to folder for output files
    """
    G = from_p_file(os.path.abspath(os.path.join(graph_path, graph)))
    start_end_nodes = ODs[['route_nr', 'start_id', 'end_id', 'lower', 'upper']]
    
    res = dict([(w, array_to_dict(cn)) for w in weights])
    # filter_in_dijkstra = True  # set to True if filter conditions should be included in the shortest path computation
    # if the scenario run is results_nofilters do not include filters
    if os.path.basename(out_path) != 'nofilters':
        filter_in_dijkstra = True  # set to True if filter conditions should be included in the shortest path computation
    else :
        print('Feasibility filters do not apply')
        filter_in_dijkstra = False
        
    for number, nodes in start_end_nodes.iterrows():
        route_nr, osm_id1, osm_id2, lower, upper = nodes

        # add "parent" node, connect it to all modes available at starting node
        G, osm_id1 = add_parent_child_edges(G, osm_id1, 'parent')
        G, osm_id2 = add_parent_child_edges(G, osm_id2, 'child')

        # shortest paths with different weights
        for weight in weights:
            # length category as string
            cat = str(lower) + '-' + str(upper)

            # get list of all shortest paths
            data_all_paths = get_shortest_path(G, osm_id1, osm_id2, weight, filter_in_dijkstra)

            # loop all routes, extract values and append result for correct weight and distance category
            try:
                for data_one_path in data_all_paths:
                    _time, _length, osm_ids, modes, lengths_list, times_list = \
                        sum_time_length_labels(data_one_path)

                    res = save_to_dict_separately(res, cat, weight, route_nr,
                                                  _length, _time, osm_ids, modes,
                                                  lengths_list, times_list)
            except TypeError:
                print(route_nr, osm_id1, osm_id2, lower, upper)
                continue

            df = pd.DataFrame(res[weight][cat])

            # save
            filepath = os.path.join(out_path, f"{weight}_{cat}.csv")
            
            if not os.path.exists(filepath):
                df.to_csv(filepath, index=False)
            else:
                df.to_csv(filepath, index=False, mode='a', header=False)
            res[weight][cat] = []

        # remove parent and child node from multi-graph
        G.remove_node(osm_id1)
        G.remove_node(osm_id2)


if __name__ == "__main__":

    modes = '_walk_bike_PT'  # empty (all modes), _walk_bike_PT, _walk_car_PT or _walk_PT
    scenario = 'transitions'  
    
    graph_name = 'MultiGraph' + modes
    od_pairs_folder = '06_OD_pairs'

    weights= ['time']

    # set the path to folder one above current working directory
    fullpath = os.path.join(os.getcwd(), '..')

    # data folder for CITYNAME specified in config.json
    path_city = os.path.abspath(os.path.join(fullpath, 'results' , config.CITYNAME))
    
    # path to data folders
    graph_folder = os.path.abspath(os.path.join(path_city,'..','..','data','05_graph'))
    od_pairs_folder = os.path.abspath(os.path.join(path_city,'..','..','data', od_pairs_folder))

# INDIVIDUAL PARAMETER RUNS 
    parameter_sets = {   
        "feasibility_filter_bike": [3750, 2500, 1250],
        "feasibility_filter_walk": [1125, 750, 375],
        "feasibility_filter_transitions": [6, 4, 2]}
    
    original_values = {"feasibility_filter_bike": config.feasibility_filter_bike,
    "feasibility_filter_walk": config.feasibility_filter_walk,
    "feasibility_filter_transitions": config.feasibility_filter_transitions}
    
    
    for param_name, values in parameter_sets.items():
        for value in values:
            print(f"\n=== Running with {param_name} = {value} ===")
            
            for k, v in original_values.items():
                setattr(config, k, v)

            # dynamically set the config parameter
            setattr(config, param_name, value)
            print(f"Bike filter: {config.feasibility_filter_bike}, Walk filter:{config.feasibility_filter_walk}, Trans filter: {config.feasibility_filter_transitions}")
            # create folder for results
            folder_name = f"{param_name}_{value}"
            results_folder = os.path.abspath(os.path.join(path_city, scenario, graph_name, folder_name))
            print(f"DEBUG: results_folder = {results_folder}")
            if not os.path.exists(results_folder):
                print(f"DEBUG: Attempting to makedirs: {results_folder}")
                os.makedirs(results_folder)

            start_time = time.time()

            # list with CSV files in OD pairs folder
            csv_files = [f for f in os.listdir(od_pairs_folder) if f.endswith('.csv')]
            num_chunks = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))
            for csv_file in csv_files:
                csv_file_path = os.path.join(od_pairs_folder, csv_file)
                print(f"Processing file: {csv_file}")

                ods = pd.read_csv(csv_file_path)
                n = int(len(ods) / num_chunks)
                source = [ods[i:i+n] for i in range(0, ods.shape[0], n)]

                pool = mp.Pool(processes=num_chunks)
                p1 = pool.starmap_async(
                    shortest_path_computation,
                    [(chunk, graph_folder, graph_name, weights, results_folder) for chunk in source]
                )
                p1.get()

            runtime = round((time.time() - start_time) / 60, 2)
            print(f" Run with {param_name} = {value} finished in {runtime} minutes")


# COMBINED SCENARIO RUNS 
    combined_scenarios = [
        {"feasibility_filter_transitions": 6, "feasibility_filter_walk": 1125, "feasibility_filter_bike": 3750},
        {"feasibility_filter_transitions": 4, "feasibility_filter_walk": 750,  "feasibility_filter_bike": 2500},
        {"feasibility_filter_transitions": 2, "feasibility_filter_walk": 375,  "feasibility_filter_bike": 1250},
    ]

    for combo in combined_scenarios:
        print(f"\n=== Running COMBINATION: transitions={combo['feasibility_filter_transitions']}, "
              f"walk={combo['feasibility_filter_walk']}, bike={combo['feasibility_filter_bike']} ===")

        # set all three config parameters
        for param_name, value in combo.items():
            setattr(config, param_name, value)
        
        print(f"Bike filter: {config.feasibility_filter_bike}, Walk filter:{config.feasibility_filter_walk}, Trans filter: {config.feasibility_filter_transitions}")

        folder_name = (f"combo_trans{combo['feasibility_filter_transitions']}_"
                       f"walk{combo['feasibility_filter_walk']}_bike{combo['feasibility_filter_bike']}")
        results_folder = os.path.abspath(os.path.join(path_city, scenario, graph_name, folder_name))
        os.makedirs(results_folder, exist_ok=True)

        start_time = time.time()
        csv_files = [f for f in os.listdir(od_pairs_folder) if f.endswith('.csv')]
        num_chunks = mp.cpu_count() - 8
        for csv_file in csv_files:
            csv_file_path = os.path.join(od_pairs_folder, csv_file)
            print(f"Processing file: {csv_file}")

            ods = pd.read_csv(csv_file_path)
            n = int(len(ods) / num_chunks)
            source = [ods[i:i+n] for i in range(0, ods.shape[0], n)]

            pool = mp.Pool(processes=num_chunks)
            p1 = pool.starmap_async(
                shortest_path_computation,
                [(chunk, graph_folder, graph_name, weights, results_folder) for chunk in source]
            )
            p1.get()

        runtime = round((time.time() - start_time) / 60, 2)
        print(f" Combined run finished in {runtime} minutes")

print("\n All runs (individual and combined) finished successfully.")