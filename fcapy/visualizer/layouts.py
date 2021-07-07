"""
This module provides a set of functions to derive a layout (node positions) for a given POSet

"""

import networkx as nx
from frozendict import frozendict


def calc_levels(poset):
    """Return levels (y position) of nodes and dict with {`level`: `nodes`} mapping in a line diagram"""
    c_levels = [0] * len(poset)
    nodes_to_visit = poset.top_elements
    nodes_visited = set()
    while len(nodes_to_visit) > 0:
        node_id = nodes_to_visit.pop(0)
        nodes_visited.add(node_id)
        dsups_ids = poset.direct_super_elements(node_id)
        c_levels[node_id] = max([c_levels[dsup_id] for dsup_id in dsups_ids]) + 1 if len(dsups_ids) > 0 else 0
        nodes_to_visit += [n_i for n_i in poset.direct_sub_elements(node_id) if n_i not in nodes_visited]

    levels_dict = {i: [] for i in range(max(c_levels) + 1)}
    for c_i in range(len(poset)):
        levels_dict[c_levels[c_i]].append(c_i)
    return c_levels, levels_dict


def multipartite_layout(poset):
    """A basic layout generated by networkx.multipartite_layout function"""
    c_levels, levels_dict = calc_levels(poset)
    G = poset.to_networkx('down')
    nx.set_node_attributes(G, dict(enumerate(c_levels)), 'level')
    pos = nx.multipartite_layout(G, subset_key='level', align='horizontal')
    pos = {c_i: [p[0], -p[1]] for c_i, p in pos.items()}
    return pos


LAYOUTS = frozendict({
    'multipartite': multipartite_layout,
})