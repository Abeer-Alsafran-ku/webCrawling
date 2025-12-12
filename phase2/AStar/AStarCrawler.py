from AStar.AStarHelperFunctions import *
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urldefrag, urlparse
import heapq
from pathlib import Path
import joblib
import re

print(f"[DEBUG] AStarCrawler module loaded from: {__file__}")

# Polite-ish browsery headers
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# -------------------------
# Load ML Model + Vectorizer
# -------------------------
PHASE2_DIR = Path(__file__).resolve().parents[1]  # .../phase2/
MNB_MODEL_PATH = PHASE2_DIR / "MNB_model.pkl"
MNB_VECTORIZER_PATH = PHASE2_DIR / "tfidf_MNB_vectorizer.pkl"

mnb_model = joblib.load(MNB_MODEL_PATH)
mnb_vectorizer = joblib.load(MNB_VECTORIZER_PATH)


def score_link_with_mnb(link_tag):
    """
    Score a link using ONLY the MNB model probability
    on the link's local textual context (anchor + nearby text).

    Returns a heuristic in roughly [0, 1000].
    """
    pieces = []

    if link_tag:
        # Anchor text
        link_text = link_tag.get_text(separator=" ", strip=True)
        if link_text:
            pieces.append(link_text)

        # Surrounding paragraph or block
        parent_paragraph = link_tag.find_parent("p")
        if parent_paragraph:
            pieces.append(parent_paragraph.get_text(separator=" ", strip=True))
        else:
            parent_block = link_tag.find_parent(["section", "article", "div"])
            if parent_block:
                pieces.append(parent_block.get_text(separator=" ", strip=True))

    combined_text = " ".join(pieces).strip().lower()

    if not combined_text:
        return 0.0

    X = mnb_vectorizer.transform([combined_text]).toarray()

    if hasattr(mnb_model, "predict_proba"):
        # Probability of the "AI-related / relevant" class (index 1)
        ml_score = float(mnb_model.predict_proba(X)[0][1])  # 0..1
    else:
        # Fallback to predicted label in {0,1}
        label = int(mnb_model.predict(X)[0])
        ml_score = float(label)

    # Scale to a 0..1000-ish range for compatibility with old heuristic scale
    heuristic_value = 1000.0 * ml_score
    return heuristic_value


def a_star_web_crawl(
    seed_web_address,
    target_phrase,
    maximum_pages_to_visit=200,
    maximum_child_links_per_page=100,
    requests_timeout_seconds=5,
    depth_penalty_per_level=75.0,
    base_domain=None,  # optional base domain
):

    start_time_seconds = time.time()

    # Determine base_domain for is_within_domain
    if base_domain is None or not base_domain.strip():
        base_domain = urlparse(seed_web_address).netloc
    else:
        base_domain = base_domain.strip()
        # If user pasted a full URL as base_domain, extract netloc
        parsed = urlparse(base_domain)
        if parsed.netloc:
            base_domain = parsed.netloc

    visited = set()
    parent_of = {}
    depth_of = {}

    non_html_ext = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx")

    # -------- Fetch seed page --------
    try:
        print(f"[DEBUG] Fetching seed: {seed_web_address}")
        seed_res = requests.get(
            seed_web_address,
            headers=HEADERS,
            timeout=requests_timeout_seconds
        )
        print(f"[DEBUG] Seed status: {seed_res.status_code}, length: {len(seed_res.text)}")
        seed_res.encoding = seed_res.encoding or "utf-8"
        seed_soup = BeautifulSoup(seed_res.text, "html.parser")
    except Exception as e:
        print("Failed to fetch seed URL:", e)
        return None

    depth_of[seed_web_address] = 0

    start_node = AStarNode(
        web_address=seed_web_address,
        cumulative_relevance=0.0,
        heuristic_relevance=0.0
    )

    frontier = []
    heapq.heappush(frontier, start_node)
    parent_of[seed_web_address] = None

    print("=== A* Web Crawler (MNB Model) ===")
    print("Seed URL       :", seed_web_address)
    print("Base domain    :", base_domain)
    print("Target phrase  :", repr(target_phrase))
    print()

    search_steps = 0
    stopped_reason = "unknown"
    current_url = seed_web_address  # in case we never move

    while frontier and len(visited) < maximum_pages_to_visit:
        current = heapq.heappop(frontier)
        current_url = current.web_address

        if current_url in visited:
            continue

        visited.add(current_url)
        search_steps += 1
        print(f"[A*] Exploring {search_steps}: {current_url}", flush=True)

        current_depth = depth_of.get(current_url, 0)

        # -------- Fetch current page --------
        try:
            time.sleep(1.0)  # be polite
            res = requests.get(
                current_url,
                headers=HEADERS,
                timeout=requests_timeout_seconds
            )
            print(f"[DEBUG] Fetch {current_url} -> status {res.status_code}, length {len(res.text)}")
            res.encoding = res.encoding or "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
        except Exception as e:
            print(f"[A*] Skipping unreachable page: {current_url} ({e})")
            continue

        # -------- Check for target phrase on this page --------
        if page_contains_phrase(soup, target_phrase) or find_tgt(target_phrase, soup):
            stopped_reason = "goal_found"
            break

        # -------- Child expansion (ML-guided top-K) --------
        all_links = soup.find_all("a", href=True)
        print(f"[DEBUG] Found {len(all_links)} links on this page")

        candidates = []
        seen_urls = set()

        for link in all_links:
            absolute_url = requests.compat.urljoin(current_url, link["href"])
            absolute_url, _ = urldefrag(absolute_url)

            # De-duplicate URLs within this page
            if absolute_url in seen_urls:
                continue
            seen_urls.add(absolute_url)

            # Already visited?
            if absolute_url in visited:
                continue

            # Domain restriction using helper
            if not is_within_domain(base_domain, absolute_url):
                continue

            # Skip obviously non-HTML resources
            if absolute_url.lower().endswith(non_html_ext):
                continue

            child_depth = current_depth + 1

            # ML-only heuristic based on link context
            heur = score_link_with_mnb(link)

            candidates.append((heur, absolute_url, child_depth))

        # Sort by heuristic score (high → low) and take top-K
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_k = candidates[:maximum_child_links_per_page]

        debug_limit = 10
        for idx, (heur, absolute_url, child_depth) in enumerate(top_k):
            if absolute_url not in parent_of and absolute_url not in visited:
                parent_of[absolute_url] = current_url
                depth_of[absolute_url] = child_depth

                node = AStarNode(
                    web_address=absolute_url,
                    cumulative_relevance=-depth_penalty_per_level * float(child_depth),
                    heuristic_relevance=heur
                )
                heapq.heappush(frontier, node)

                if idx < debug_limit:
                    print("  [DEBUG] Add to frontier (top-K):", absolute_url, "| heuristic:", heur)

    end = time.time()

    if stopped_reason == "goal_found":
        path = []
        t = current_url
        while t is not None:
            path.append(t)
            t = parent_of[t]
        path.reverse()

        print("\nTarget phrase FOUND at:", current_url)
        print("Pages visited:", len(visited))
        print("Time taken:", round(end - start_time_seconds, 2), "seconds")
        print("\nA* Path:")
        for step in path:
            print("  ", step)
        return path

    print("\nTarget phrase NOT found.")
    print("Pages visited:", len(visited))
    print("Time taken:", round(end - start_time_seconds, 2), "seconds")
    return None
