import pickle
import networkx as nx
import matplotlib.pyplot as plt
from best_first.h import analyze_graph


# ----------------------------------------------
# Function to show graph G as a dictionary of nodes and their edges
# ----------------------------------------------
def create_graph_dict(G):
    graph_dict = nx.to_dict_of_dicts(G)
    # Save node edges to a text file
    for node, edges in graph_dict.items():
        with open("node_edges.txt", "a") as f:
            f.write(f"{node}: {edges}\n")

# ----------------------------------------------
# Check top k similar nodes based on heuristic scores
# ----------------------------------------------
def check_top_k(k,similars, heuristic):
    # Higher score is better; default missing scores to -inf so they sink
    ranked = sorted(
        ((node, heuristic.get(node, float('-inf'))) for node in similars),
        key=lambda item: item[1],
        reverse=True
    )
    print(f"\nTop similar nodes based on heuristic scores out of {len(similars)} similar nodes:")
    for node, score in ranked[:k]:
        print(f"Node: {node}, Score: {score}")
    return ranked[0][0] if ranked else None



# ----------------------------------------------
# Check similarity of nodes in graph to the given keyword (version 4)
# ----------------------------------------------
def check_similarity(graph, keyword, heuristic):
    keyword = keyword.lower()
    similars = set()

    def has_any_h(n):
        # treat missing as 0 instead of -inf so we don't drop nodes prematurely
        return heuristic.get(n, 0) >= 0

    for node in graph.nodes():
        node_l = node.lower()

        if keyword in node_l and has_any_h(node):
            similars.add(node)

        for _, _, data in graph.edges(node, data=True):
            link_text = (data.get('link_text') or '').lower()
            para = (data.get('surrounding_paragraph') or '').lower()

            # prefer edge body, else node body (either direction)
            body = (data.get('body') or
                    (graph.nodes.get(node, {}).get('body') or '')).lower()

            if (keyword in link_text or keyword in para or keyword in body) and has_any_h(node):
                similars.add(node)

    return check_top_k(k=3, similars=similars, heuristic=heuristic) if similars else None


# ----------------------------------------------
# Main execution
# ----------------------------------------------
if __name__ == "__main__":
    src = "https://www.cs.ku.edu.kw"

    keyword = "Hamid alhamadi"  # replace with the target keyword
    # Graph loading
    with open("crawled_graph1.gpickle", "rb") as f:
        G = pickle.load(f)
        print(f"\nCrawled nodes: {len(G.nodes())}, edges: {len(G.edges())}\n\n")
    
    # create_graph_dict(G)  # just to create the file

    heuristic = analyze_graph(G, keyword)

    num1 = check_similarity(G, keyword, heuristic)
    
    print("\nMost similar node to 'Hamid alhamadi':", num1)
    

