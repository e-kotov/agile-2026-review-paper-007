#!/usr/bin/env python3

import networkx as nx
from heapq import heappop, heappush
from itertools import count

import config


def _dijkstra(G, source, weight, feas_update, feas_init, feas_filter=None, pred=None, paths=None, cutoff=None):
    """Uses Dijkstra's algorithm to find shortest weighted paths from a
    single source.

    This is a convenience function for :func:`_dijkstra_multisource`
    with all the arguments the same, except the keyword argument
    `sources` set to ``[source]``.

    """
    return _dijkstra_multisource(
        G, [source], weight, feas_update=feas_update, feas_init=feas_init, feas_filter=feas_filter, pred=pred, paths=paths, cutoff=cutoff,
    )


def _dijkstra_multisource(
    G, sources, weight, feas_update, feas_init, feas_filter=None, pred=None, paths=None,cutoff=None,
):
    """Uses Dijkstra's algorithm to find shortest weighted paths

    Parameters
    ----------
    G : NetworkX graph

    sources : non-empty iterable of nodes
        Starting nodes for paths. If this is just an iterable containing
        a single node, then all paths computed by this function will
        start from that node. If there are two or more nodes in this
        iterable, the computed paths may begin from any one of the start
        nodes.

    weight: function
        Function with (u, v, data) input that returns that edge's weight
        or None to indicate a hidden edge

    feas_update: function
        Function with (feasility_u, u, v, e) input and returns the new
        feasibility which is feasibility of u plus traversing the edge u->v

    pred: dict of lists, optional(default=None)
        dict to store a list of predecessors keyed by that node
        If None, predecessors are not stored.

    paths: dict, optional (default=None)
        dict to store the path list from source to each node, keyed by node.
        If None, paths are not stored.

    target : node label, optional
        Ending node for path. Search is halted when target is found.

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    Returns
    -------
    distance : dictionary
        A mapping from node to shortest distance to that node from one
        of the source nodes.

    Raises
    ------
    NodeNotFound
        If any of `sources` is not in `G`.

    Notes
    -----
    The optional predecessor and path dictionaries can be accessed by
    the caller through the original pred and paths objects passed
    as arguments. No need to explicitly return pred or paths.

    """
    G_succ = G._adj  # For speed-up (and works for both directed and undirected graphs)

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {}
    # fringe is heapq with 4-tuples (distance,c,node,feasibility)
    # use the count c to avoid comparing nodes (may not be able to)
    c = count()
    fringe = []
    for source in sources:
        seen[source] = 0
        push(fringe, (0, next(c), source, feas_init))

    while fringe:
        (d, _, v, f) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        for u, e in G_succ[v].items():
            cost = weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + cost
            if cutoff is not None:
                if vu_dist > cutoff:
                    continue

            # compute feasibility
            vu_feas = feas_update(f, e)
            # ignore path if feasibility is not satisfied
            if feas_filter is not None and feas_filter(vu_feas) is False:
                continue

            if u in dist:
                u_dist = dist[u]
                if vu_dist < u_dist:
                    raise ValueError("Contradictory paths found:", "negative weights?")
                elif pred is not None and vu_dist == u_dist:
                    pred[u].append(v)
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u, vu_feas))
                if paths is not None:
                    paths[u] = paths[v] + [u]
                if pred is not None:
                    pred[u] = [v]
            elif vu_dist == seen[u]:
                if pred is not None:
                    pred[u].append(v)

    # The optional predecessor and path dictionaries can be accessed
    # by the caller via the pred and paths objects passed as arguments.
    return dist


def all_shortest_paths(G, source, target, feas_update, feas_init, feas_filter=None, weight=None, method="dijkstra",
):
    """Compute all shortest simple paths in the graph.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path.

    target : node
       Ending node for path.

    weight : None, string or function, optional (default = None)
        If None, every edge has weight/distance/cost 1.
        If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.
        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly
        three positional arguments: the two endpoints of an edge and
        the dictionary of edge attributes for that edge.
        The function must return a number.

    method : string, optional (default = 'dijkstra')
       The algorithm to use to compute the path lengths.
       Supported options: 'dijkstra', 'bellman-ford'.
       Other inputs produce a ValueError.
       If `weight` is None, unweighted graph methods are used, and this
       suggestion is ignored.

    Returns
    -------
    paths : generator of lists
        A generator of all paths between source and target.

    Raises
    ------
    ValueError
        If `method` is not among the supported options.

    NetworkXNoPath
        If `target` cannot be reached from `source`.

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_path(G, [0, 1, 2])
    >>> nx.add_path(G, [0, 10, 2])
    >>> print([p for p in nx.all_shortest_paths(G, source=0, target=2)])
    [[0, 1, 2], [0, 10, 2]]

    Notes
    -----
    There may be many shortest paths between the source and target.  If G
    contains zero-weight cycles, this function will not produce all shortest
    paths because doing so would produce infinitely many paths of unbounded
    length -- instead, we only produce the shortest simple paths.

    See Also
    --------
    shortest_path
    single_source_shortest_path
    all_pairs_shortest_path
    """
    if weight is None:
        raise ValueError("Only weighted graphs are supported")
    if method != "dijkstra":
        raise ValueError("Only dijkstra supported")

    pred, dist = dijkstra_predecessor_and_distance(
        G,
        source,
        feas_update=feas_update,
        feas_init=feas_init,
        feas_filter=feas_filter,
        weight=weight,
    )

    return _build_paths_from_predecessors({source}, target, pred)

