import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt


# -----------------------------
# function to calculate heuristic score based on given parameters
# -----------------------------
def calculate_hueristic(occr_goal_key_in_link_text, occr_in_surr_paragraph, occr_in_body, number_of_links_containing_similar_keyword):
# def calculate_hueristic(occr_goal_key_in_link_text, occr_in_surr_paragraph, number_of_links_containing_similar_keyword):
    # return (occr_goal_key_in_link_text * 5) + (occr_in_surr_paragraph * 3) + (number_of_links_containing_similar_keyword * 1)
    return (occr_goal_key_in_link_text * 5) + (occr_in_surr_paragraph * 3) + (occr_in_body * 2) + (number_of_links_containing_similar_keyword * 1)

# link text
def get_occr_goal_key_in_link_text(link_text,keyword): # link_text is the link text
    return link_text.lower().count(keyword.lower())

# surrounding paragraph
def get_occr_in_surr_paragraph(surrounding_paragraph, keyword): # surrounding_paragraph is the text inside the tags in the link
    return surrounding_paragraph.lower().count(keyword.lower()) 
# body text
def get_occr_in_body(body, keyword): # body is the full text of the page
    if body:
        if keyword.lower() in body.lower():
            return body.lower().count(keyword.lower())
    return 0
# number of links containing similar keyword
def get_number_of_links_containing_similar_keyword(links, keyword): # links is a list of link of child links
    count = 0
    for link in links:
        if keyword.lower() in link.lower():
            count += 1
    return count

def analyze_graph(graph, keyword):
    heuristic_scores = {}

    for u, v, data in graph.edges(data=True):
        link_text = data.get('link_text', '') or ''
        surrounding_paragraph = data.get('surrounding_paragraph', '') or ''

        # Try edge body first, then node[v], then node[u]
        body = (data.get('body') or
                graph.nodes.get(v, {}).get('body') or
                graph.nodes.get(u, {}).get('body') or '')

        occr_goal_key_in_link_text = get_occr_goal_key_in_link_text(link_text, keyword)
        occr_in_surr_paragraph = get_occr_in_surr_paragraph(surrounding_paragraph, keyword)
        occr_in_body = get_occr_in_body(body, keyword)

        # neighbors of u (outgoing from u)
        neighbors_of_u = [nbr for _, nbr in graph.out_edges(u)] if graph.is_directed() else [nbr for nbr in graph.neighbors(u)]
        number_of_links_containing_similar_keyword = get_number_of_links_containing_similar_keyword(neighbors_of_u, keyword)

        score = calculate_hueristic(
            occr_goal_key_in_link_text,
            occr_in_surr_paragraph,
            occr_in_body,
            number_of_links_containing_similar_keyword
        )

        # Aggregate instead of overwrite (max is usually good for “best” edge)
        prev = heuristic_scores.get(v, float('-inf'))
        heuristic_scores[v] = max(prev, score)

        # with open("heuristic_scores.txt", "a") as f:
        #     f.write(f"Edge {u} -> {v} | link:{occr_goal_key_in_link_text} para:{occr_in_surr_paragraph} body:{occr_in_body} links_like:{number_of_links_containing_similar_keyword} => score:{score}\n")

    return heuristic_scores


# -----------------------------
# visualize the graph and highlight top 3 links by heuristic score
# -----------------------------
def visualize_graph_with_top3(graph,scores):
    import matplotlib.pyplot as plt
    import networkx as nx

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)

    # Get top 3 links by heuristic score
    top3_links = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for link, score in top3_links:
        plt.annotate(f"Score: {score}", xy=pos[link], xytext=(5, 5), textcoords="offset points", fontsize=9, color="red")

    plt.show()



# ----------------------------------------------
# Function to show subgraph H highlighted within graph G
# ----------------------------------------------
def show_subgraph(G, H):

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

# ----------------------------------------------
# Main execution
# ----------------------------------------------
# if __name__ == "__main__":
#     src = "https://www.cs.ku.edu.kw"  # replace with the source URL
#     keyword = "Alumni"  # replace with the target keyword


#     print("\n\n\nCreating graph from source URL...\n\n\n")

#     with open("crawled_graph3.gpickle", "rb") as f:
#         graph = nx.read_gpickle(f)

#     print("\n\n\nAnalyzing graph for heuristic scores...\n\n\n")
#     scores = analyze_graph(graph, keyword)

#     # for link, score in scores.items():
#     #     print(f"Link: {link}, Heuristic Score: {score}")

#     visualize_graph_with_top3(graph,scores)
#     # print(graph.edges(data=True))


