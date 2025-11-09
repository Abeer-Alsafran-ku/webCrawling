from AStar.AStarHelperFunctions import *
from AStar.AStarHeuristicFunction import estimate_child_relevance_weighted
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urldefrag
import heapq

def a_star_web_crawl(
    seed_web_address,
    target_phrase,
    topic_description,
    maximum_pages_to_visit=200,
    maximum_child_links_per_page=100,
    requests_timeout_seconds=5,
    depth_penalty_per_level=75.0
):

    start_time_seconds = time.time()

    # Topic keywords from description (site-wide context)
    topic_keyword_list = [
        word.lower() for word in topic_description.split() if word.strip()
    ]

    # Phrase tokens from target phrase (names, numbers, etc.)
    phrase_token_list = [
        token.lower()
        for token in re.split(r"[^0-9A-Za-z\u0600-\u06FF]+", target_phrase) #0600 - 06FF is arabic letter range in unicode
        if token.strip()
    ]

    visited_web_addresses = set()
    parent_web_address = {}
    depth_of_page = {}

    non_html_extensions = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx")

    # ----- Fetch seed page -----
    try:
        seed_response = requests.get(seed_web_address, timeout=requests_timeout_seconds)
        if not getattr(seed_response, "encoding", None):
            seed_response.encoding = "utf-8"
        seed_html_text = seed_response.text
        seed_soup_object = BeautifulSoup(seed_html_text, "html.parser")
    except Exception as fetch_error:
        print("Failed to fetch seed web address:", fetch_error)
        return None

    
    seed_page_relevance = calculate_relevance_value(topic_keyword_list, seed_soup_object)
    depth_of_page[seed_web_address] = 0

    start_node = AStarNode(
        web_address=seed_web_address,
        cumulative_relevance=0.0,              
        heuristic_relevance=float(seed_page_relevance)  
    )

    frontier_queue = []
    heapq.heappush(frontier_queue, start_node)
    parent_web_address[seed_web_address] = None

    print("=== A* Web Crawler ===")
    print("Start web address : ", seed_web_address)
    print("Target phrase     : ", repr(target_phrase))
    print("Topic keywords    : ", topic_keyword_list)
    print()

    search_step_counter = 0
    stopped_reason = "unknown"

    while frontier_queue and len(visited_web_addresses) < maximum_pages_to_visit:
        current_node = heapq.heappop(frontier_queue)
        current_web_address = current_node.web_address

        if current_web_address in visited_web_addresses:
            continue

        visited_web_addresses.add(current_web_address)
        search_step_counter += 1
        print(f"[A*] Exploring page {search_step_counter}: {current_web_address}", flush=True)

        current_depth = depth_of_page.get(current_web_address, 0)

        # ----- Fetch and parse current page -----
        try:
            current_response = requests.get(current_web_address, timeout=requests_timeout_seconds)
            if not getattr(current_response, "encoding", None):
                current_response.encoding = "utf-8"
            current_html_text = current_response.text
            current_soup_object = BeautifulSoup(current_html_text, "html.parser")
        except Exception as exception_error:
            print(f"[A*] Skipping unreachable page: {current_web_address} ({exception_error})", flush=True)
            continue

        
        if page_contains_phrase(current_soup_object, target_phrase) or find_tgt(target_phrase, current_soup_object):
            stopped_reason = "goal_found"
            break

        # ----- CHILD EXPANSION -----
        all_link_tags_on_page = current_soup_object.find_all("a", href=True)
        links_considered = 0

        for link_tag in all_link_tags_on_page:
            if links_considered >= maximum_child_links_per_page:
                break

            absolute_url = requests.compat.urljoin(current_web_address, link_tag["href"])
            absolute_url, _fragment = urldefrag(absolute_url)

            if absolute_url in visited_web_addresses:
                continue

            # Stay within domain
            if not is_within_domain("www.cs.ku.edu.kw", absolute_url) and not is_within_domain("cs.ku.edu.kw", absolute_url):
                continue

            # Skip obvious non-HTML
            if absolute_url.lower().endswith(non_html_extensions):
                continue

            # --- Heuristic scoring ---

            
            topic_relevance_score = estimate_child_relevance_weighted(
                topic_keyword_list,
                link_tag,
                all_link_tags_on_page
            )

            
            if phrase_token_list:
                phrase_relevance_score = estimate_child_relevance_weighted(
                    phrase_token_list,
                    link_tag,
                    all_link_tags_on_page
                )
            else:
                phrase_relevance_score = 0.0

            
            blended_relevance_score = (
                0.3 * float(topic_relevance_score)
                + 0.7 * float(phrase_relevance_score)
            )

            child_depth = current_depth + 1

            
            child_cumulative_relevance = -depth_penalty_per_level * float(child_depth)

            
            child_heuristic_relevance = blended_relevance_score

            child_node = AStarNode(
                web_address=absolute_url,
                cumulative_relevance=child_cumulative_relevance,
                heuristic_relevance=child_heuristic_relevance
            )

            if absolute_url not in parent_web_address:
                parent_web_address[absolute_url] = current_web_address
                depth_of_page[absolute_url] = child_depth
                heapq.heappush(frontier_queue, child_node)
                links_considered += 1

    # ----- Determine stop reason -----
    if not frontier_queue and stopped_reason == "unknown" and len(visited_web_addresses) < maximum_pages_to_visit:
        stopped_reason = "frontier_empty"
    elif len(visited_web_addresses) >= maximum_pages_to_visit and stopped_reason == "unknown":
        stopped_reason = "hit_page_limit"

    end_time_seconds = time.time()

    if stopped_reason == "goal_found":
        path_from_seed_to_target = []
        trace_web_address = current_web_address
        while trace_web_address is not None:
            path_from_seed_to_target.append(trace_web_address)
            trace_web_address = parent_web_address[trace_web_address]
        path_from_seed_to_target.reverse()

        print("\nTarget phrase FOUND at:", current_web_address)
        print("Stop reason            :", stopped_reason)
        print("Pages visited          :", len(visited_web_addresses))
        print("Time taken             : {:.2f} seconds".format(end_time_seconds - start_time_seconds))
        print("\nA* path from seed to target:")
        for path_step in path_from_seed_to_target:
            print("  ", path_step)
        return path_from_seed_to_target

    print("\nTarget phrase NOT found.")
    print("Stop reason            :", stopped_reason)
    print("Pages visited          :", len(visited_web_addresses))
    print("Time taken             : {:.2f} seconds".format(end_time_seconds - start_time_seconds))
    return None