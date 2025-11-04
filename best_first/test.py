import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)])

# Create an induced subgraph with nodes 1, 2, and 3
subgraph_nodes = [1, 2, 3]
H = G.subgraph(subgraph_nodes)

print("\nNodes in H (subgraph):", H.nodes())
print("Edges in H (subgraph):", H.edges())

# Example of subgraph_view to include only nodes with an even number
def filter_even_nodes(node):
    return node % 2 == 0

J = nx.subgraph_view(G, filter_node=filter_even_nodes)
print("\nNodes in J (filtered subgraph):", J.nodes())
print("Edges in J (filtered subgraph):", J.edges())

print("\nOriginal Graph G nodes:",H)

# # -------- Visualization of subgraph H --------
# plt.figure(figsize=(5, 4))
# pos = nx.spring_layout(G, seed=42)  # layout for consistent node positions
# nx.draw(
#     G,
#     pos,
#     with_labels=True,
#     node_color="skyblue",
#     node_size=1500,
#     font_size=12,
#     font_weight="bold",
#     edge_color="gray"
# )
# plt.title("Subgraph H (Nodes 1, 2, 3)")
# plt.show()

pos = nx.spring_layout(G, seed=42)

plt.figure(figsize=(6, 5))
plt.title("Original Graph G with Subgraph H Highlighted")

# Draw the entire graph first (light gray)
nx.draw(
    G, pos,
    with_labels=True,
    node_color="lightgray",
    edge_color="lightgray",
    node_size=1200,
    font_size=12
)

# Draw the subgraph (highlighted)
nx.draw_networkx_nodes(
    H, pos,
    node_color="skyblue",
    node_size=1200,
    edgecolors="black",
    linewidths=2
)
nx.draw_networkx_edges(
    H, pos,
    edge_color="deepskyblue",
    width=3
)
nx.draw_networkx_labels(H, pos, font_weight="bold", font_color="black")

plt.show()