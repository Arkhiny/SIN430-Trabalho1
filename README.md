# Graph Algorithms Project

A comprehensive implementation of graph data structures and algorithms, supporting both adjacency list and adjacency matrix representations.

## Project Overview

This project implements core graph algorithms and provides testing infrastructure for analyzing graph properties and performance across different graph representations.

## Main Module: `Grafos.py`

The core module containing graph implementations and algorithms:

### Graph Representations

- **AdjacencyListGraph**: Graph representation using dictionary-based adjacency lists (space-efficient for sparse graphs)
- **AdjacencyMatrixGraph**: Graph representation using 2D boolean matrix (efficient for dense graphs)
- **Factory Method**: `create_graph(num_vertices, representation)` - creates graph instances with selected representation

### Graph Algorithms

#### Search Algorithms
- **BFS (Breadth-First Search)**: `bfs_search_tree(graph, start_vertex)` - builds search tree from a starting vertex
- **DFS (Depth-First Search)**: `dfs_search_tree(graph, start_vertex)` - builds search tree using depth-first traversal

#### Distance & Connectivity
- **BFS Distances**: `bfs_distances(graph, start_vertex)` - computes shortest distances from start vertex to all reachable vertices
- **Shortest Path**: `shortest_distance(graph, source_vertex, target_vertex)` - finds shortest distance between two specific vertices
- **Graph Diameter**: `graph_diameter(graph)` - computes the maximum shortest path distance between any two vertices
- **Connected Components**: `get_connected_components(graph)` - identifies all connected components

#### Analysis Functions
- **Degree Statistics**: `get_degree_stats(graph)` - computes min, max, average, and median vertex degrees
- **Graph Report**: `build_graph_report_data(graph)` - generates comprehensive graph statistics

### Utility Functions
- **File I/O**: `read_graph_file(file_path, representation)` - loads graph from edge list format
- **Report Generation**: Various write functions to export results to text files

## Test Cases

### Case 1: Memory Analysis (`Caso1.py`)
Tests memory usage of graph representations (list vs. matrix) across different graphs.

**Tested Graphs**: grafo_1 to grafo_5

**Output Directory**: `Caso1/`
- `memory_report_grafo_[1-5]_list.txt` - Memory usage for adjacency list representation
- `memory_report_grafo_[1-5]_matrix.txt` - Memory usage for adjacency matrix representation

### Case 2: Breadth-First Search (`Caso2.py`)
Tests BFS algorithm by building search trees from random starting vertices and measuring execution times.

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso2/`
- `bfs_grafo_[1-6]_list.txt` - BFS results using adjacency list
- `bfs_grafo_1_matrix.txt` - BFS results using adjacency matrix

### Case 3: Depth-First Search
Tests DFS algorithm for graph exploration and tree building.

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso3/`
- `dfs_grafo_[1-6]_list.txt` - DFS results using adjacency list
- `dfs_grafo_1_matrix.txt` - DFS results using adjacency matrix

### Case 4: Parent Tracking (`Caso4_7.py`)
Analyzes parent-child relationships in search trees (identifies which vertex discovered each vertex in search).

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso4/`
- `task4_parents_grafo_[1-6]_list.txt` - Parent relationships using adjacency list
- `task4_parents_grafo_1_matrix.txt` - Parent relationships using adjacency matrix

### Case 5: Distance Analysis (`Caso4_7.py`)
Computes shortest distances between specific vertex pairs and graph diameter.

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso5/`
- `task5_distances_grafo_[1-6]_list.txt` - Distance calculations using adjacency list
- `task5_distances_grafo_1_matrix.txt` - Distance calculations using adjacency matrix

### Case 6: Connected Components (`Caso4_7.py`)
Identifies and analyzes all connected components in each graph.

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso6/`
- `task6_components_grafo_[1-6]_list.txt` - Connected components using adjacency list
- `task6_components_grafo_1_matrix.txt` - Connected components using adjacency matrix

### Case 7: Graph Diameter Approximation (`Caso4_7.py`)
Computes exact graph diameter for small graphs and approximations for larger graphs using sampling.

**Tested Graphs**: grafo_1 to grafo_6

**Output Directory**: `caso7/`
- `task7_exact_diameter_grafo_1_list.txt` - Exact diameter for grafo_1
- `task7_approx_diameter_grafo_[2-6]_list.txt` - Approximated diameters for larger graphs

## Input Data

Download the dataset from [this Google Drive folder](https://drive.google.com/drive/folders/1BaUij5X2DA9vmvrIzZKRtNzVjVgeZsL-?usp=sharing) and place the graph files inside `Data/`.

The `Data/` folder is kept in the repository, but the dataset files inside it are ignored by git. Each local copy of the project should contain the downloaded graph files.

Graph definitions are stored in edge list format:

**File Format**: `Data/grafo_[1-6].txt`
- First line: number of vertices
- Subsequent lines: space-separated pairs `u v` representing edges

## Running the Tests

Execute the corresponding case file:

```bash
python Caso1.py    # Memory analysis
python Caso2.py    # BFS testing
python Caso4_7.py  # Cases 4-7 (distance, components, diameter)
```

## Dependencies

- Python 3.7+
- Standard library only (`abc`, `collections`, `statistics`)


## Author Notes

- All code is written in English due to personal preference
- Graphs are undirected and support self-loops
- Vertex indices are 1-based (1 to num_vertices)
- Results include execution time measurements for performance analysis
