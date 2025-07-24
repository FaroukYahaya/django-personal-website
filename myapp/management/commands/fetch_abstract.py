# Create this file: myapp/management/commands/fetch_abstracts.py

from django.core.management.base import BaseCommand
from myapp.models import Publication
import requests
import time
import re
from django.utils import timezone


class Command(BaseCommand):
    help = 'Fetch abstracts for publications from various sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Limit number of publications to process',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Fetching abstracts for publications...")

        # Get publications without abstracts
        publications = Publication.objects.filter(abstract__exact='')[:options['limit']]

        if not publications:
            self.stdout.write(self.style.SUCCESS("✅ All publications already have abstracts!"))
            return

        self.stdout.write(f"📄 Processing {len(publications)} publications...")

        for pub in publications:
            self.stdout.write(f"\n📖 Processing: {pub.title[:50]}...")

            abstract = None

            # Try different sources
            if pub.doi:
                abstract = self.fetch_from_crossref(pub.doi)

            if not abstract and pub.title:
                abstract = self.fetch_from_semantic_scholar(pub.title)

            if not abstract and pub.url:
                abstract = self.fetch_from_url(pub.url)

            if abstract:
                pub.abstract = abstract
                pub.save()
                self.stdout.write(self.style.SUCCESS(f"  ✅ Found abstract ({len(abstract)} chars)"))
                self.stdout.write(f"  📝 Preview: {abstract[:100]}...")
            else:
                self.stdout.write(self.style.WARNING("  ⚠️ No abstract found"))

            # Be respectful with delays
            time.sleep(2)

        self.stdout.write(self.style.SUCCESS("\n🎉 Abstract fetching complete!"))

    def fetch_from_crossref(self, doi):
        """Fetch abstract from CrossRef API"""
        try:
            url = f"https://api.crossref.org/works/{doi}"
            headers = {'User-Agent': 'Mozilla/5.0 (Academic Research)'}

            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                work = data.get('message', {})
                abstract = work.get('abstract')

                if abstract:
                    # Clean HTML tags if present
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                    return abstract.strip()

        except Exception as e:
            self.stdout.write(f"  ❌ CrossRef error: {e}")

        return None

    def fetch_from_semantic_scholar(self, title):
        """Fetch abstract from Semantic Scholar API"""
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {
                'query': title,
                'limit': 1,
                'fields': 'abstract,title'
            }
            headers = {'User-Agent': 'Mozilla/5.0 (Academic Research)'}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])

                if papers:
                    paper = papers[0]
                    # Check if title matches reasonably well
                    if self.titles_match(title, paper.get('title', '')):
                        abstract = paper.get('abstract')
                        if abstract:
                            return abstract.strip()

        except Exception as e:
            self.stdout.write(f"  ❌ Semantic Scholar error: {e}")

        return None

    def fetch_from_url(self, url):
        """Try to extract abstract from publication URL"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Academic Research)'}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                content = response.text

                # Look for common abstract patterns
                patterns = [
                    r'<meta name="description" content="([^"]+)"',
                    r'<meta property="og:description" content="([^"]+)"',
                    r'<div[^>]*class="[^"]*abstract[^"]*"[^>]*>([^<]+)',
                    r'<p[^>]*class="[^"]*abstract[^"]*"[^>]*>([^<]+)',
                ]

                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                    if match:
                        abstract = match.group(1).strip()
                        if len(abstract) > 50:  # Reasonable length for abstract
                            # Clean HTML entities
                            abstract = re.sub(r'&[a-zA-Z0-9#]+;', ' ', abstract)
                            return abstract

        except Exception as e:
            self.stdout.write(f"  ❌ URL fetch error: {e}")

        return None

    def titles_match(self, title1, title2, threshold=0.7):
        """Check if two titles match reasonably well"""
        if not title1 or not title2:
            return False

        # Simple word overlap check
        words1 = set(re.findall(r'\w+', title1.lower()))
        words2 = set(re.findall(r'\w+', title2.lower()))

        if not words1 or not words2:
            return False

        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))

        return (overlap / total) >= threshold


# Alternative: Manual abstract injection script
# Create this file: inject_abstracts_manual.py (in project root)

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perswebsite.settings')
django.setup()

from myapp.models import Publication


def inject_sample_abstracts():
    """Inject some sample abstracts for key publications"""

    abstracts = {
        "Random projection streams": """
        This paper introduces random projection streams for weighted nonnegative matrix factorization (NMF). 
        We propose a novel streaming approach that maintains the factorization quality while significantly 
        reducing computational complexity. The method is particularly effective for large-scale data processing 
        where traditional batch methods become computationally prohibitive.
        """,

        "framework for compressed weighted": """
        We present a comprehensive framework for compressed weighted nonnegative matrix factorization that 
        addresses the challenges of processing large-scale, incomplete datasets. The proposed method combines 
        compression techniques with weighted factorization to achieve both computational efficiency and 
        improved reconstruction quality in the presence of missing data.
        """,

        "How to apply random projections": """
        This work investigates the application of random projections to nonnegative matrix factorization 
        with missing entries. We analyze the theoretical properties of the proposed approach and demonstrate 
        its effectiveness on various real-world datasets, showing significant improvements in both speed 
        and accuracy compared to existing methods.
        """,

        "Edge finding in magnetic resonance": """
        This paper presents a novel approach for edge detection in magnetic resonance imaging applications. 
        We develop a method for calculating the first-order derivative of two-dimensional images that is 
        specifically optimized for MRI data characteristics, improving edge detection accuracy while 
        maintaining computational efficiency.
        """,

        "In situ calibration": """
        We propose an in-situ calibration method for cross-sensitive sensors in mobile sensor arrays using 
        fast informed non-negative matrix factorization. The approach enables real-time calibration without 
        requiring reference measurements, making it particularly suitable for environmental monitoring 
        applications with mobile sensor networks.
        """
    }

    print("🚀 Injecting sample abstracts...")

    for search_term, abstract in abstracts.items():
        try:
            pub = Publication.objects.filter(title__icontains=search_term).first()
            if pub and not pub.abstract:
                pub.abstract = abstract.strip()
                pub.save()
                print(f"✅ Added abstract for: {pub.title[:50]}...")
            elif pub and pub.abstract:
                print(f"⚠️ Already has abstract: {pub.title[:50]}...")
            else:
                print(f"❌ Not found: {search_term}")
        except Exception as e:
            print(f"💥 Error: {e}")

    print("🎉 Abstract injection complete!")


if __name__ == "__main__":
    inject_sample_abstracts()