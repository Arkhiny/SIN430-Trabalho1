from pathlib import Path
from random import Random
from time import perf_counter
import gc

from Grafos import bfs_distances, read_graph_file


NUM_SEARCH_RUNS = 100
RANDOM_SEED = 42
SECONDS_TO_MS = 1000.0
BACK_OPTION = "back"
EXIT_OPTION = "exit"


def choose_graph_option():
    print("Select the graph file for Case 2:")
    for option in range(1, 7):
        print(f"  {option}. grafo_{option}.txt")
    print("  7. Exit")

    while True:
        raw_value = input("Enter an option from 1 to 7: ").strip()
        if raw_value.isdigit():
            option = int(raw_value)
            if 1 <= option <= 6:
                return option
            if option == 7:
                return EXIT_OPTION

        print("Invalid option. Please enter a number between 1 and 7.")


def choose_representation_option(graph_option):
    print(f"\nSelected graph: grafo_{graph_option}.txt")
    print("Choose the graph representation:")
    print("  1. Adjacency List")
    print("  2. Adjacency Matrix")
    print("  3. Back to graph selection")
    print("  4. Exit")

    while True:
        raw_value = input("Enter an option from 1 to 4: ").strip()

        if raw_value == "1":
            return "list"
        if raw_value == "2":
            return "matrix"
        if raw_value == "3":
            return BACK_OPTION
        if raw_value == "4":
            return EXIT_OPTION

        print("Invalid option. Please enter a number between 1 and 4.")


def choose_search_type_option(graph_option, representation):
    print(f"\nSelected graph: grafo_{graph_option}.txt")
    print(f"Selected representation: {representation_label(representation)}")
    print("Choose the search type:")
    print("  1. Breadth-First Search (BFS)")
    print("  2. Depth-First Search (DFS)")
    print("  3. Back to representation selection")
    print("  4. Exit")

    while True:
        raw_value = input("Enter an option from 1 to 4: ").strip()

        if raw_value == "1":
            return "bfs"
        if raw_value == "2":
            return "dfs"
        if raw_value == "3":
            return BACK_OPTION
        if raw_value == "4":
            return EXIT_OPTION

        print("Invalid option. Please enter a number between 1 and 4.")


def get_graph_file(graph_option):
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "Data" / f"grafo_{graph_option}.txt",
        base_dir / "data" / f"grafo_{graph_option}.txt",
    ]

    for file_path in candidates:
        if file_path.exists():
            return file_path

    raise FileNotFoundError(
        f"Could not find grafo_{graph_option}.txt in Data/ or data/."
    )


