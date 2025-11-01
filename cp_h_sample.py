# ----------------------------------------------
# Greedy Best-First Search Example
# https://www.geeksforgeeks.org/artificial-intelligence/greedy-best-first-search-in-ai/
# ----------------------------------------------
import time
import heapq
import pickle
import networkx as nx      # For graph visualization
import matplotlib.pyplot as plt   # For plotting the graph
from h import analyze_graph
from prog import check_similarity

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
    # Resolve the textual goal description into an actual node in the graph.
    # We only need to run the similarity check once; doing so inside the main
    # loop forced us to rescan the entire graph on every iteration, effectively
    # stalling the search when a match was found.
    resolved_goal = check_similarity(graph, goal, heuristic)
    if not resolved_goal:
        return None

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
        if current_node == resolved_goal:
            return reconstruct_path(path, resolved_goal)

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
def reconstruct_path(path, goal):
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
    # for node, neighbors in graph.items():
    for node, neighbors in graph.adjacency():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)

    # Draw the full graph
    plt.figure(figsize=(10, 8))
    nx.draw(
        G, pos, with_labels=True,
        node_size=4000, node_color='skyblue',
        font_size=6, font_weight='bold',
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
# with open("crawled_graph1.gpickle", "rb") as f: # Depth = 1 
with open("crawled_graph2.gpickle", "rb") as f: # Depth = 2 
    graph = pickle.load(f)

# ----------------------------------------------
# Heuristic values (e.g., estimated distance to goal)
# ----------------------------------------------
# goal_node = 'Autonomous Vehicular Networks'
goal_node = 'iReview'

heuristic = analyze_graph(graph, goal_node)

# ----------------------------------------------
# Node positions for visualization
# ----------------------------------------------
pos = nx.spring_layout(graph, seed=42)

# ----------------------------------------------
# Run the greedy best-first search
# ----------------------------------------------
start_node = 'https://www.cs.ku.edu.kw'
stime = time.time()
result_path = greedy_best_first_search(graph, start_node, goal_node, heuristic)
etime = time.time()
print(f"Greedy Best-First Search took {etime - stime:.4f} seconds.")
# Print the result
print(f"Path from {start_node} to {goal_node}: {result_path}")
# print(f"Path from {start_node} to {goal_node}: {result_path} and the score is {heuristic[goal_node]}")
# from array to graph
if result_path:
    nx_path = nx.path_graph(result_path)
    print("Resulting path as graph edges:", nx_path.edges())
    # Visualize the graph and the resulting path
    visualize_graph(nx_path, result_path, pos)
