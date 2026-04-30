from pathlib import Path
from random import Random
import gc

from Grafos import (
	bfs_distances,
	bfs_search_tree,
	connected_components_summary,
	dfs_search_tree,
	graph_diameter,
	read_graph_file,
	shortest_distance,
)


START_VERTICES = (1, 2, 3)
TARGET_VERTICES = (10, 20, 30)
DISTANCE_PAIRS = ((10, 20), (10, 30), (20, 30))

APPROX_START_SAMPLES = 8
APPROX_RANDOM_SEED = 42
EXACT_DIAMETER_VERTEX_LIMIT = 50000

BACK_OPTION = "back"
EXIT_OPTION = "exit"


def choose_graph_option():
	print("Select the graph file:")
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


def choose_analysis_option(graph_option, representation):
	print(f"\nSelected graph: grafo_{graph_option}.txt")
	print(f"Selected representation: {representation_label(representation)}")
	print("Choose an analysis:")
	print("  1. BFS/DFS parents for vertices 10, 20, 30")
	print("  2. Distances for pairs (10,20), (10,30), (20,30)")
	print("  3. Connected components summary")
	print("  4. Exact diameter")
	print("  5. Approximate diameter")
	print("  6. Back to representation selection")
	print("  7. Exit")

	while True:
		raw_value = input("Enter an option from 1 to 7: ").strip()

		if raw_value == "1":
			return "task4"
		if raw_value == "2":
			return "task5"
		if raw_value == "3":
			return "task6"
		if raw_value == "4":
			return "task7_exact"
		if raw_value == "5":
			return "task7_approx"
		if raw_value == "6":
			return BACK_OPTION
		if raw_value == "7":
			return EXIT_OPTION

		print("Invalid option. Please enter a number between 1 and 7.")


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


def load_graph(graph_option, representation):
	graph_file = get_graph_file(graph_option)
	graph = read_graph_file(graph_file, representation=representation)

	if graph is None:
		raise ValueError("Failed to load graph from input file.")

	return graph_file, graph


def representation_label(representation):
	return "Adjacency Matrix" if representation == "matrix" else "Adjacency List"


def validate_required_vertices(graph, vertices):
	missing = sorted(
		vertex
		for vertex in set(vertices)
		if vertex < 1 or vertex > graph.num_vertices
	)
	if missing:
		raise ValueError(
			"Graph does not contain all required vertices. "
			f"Current vertex range is 1..{graph.num_vertices}. "
			f"Missing required vertices: {missing}."
		)


def format_parent(parent_value):
	return "-" if parent_value is None else str(parent_value)


def analyze_task_4_parents(graph):
	validate_required_vertices(graph, START_VERTICES + TARGET_VERTICES)

	lines = [
		"Task 4 - Parent vertices in BFS and DFS trees",
		f"Start vertices: {', '.join(str(v) for v in START_VERTICES)}",
		f"Target vertices: {', '.join(str(v) for v in TARGET_VERTICES)}",
		"",
	]

	for start_vertex in START_VERTICES:
		bfs_data = bfs_search_tree(graph, start_vertex)
		dfs_data = dfs_search_tree(graph, start_vertex)

		lines.append(f"Start vertex {start_vertex}:")
		lines.append("  Vertex | BFS parent | DFS parent")

		for target_vertex in TARGET_VERTICES:
			bfs_parent = format_parent(bfs_data["parent"][target_vertex])
			dfs_parent = format_parent(dfs_data["parent"][target_vertex])
			lines.append(
				f"  {target_vertex:>6} | {bfs_parent:>10} | {dfs_parent:>10}"
			)

		lines.append("")

	return "\n".join(lines).rstrip() + "\n"


def analyze_task_5_distances(graph):
	vertices_in_pairs = tuple(
		vertex for pair in DISTANCE_PAIRS for vertex in pair
	)
	validate_required_vertices(graph, vertices_in_pairs)

	lines = [
		"Task 5 - Distances between selected vertex pairs",
		"",
	]

	for source_vertex, target_vertex in DISTANCE_PAIRS:
		distance = shortest_distance(graph, source_vertex, target_vertex)
		distance_text = "unreachable" if distance == -1 else str(distance)
		lines.append(
			f"Distance({source_vertex}, {target_vertex}) = {distance_text}"
		)

	return "\n".join(lines) + "\n"


def analyze_task_6_components(graph):
	summary = connected_components_summary(graph)
	num_components = summary["num_components"]
	sizes = [component["size"] for component in summary["components"]]

	largest_size = max(sizes, default=0)
	smallest_size = min(sizes, default=0)

	lines = [
		"Task 6 - Connected components",
		f"Number of connected components: {num_components}",
		f"Largest component size: {largest_size}",
		f"Smallest component size: {smallest_size}",
	]

	if num_components > 0:
		preview_limit = 12
		preview_sizes = sizes[:preview_limit]
		preview_text = ", ".join(str(size) for size in preview_sizes)
		if num_components > preview_limit:
			preview_text += ", ..."

		lines.append(f"Component sizes preview: {preview_text}")

	return "\n".join(lines) + "\n"


def farthest_vertex_with_distance(graph, start_vertex):
	distances = bfs_distances(graph, start_vertex)
	farthest_vertex = start_vertex
	farthest_distance = 0

	for vertex, distance in distances.items():
		if distance > farthest_distance:
			farthest_distance = distance
			farthest_vertex = vertex

	return farthest_vertex, farthest_distance


