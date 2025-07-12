import json
import logging

logger = logging.getLogger("zbeam.author_utils")

def get_author_by_id(author_id, authors_file="authors/authors.json"):
    logger.info("Fetching author with ID: %s", author_id)
    with open(authors_file, "r") as f:
        authors = json.load(f)
    author = next((a for a in authors if a.get("id") == author_id), None)
    logger.info("Author found: %s", author)
    return author