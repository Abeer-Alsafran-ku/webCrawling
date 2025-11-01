
import time
import requests
from urllib.parse import urlsplit, urlunsplit, urljoin
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import pickle
# -----------------------------
# URL normalization utilities
# -----------------------------
def normalize_url(url: str) -> str:
    """
    Normalize a URL to avoid duplicate nodes like ... and .../ .
    Also strips query and fragment for node identity.
    """
    s = urlsplit(url.strip())
    # Keep scheme+netloc as-is, normalize path (drop trailing '/'), strip query/fragment
    norm_path = s.path.rstrip('/') if s.path not in ('', '/') else ''
    s = s._replace(path=norm_path, query='', fragment='')
    return urlunsplit(s)

def absolutize_and_normalize(base: str, href: str) -> str:
    return normalize_url(urljoin(base, href))


# -----------------------------
# HTTP helpers
# -----------------------------
_DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MiniCrawler/1.0; +https://example.org/bot)"
}

def safe_get(url: str, timeout: int = 10) -> requests.Response | None:
    try:
        r = requests.get(url, headers=_DEFAULT_HEADERS, timeout=timeout)
        r.raise_for_status()
        return r
    except requests.RequestException:
        return None


# -----------------------------
# Graph construction
# -----------------------------
def create_graph(src: str) -> nx.DiGraph:
    src = normalize_url(src)
    graph = nx.DiGraph()
    graph.add_node(src)

    resp = safe_get(src)
    if resp is None:
        return graph

    soup = BeautifulSoup(resp.text, 'html.parser')

    for a in soup.find_all('a', href=True):
        full = absolutize_and_normalize(src, a['href'])
        # Keep only http(s) and not self-loops
        if not (full.startswith('http://') or full.startswith('https://')):
            continue
        if full == src:
            continue

        link_text = a.get_text(strip=True) or ''
        p = a.find_parent('p')
        surrounding_paragraph = p.get_text(' ', strip=True) if p else ''
        graph.add_edge(src, full,
                       link_text=link_text,
                       surrounding_paragraph=surrounding_paragraph,
                       body=resp.text)
    return graph



# -----------------------------
# Visualization helpers
# -----------------------------
def show_subgraph(G: nx.DiGraph, H: nx.DiGraph, pos: dict | None = None, title: str = "Original Graph G with Subgraph H Highlighted"):
    # Compose ensures positions exist for every node to draw
    U = nx.compose(G, H)
    if pos is None:
        pos = nx.spring_layout(U, seed=42)
    else:
        # warm-start the layout, fixing old nodes
        pos = nx.spring_layout(U, pos=pos, fixed=list(pos.keys()), seed=42)

    plt.figure(figsize=(8, 6))
    plt.title(title)

    # Base (union) in light gray
    nx.draw(U, pos,
            with_labels=False,
            node_color="lightgray",
            edge_color="lightgray",
            node_size=800,
            arrows=True)

    # Highlight H
    nx.draw_networkx_nodes(H, pos,
                           node_color="skyblue",
                           node_size=900,
                           edgecolors="black",
                           linewidths=2)
    nx.draw_networkx_edges(H, pos,
                           edge_color="deepskyblue",
                           width=2.5)
    nx.draw_networkx_labels(H, pos, font_weight="bold", font_size=8)

    plt.tight_layout()
    plt.show()
    return pos

def visualize_graph_with_top3(graph: nx.DiGraph, scores: dict[str, int]):
    pos = nx.spring_layout(graph, seed=42)
    nx.draw(graph, pos, with_labels=True, node_size=1200, node_color="lightblue",
            font_size=10, font_weight="bold", arrows=True)

    top3_links = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for link, score in top3_links:
        if link in pos:
            plt.annotate(f"Score: {score}", xy=pos[link], xytext=(5, 5),
                         textcoords="offset points", fontsize=9, color="red")
    plt.tight_layout()
    plt.show()


# -----------------------------
# save_crawling
# -----------------------------
def save_crawling(src: str,
                  max_depth: int = 1,
                  same_domain: bool = True,
                  delay_sec: float = 0.0,
                  visualize_each: bool = False) -> nx.DiGraph:
    """
    Crawl starting at `src`, expanding links up to `max_depth`, merging subgraphs into a single DiGraph.
    Includes the checks/fixes:
      - URL normalization (avoid trailing-slash duplicates).
      - No mutation during iteration (iterate over a snapshot).
      - Draw subgraph using positions computed on the union (avoid 'no position' errors).
      - Skip non-http(s) links and self-loops.
      - Optional same-domain restriction.
      - Optional polite delay between requests.
    Returns the merged graph.
    """
    src = normalize_url(src)
    root_domain = urlsplit(src).netloc

    # Build the initial page graph
    graph = create_graph(src)

    # BFS frontier up to max_depth
    visited = {src}
    frontier = [src]
    depth = 0

    # optional: keep a running layout for smooth visualization
    pos = None

    while depth < max_depth and frontier:
        next_frontier: list[str] = []
        # iterate over a stable snapshot of nodes in the current frontier
        for node in list(frontier):
            # Expand out-edges from this node to get candidate child pages
            children = [v for _, v in graph.out_edges(node)] # directed graph
            # children = [v for _, v in graph.edges(node)]

            # Iterate over a stable copy
            for child in list(children):
                if child in visited:
                    continue
                if same_domain and urlsplit(child).netloc != root_domain:
                    continue

                subgraph = create_graph(child)

                # Merge BEFORE optionally visualizing so the union has all nodes
                graph.add_nodes_from(subgraph.nodes(data=True))
                graph.add_edges_from(subgraph.edges(data=True))

                visited.add(child)
                next_frontier.append(child)

                if visualize_each:
                    pos = show_subgraph(graph, subgraph, pos=pos,
                                        title=f"Graph with subgraph from: {child}")

                if delay_sec > 0:
                    time.sleep(delay_sec)

        frontier = next_frontier
        depth += 1

    return graph


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    src = "https://www.cs.ku.edu.kw"
    stime = time.time()
    # Crawl one depth level, same domain only, visualize each subgraph while growing
    G = save_crawling(src, max_depth=1, same_domain=True, delay_sec=0.0, visualize_each=False)
    etime = time.time()
    print(f"Crawling completed in {etime - stime:.2f} seconds.")
    # Save the graph for later analysis
    with open("crawled_graph1.gpickle", "wb") as f:
        pickle.dump(G, f)

    print(f"Crawled nodes: {len(G.nodes())}, edges: {len(G.edges())}")

    # # show the graph as dictionary
    # graph_dict = nx.to_dict_of_dicts(G)
    # print(graph_dict)

