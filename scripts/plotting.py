"""
plotting.py: helper functions for plotting.

* If you want to save bokeh plot into html:
    output_file('<name>.html', mode='inline')
    save(plot)
"""
import warnings

from math import pi
import networkx as nx
import pandas as pd
from networkx.classes.graph import Graph

from bokeh.io import output_notebook, curdoc
from bokeh.plotting import figure, from_networkx
from bokeh.models import Circle, MultiLine, BasicTicker
from bokeh.transform import linear_cmap
from bokeh.palettes import cividis

warnings.filterwarnings('ignore')

output_notebook()


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
    :param figure_kwargs: for Jekyll {'sizing_mode':'stretch_width', 'height'=450}
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

    # specify bins and frequency
    bins = count_series.index.to_series().reset_index(drop=True)
    frequency = count_series.reset_index(drop=True)

    plot.quad(
        top=frequency, bottom=0, left=bins[:-1], right=bins[1:],
        fill_color=cividis(1)[0], line_color="white"
    )

    plot.y_range.start = 0
    plot.yaxis.axis_label = "Frequency"

    return plot
