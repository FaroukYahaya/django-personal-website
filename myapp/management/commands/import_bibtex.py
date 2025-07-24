import bibtexparser
from django.core.management.base import BaseCommand
from myapp.models import Publication

class Command(BaseCommand):
    help = 'Import publications from a BibTeX file'

    def add_arguments(self, parser):
        parser.add_argument('bibtex_file', type=str, help='Path to the BibTeX file')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing publications before importing',
        )
        parser.add_argument(
            '--featured',
            action='store_true',
            help='Mark all imported publications as featured',
        )

    def handle(self, *args, **options):
        bibtex_file = options['bibtex_file']

        if options['clear']:
            Publication.objects.all().delete()
            self.stdout.write("Cleared existing publications")

        try:
            with open(bibtex_file, 'r', encoding='utf-8') as file:
                bib_database = bibtexparser.load(file)

            created_count = 0
            for entry in bib_database.entries:
                try:
                    # Convert the entry back to BibTeX string
                    bibtex_str = bibtexparser.dumps(bibtexparser.bibliographydatabase.BibliographyDatabase([entry]))

                    publication = Publication(
                        bibtex_entry=bibtex_str,
                        featured=options['featured']
                    )
                    publication.save()  # This will automatically parse the BibTeX
                    created_count += 1
                    self.stdout.write(f"Created: {publication.title}")
                except Exception as e:
                    self.stdout.write(f"Error creating publication from entry {entry.get('ID', 'unknown')}: {e}")

            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {created_count} publications from {bibtex_file}')
            )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {bibtex_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading BibTeX file: {e}')
            )
