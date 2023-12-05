const nodes = node_dict;
const edges = edges_dict;
let selected_release_year = cb_obj.value;

if (selected_release_year === undefined) {
    selected_release_year = Math.min(... nodes.release_year);
}

// Update the nodes source with nodes filtered by the selected release date

const indices = [];
const wikipediaIds = [];
for (let i = 0; i < nodes['release_year'].length; i++) {
    if (nodes['release_year'][i] === selected_release_year) {
        indices.push(i);
        wikipediaIds.push(nodes['wikipedia_id'][i]);
    }
}

debugger;

const newNodes = Object.keys(nodes).reduce((result, key) => {
    result[key] = [];
    return result;
}, {});

Object.keys(nodes).forEach(key => {
    newNodes[key] = nodes[key].filter((value, index) => indices.includes(index));
});

// Use map and filter to create the filteredData dictionary
const filteredEdges = {};

Object.keys(edges).forEach(key => {
    filteredEdges[key] = edges[key].filter((value, index) =>
        wikipediaIds.includes(edges['start'][index]) &&
        wikipediaIds.includes(edges['end'][index])
    );
});

console.log(indices)
console.log(filteredEdges['start'])

// Trigger update
graph.node_renderer.data_source.data = newNodes;
graph.edge_renderer.data_source.data = filteredEdges;
graph.change.emit();
