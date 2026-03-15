import networkx as nx
import pandas as pd
import pickle

from helpers.multigraph_helpers import generate_node_id, extract_node_id


def split_by_semicolon(string, type='float'):
    try:
        splitted = string.split(';')
        if type == 'float':
            try:
                splitted_float = [float(x) for x in splitted]
                return splitted_float
            except ValueError:
                return splitted
        elif type == 'int':
            try:
                splitted_float = [int(x) for x in splitted]
                return splitted_float
            except ValueError:
                return splitted
    except AttributeError:
        return string


def to_p_file(graph, name):
    pickle.dump(graph, open(f'{name}.p', "wb"))
    return True


def from_p_file(name):
    g = pickle.load(open(f'{name}.p', "rb"))
    return g


def array_to_dict(arr):
    res = {}
    for i in arr:
        res[str(i[0])+'-'+str(i[1])] = []
    return res


def get_index_of_category(cn, sp_length):
    for ix, category in enumerate(cn):
        if category[0] < sp_length <= category[1]:
            return ix


def sum_energy_time_length_labels(datas):
    _energy = 0
    _time = 0
    _length = 0
    osm_ids = []
    modes = []
    lengths = []
    energies = []
    times = []
    for i in datas:
        osm_ids.append(str(i['osm_ids']))
        modes.append(str(i['label']))
        lengths.append(str(i['length']))
        energies.append(str(i['energy']))
        times.append(str(i['time']))
        _length += i['length']
        _energy += i['energy']
        _time += i['time']
    return _energy, _time, _length,osm_ids,modes,lengths,energies,times


def add_parent_child_edges(graph, node_id, direction):
    pre_fix, osm_id, _ = extract_node_id(node_id)

    # add additional "parent" node to nodes of different layers, but at same location (aka node "siblings")
    if pre_fix == '110011' or pre_fix == '220022':
        node_id = generate_node_id(osm_id, 'walk', '0000')
    neighbors = list(nx.all_neighbors(graph, node_id))
    node_siblings = [n for n in neighbors if '_' + osm_id + '_' in n] + [node_id]

    # new node ID of parent or child
    node_id_new = generate_node_id(osm_id=osm_id, mode=direction, postfix='0000')

    # add parent node to graph
    graph.add_node(node_id_new,
                   geom=graph.nodes[node_siblings[0]]['geom'])

    # add edges between parent node and all siblings
    for sibling in node_siblings:
        #  select correct connection of parent with node-siblings (for start- or end-node)
        if direction == 'parent':
            A, B = node_id_new, sibling
        elif direction == 'child':
            A, B = sibling, node_id_new
        else:
            print('select direction of connection ("parent" or "child")')
            return
        graph.add_edge(
            A,
            B,
            osm_ids=f'{str(A)};{str(B)}',
            length=0,
            time=0,
            geom=None,
            relation_id=0,
            label='parent'
        )
    return graph, node_id_new
