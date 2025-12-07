from bs4 import BeautifulSoup
import requests 

import time
import http.client
import csv
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a session with retry logic
def create_session(
    total_retries=5,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504),
):
    session = requests.Session()

    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff_factor,  # 1 -> 1s, 2s, 4s, 8s...
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["HEAD", "GET", "OPTIONS", "POST"]),
        raise_on_status=False,
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Optional: set a default header
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; SafeCrawler/1.0)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    return session


session = create_session()


def safe_request(
    method: str,
    url: str,
    *,
    timeout: float = 10,
    max_manual_retries: int = 3,
    sleep_between_retries: float = 1,
    **kwargs,
):
    """
    Make a 'safe' HTTP request:
      - timeout
      - automatic retries (via session)
      - manual retries on RemoteDisconnected / ConnectionError
    """
    last_exc = None

    for attempt in range(1, max_manual_retries + 1):
        try:
            # Example: session.request("GET", url, timeout=10, params=..., headers=...)
            resp = session.request(method, url, timeout=timeout, **kwargs)
            resp.raise_for_status()  # raise HTTPError for 4xx/5xx
            return resp

        except requests.exceptions.Timeout as e:
            print(f"[Attempt {attempt}] Timeout for {url}: {e}")
            last_exc = e

        except (requests.exceptions.ConnectionError, http.client.RemoteDisconnected) as e:
            # This is where your "Remote end closed connection without response" will come
            print(f"[Attempt {attempt}] Connection issue for {url}: {e}")
            last_exc = e

        except requests.exceptions.HTTPError as e:
            # 4xx/5xx after resp.raise_for_status()
            # You can choose to break immediately on 4xx
            print(f"[Attempt {attempt}] HTTP error for {url}: {e}")
            last_exc = e
            # If you don't want to retry on 4xx, break here:
            break

        # If we still have retries left, wait and try again
        if attempt < max_manual_retries:
            time.sleep(sleep_between_retries * attempt)  # simple backoff

    # If we get here, all retries failed
    raise last_exc if last_exc else RuntimeError("Unknown error during request")


links_arr = []

# read from txt file the web pages links
with open('non_ai_related_webpages.txt','r') as f :
    while True:
        links = f.readline()
        if not links :
            break
        links_arr.append(links.strip())

with open('dataset.csv', 'a', newline='', encoding='utf-8') as fd:
    
    writer = csv.writer(fd, quoting=csv.QUOTE_ALL)
    # step 1 : loop over the urls and make a request
    for link in links_arr:
        # step 2 : save the content of the html page
        if not link.startswith('https:'):
            link = link[4:]

        try:
            resp = safe_request("GET", link)
        except requests.exceptions.HTTPError as e:
            print(f"Skipping {link} due to HTTP error: {e}")
            continue
        except Exception as e:
            print(f"Skipping {link} due to unexpected error: {e}")
            continue

        html = resp.content
        soup = BeautifulSoup(html,'html.parser')
        content = soup.get_text(separator=' ', strip=True)

        # step 3 : write the content and label it as 1 to the dataset csv file
        writer.writerow([content, 0])

        print(type(link))

print('done')
