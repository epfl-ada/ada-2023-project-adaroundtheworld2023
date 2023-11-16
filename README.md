# “Creative breakthroughs occur, when worlds collide”

<br>

## Table of Contents
<p>
  <a href="#abstract-">Abstract</a> •
  <a href="#research-questions-">Research Questions</a> •
  <a href="#additional-datasets-">Additional Datasets</a> •
  <a href="#methods-">Methods</a> •
  <a href="#timeline-">Timeline</a> •
  <a href="#team-organization-">Team Organization</a>
</p>

## Abstract 📌

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

## Research Questions 🔎

Since we apply two different methods for uncovering the patterns 
(see [Methods](https://github.com/epfl-ada/ada-2023-project-adaroundtheworld2023/tree/update-readme#methods-)), 
the research questions fall into two domains: 
(1) *Research Specific* and (2) *Comparison of Methods*.

**Research Specific**. We will examine the relationship 
between “_**being at the intersection**_” and the success of a movie. 
The success is defined as the IMDB rating. Being at the intersection 
will be a bit more challenging to quantify, but we decided to use a 
metric called "betweenness centrality" (see more detailed description 
in [Metrics](#step-2-metrics)). The intuition here would be that the 
movies that have high betweenness measure would be similar to different 
clusters... in other words, they would entail different genres. 
The opposite to the betweenness would be "_**degree**_" (see [Metrics](#step-2-metrics)).
A movie with a high degree would be similar to many other movies, possibly in
one domain and would then be one-genre-specific. Therefore, 
we would like to answer the following questions:

- Is there a relationship between “being at the intersection of different genres” and the success of a movie? Do movies with more betweenness centrality have better IMDB ratings than the rest?
- Maybe it's opposite and movies that do not resemble to many others are more successful? Therefore, do movies with smaller degree have better IMDB ratings than the rest?

**Comparison of Methods**. We will compare two approaches 
described in [Graph Generation](#step-1-graph-generation). One uses
embedded plots and calculates the similarity, the other let's LLM predict
the probability of belonging to different genres. The questions are as follows:

- How different are the network graphs generated by the two different approaches? What are the reasons for this? Is this expected?
- Does the final result of the analysis differ depending on the graph generation strategy? Why is it so and what could be the reason?

## Additional Datasets 📚

In order to be able to discern between a "good" and a "bad" movie we need quantifiable 
information available to all the movies (or a big proportion of them). As 89% of 
revenue seems to be missing, we'll use ratings instead.  

While ratings are not initially in the dataset, we can use the 
[IMDb Movies Dataset](https://developer.imdb.com/non-commercial-datasets/) 
in order to extend the current one with both average ratings and the number 
of voters (As just the average may not hold enough information).

## Methods 🎯

First we will explain the data preprocessing pipeline and then 
focus on the analysis. The analysis relies mainly on the graphs, 
which will be generated using two different approaches.

### Preprocessing

**Movie Metadata**. In the preprocessing stage, the focus was on handling missing values, 
which varied by column, being either NaN or empty lists. The approach 
to missing data was tailored to the relevance of the information. 

**Plot Summaries**. As the analysis is mostly based on summaries of the plots,
they will be merged with the metadata.

**IMDB Ratings**. To add a measure of success for each movie, 
IMDb ratings will also be merged with the dataset. 
There isn't an exact id match, so we will use the (`release year`, `movie name`) 
index for matching the existing dataset with the IMDb one.

The analysis of the processed data can be found from [preprocess.ipynb](notebooks/preprocess.ipynb).
            
### Analysis

#### Step 1: Graph Generation

As analysis relies on the network graphs, we first need to generate 
them. For that purpose, two different approaches will be used.

**Embedding Models and Similarity**. We are going to use an embedding 
model [[2](https://arxiv.org/pdf/2212.03533.pdf)] to turn the 
movie plots into vectors and find the similarity 
between them by using matrix multiplication. We can then specify a 
threshold for the similarity to generate a graph. See the first endeavours 
in [embedding.ipynb](notebooks/embedding.ipynb).

**NLI-based Text Classification**. As an alternative approach, we will let 
the LLM predict the probability that the plot belongs to any of the 
genres [[3](https://arxiv.org/pdf/1909.00161.pdf)]. Although we already have a set of genres specified for every 
movie, (1) this might depend on the data collection and by using models, 
we can (2) limit the genre space and (3) turn the discrete list of genres 
into probabilities. We will then again set the probability threshold and generate a 
graph that will be used in the following analysis.

#### Step 2: Metrics

Our aim is to test whether “being at the intersection” is correlated with 
the success of a movie. Being at the intersection can be proxied with 
*betweenness centrality* measure 
[[4](https://www.sciencedirect.com/science/article/abs/pii/S0378873307000731?via%3Dihub)]. 
Betweenness centrality of a node $v$ is 
the sum of the fraction of all-pairs shortest paths that pass through $v$:

$$ c_B(v) =  \sum_{s,t \in V}^{}  \frac{ \sigma (s, t | v) }{\sigma (s, t)}, $$

where $V$ is the set of nodes, $\sigma (s, t)$ is the number of shortest 
$(s, t)$-paths, and $\sigma (s, t | v)$ is the number of those paths 
passing through some node $V$ other than $s, t$.

Alternatively, we can take a slightly different approach and focus not 
only on the intersections but look at the plots that are simply similar 
to many others. This can easily be quantified by the degree of the node, i.e. 
the number of edges connected to the node.

#### Step 3: Analysis

The analysis will be conducted by first examining the relationship 
visually from the network graphs and then performing correlation analysis.

**Visual Inspection**. We can examine the relationship between “being at 
the intersection” and success visually on the graph by setting the size 
of the node equal to the betweenness measure and color of the node to 
the IMDB rating. We can similarly compare the degree with the IMDB rating.

**Correlation Analysis**. We can perform correlation analysis between the 
IMDB rating and the measures. In addition to marginal correlation, 
we can look at the partial correlation (e.g. decade) by using linear 
regression and dummy variables. 

## Timeline 📅

```
.
├── Week 8  - Preprocessing
│  
├── Week 9  - Embedding & classification
│  
├── Week 10 - Homework 2
│  
├── Week 11 - Graph generation & data story
│  
├── Week 12 - Correlation analysis & data story
│    
├── Week 13 - Github pages
│  
├── Week 14 - Finalization
.
```

## Team Organization 👬

- **Nam**: GitHub pages 
- **Valentin**: preprocessing & network graph analysis
- **Paul**: correlation analysis & data story
- **Quentin**: NLI based text classification & data story
- **Jan**: network graphs & data story

