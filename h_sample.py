# ----------------------------------------------
# Greedy Best-First Search Example
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
# Standard Greedy Best-First Search
# ----------------------------------------------
def greedy_best_first_search(graph, start, goal, heuristic):
    """
    Perform Greedy Best-First Search using only heuristic values.

    Parameters:
        graph: dict - adjacency list of nodes
        start: str - starting node
        goal: str - target node
        heuristic: dict - heuristic values for each node
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

        # Explore neighbors based solely on their heuristic values
        for neighbor in graph[current_node]:
            if neighbor not in visited:
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
def visualize_graph(graph, path, pos):
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

    plt.title("Greedy Best-First Search Path", size=20)
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
    'F': ['K', 'M', 'E'],   # F connects to nodes in multiple branches
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
# Node positions for visualization
# ----------------------------------------------
pos = {
    'A': (0, 0), 'B': (-1, 1), 'C': (1, 1),
    'D': (-1.5, 2), 'E': (-0.5, 2), 'F': (0.5, 2), 'G': (1.5, 2),
    'H': (-2, 3), 'I': (-1, 3), 'J': (0, 3),
    'K': (1, 3), 'L': (2, 3), 'M': (3, 3)
}

# ----------------------------------------------
# Run the greedy best-first search
# ----------------------------------------------
start_node = 'A'
goal_node = 'M'
result_path = greedy_best_first_search(graph, start_node, goal_node, heuristic)

# Print the result
print(f"Path from {start_node} to {goal_node}: {result_path}")

# Visualize the graph and the resulting path
visualize_graph(graph, result_path, pos)
