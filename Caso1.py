from pathlib import Path
import gc
import tracemalloc

from Grafos import create_graph


BYTES_IN_MB = 1024 * 1024


def load_edges(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        first_line = file.readline().strip()
        if not first_line:
            raise ValueError("The first line must contain the number of vertices.")

        num_vertices = int(first_line)
        edges = []

        for line_number, line in enumerate(file, start=2):
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 2:
                raise ValueError(
                    f"Invalid line {line_number}: expected format 'u v'."
                )

            u, v = map(int, parts[:2])
            edges.append((u, v))

    return num_vertices, edges


def measure_memory(num_vertices, edges, representation):
    graph = None
    gc.collect()
    tracemalloc.start()

    try:
        graph = create_graph(num_vertices, representation=representation)

        for u, v in edges:
            graph.add_edge(u, v)

        gc.collect()
        current_bytes, peak_bytes = tracemalloc.get_traced_memory()

        return {
            "representation": representation,
            "num_vertices": graph.num_vertices,
            "num_edges": graph.edge_count(),
            "current_mb": current_bytes / BYTES_IN_MB,
            "peak_mb": peak_bytes / BYTES_IN_MB,
            "error": None,
        }

    except MemoryError:
        return {
            "representation": representation,
            "num_vertices": num_vertices,
            "num_edges": None,
            "current_mb": None,
            "peak_mb": None,
            "error": "MemoryError while building this representation.",
        }

    finally:
        tracemalloc.stop()
        del graph
        gc.collect()


def choose_graph_option():
    print("Select the graph file to test:")
    for option in range(1, 7):
        print(f"  {option}. grafo_{option}.txt")
    print("  7. Exit")

    while True:
        raw_value = input("Enter an option from 1 to 7: ").strip()
        if raw_value.isdigit():
            option = int(raw_value)
            if 1 <= option <= 7:
                return option

        print("Invalid option. Please enter a number between 1 and 7.")


def choose_representation_option():
    print("\nSelect the representation to test:")
    print("  1. Adjacency List")
    print("  2. Adjacency Matrix")

    while True:
        raw_value = input("Enter 1 for list or 2 for matrix: ").strip()
        if raw_value == "1":
            return "list"
        if raw_value == "2":
            return "matrix"

        print("Invalid option. Please enter 1 or 2.")


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


def result_to_text_lines(result):
    name = (
        "Adjacency Matrix"
        if result["representation"] == "matrix"
        else "Adjacency List"
    )

    lines = [f"{name}:"]
    if result["error"]:
        lines.append(f"  Error: {result['error']}")
        return lines

    lines.append(f"  Vertices: {result['num_vertices']}")
    lines.append(f"  Edges: {result['num_edges']}")
    lines.append(f"  Memory in use after load: {result['current_mb']:.2f} MB")
    lines.append(f"  Peak memory during load: {result['peak_mb']:.2f} MB")
    return lines


def build_report_text(
    graph_file,
    num_vertices,
    num_edges,
    result,
):
    lines = [
        f"Graph source: {graph_file}",
        f"Input summary: {num_vertices} vertices, {num_edges} edges",
        "",
    ]

    lines.extend(result_to_text_lines(result))

    return "\n".join(lines) + "\n"


def save_report(report_text, graph_option, representation):
    output_path = (
        Path(__file__).resolve().parent
        / f"memory_report_grafo_{graph_option}_{representation}.txt"
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(report_text)

    return output_path


def print_result(result):
    name = (
        "Adjacency Matrix"
        if result["representation"] == "matrix"
        else "Adjacency List"
    )

    print(f"{name}:")
    if result["error"]:
        print(f"  Error: {result['error']}")
        return

    print(f"  Vertices: {result['num_vertices']}")
    print(f"  Edges: {result['num_edges']}")
    print(f"  Memory in use after load: {result['current_mb']:.2f} MB")
    print(f"  Peak memory during load: {result['peak_mb']:.2f} MB")


def run_single_test(graph_option, representation):
    try:
        graph_file = get_graph_file(graph_option)
        num_vertices, edges = load_edges(graph_file)
    except Exception as error:
        print(f"Failed to load graph input: {error}")
        return

    print(f"Graph source: {graph_file}")
    print(f"Input summary: {num_vertices} vertices, {len(edges)} edges\n")

    result = measure_memory(
        num_vertices=num_vertices,
        edges=edges,
        representation=representation,
    )
    print_result(result)

    report_text = build_report_text(
        graph_file=graph_file,
        num_vertices=num_vertices,
        num_edges=len(edges),
        result=result,
    )
    output_path = save_report(report_text, graph_option, representation)
    print(f"\nText report saved to: {output_path}")


def should_run_another_test():
    while True:
        answer = input("\nRun another test? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False

        print("Invalid option. Please enter 'y' or 'n'.")


def main():
    while True:
        graph_option = choose_graph_option()
        if graph_option == 7:
            break

        representation = choose_representation_option()
        print()

        run_single_test(graph_option, representation)

    print("\nProgram finished.")
    input("Press Enter to continue and close the process...")


if __name__ == "__main__":
    main()