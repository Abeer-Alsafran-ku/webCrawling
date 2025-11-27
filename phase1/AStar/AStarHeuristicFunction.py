def estimate_child_relevance_weighted(topic_keyword_list, link_tag, all_link_tags_on_page):
    if link_tag is None:
        return 0

    # Link text matches
    link_text = link_tag.get_text(separator=" ", strip=True).lower()
    link_text_matches = sum(link_text.count(word) for word in topic_keyword_list)

    # Surrounding paragraph matches (fallback to closest parent text if no <p>)
    paragraph_text = ""
    parent_paragraph = link_tag.find_parent("p")
    if parent_paragraph:
        paragraph_text = parent_paragraph.get_text(separator=" ", strip=True).lower()
    else:
        parent_block = link_tag.find_parent(["section", "article", "div"])
        if parent_block:
            paragraph_text = parent_block.get_text(separator=" ", strip=True).lower()

    paragraph_matches = sum(paragraph_text.count(word) for word in topic_keyword_list)

    # Sibling links on the same page that contain any keyword
    sibling_keyword_links = 0
    for other_link in all_link_tags_on_page:
        if other_link is link_tag:
            continue
        other_text = other_link.get_text(separator=" ", strip=True).lower()
        if any(word in other_text for word in topic_keyword_list):
            sibling_keyword_links += 1

    
    heuristic_score = (4 * link_text_matches) + (2 * paragraph_matches) + (1 * sibling_keyword_links)
    return heuristic_score