# myapp/utils.py
from scholarly import scholarly
import time
import logging

logger = logging.getLogger(__name__)

def get_citations_for_publication(title, authors):
    """
    Fetch citation count for a publication from Google Scholar
    """
    try:
        # Search for the publication
        search_query = f'"{title}" {authors.split(",")[0] if authors else ""}'
        search_result = scholarly.search_pubs(search_query)

        # Get the first result (most relevant)
        pub = next(search_result, None)

        if pub:
            # Fill in the citation details
            pub_filled = scholarly.fill(pub)
            return pub_filled.get('num_citations', 0)

        return 0

    except Exception as e:
        logger.error(f"Error fetching citations for '{title}': {e}")
        return 0

def update_all_citation_counts():
    """
    Update citation counts for all publications
    This should be run as a management command or background task
    """
    from .models import Publication

    publications = Publication.objects.all()
    updated_count = 0

    for pub in publications:
        if pub.title and pub.authors:
            try:
                citation_count = get_citations_for_publication(pub.title, pub.authors)
                pub.citation_count = citation_count
                pub.save()
                updated_count += 1

                # Be respectful to Google Scholar - add delay
                time.sleep(2)

                print(f"Updated {pub.title}: {citation_count} citations")

            except Exception as e:
                print(f"Error updating {pub.title}: {e}")
                continue

    print(f"Updated {updated_count} publications with citation counts")
