"""
plotting.py: helper functions for plotting.

* If you want to save bokeh plot into html:
    from bokeh.plotting import output_file, save
    output_file('<name>.html')
    save(plot)
"""
import os
import warnings

from math import pi
from pathlib import Path
from typing import Union

import networkx as nx
import numpy as np
import pandas as pd
from networkx.classes.graph import Graph

from bokeh import events
from bokeh.io import output_notebook
from bokeh.plotting import figure, from_networkx, curdoc
from bokeh.models import (Circle, MultiLine, BasicTicker, CustomJS, NodesAndLinkedEdges,
                          RangeSlider, InlineStyleSheet, ColumnDataSource, Slope)
from bokeh.transform import linear_cmap
from bokeh.palettes import cividis, viridis, Cividis10, Sunset10
from bokeh.layouts import column

warnings.filterwarnings('ignore')

# output_notebook()


def _generate_plottable_graph(graph: Graph):
    """
    This is a helper function for all networkx graphs, that add default
        degree and betweenness to the graph and make it plottable.

    :param graph: networkx instance
    :return: enriched graph instance
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

    # some annoying bokeh thing that otherwise wouldn't let plot
    mapping = dict((n, i) for i, n in enumerate(graph.nodes))
    return nx.relabel_nodes(graph, mapping)


def plot_example_graph(graph: Graph, color_attribute: str, **figure_kwargs):
    """
    Return a plot with an example graph, with color depending on the attribute.

    :param graph: networkx instance
    :param color_attribute: that will be used for coloring the graph
    :param figure_kwargs: specify the size of the plot
            (sizing_mode='stretch_width' for web)
    :return: bokeh plot instance
    """
    # specify the theme
    curdoc().theme = 'light_minimal'

    graph = _generate_plottable_graph(graph)

    plot = figure(
        toolbar_location=None,
        active_scroll='wheel_zoom',
        **figure_kwargs
    )

    plot.axis.visible = False
    plot.grid.visible = False
    plot.outline_line_color = None

    # generate bokeh object from networkx
    network_graph = from_networkx(graph, layout_function=nx.spring_layout, scale=10)
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=0.5)

    # set node colors according to color_attribute
    min_color = min(network_graph.node_renderer.data_source.data[color_attribute])
    max_color = max(network_graph.node_renderer.data_source.data[color_attribute])

    # specify node size and color
    network_graph.node_renderer.glyph = Circle(
        size=40,
        fill_color=linear_cmap(color_attribute, cividis(256), min_color, max_color)
    )

    plot.renderers.append(network_graph)

    return plot


def plot_similarity_matrix(similarity_df: pd.DataFrame, **figure_kwargs):
    """
    Plot bokeh similarity matrix for limited amount of movies.

    :param similarity_df: df with columns as (movie_1, movie_2, similarity)
    :param figure_kwargs: specify the size of the plot
            (sizing_mode='stretch_width' for web)
    :return: bokeh plot instance
    """
    curdoc().theme = 'light_minimal'

    # get unique movies
    movies = similarity_df.movie_1.unique().tolist()

    plot = figure(
        x_range=movies,
        y_range=movies[::-1],
        x_axis_location="above",
        tooltips=[('movies', '@movie_1 @ @movie_2'), ('similarity', '@similarity{0.00}')],
        toolbar_location=None,
        aspect_ratio=1,
        **figure_kwargs
    )

    plot.grid.grid_line_color = None
    plot.axis.axis_line_color = None

    # bring labels closer and add rotation for x-axis
    plot.axis.major_label_standoff = 0
    plot.xaxis.major_label_orientation = pi / 3

    min_color, max_color = similarity_df.similarity.min(), similarity_df.similarity.max()
    colormap = linear_cmap("similarity", cividis(256), low=min_color, high=max_color)
    rect_kwargs = {
        'width': 1, 'height': 1, 'source': similarity_df,
        'fill_color': colormap, 'line_color': None
    }

    # fill the matrix
    r = plot.rect(x="movie_1", y="movie_2", **rect_kwargs)
    _ = plot.rect(x="movie_2", y="movie_1", **rect_kwargs)

    # add to layout
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


def plot_bokeh_histogram(df: pd.DataFrame, group_col: str, **figure_kwargs):
    """
    Plot bokeh histogram for Milestone 3 website (interactive).

    :param df: with the processed and merged movie data
    :param group_col: column used for group_by
    :param figure_kwargs: for Jekyll: {'sizing_mode':'stretch_width', 'height':450}
    :return:
    """
    curdoc().theme = 'light_minimal'

    plot = figure(
        tooltips=[('frequency', '@top'), ('year', '@right')],
        toolbar_location=None,
        **figure_kwargs
    )

    # get count per group_col
    count_series = df.groupby(group_col).name.count().rename('count')
    count_series.index = count_series.index.astype(object)
    count_series = count_series.shift(-1)

    # specify bins and frequency
    bins = count_series.index.to_series().reset_index(drop=True)
    frequency = count_series.reset_index(drop=True)

    plot.quad(
        top=frequency, bottom=0, left=bins[:-1], right=bins[1:],
        fill_color=cividis(1)[0], line_color="white"
    )

    plot.y_range.start = 0
    plot.yaxis.axis_label = "Frequency"
    plot.xaxis.axis_label = "Year"

    return plot


def _get_rangeslider(bokeh_graph):
    """
    Return the rangeslider with IMDB rating as the filtering value.

    :param bokeh_graph: instance of bokeh graph
    :return: range slider object
    """
    # get callback javascript file
    js_file_path = os.path.join(Path(__file__).parent, 'bokeh_callback.js')
    with open(js_file_path, 'r') as js_file:
        js_callback = js_file.read()

    range_slider = RangeSlider(start=0, end=10, value=(1, 9), step=.25, title="IMDB Rating")

    input_feats = {
        'graph': bokeh_graph,
        'node_dict': bokeh_graph.node_renderer.data_source.data.copy(),
        'edges_dict': bokeh_graph.edge_renderer.data_source.data.copy()
    }

    # Create a callback function to update the plot based on the selected release date
    callback = CustomJS(args=input_feats, code=js_callback)

    # Attach the callback to the slider
    range_slider.js_on_change('value', callback)
    curdoc().on_event(events.DocumentReady, callback)

    return range_slider


def plot_bokeh_graph(
        graph,
        color_attribute: str = 'degree',
        size_attribute: str = 'adjusted_node_size',
        layout = nx.spring_layout,
        **figure_kwargs
):
    """
    Plot bokeh graph with stylized nodes and slider with IMDB ratings.

    :param graph: networkx instance
    :param color_attribute: attribute of graph that will be used for coloring the nodes
    :param size_attribute: attribute of graph that will be used for sizing the nodes
    :param figure_kwargs: {sizing_mode: 'stretch_both'} for website
    :return: bokeh plot
    """
    curdoc().theme = 'light_minimal'
    color_palette = viridis(256)

    # establish which categories will appear when hovering over each node
    tooltips = [
        ("Name", "@name"),
        ("Release year", "@release_year"),
        ("Rating", "@rating{0.0}"),
        ("Degree", "@degree{0}"),
        ("Betweenness", "@betweenness{0.00}"),
    ]

    # create a plot — set dimensions, toolbar, and title
    plot = figure(
        tooltips=tooltips,
        toolbar_location=None,
        tools="pan,wheel_zoom,tap",
        active_scroll='wheel_zoom',
        **figure_kwargs
    )

    plot.axis.visible = False
    plot.grid.visible = False
    plot.outline_line_color = None

    # create a network graph object with spring layout
    bokeh_graph = from_networkx(graph, layout, scale=10)

    # set node sizes and colors according to node degree (color as spectrum of color palette)
    node_attributes = bokeh_graph.node_renderer.data_source.data
    attribute = node_attributes[color_attribute]
    colormap = linear_cmap(color_attribute, color_palette, min(attribute), max(attribute))

    bokeh_graph.node_renderer.glyph = Circle(size=size_attribute, fill_color=colormap)

    # set edge opacity and width
    bokeh_graph.edge_renderer.glyph = MultiLine(
        line_alpha=0.3, line_width=1, line_color="#CCCCCC"
    )
    bokeh_graph.edge_renderer.selection_glyph = MultiLine(
        line_alpha=1, line_width=1.3, line_color="#F0610F"
    )

    bokeh_graph.selection_policy = NodesAndLinkedEdges()
    bokeh_graph.inspection_policy = NodesAndLinkedEdges()

    # add network graph to the plot
    plot.renderers.append(bokeh_graph)

    widget = _get_rangeslider(bokeh_graph)

    custom_css = ".bk-RangeSlider { margin-left: auto; margin-right: auto }"
    stylesheet = InlineStyleSheet(css=custom_css)

    # Create a layout with the plot and the slider
    return column(widget, plot, sizing_mode='stretch_width', height=700, stylesheets=[stylesheet])


def plot_bokeh_histogram_w_threshold(frequency, bins, threshold):
    """TODO: add comments"""
    curdoc().theme = 'light_minimal'

    plot = figure(
        toolbar_location=None,
        **{'sizing_mode': 'stretch_width', 'height': 450}
    )

    plot.quad(
        top=frequency, bottom=0, left=bins[:-1], right=bins[1:],
        fill_color=cividis(1)[0], line_color="white"
    )

    plot.vspan(x=threshold, line_width=3, line_color="red")

    plot.y_range.start = 0
    plot.yaxis.axis_label = "Frequency"
    plot.xaxis.axis_label = "Cosine Similarity"


def plot_bokeh_scatter(df: pd.DataFrame, x: str, slope: float, intercept: float):
    """
    TODO: update
    :param df:
    :param x:
    :param slope:
    :param intercept:
    :return:
    """
    curdoc().theme = 'light_minimal'

    blue, yellow = Cividis10[0], Sunset10[5]

    source = ColumnDataSource(df)

    plot = figure(
        sizing_mode='stretch_width', height=450,
        toolbar_location=None,
        x_axis_label='degree',
        y_axis_label='rating',
        tooltips=[
            ("Name", "@name"),
            ("Release year", "@release_year"),
            ('Rating', '@rating{0.0}'),
            ("Degree", "@degree{0}"),
            ("Betweenness", "@betweenness{0.00}")
        ]
    )

    plot.y_range.start = 0

    plot.circle(
        x, 'rating', source=source, size=8,
        alpha=0.7, fill_color=yellow, line_color="black"
    )

    slope = Slope(
        gradient=slope, y_intercept=intercept,
        line_color=blue, line_dash='dashed', line_width=3
    )

    plot.add_layout(slope)

    return plot
