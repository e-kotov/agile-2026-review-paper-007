import random
import sys
import time
import multiprocessing as mp
import pdb
import os
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
    _time, _length = 0, 0
    osm_ids, modes, lengths, times = [], [], [], []
    for i in datas:
        osm_ids.append(str(i['osm_ids']))
        modes.append(str(i['label']))
        lengths.append(str(i['length']))
        times.append(str(i['time']))
        _length += i['length']
        _time += i['time']
    return _time, _length, osm_ids, modes, lengths, times

def get_shortest_path(graph, _from, _to, _weight, filters_within=False):
    try:
        if filters_within:
            sp_generator = my_all_shortest_paths(graph, _from, _to, weight=_weight)
        else:
            sp_generator = nx.all_shortest_paths(graph, _from, _to, weight=_weight)
        all_datas = []
        all_paths = list(sp_generator)
        if _weight == 'length':
            all_paths = all_paths[:2] 
        for sp in all_paths: 
            pathGraph = nx.path_graph(sp)
            arr = pathGraph.edges
            datas = []
            for i in arr:
                data = get_data_from_edge(graph, i, _weight)
                if data is None: continue
                datas.append(data)
            all_datas.append(datas)
        return all_datas
    except:
        return None

def shortest_path_computation(ODs, graph_path, graph, weights, out_path):
    G = from_p_file(os.path.abspath(os.path.join(graph_path, graph)))
    start_end_nodes = ODs[['route_nr', 'start_id', 'end_id', 'lower', 'upper']]
    res = dict([(w, array_to_dict(cn)) for w in weights])
    filter_in_dijkstra = (os.path.basename(out_path) != 'nofilters')
    for number, nodes in start_end_nodes.iterrows():
        route_nr, osm_id1, osm_id2, lower, upper = nodes
        G, osm_id1 = add_parent_child_edges(G, osm_id1, 'parent')
        G, osm_id2 = add_parent_child_edges(G, osm_id2, 'child')
        for weight in weights:
            cat = str(lower) + '-' + str(upper)
            data_all_paths = get_shortest_path(G, osm_id1, osm_id2, weight, filter_in_dijkstra)
            try:
                for data_one_path in data_all_paths:
                    _time, _length, osm_ids, modes, lengths_list, times_list = sum_time_length_labels(data_one_path)
                    res = save_to_dict_separately(res, cat, weight, route_nr, _length, _time, osm_ids, modes, lengths_list, times_list)
            except TypeError: continue
            df = pd.DataFrame(res[weight][cat])
            filepath = os.path.join(out_path, f"{weight}_{cat}.csv")
            if not os.path.exists(filepath):
                df.to_csv(filepath, index=False)
            else:
                df.to_csv(filepath, index=False, mode='a', header=False)
            res[weight][cat] = []
        G.remove_node(osm_id1)
        G.remove_node(osm_id2)

if __name__ == "__main__":
    modes = '_walk_bike_PT'
    scenario = 'transitions'  
    graph_name = 'MultiGraph' + modes
    od_pairs_folder = '06_OD_pairs'
    weights = ['time']
    num_chunks = int(os.environ.get("SLURM_CPUS_PER_TASK", 1))

    fullpath = os.path.abspath('..')
    # USE INDEPENDENT OUTPUT FOLDER
    path_city = os.path.join(fullpath, 'results_final', config.CITYNAME)
    graph_folder = os.path.join(fullpath, 'data', '05_graph')
    od_pairs_folder = os.path.join(fullpath, 'data', od_pairs_folder)

    parameter_sets = {   
        "feasibility_filter_bike": [3750, 2500, 1250],
        "feasibility_filter_walk": [1125, 750, 375],
        "feasibility_filter_transitions": [6, 4, 2]}
    
    original_values = {"feasibility_filter_bike": config.feasibility_filter_bike,
                       "feasibility_filter_walk": config.feasibility_filter_walk,
                       "feasibility_filter_transitions": config.feasibility_filter_transitions}
    
    for param_name, values in parameter_sets.items():
        for value in values:
            folder_name = f"{param_name}_{value}"
            results_folder = os.path.join(path_city, scenario, graph_name, folder_name)
            
            # RESUME LOGIC: Check if at least 20 CSV files exist (there are 20 length bins)
            if os.path.exists(results_folder) and len([f for f in os.listdir(results_folder) if f.endswith('.csv')]) >= 20:
                print(f"SKIPPING: {folder_name} (Already complete)")
                continue

            print(f"\n=== Running with {param_name} = {value} ===")
            for k, v in original_values.items(): setattr(config, k, v)
            setattr(config, param_name, value)
            os.makedirs(results_folder, exist_ok=True)

            start_time = time.time()
            csv_files = [f for f in os.listdir(od_pairs_folder) if f.endswith('.csv')]
            for csv_file in csv_files:
                ods = pd.read_csv(os.path.join(od_pairs_folder, csv_file))
                n = int(len(ods) / num_chunks)
                source = [ods[i:i+n] for i in range(0, ods.shape[0], n)]
                pool = mp.Pool(processes=num_chunks)
                pool.starmap_async(shortest_path_computation, [(chunk, graph_folder, graph_name, weights, results_folder) for chunk in source]).get()
                pool.close()
                pool.join()

            print(f" Done in {round((time.time() - start_time) / 60, 2)} minutes")

    combined_scenarios = [
        {"feasibility_filter_transitions": 6, "feasibility_filter_walk": 1125, "feasibility_filter_bike": 3750},
        {"feasibility_filter_transitions": 4, "feasibility_filter_walk": 750,  "feasibility_filter_bike": 2500},
        {"feasibility_filter_transitions": 2, "feasibility_filter_walk": 375,  "feasibility_filter_bike": 1250},
    ]

    for combo in combined_scenarios:
        folder_name = (f"combo_trans{combo['feasibility_filter_transitions']}_"
                       f"walk{combo['feasibility_filter_walk']}_bike{combo['feasibility_filter_bike']}")
        results_folder = os.path.join(path_city, scenario, graph_name, folder_name)

        if os.path.exists(results_folder) and len([f for f in os.listdir(results_folder) if f.endswith('.csv')]) >= 20:
            print(f"SKIPPING: {folder_name} (Already complete)")
            continue

        print(f"\n=== Running COMBINATION: {folder_name} ===")
        for param_name, value in combo.items(): setattr(config, param_name, value)
        os.makedirs(results_folder, exist_ok=True)

        start_time = time.time()
        csv_files = [f for f in os.listdir(od_pairs_folder) if f.endswith('.csv')]
        for csv_file in csv_files:
            ods = pd.read_csv(os.path.join(od_pairs_folder, csv_file))
            n = int(len(ods) / num_chunks)
            source = [ods[i:i+n] for i in range(0, ods.shape[0], n)]
            pool = mp.Pool(processes=num_chunks)
            pool.starmap_async(shortest_path_computation, [(chunk, graph_folder, graph_name, weights, results_folder) for chunk in source]).get()
            pool.close()
            pool.join()
        print(f" Combined run finished in {round((time.time() - start_time) / 60, 2)} minutes")

print("\n All variations finished.")
