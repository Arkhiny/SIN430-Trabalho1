from abc import ABC, abstractmethod
from collections import deque
from statistics import median


# Base abstract class for graph implementations.
# It defines common behavior and the required methods for subclasses.
class GraphBase(ABC):
    def __init__(self, num_vertices):
        # Validate number of vertices.
        if num_vertices < 0:
            raise ValueError("Number of vertices must be non-negative.")
        self.num_vertices = num_vertices
        self._num_edges = 0

    # Internal helper to validate if a vertex index is valid (1..num_vertices).
    def _validate_vertex(self, v):
        if not isinstance(v, int) or v < 1 or v > self.num_vertices:
            raise ValueError(
                f"Invalid vertex {v}: vertices must be between 1 and {self.num_vertices}."
            )

    # Add an edge between u and v (implementation depends on representation).
    @abstractmethod
    def add_edge(self, u, v):
        pass

    # Return an iterator over neighbors of vertex v.
    @abstractmethod
    def neighbors(self, v):
        pass

    # Return degree of vertex v.
    @abstractmethod
    def degree(self, v):
        pass

    # Return degree for all vertices.
    def degrees(self):
        return [self.degree(v) for v in range(1, self.num_vertices + 1)]

    # Return number of edges currently in the graph.
    def edge_count(self):
        return self._num_edges


# Graph represented by adjacency list.
class AdjacencyListGraph(GraphBase):
    def __init__(self, num_vertices):
        super().__init__(num_vertices)
        # Dictionary: vertex -> list of adjacent vertices.
        self.adj_list = {i: [] for i in range(1, num_vertices + 1)}

    def add_edge(self, u, v):
        self._validate_vertex(u)
        self._validate_vertex(v)

        # Handle self-loop (u == v).
        if u == v:
            if v not in self.adj_list[u]:
                self.adj_list[u].append(v)
                self._num_edges += 1
            return

        # Undirected graph: add both directions if edge does not already exist.
        if v not in self.adj_list[u]:
            self.adj_list[u].append(v)
            self.adj_list[v].append(u)
            self._num_edges += 1

    def neighbors(self, v):
        self._validate_vertex(v)
        return iter(self.adj_list[v])

    def degree(self, v):
        self._validate_vertex(v)
        return len(self.adj_list[v])


# Graph represented by adjacency matrix.
class AdjacencyMatrixGraph(GraphBase):
    def __init__(self, num_vertices):
        super().__init__(num_vertices)
        # 1-based indexing: row/column 0 are unused.
        self.matrix = [
            [False] * (num_vertices + 1) for _ in range(num_vertices + 1)
        ]

    def add_edge(self, u, v):
        self._validate_vertex(u)
        self._validate_vertex(v)

        # If edge does not exist, add both directions.
        if not self.matrix[u][v]:
            self.matrix[u][v] = True
            self.matrix[v][u] = True
            self._num_edges += 1

    def neighbors(self, v):
        self._validate_vertex(v)
        for w in range(1, self.num_vertices + 1):
            if self.matrix[v][w]:
                yield w

    def degree(self, v):
        self._validate_vertex(v)
        return sum(1 for w in range(1, self.num_vertices + 1) if self.matrix[v][w])


# Backward compatibility alias (old code can still use Graph).
class Graph(AdjacencyListGraph):
    pass


# Factory: create graph using selected representation.
def create_graph(num_vertices, representation="list"):
    rep = representation.strip().lower()

    if rep in ("list", "adjacency_list", "vector"):
        return AdjacencyListGraph(num_vertices)

    if rep in ("matrix", "adjacency_matrix"):
        return AdjacencyMatrixGraph(num_vertices)

    raise ValueError("Invalid representation. Use 'list' or 'matrix'.")


# Format numeric values for report output.
def _format_number(value):
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6f}"
    return str(value)


# Compute min, max, average and median of vertex degrees.
def get_degree_stats(graph):
    degree_list = graph.degrees()
    if not degree_list:
        return 0, 0, 0.0, 0.0

    ordered = sorted(degree_list)
    min_degree = ordered[0]
    max_degree = ordered[-1]
    avg_degree = sum(degree_list) / len(degree_list)
    median_degree = median(ordered)
    return min_degree, max_degree, avg_degree, median_degree


# Find all connected components using BFS.
def get_connected_components(graph):
    visited = set()
    components = []

    for start in range(1, graph.num_vertices + 1):
        if start in visited:
            continue

        # Start BFS from an unvisited vertex.
        queue = deque([start])
        visited.add(start)
        component = []

        while queue:
            current = queue.popleft()
            component.append(current)

            for neighbor in graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # Keep vertices sorted inside each component.
        component.sort()
        components.append(component)

    # Sort components by size (descending).
    components.sort(key=len, reverse=True)
    return components


# Return connected components in summary dictionary format.
def connected_components_summary(graph):
    components = get_connected_components(graph)
    return {
        "num_components": len(components),
        "components": [
            {
                "size": len(component),
                "vertices": component,
            }
            for component in components
        ],
    }


