# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import plotly.figure_factory as ff

import seaborn as sns
import plotly.graph_objects as go

# Set page config
st.set_page_config(page_title="Breakthrough", page_icon="🎬", layout="centered")

# Set page title
st.title("_\"Creative breakthroughs occur, when worlds collide\"_")
# Contribution
st.subheader("by Thai-Nam Hoang, Valentin Peyron, Paul-Bogdan Jurcut, Quentin Esteban, Jan Kokla")

# Abstract
st.write("""
In 2004, American entrepreneur Frans Johansson published a book 
“The Medici Effect: Breakthrough Insights at the Intersection of 
Ideas, Concepts, and Cultures” [[1](https://www.goodreads.com/pt/book/show/20482413)]
, where he argues that the biggest 
innovation happens when disciplines, ideas or domains intersect. 
In other words, by merging ideas from a range of diverse backgrounds, 
one can increase the likelihood of intellectual cross-pollination, 
which might lead to innovation and success.

Our aim is to examine if this holds true in the movie industry. 
We focus on the plots and genres and with the help of the embedding 
models we will generate the network graphs. These will help us to 
verify if the relationship between “being at the intersection” 
and the success are linked in the movie industry.
""")

# Analysis
st.header("Analysis")
# Load dataframe
df = pd.read_csv("./data/processed/preprocessed.csv")

st.dataframe(df.describe(), use_container_width=True)

st.subheader("Distributions")
# Bin width
iqr = np.percentile(df['release_year'], 75) - np.percentile(df['release_year'], 25)
n = len(df['release_year'])
bin_width = 2 * (iqr / np.power(n, 1 / 3))

group_labels = ["distplot"]  # name of the dataset

fig = ff.create_distplot([df.release_year], group_labels, show_rug=False, show_hist=True, show_curve=True,
                         bin_size=bin_width)
fig.update_layout(
    xaxis_title='release_year',
    yaxis_title='Count',
    showlegend=True,
    bargap=0.1
)
st.plotly_chart(fig, use_container_width=True)
