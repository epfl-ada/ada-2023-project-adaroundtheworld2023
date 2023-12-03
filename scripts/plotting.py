"""plotting.py: helper functions for plotting."""
from math import pi
from typing import Union

import networkx as nx
import pandas as pd
from networkx.classes.graph import Graph

from bokeh.io import output_file, show, output_notebook, save, curdoc
from bokeh.plotting import figure, from_networkx
from bokeh.models import Circle, MultiLine, BasicTicker
from bokeh.transform import linear_cmap
from bokeh.palettes import Blues8, RdBu, cividis, OrRd, magma, plasma, viridis

output_notebook()


def _generate_plottable_graph(graph: Graph):
    """

    :param graph:
    :return:
    """
    # calculate degrees
    degree = nx.degree_centrality(graph)
    nx.set_node_attributes(graph, name='degree', values=degree)

    # calculate betweenness
    betweenness = nx.betweenness_centrality(graph)
    nx.set_node_attributes(graph, name='betweenness', values=betweenness)

    # add name as an attribute
    names = dict((id_, id_) for id_ in graph.nodes)
    nx.set_node_attributes(graph, name='name', values=names)

    # some annoying bokeh thing
    mapping = dict((n, i) for i, n in enumerate(graph.nodes))
    H = nx.relabel_nodes(graph, mapping)

    return H


def plot_example_graph(
        graph: Graph,
        color_attribute: str,
        **figure_kwargs
):
    """

    :param graph:
    :param color_attribute:
    :param figure_kwargs:
    :return:
    """
    G = _generate_plottable_graph(graph)

    curdoc().theme = 'light_minimal'

    plot = figure(
        toolbar_location=None,
        active_scroll='wheel_zoom',
        **figure_kwargs
    )

    plot.axis.visible = False
    plot.grid.visible = False

    # generate bokeh object from networkx
    network_graph = from_networkx(G, layout_function=nx.spring_layout, scale=10)
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=0.5)

    # set node colors according to color_attribute
    min_color = min(network_graph.node_renderer.data_source.data[color_attribute])
    max_color = max(network_graph.node_renderer.data_source.data[color_attribute])

    network_graph.node_renderer.glyph = Circle(
        size=40,
        fill_color=linear_cmap(color_attribute, cividis(256), min_color, max_color)
    )

    plot.renderers.append(network_graph)

    return plot


def plot_similarity_matrix(similarity_df: pd.DataFrame):

    movies = similarity_df.movie_1.unique().tolist()

    plot = figure(
        x_range=movies,
        y_range=movies[::-1],
        x_axis_location="above",
        sizing_mode='stretch_width',
        aspect_ratio=1,
        tooltips=[('movies', '@movie_1 @ @movie_2'), ('similarity', '@similarity{0.00}')],
        toolbar_location=None
    )

    curdoc().theme = 'light_minimal'

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None

    plot.axis.major_label_standoff = 0
    plot.xaxis.major_label_orientation = pi / 3

    r = plot.rect(x="movie_1", y="movie_2", width=1, height=1, source=similarity_df,
                  fill_color=linear_cmap("similarity", cividis(256), low=similarity_df.similarity.min(),
                                         high=similarity_df.similarity.max()),
                  line_color=None)

    _ = plot.rect(x="movie_2", y="movie_1", width=1, height=1, source=similarity_df,
                  fill_color=linear_cmap("similarity", cividis(256), low=similarity_df.similarity.min(),
                                         high=similarity_df.similarity.max()),
                  line_color=None)

    plot.add_layout(r.construct_color_bar(
        major_label_text_font_size="12px",
        ticker=BasicTicker(desired_num_ticks=10),
        label_standoff=12,
        background_fill_alpha=0,
        major_label_text_color="black",
        border_line_color=None,
        padding=10,
    ), 'right')

    return plot