# Write connected components report to file.
def write_connected_components_report(graph, output_file_path):
    summary = connected_components_summary(graph)

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(
            f"# number of connected components = {summary['num_components']}\n"
        )

        for index, component in enumerate(summary["components"], start=1):
            vertices_text = ", ".join(str(v) for v in component["vertices"])
            file.write(f"# component {index}: size = {component['size']}\n")
            file.write(f"# vertices = {vertices_text}\n")


# Read graph from file and generate connected components output file.
def generate_connected_components_file(
    input_graph_path,
    output_file_path="connected_components.txt",
    representation="list",
):
    graph = read_graph_file(input_graph_path, representation=representation)
    if graph is None:
        return False

    write_connected_components_report(graph, output_file_path)
    return True


# Validate BFS/DFS starting vertex.
def _validate_start_vertex(graph, start_vertex):
    if not isinstance(start_vertex, int):
        raise ValueError("Start vertex must be an integer.")
    if start_vertex < 1 or start_vertex > graph.num_vertices:
        raise ValueError(
            f"Invalid start vertex {start_vertex}: must be between 1 and {graph.num_vertices}."
        )


# Build BFS search tree data from a starting vertex.
def bfs_search_tree(graph, start_vertex):
    _validate_start_vertex(graph, start_vertex)

    # parent[v] = predecessor of v in BFS tree.
    parent = {v: None for v in range(1, graph.num_vertices + 1)}
    # level[v] = distance from start vertex (-1 means unreachable).
    level = {v: -1 for v in range(1, graph.num_vertices + 1)}
    # order of visitation.
    order = []

    visited = {start_vertex}
    queue = deque([start_vertex])
    level[start_vertex] = 0

    while queue:
        current = queue.popleft()
        order.append(current)

        # Sort neighbors for deterministic output.
        for neighbor in sorted(graph.neighbors(current)):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                level[neighbor] = level[current] + 1
                queue.append(neighbor)

    return {
        "algorithm": "BFS",
        "start_vertex": start_vertex,
        "num_vertices": graph.num_vertices,
        "parent": parent,
        "level": level,
        "order": order,
    }


# Build DFS search tree data from a starting vertex (iterative).
def dfs_search_tree(graph, start_vertex):
    _validate_start_vertex(graph, start_vertex)

    parent = {v: None for v in range(1, graph.num_vertices + 1)}
    level = {v: -1 for v in range(1, graph.num_vertices + 1)}
    order = []

    discovered = {start_vertex}
    stack = [start_vertex]
    level[start_vertex] = 0

    while stack:
        current = stack.pop()
        order.append(current)

        # Reverse sorted order keeps DFS deterministic with LIFO stack.
        for neighbor in sorted(graph.neighbors(current), reverse=True):
            if neighbor not in discovered:
                discovered.add(neighbor)
                parent[neighbor] = current
                level[neighbor] = level[current] + 1
                stack.append(neighbor)

    return {
        "algorithm": "DFS",
        "start_vertex": start_vertex,
        "num_vertices": graph.num_vertices,
        "parent": parent,
        "level": level,
        "order": order,
    }


# Write BFS/DFS tree information to file.
def write_search_tree(search_tree_data, output_file_path):
    num_vertices = search_tree_data["num_vertices"]
    algorithm = search_tree_data["algorithm"]
    start_vertex = search_tree_data["start_vertex"]
    parent = search_tree_data["parent"]
    level = search_tree_data["level"]

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(f"# algorithm = {algorithm}\n")
        file.write(f"# start_vertex = {start_vertex}\n")

        for vertex in range(1, num_vertices + 1):
            parent_value = parent[vertex]
            level_value = level[vertex]

            parent_text = "-" if parent_value is None else str(parent_value)
            level_text = "-" if level_value == -1 else str(level_value)

            file.write(
                f"Vertex: {vertex}, Parent: {parent_text}, Level: {level_text}\n"
            )


# Generate BFS tree file directly from input graph file.
def generate_bfs_tree_file(
    input_graph_path,
    start_vertex,
    output_file_path="bfs_tree.txt",
    representation="list",
):
    graph = read_graph_file(input_graph_path, representation=representation)
    if graph is None:
        return False

    search_tree_data = bfs_search_tree(graph, start_vertex)
    write_search_tree(search_tree_data, output_file_path)
    return True


# Generate DFS tree file directly from input graph file.
def generate_dfs_tree_file(
    input_graph_path,
    start_vertex,
    output_file_path="dfs_tree.txt",
    representation="list",
):
    graph = read_graph_file(input_graph_path, representation=representation)
    if graph is None:
        return False

    search_tree_data = dfs_search_tree(graph, start_vertex)
    write_search_tree(search_tree_data, output_file_path)
    return True