def approximate_diameter(
	graph,
	sample_count=APPROX_START_SAMPLES,
	seed=APPROX_RANDOM_SEED,
):
	if graph.num_vertices == 0:
		return {
			"estimate": 0,
			"best_pair": (None, None),
			"num_samples": 0,
			"sweep_results": [],
		}

	all_vertices = list(range(1, graph.num_vertices + 1))
	random_generator = Random(seed)

	num_samples = min(sample_count, graph.num_vertices)
	sampled_starts = random_generator.sample(all_vertices, num_samples)

	if 1 <= graph.num_vertices and 1 not in sampled_starts:
		sampled_starts[0] = 1

	best_estimate = 0
	best_pair = (sampled_starts[0], sampled_starts[0])
	sweep_results = []

	for start_vertex in sampled_starts:
		first_far, first_dist = farthest_vertex_with_distance(graph, start_vertex)
		second_far, second_dist = farthest_vertex_with_distance(graph, first_far)

		sweep_results.append(
			{
				"start": start_vertex,
				"first_far": first_far,
				"first_dist": first_dist,
				"second_far": second_far,
				"second_dist": second_dist,
			}
		)

		if second_dist > best_estimate:
			best_estimate = second_dist
			best_pair = (first_far, second_far)

	return {
		"estimate": best_estimate,
		"best_pair": best_pair,
		"num_samples": num_samples,
		"sweep_results": sweep_results,
	}


def analyze_task_7_exact_diameter(graph):
	lines = ["Task 7 - Exact diameter"]

	if graph.num_vertices > EXACT_DIAMETER_VERTEX_LIMIT:
		lines.append(
			"Exact diameter was skipped for this graph size because it is "
			f"expensive for large graphs (limit: {EXACT_DIAMETER_VERTEX_LIMIT} "
			f"vertices, current: {graph.num_vertices})."
		)
		lines.append("Use the approximate diameter option for large graphs.")
		return "\n".join(lines) + "\n"

	diameter = graph_diameter(graph)
	if diameter is None:
		lines.append("Diameter is undefined because the graph is disconnected.")
	else:
		lines.append(f"Exact diameter: {diameter}")

	return "\n".join(lines) + "\n"


def analyze_task_7_approximate_diameter(graph):
	result = approximate_diameter(graph)

	lines = [
		"Task 7 - Approximate diameter",
		f"Estimated diameter (lower bound): {result['estimate']}",
		(
			"Best endpoint pair from sweeps: "
			f"({result['best_pair'][0]}, {result['best_pair'][1]})"
		),
		f"Number of sampled starts: {result['num_samples']}",
		f"Random seed: {APPROX_RANDOM_SEED}",
	]

	if result["sweep_results"]:
		preview_limit = 8
		lines.append("Sweep preview:")

		for item in result["sweep_results"][:preview_limit]:
			lines.append(
				"  "
				f"start={item['start']} -> far={item['first_far']} "
				f"(dist={item['first_dist']}), then far={item['second_far']} "
				f"(dist={item['second_dist']})"
			)

		if len(result["sweep_results"]) > preview_limit:
			lines.append("  ...")

	return "\n".join(lines) + "\n"


def build_header(graph_file, representation):
	return (
		"Case 4-7 report\n"
		f"Graph source: {graph_file}\n"
		f"Representation: {representation_label(representation)}\n\n"
	)


def output_folder_for_action(action_name):
	if action_name.startswith("task4"):
		return "caso4"
	if action_name.startswith("task5"):
		return "caso5"
	if action_name.startswith("task6"):
		return "caso6"
	if action_name.startswith("task7"):
		return "caso7"

	return "caso4_7"


def save_report(report_text, graph_option, representation, action_name):
	output_dir = (
		Path(__file__).resolve().parent
		/ output_folder_for_action(action_name)
	)
	output_dir.mkdir(parents=True, exist_ok=True)

	output_file = (
		output_dir / f"{action_name}_grafo_{graph_option}_{representation}.txt"
	)

	with open(output_file, "w", encoding="utf-8") as file:
		file.write(report_text)

	return output_file


def run_single_analysis(graph, graph_file, graph_option, representation, option):
	analysis_map = {
		"task4": (
			"task4_parents",
			analyze_task_4_parents,
		),
		"task5": (
			"task5_distances",
			analyze_task_5_distances,
		),
		"task6": (
			"task6_components",
			analyze_task_6_components,
		),
		"task7_exact": (
			"task7_exact_diameter",
			analyze_task_7_exact_diameter,
		),
		"task7_approx": (
			"task7_approx_diameter",
			analyze_task_7_approximate_diameter,
		),
	}

	action_name, action_function = analysis_map[option]

	body_text = action_function(graph)
	report_text = build_header(graph_file, representation) + body_text

	print("\n" + body_text.rstrip())

	output_file = save_report(
		report_text=report_text,
		graph_option=graph_option,
		representation=representation,
		action_name=action_name,
	)
	print(f"\nText report saved to: {output_file}")


def run_selected_option(graph, graph_file, graph_option, representation, option):
	run_single_analysis(graph, graph_file, graph_option, representation, option)


def finish_program():
	print("\nProgram finished.")
	input("Press Enter to continue and close the process...")


def main():
	while True:
		graph_option = choose_graph_option()
		if graph_option == EXIT_OPTION:
			break

		while True:
			representation = choose_representation_option(graph_option)
			if representation == EXIT_OPTION:
				finish_program()
				return
			if representation == BACK_OPTION:
				break

			try:
				graph_file, graph = load_graph(graph_option, representation)
			except Exception as error:
				print(f"\nFailed to load graph: {error}")
				continue

			try:
				while True:
					option = choose_analysis_option(graph_option, representation)
					if option == EXIT_OPTION:
						finish_program()
						return
					if option == BACK_OPTION:
						break

					run_selected_option(
						graph=graph,
						graph_file=graph_file,
						graph_option=graph_option,
						representation=representation,
						option=option,
					)
			finally:
				del graph
				gc.collect()

	finish_program()


if __name__ == "__main__":
	main()
