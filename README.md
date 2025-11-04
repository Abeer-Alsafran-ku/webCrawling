# webCrawling
Web crawling using hueristic search (A* and Greedy Best-First Search Algorithm)

# Web Crawler using Greedy Best First Search

This project implements a web crawler that navigates web pages using the **Greedy Best First Search (GBFS)** algorithm. The crawler prioritizes links based on a heuristic function, aiming to efficiently reach target pages or maximize coverage based on link relevance.  

## Features
- Greedy Best First Search-based crawling.
- Configurable start URL and target keywords.
- Simple and modular Python implementation.
- Tracks visited pages to avoid loops.

## File Structure
```text
webCrawling/
  naiev/
    └──  naiev.py # Very basic and naiev approach
  best_first/
    ├── cp_h_sample.py # Main crawler implementation using GBFS
    ├── h.py # Heuristic functions for prioritizing links
    ├── prog.py # Utility functions (e.g., URL normalization, request handling)
    ├── config.py # Configuration file (start URL, target keywords, max depth, etc.)
    └──  requirements.txt # Python dependencies
└──  README.md # Project documentation
```

## How to Run the Code

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/web-crawler-gbfs.git
cd webCrawling
pip install -r requirements.txt
python main.py
```

The crawler will print the pages visited and the path followed based on the Greedy Best-First Search or A* heuristic


## How GBFS Works in This Crawler

The Greedy Best First Search algorithm selects which page to visit next based on a heuristic that estimates “closeness” to the target. It does **not** explore all paths equally but always chooses the link that seems most promising.

**Steps GBFS:**
1. Start from the initial URL (`START_URL`).
2. Add all outgoing links from the current page to a priority queue based on heuristic score.
3. Pop the link with the best (lowest) heuristic value.
4. Visit the page and repeat until the target or maximum depth is reached.

**Diagram:**
- To be added
