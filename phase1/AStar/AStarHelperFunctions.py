import re
import requests
import unicodedata 

def calculate_relevance_value(topic_keyword_list, soup_object):
    if soup_object is None:
        return 0

    page_text = soup_object.get_text(separator=" ", strip=True).lower()
    relevance_score = 0

    for topic_word in topic_keyword_list:
        cleaned_topic_word = topic_word.strip().lower()
        if not cleaned_topic_word:
            continue

        
        relevance_score += page_text.count(cleaned_topic_word)

    return relevance_score

class AStarNode:
    def __init__(self, web_address, cumulative_relevance, heuristic_relevance):
        self.web_address = web_address
        self.cumulative_relevance = cumulative_relevance
        self.heuristic_relevance = heuristic_relevance
        self.total_relevance = cumulative_relevance + heuristic_relevance

    # heapq is a min-heap; we invert comparison so that nodes
    # with higher total_relevance are popped first.
    def __lt__(self, other_node):
        return self.total_relevance > other_node.total_relevance


def normalize_arabic_text(text):
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    # remove Arabic diacritics
    text = re.sub(r"[\u0617-\u061A\u064B-\u0652]", "", text)
    # unify common forms
    text = (text
            .replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
            .replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي").replace("ة", "ه"))
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def contains_arabic(text):
    return any('\u0600' <= ch <= '\u06FF' for ch in text or "") #0600 - 06FF is arabic letter range in unicode

def page_contains_phrase(soup_object, target_phrase):
    if soup_object is None:
        return False

    page_text_raw = soup_object.get_text(separator=" ", strip=True)
    target_raw = target_phrase or ""

    # Decide if we should apply Arabic normalization
    arabic_mode = contains_arabic(target_raw) or contains_arabic(page_text_raw)

    if arabic_mode:
        page_text = normalize_arabic_text(page_text_raw.lower())
        target_text = normalize_arabic_text(target_raw.lower())
    else:
        page_text = re.sub(r"\s+", " ", page_text_raw).strip().lower()
        target_text = re.sub(r"\s+", " ", target_raw).strip().lower()

    return target_text in page_text

def extract_anchor_text_map(soup_object, base_web_address):
    anchor_tuples = []
    if soup_object is None:
        return anchor_tuples
    for anchor in soup_object.find_all("a", href=True):
        href = requests.compat.urljoin(base_web_address, anchor["href"])
        anchor_text = anchor.get_text(separator=" ", strip=True).lower()
        anchor_tuples.append((href, anchor_text))
    return anchor_tuples

def is_within_domain(base_domain, url):
    return url.startswith(f"https://{base_domain}") or url.startswith(f"http://{base_domain}")

### The following two functions are Abeer's work'

def find_tgt(tgt, content):
    content = content.get_text()
    # content = content.strip(' ')
    if tgt in content:
        return True
        # return 'Tgt found'
    return False
    # return 'Tgt not found'

def get_sublink(soup, src):
    sub = soup.find_all('a')
    links = []
    for link in sub:
        sub_link = link.get('href')
        if sub_link is not None and sub_link.startswith('http'):
            if sub_link not in links and sub_link != src and sub_link != src + '/':
                links.append(sub_link)
    return links