def _build_paths_from_predecessors(sources, target, pred):
    """Compute all simple paths to target, given the predecessors found in
    pred, terminating when any source in sources is found.

    Parameters
    ----------
    sources : set
       Starting nodes for path.

    target : node
       Ending node for path.

    pred : dict
       A dictionary of predecessor lists, keyed by node

    Returns
    -------
    paths : generator of lists
        A generator of all paths between source and target.

    Raises
    ------
    NetworkXNoPath
        If `target` cannot be reached from `source`.

    Notes
    -----
    There may be many paths between the sources and target.  If there are
    cycles among the predecessors, this function will not produce all
    possible paths because doing so would produce infinitely many paths
    of unbounded length -- instead, we only produce simple paths.

    See Also
    --------
    shortest_path
    single_source_shortest_path
    all_pairs_shortest_path
    all_shortest_paths
    bellman_ford_path
    """
    if target not in pred:
        raise nx.NetworkXNoPath(f"Target {target} cannot be reached from given sources")

    seen = {target}
    stack = [[target, 0]]
    top = 0
    while top >= 0:
        node, i = stack[top]
        if node in sources:
            yield [p for p, n in reversed(stack[: top + 1])]
        if len(pred[node]) > i:
            stack[top][1] = i + 1
            next = pred[node][i]
            if next in seen:
                continue
            else:
                seen.add(next)
            top += 1
            if top == len(stack):
                stack.append([next, 0])
            else:
                stack[top][:] = [next, 0]
        else:
            seen.discard(node)
            top -= 1


def dijkstra_predecessor_and_distance(G, source, feas_update, feas_init, feas_filter=None, cutoff=None, weight="weight",
):
    """Compute weighted shortest path length and predecessors.

    Uses Dijkstra's Method to obtain the shortest weighted paths
    and return dictionaries of predecessors for each node and
    distance for each node from the `source`.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
        Starting node for path

    cutoff : integer or float, optional
        Length (sum of edge weights) at which the search is stopped.
        If cutoff is provided, only return paths with summed weight <= cutoff.

    weight : string or function
        If this is a string, then edge weights will be accessed via the
        edge attribute with this key (that is, the weight of the edge
        joining `u` to `v` will be ``G.edges[u, v][weight]``). If no
        such edge attribute exists, the weight of the edge is assumed to
        be one.

        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    Returns
    -------
    pred, distance : dictionaries
        Returns two dictionaries representing a list of predecessors
        of a node and the distance to each node.

    Raises
    ------
    NodeNotFound
        If `source` is not in `G`.

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The list of predecessors contains more than one element only when
    there are more than one shortest paths to the key node.

    Examples
    --------
    >>> G = nx.path_graph(5, create_using=nx.DiGraph())
    >>> pred, dist = nx.dijkstra_predecessor_and_distance(G, 0)
    >>> sorted(pred.items())
    [(0, []), (1, [0]), (2, [1]), (3, [2]), (4, [3])]
    >>> sorted(dist.items())
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

    >>> pred, dist = nx.dijkstra_predecessor_and_distance(G, 0, 1)
    >>> sorted(pred.items())
    [(0, []), (1, [0])]
    >>> sorted(dist.items())
    [(0, 0), (1, 1)]
    """
    if source not in G:
        raise nx.NodeNotFound(f"Node {source} is not found in the graph")
    weight = _weight_function(G, weight)
    pred = {source: []}  # dictionary of predecessors
    return (pred, _dijkstra(G, source, weight, feas_update=feas_update, feas_init=feas_init, feas_filter=feas_filter, pred=pred, cutoff=cutoff))

def _weight_function(G, weight):
    """Returns a function that returns the weight of an edge.

    The returned function is specifically suitable for input to
    functions :func:`_dijkstra` and :func:`_bellman_ford_relaxation`.

    Parameters
    ----------
    G : NetworkX graph.

    weight : string or function
        If it is callable, `weight` itself is returned. If it is a string,
        it is assumed to be the name of the edge attribute that represents
        the weight of an edge. In that case, a function is returned that
        gets the edge weight according to the specified edge attribute.

    Returns
    -------
    function
        This function returns a callable that accepts exactly three inputs:
        a node, an node adjacent to the first one, and the edge attribute
        dictionary for the eedge joining those nodes. That function returns
        a number representing the weight of an edge.

    If `G` is a multigraph, and `weight` is not callable, the
    minimum edge weight over all parallel edges is returned. If any edge
    does not have an attribute with key `weight`, it is assumed to
    have weight one.

    """
    if callable(weight):
        return weight
    # If the weight keyword argument is not callable, we assume it is a
    # string representing the edge attribute containing the weight of
    # the edge.
    if G.is_multigraph():
        return lambda u, v, d: min(attr.get(weight, 1) for attr in d.values())
    return lambda u, v, data: data.get(weight, 1)


def my_all_shortest_paths(G, source, target, weight=None, method="dijkstra"):
    is_multigraph = G.is_multigraph()

    def feas_update(feas_v, e):
        if is_multigraph:
            weight = min(edge.get('length', 1) for edge in e.values())  # minimum length
            label = [edge.get('label', '') for edge in e.values() if weight == edge.get('length', 1)][0]
        else:
            weight = e.get('length', 1)
            label = e.get('label', '')

        walk = feas_v[0]
        if label == "walk":
            walk += weight

        bike = feas_v[1]
        if label == 'bike':
            bike += weight

        transitions = feas_v[2]
        if label == 'transition':
            transitions += 1

        return (walk, bike, transitions)

    def feas_filter(v):
        if v[0] > config.feasibility_filter_walk:
            return False
        if v[1] > config.feasibility_filter_bike:
            return False
        if v[2] > config.feasibility_filter_transitions:
            return False
        return True

    return all_shortest_paths(G, source=source, target=target, feas_init=(0, 0, 0), feas_update=feas_update, feas_filter=feas_filter, weight=weight)
