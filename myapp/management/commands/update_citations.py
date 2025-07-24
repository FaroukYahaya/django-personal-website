# myapp/management/commands/update_citations.py
from django.core.management.base import BaseCommand
from myapp.models import Publication
from myapp.utils import get_citations_for_publication
import time

class Command(BaseCommand):
    help = 'Update citation counts for all publications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of publications to update',
        )
        parser.add_argument(
            '--delay',
            type=int,
            default=2,
            help='Delay between requests in seconds',
        )

    def handle(self, *args, **options):
        publications = Publication.objects.all()

        if options['limit']:
            publications = publications[:options['limit']]

        updated_count = 0
        total_count = publications.count()

        self.stdout.write(f"Updating citations for {total_count} publications...")

        for i, pub in enumerate(publications, 1):
            if pub.title and pub.authors:
                try:
                    self.stdout.write(f"[{i}/{total_count}] Updating: {pub.title[:50]}...")

                    citation_count = get_citations_for_publication(pub.title, pub.authors)
                    pub.citation_count = citation_count
                    pub.save()

                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"  → {citation_count} citations")
                    )

                    # Delay to be respectful to Google Scholar
                    if i < total_count:  # Don't delay after the last one
                        time.sleep(options['delay'])

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  → Error: {e}")
                    )
                    continue
            else:
                self.stdout.write(
                    self.style.WARNING(f"[{i}/{total_count}] Skipping: Missing title or authors")
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} publications')
        )