# Return shortest-path distances from start_vertex to all vertices using BFS.
def bfs_distances(graph, start_vertex):
    _validate_start_vertex(graph, start_vertex)

    distances = {v: -1 for v in range(1, graph.num_vertices + 1)}
    queue = deque([start_vertex])
    distances[start_vertex] = 0

    while queue:
        current = queue.popleft()

        for neighbor in graph.neighbors(current):
            if distances[neighbor] == -1:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances


# Return shortest distance between source and target vertices.
def shortest_distance(graph, source_vertex, target_vertex):
    _validate_start_vertex(graph, source_vertex)
    _validate_start_vertex(graph, target_vertex)

    distances = bfs_distances(graph, source_vertex)
    return distances[target_vertex]


# Compute graph diameter (max shortest-path distance between any two vertices).
# Returns None if graph is disconnected.
def graph_diameter(graph):
    if graph.num_vertices == 0:
        return 0

    max_shortest_path = 0
    is_disconnected = False

    for vertex in range(1, graph.num_vertices + 1):
        distances = bfs_distances(graph, vertex)

        # If any vertex is unreachable, graph is disconnected.
        if any(distance == -1 for distance in distances.values()):
            is_disconnected = True

        # Farthest reachable vertex from current source.
        farthest_reachable = max(
            (distance for distance in distances.values() if distance != -1),
            default=0,
        )
        if farthest_reachable > max_shortest_path:
            max_shortest_path = farthest_reachable

    if is_disconnected:
        return None

    return max_shortest_path


# Write shortest distance and diameter report.
def write_distance_and_diameter_report(
    graph,
    source_vertex,
    target_vertex,
    output_file_path,
):
    distance = shortest_distance(graph, source_vertex, target_vertex)
    diameter = graph_diameter(graph)

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(f"# source_vertex = {source_vertex}\n")
        file.write(f"# target_vertex = {target_vertex}\n")

        if distance == -1:
            file.write("# distance = unreachable\n")
        else:
            file.write(f"# distance = {distance}\n")

        if diameter is None:
            file.write("# diameter = undefined (graph is disconnected)\n")
        else:
            file.write(f"# diameter = {diameter}\n")


# Read graph and generate distance+diameter report file.
def generate_distance_and_diameter_file(
    input_graph_path,
    source_vertex,
    target_vertex,
    output_file_path="distance_diameter.txt",
    representation="list",
):
    graph = read_graph_file(input_graph_path, representation=representation)
    if graph is None:
        return False

    write_distance_and_diameter_report(
        graph=graph,
        source_vertex=source_vertex,
        target_vertex=target_vertex,
        output_file_path=output_file_path,
    )
    return True


# Build dictionary with general graph report information.
def build_graph_report_data(graph):
    min_degree, max_degree, avg_degree, median_degree = get_degree_stats(graph)
    components = get_connected_components(graph)

    return {
        "n": graph.num_vertices,
        "m": graph.edge_count(),
        "g_min": min_degree,
        "g_max": max_degree,
        "g_avg": avg_degree,
        "median": median_degree,
        "num_components": len(components),
        "components": components,
    }


# Write general graph report to file.
def write_graph_report(graph, output_file_path):
    data = build_graph_report_data(graph)

    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(f"# n = {data['n']}\n")
        file.write(f"# m = {data['m']}\n")
        file.write(f"# g_max = {data['g_max']}\n")
        file.write(f"# g_min = {data['g_min']}\n")
        file.write(f"# g_avg = {_format_number(data['g_avg'])}\n")
        file.write(f"# median = {_format_number(data['median'])}\n")
        file.write(f"# number of connected components = {data['num_components']}\n")

        for index, component in enumerate(data["components"], start=1):
            vertices = ", ".join(str(v) for v in component)
            file.write(f"# component {index}: size = {len(component)}\n")
            file.write(f"# vertices = {vertices}\n")


# Read graph from text file.
# Expected format:
#   line 1: number of vertices (n)
#   next lines: "u v" for each edge
def read_graph_file(file_path, representation="list"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            first_line = file.readline().strip()
            if not first_line:
                raise ValueError("The first line must contain the number of vertices.")

            num_vertices = int(first_line)
            graph = create_graph(num_vertices, representation=representation)

            for line_number, line in enumerate(file, start=2):
                line = line.strip()
                if not line:
                    continue

                values = line.split()
                if len(values) < 2:
                    raise ValueError(
                        f"Invalid line {line_number}: expected format 'u v'."
                    )

                u, v = map(int, values[:2])
                graph.add_edge(u, v)

            return graph

    except FileNotFoundError:
        print(f"Error: file '{file_path}' was not found.")
        return None
    except ValueError as error:
        print(f"Error while reading file '{file_path}': {error}")
        return None


# Generate full graph info report from an input graph file.
def generate_info_file(
    input_graph_path, output_info_path="info.txt", representation="list"
):
    graph = read_graph_file(input_graph_path, representation=representation)
    if graph is None:
        return False

    write_graph_report(graph, output_info_path)
    return True
