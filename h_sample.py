# ----------------------------------------------
# Greedy Best-First Search for Hierarchical Routing
# https://www.geeksforgeeks.org/artificial-intelligence/greedy-best-first-search-in-ai/
# ----------------------------------------------

import heapq               # For implementing the priority queue (min-heap)
import networkx as nx      # For graph visualization
import matplotlib.pyplot as plt   # For plotting the graph


# ----------------------------------------------
# Node class to store a node's name and heuristic value
# ----------------------------------------------
class Node:
    def __init__(self, name, heuristic):
        self.name = name              # The name (or label) of the node
        self.heuristic = heuristic    # The heuristic value (used to prioritize nodes)

    # Define comparison rule for priority queue (heapq)
    def __lt__(self, other):
        return self.heuristic > other.heuristic


# ----------------------------------------------
# Greedy Best-First Search with Hierarchical Regions
# ----------------------------------------------
def greedy_best_first_search_hierarchical(graph, start, goal, heuristic, region_map):
    """
    Perform Greedy Best-First Search considering regions.
    Nodes within the same region are prioritized before exploring other regions.

    Parameters:
        graph: dict - adjacency list of nodes
        start: str - starting node
        goal: str - target node
        heuristic: dict - heuristic values for each node
        region_map: dict - maps each node to a region ID
    """
    # Initialize priority queue with the start node (using its heuristic as priority)
    priority_queue = []
    heapq.heappush(priority_queue, Node(start, heuristic[start]))

    visited = set()          # To track visited nodes
    path = {start: None}     # To reconstruct the final path later

    # Continue exploring while there are nodes in the queue
    while priority_queue:
        # Pop the node with the smallest heuristic value
        current_node = heapq.heappop(priority_queue).name

        # Goal test: stop when we reach the target
        if current_node == goal:
            return reconstruct_path(path, start, goal)

        # Mark current node as visited
        visited.add(current_node)

        # Identify current region of the node
        current_region = region_map[current_node]

        # -------------------------------
        # Phase 1: Explore neighbors in the same region first
        # -------------------------------
        for neighbor in graph[current_node]:
            if neighbor not in visited and region_map[neighbor] == current_region:
                heapq.heappush(priority_queue, Node(neighbor, heuristic[neighbor]))
                if neighbor not in path:
                    path[neighbor] = current_node

        # -------------------------------
        # Phase 2: Then explore neighbors from different regions
        # -------------------------------
        for neighbor in graph[current_node]:
            if neighbor not in visited and region_map[neighbor] != current_region:
                heapq.heappush(priority_queue, Node(neighbor, heuristic[neighbor]))
                if neighbor not in path:
                    path[neighbor] = current_node

    # If goal not reached, return None
    return None


# ----------------------------------------------
# Reconstruct the path from start to goal using parent mapping
# ----------------------------------------------
def reconstruct_path(path, start, goal):
    current = goal
    result_path = []

    # Backtrack from goal to start
    while current is not None:
        result_path.append(current)
        current = path[current]

    # Reverse the list to get correct order: start → goal
    result_path.reverse()
    return result_path


# ----------------------------------------------
# Visualize the graph and highlight the final path
# ----------------------------------------------
def visualize_graph(graph, path, pos, region_map):
    G = nx.Graph()

    # Build edges from the adjacency list
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)

    # Draw the full graph
    plt.figure(figsize=(10, 8))
    nx.draw(
        G, pos, with_labels=True,
        node_size=4000, node_color='skyblue',
        font_size=15, font_weight='bold',
        edge_color='gray'
    )

    # Highlight the found path in green
    if path:
        path_edges = list(zip(path, path[1:]))  # Pairwise edges along path
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='green', width=3)
        nx.draw_networkx_nodes(G, pos, nodelist=path, node_color='lightgreen')

    # Annotate nodes with their region IDs below their labels
    for node, region in region_map.items():
        plt.text(pos[node][0], pos[node][1] - 0.2, f"Region {region}", fontsize=12, color='black')

    plt.title("Greedy Best-First Search for Hierarchical Routing", size=20)
    plt.show()


# ----------------------------------------------
# Graph Definition (Adjacency List)
# ----------------------------------------------
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F', 'G'],
    'D': ['H'],
    'E': ['I', 'J'],
    'F': ['K', 'M', 'E'],   # F connects across regions
    'G': ['L', 'M'],
    'H': [], 'I': [], 'J': [], 'K': [], 'L': [], 'M': []
}

# ----------------------------------------------
# Heuristic values (e.g., estimated distance to goal)
# ----------------------------------------------
heuristic = {
    'A': 8, 'B': 6, 'C': 7, 'D': 5, 'E': 4, 'F': 5,
    'G': 4, 'H': 3, 'I': 2, 'J': 1, 'K': 3, 'L': 2, 'M': 1
}

# ----------------------------------------------
# Region mapping for hierarchical search
# ----------------------------------------------
region_map = {
    'A': 1, 'B': 1, 'C': 1,   # Region 1
    'D': 2, 'E': 2,           # Region 2
    'F': 3, 'G': 3,           # Region 3
    'H': 2, 'I': 2, 'J': 2,   # Region 2
    'K': 3, 'L': 3, 'M': 3    # Region 3
}

# ----------------------------------------------
# Node positions for visualization
# ----------------------------------------------
pos = {
    'A': (0, 0), 'B': (-1, 1), 'C': (1, 1),
    'D': (-1.5, 2), 'E': (-0.5, 2), 'F': (0.5, 2), 'G': (1.5, 2),
    'H': (-2, 3), 'I': (-1, 3), 'J': (0, 3),
    'K': (1, 3), 'L': (2, 3), 'M': (3, 3)
}

# ----------------------------------------------
# Run the hierarchical greedy best-first search
# ----------------------------------------------
start_node = 'A'
goal_node = 'M'
result_path = greedy_best_first_search_hierarchical(graph, start_node, goal_node, heuristic, region_map)

# Print the result
print(f"Path from {start_node} to {goal_node}: {result_path}")

# Visualize the graph and the resulting path
visualize_graph(graph, result_path, pos, region_map)
