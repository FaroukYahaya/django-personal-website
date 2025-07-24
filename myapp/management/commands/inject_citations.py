# Create this file: myapp/management/commands/inject_citations.py
from django.db import models
from django.core.management.base import BaseCommand
from myapp.models import Publication
from django.utils import timezone


class Command(BaseCommand):
    help = 'Inject real citation data from Google Scholar profile'

    def handle(self, *args, **options):
        # Real citation data from your Google Scholar page
        # https://scholar.google.com/citations?user=p8zrh5gAAAAJ&hl=en

        citation_data = {
            # Title (partial match) : Citation Count
            "Random projection streams for (weighted) nonnegative matrix factorization": 12,
            "A compilation on the contribution of the classic-curvature and the intensity-curvature functional": 12,
            "How to apply random projections to nonnegative matrix factorization with missing entries": 11,
            "Faster-than-fast NMF using random projections and Nesterov iterations": 8,
            "In situ calibration of cross-sensitive sensors in mobile sensor arrays": 7,
            "Edge finding in magnetic resonance imaging applications": 7,
            "A framework for compressed weighted nonnegative matrix factorization": 4,
            "Compressive informed (semi-) non-negative matrix factorization methods": 4,
            "A novel approach to T2-weighted MRI filtering": 4,
            "Gaussian compression stream: principle and preliminary results": 3,
            "Acceleration de la factorisation ponderee en matrices non-negatives": 2,
            "Fast & furious: accelerating weighted NMF using random projections": 2,
            "NMF for Big Data with Missing Entries": 2,
            "Non-Negative Matrix Factorization with Missing Entries": 2,
            "Cartographie et etalonnage de capteurs conjoints": 2,
            "Calibration en ligne d'un reseau de capteurs mobiles": 1,
            "Do random projections fasten an already fast NMF technique": 1,
            "Towards an Optimized Mathematical Form of an Edge Detector": 1,
            "Fast informed nonnegative matrix factorization for mobile sensor calibration": 0,
            "Methodes etendues de factorisation informee de matrices": 0,
            "Proposition de stage recherche M2 en laboratoire": 0,
        }

        self.stdout.write("🚀 Starting citation injection...")
        self.stdout.write("=" * 60)

        updated_count = 0
        not_found_count = 0

        for title_partial, citation_count in citation_data.items():
            try:
                # Try to find the publication by partial title match
                publication = None

                # First try exact match
                try:
                    publication = Publication.objects.get(title__iexact=title_partial)
                except Publication.DoesNotExist:
                    # Try partial match
                    try:
                        # Get the first 30 characters for matching
                        search_term = title_partial[:30]
                        publication = Publication.objects.get(title__icontains=search_term)
                    except Publication.DoesNotExist:
                        # Try different approach - match by key words
                        key_words = title_partial.split()[:3]  # First 3 words
                        matches = Publication.objects.filter(title__icontains=key_words[0])

                        for match in matches:
                            if any(word.lower() in match.title.lower() for word in key_words[1:]):
                                publication = match
                                break

                if publication:
                    old_count = publication.citation_count
                    publication.citation_count = citation_count
                    publication.last_citation_update = timezone.now()
                    publication.save()

                    updated_count += 1

                    # Color coding for output
                    if citation_count >= 10:
                        color = self.style.SUCCESS
                    elif citation_count >= 5:
                        color = self.style.WARNING
                    else:
                        color = self.style.NOTICE

                    self.stdout.write(
                        color(f"✅ Updated: {publication.title[:50]}...")
                    )
                    self.stdout.write(f"   Citations: {old_count} → {citation_count}")
                    self.stdout.write("")

                else:
                    not_found_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"❌ Not found: {title_partial[:50]}...")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"💥 Error processing '{title_partial[:30]}...': {e}")
                )

        # Summary
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"🎉 SUMMARY:"))
        self.stdout.write(f"✅ Successfully updated: {updated_count} publications")
        self.stdout.write(f"❌ Not found: {not_found_count} publications")

        # Calculate total citations
        total_citations = Publication.objects.aggregate(
            total=models.Sum('citation_count')
        )['total'] or 0

        self.stdout.write(f"📊 Total citations in database: {total_citations}")

        # Show top cited papers
        self.stdout.write("\n🏆 TOP CITED PAPERS:")
        top_papers = Publication.objects.filter(citation_count__gt=0).order_by('-citation_count')[:5]
        for i, paper in enumerate(top_papers, 1):
            self.stdout.write(f"  {i}. {paper.title[:40]}... ({paper.citation_count} citations)")

        self.stdout.write("\n🚀 Citation injection complete!")
        self.stdout.write("💡 Tip: Check your publications page to see the updated citation counts!")


# Alternative version if the above doesn't work well
class Command2(BaseCommand):
    help = 'Alternative citation injection method'

    def handle(self, *args, **options):
        # Manual mapping by publication ID (you'd need to check your database first)
        # Run this to get publication IDs:
        # python manage.py shell
        # from myapp.models import Publication
        # for p in Publication.objects.all():
        #     print(f"ID: {p.id}, Title: {p.title[:50]}")

        # Then update this dictionary with ID: citation_count
        id_citations = {
            # 1: 12,  # Replace with actual IDs from your database
            # 2: 11,
            # 3: 8,
            # etc...
        }

        self.stdout.write("📝 Manual ID-based citation update...")
        self.stdout.write("First, run this to see your publication IDs:")
        self.stdout.write("python manage.py shell")
        self.stdout.write("from myapp.models import Publication")
        self.stdout.write("for p in Publication.objects.all()[:5]:")
        self.stdout.write("    print(f'ID: {p.id}, Title: {p.title[:50]}')")

        if not id_citations:
            self.stdout.write(self.style.WARNING("No citation data provided. Update the id_citations dictionary first."))
            return

        for pub_id, citation_count in id_citations.items():
            try:
                pub = Publication.objects.get(id=pub_id)
                pub.citation_count = citation_count
                pub.last_citation_update = timezone.now()
                pub.save()
                self.stdout.write(f"✅ Updated ID {pub_id}: {citation_count} citations")
            except Publication.DoesNotExist:
                self.stdout.write(f"❌ Publication ID {pub_id} not found")