def read_num_vertices(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        first_line = file.readline().strip()
        if not first_line:
            raise ValueError("The first line must contain the number of vertices.")
        return int(first_line)


def select_start_vertices(num_vertices, num_runs=NUM_SEARCH_RUNS):
    if num_vertices < num_runs:
        raise ValueError(
            f"Graph has {num_vertices} vertices, but {num_runs} distinct start "
            "vertices are required."
        )

    rng = Random(RANDOM_SEED)
    return rng.sample(range(1, num_vertices + 1), num_runs)


def run_depth_first_search(graph, start_vertex):
    visited = {start_vertex}
    stack = [start_vertex]

    while stack:
        current_vertex = stack.pop()

        for neighbor in graph.neighbors(current_vertex):
            if neighbor not in visited:
                visited.add(neighbor)
                stack.append(neighbor)

    return visited


def execute_search(graph, start_vertex, search_type):
    if search_type == "bfs":
        bfs_distances(graph, start_vertex)
        return

    if search_type == "dfs":
        run_depth_first_search(graph, start_vertex)
        return

    raise ValueError("Invalid search type. Use 'bfs' or 'dfs'.")


def benchmark_search(graph, start_vertices, search_type):
    elapsed_times_s = []

    for start_vertex in start_vertices:
        start_time = perf_counter()
        execute_search(graph, start_vertex, search_type)
        end_time = perf_counter()
        elapsed_times_s.append(end_time - start_time)

    total_s = sum(elapsed_times_s)
    avg_s = total_s / len(elapsed_times_s)

    return {
        "runs": len(elapsed_times_s),
        "total_s": total_s,
        "avg_s": avg_s,
        "total_ms": total_s * SECONDS_TO_MS,
        "avg_ms": avg_s * SECONDS_TO_MS,
    }


def representation_label(representation):
    return "Adjacency Matrix" if representation == "matrix" else "Adjacency List"


def search_type_label(search_type):
    return (
        "Breadth-First Search (BFS)"
        if search_type == "bfs"
        else "Depth-First Search (DFS)"
    )


def run_representation_benchmark(
    graph_file,
    representation,
    search_type,
    start_vertices,
):
    graph = None
    gc.collect()

    try:
        graph = read_graph_file(graph_file, representation=representation)
        if graph is None:
            return {
                "representation": representation,
                "search_type": search_type,
                "error": "Failed to load graph from input file.",
            }

        timing = benchmark_search(graph, start_vertices, search_type)

        return {
            "representation": representation,
            "search_type": search_type,
            "num_vertices": graph.num_vertices,
            "num_edges": graph.edge_count(),
            "runs": timing["runs"],
            "total_s": timing["total_s"],
            "avg_s": timing["avg_s"],
            "total_ms": timing["total_ms"],
            "avg_ms": timing["avg_ms"],
            "error": None,
        }

    except MemoryError:
        return {
            "representation": representation,
            "search_type": search_type,
            "error": "MemoryError while processing this representation.",
        }

    finally:
        del graph
        gc.collect()


def result_to_text_lines(result):
    lines = [
        f"Search type: {search_type_label(result['search_type'])}",
        f"Graph representation: {representation_label(result['representation'])}",
    ]

    if result["error"]:
        lines.append(f"  Error: {result['error']}")
        return lines

    lines.append(f"  Vertices: {result['num_vertices']}")
    lines.append(f"  Edges: {result['num_edges']}")
    lines.append(f"  Search runs: {result['runs']}")
    lines.append(f"  Total time: {result['total_ms']:.3f} ms")
    lines.append(f"  Average time per search: {result['avg_ms']:.3f} ms")
    return lines


def start_vertices_preview(start_vertices, preview_size=15):
    if len(start_vertices) <= preview_size:
        return ", ".join(str(v) for v in start_vertices)

    prefix = ", ".join(str(v) for v in start_vertices[:preview_size])
    return f"{prefix}, ... (total {len(start_vertices)} start vertices)"


def build_report_text(graph_file, start_vertices, result):
    lines = [
        "Graph search execution-time report",
        f"Graph source: {graph_file}",
        f"Search type: {search_type_label(result['search_type'])}",
        f"Graph representation: {representation_label(result['representation'])}",
        f"Search runs: {NUM_SEARCH_RUNS}",
        f"Random seed used for start vertices: {RANDOM_SEED}",
        f"Start vertices: {start_vertices_preview(start_vertices)}",
        "",
    ]

    lines.extend(result_to_text_lines(result))

    return "\n".join(lines) + "\n"


def save_report(report_text, graph_option, representation, search_type):
    target_dir_name = "caso2" if search_type == "bfs" else "caso3"
    target_dir = Path(__file__).resolve().parent / target_dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        target_dir
        / f"{search_type}_grafo_{graph_option}_{representation}.txt"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_text)

    return output_path


def print_result(result):
    print(f"Search type: {search_type_label(result['search_type'])}")
    print(f"Graph representation: {representation_label(result['representation'])}")
    if result["error"]:
        print(f"  Error: {result['error']}")
        return

    print(f"  Vertices: {result['num_vertices']}")
    print(f"  Edges: {result['num_edges']}")
    print(f"  Search runs: {result['runs']}")
    print(f"  Total time: {result['total_ms']:.3f} ms")
    print(f"  Average time per search: {result['avg_ms']:.3f} ms")


def run_case_2(graph_option, representation, search_type):
    try:
        graph_file = get_graph_file(graph_option)
        num_vertices = read_num_vertices(graph_file)
        start_vertices = select_start_vertices(num_vertices, NUM_SEARCH_RUNS)
    except Exception as error:
        print(f"Failed to prepare benchmark: {error}")
        return

    print(f"\nGraph source: {graph_file}")
    print(f"Number of vertices: {num_vertices}")
    print(f"Representation: {representation_label(representation)}")
    print(f"Search type: {search_type_label(search_type)}")
    print(f"Search runs: {NUM_SEARCH_RUNS}\n")

    result = run_representation_benchmark(
        graph_file=graph_file,
        representation=representation,
        search_type=search_type,
        start_vertices=start_vertices,
    )

    print_result(result)

    report_text = build_report_text(
        graph_file=graph_file,
        start_vertices=start_vertices,
        result=result,
    )
    output_path = save_report(
        report_text,
        graph_option=graph_option,
        representation=representation,
        search_type=search_type,
    )
    print(f"\nText report saved to: {output_path}")


def main():
    while True:
        graph_option = choose_graph_option()
        if graph_option == EXIT_OPTION:
            break

        while True:
            representation = choose_representation_option(graph_option)
            if representation == EXIT_OPTION:
                print("\nProgram finished.")
                input("Press Enter to continue and close the process...")
                return
            if representation == BACK_OPTION:
                break

            while True:
                search_type = choose_search_type_option(
                    graph_option,
                    representation,
                )
                if search_type == EXIT_OPTION:
                    print("\nProgram finished.")
                    input("Press Enter to continue and close the process...")
                    return
                if search_type == BACK_OPTION:
                    break

                run_case_2(
                    graph_option=graph_option,
                    representation=representation,
                    search_type=search_type,
                )

    print("\nProgram finished.")
    input("Press Enter to continue and close the process...")


if __name__ == "__main__":
    main()