# phase2/AStarCrawlerWithMLTest.py

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent       # .../phase2/
ASTAR_DIR = CURRENT_DIR / "AStar"

sys.path.append(str(ASTAR_DIR))

from AStar.AStarCrawler import a_star_web_crawl


def main(args):
    if len(args) < 1:
        print("Usage: python main.py <model_type: MNB|SVM|GNB|DT>")
        return
    
    model_type = args[0]  # Accept model type from command line

    print(f"=== A* Crawler Test ({model_type} Model) ===\n")

    base_domain = input("Enter the base domain (e.g. en.wikipedia.org | can be empty):\n> ").strip()
    # You can leave this empty to let the crawler derive it from the seed URL.

    seed_url = input("\nEnter the seed URL to begin crawling from:\n> ").strip()
    if not seed_url:
        print("Seed URL required.")
        return

    target_phrase = input("\nEnter the target phrase you want the crawler to find:\n> ").strip()
    if not target_phrase:
        print("Target phrase required.")
        return

    print("\n=== CONFIGURATION ===")
    print(f"Base domain:   {base_domain or '(auto from seed URL i.e. can be empty)'}")
    print(f"Seed URL:      {seed_url}")
    print(f"Target phrase: {target_phrase}")
    print("=====================\n")

    print("Running crawler...\n")

    result = a_star_web_crawl(
        seed_web_address=seed_url,
        target_phrase=target_phrase,
        maximum_pages_to_visit=30,
        maximum_child_links_per_page=12,
        requests_timeout_seconds=5,
        base_domain=base_domain or None,
        model_type='MNB'
    )

    print("\n=== RESULT ===")
    if result is None:
        print("Crawler did NOT find the target phrase.")
    else:
        print("Crawler found a path:")
        for step in result:
            print(" ", step)


if __name__ == "__main__":
    main(sys.argv[1:])
