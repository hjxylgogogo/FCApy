from fcapy.visualizer import hasse_visualizers as viz, hasse_layouts
from fcapy.context import FormalContext
from fcapy.lattice.concept_lattice import ConceptLattice

import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image
import networkx as nx

import pytest


def test__init__abstract():
    vsl = viz.AbstractHasseViz()

    with pytest.raises(NotImplementedError):
        vsl.draw_poset(None)

    with pytest.raises(NotImplementedError):
        vsl.draw_quiver(None, None)

    with pytest.raises(NotImplementedError):
        vsl.draw_concept_lattice(None)


def test_filter_nodes_edges():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)
    G = L.to_networkx()

    nodes_all, edges_all = list(G.nodes), list(G.edges)
    nodes_filter = [0, 1, 3, 4, 5]
    edges_filter = [(0,1), (0,2), (1,4), (2,4)]

    vsl = viz.AbstractHasseViz()
    nodes, edges = vsl._filter_nodes_edges(G)
    assert nodes == nodes_all
    assert edges == edges_all

    nodes, edges = vsl._filter_nodes_edges(G, nodelist=nodes_filter)
    assert nodes == nodes_filter
    assert edges == [e for e in edges_all if e[0] in nodes_filter and e[1] in nodes_filter]

    nodes, edges = vsl._filter_nodes_edges(G, edgelist=edges_filter)
    assert nodes == nodes_all
    assert edges == edges_filter

    nodes, edges = vsl._filter_nodes_edges(G, nodelist=nodes_filter, edgelist=edges_filter)
    assert nodes == nodes_filter
    assert edges == [e for e in edges_filter if e[0] in nodes_filter and e[1] in nodes_filter]


def test_concept_lattice_label_func():
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)
    vsl = viz.AbstractHasseViz()

    lbl = vsl.concept_lattice_label_func(0, L)
    assert lbl == '\n\n2: cow, hen'

    lbl = vsl.concept_lattice_label_func(2, L, max_new_extent_count=3)
    assert lbl == '1: run\n\n3: dog, horse, zebra'


def test_draw_concept_lattice_networkx():
    def compare_figure_png(fig, fname):
        with io.BytesIO() as buff:
            fig.savefig(buff, format='png', dpi=300)
            buff.seek(0)
            im_fig = plt.imread(buff)

        im_file = image.imread(fname)
        assert ((im_fig-im_file) < 1e-2).all(), f"Cannot recreate the figure from file {fname}"
        # TODO Make the assertion more strict

    # The simplest case
    path = 'data/animal_movement.json'
    K = FormalContext.read_json(path)
    L = ConceptLattice.from_context(K)

    plt.rcParams['figure.facecolor'] = (1, 1, 1, 1)
    fig, ax = plt.subplots(figsize=(7, 5))
    vsl = viz.HasseVizNx()
    vsl.draw_concept_lattice(
        L, ax=ax, flg_node_indices=False, flg_axes=False
    )
    ax.set_xlim(-0.6, 0.65)
    ax.set_ylim(-0.6, 1.1)
    fig.tight_layout()

    compare_figure_png(fig, 'data/animal_movement_lattice.png')

    # Specify optional parameters
    pos = hasse_layouts.fcart_layout(L)
    G = L.to_networkx()
    nodelist = list(G.nodes)
    edgelist = list(G.edges)

    fig, ax = plt.subplots(figsize=(7, 5))
    vsl.draw_concept_lattice(
        L, ax=ax, flg_node_indices=True, flg_axes=True,
        pos=pos, nodelist=nodelist, edgelist=edgelist
    )
    ax.set_ylim(-0.6, 1.1)
    ax.set_xlim(-0.6, 0.65)
    fig.tight_layout()

    compare_figure_png(fig, 'data/animal_movement_lattice_overloaded.png')


def test_flg_drop_empty_bottom():
    path = 'data/liveinwater.cxt'
    K = FormalContext.read_cxt(path)
    L = ConceptLattice.from_context(K)

    def lattice_to_img(L, nodelist, flg_drop_empty_bottom):
        plt.rcParams['figure.facecolor'] = (1, 1, 1, 1)

        fig, ax = plt.subplots(figsize=(7, 5))
        vsl = viz.HasseVizNx()
        vsl.draw_concept_lattice(
            L, ax=ax, flg_node_indices=False, flg_axes=False,
            nodelist=nodelist, flg_drop_empty_bottom = flg_drop_empty_bottom
        )

        with io.BytesIO() as buff:
            fig.savefig(buff, format='png', dpi=300)
            buff.seek(0)
            img = plt.imread(buff)

        return img

    img0 = lattice_to_img(L, [c_i for c_i in range(len(L)) if c_i != L.bottom_concept_i], False)
    img1 = lattice_to_img(L, None, True)
    assert (img0 == img1).all()


def _retrieve_node_varying_parameter():
    G = nx.Graph([(0, 1), (1, 2), (0, 2)])
    vsl = viz.HasseVizNx()
    clr = vsl._retrieve_node_varying_parameter(None, 'DefaultValue', [0, 1, 2], len(G), 'ParamType')
    assert clr == ['DefaultValue'] * 3

    clr_orig = ['green', 'yellow', 'blue']
    clr = vsl._retrieve_node_varying_parameter(clr_orig, 'DefaultValue', [0, 1], len(G), 'ParamType')
    assert clr == clr_orig[:2]

    clr = vsl._retrieve_node_varying_parameter(clr_orig[1:], 'DefaultValue', [0, 1], len(G), 'ParamType')
    assert clr == clr_orig[1:]

    with pytest.raises(viz.UnsupportedNodeVaryingParameterError):
        vsl._retrieve_node_varying_parameter([clr_orig[0]], 'DefaultValue', [0, 1], len(G), 'ParamType')

    with pytest.raises(viz.UnsupportedNodeVaryingParameterError):
        vsl._retrieve_node_varying_parameter(['yellow'] * 5, 'DefaultValue', [0, 1, 2], len(G), 'ParamType')
