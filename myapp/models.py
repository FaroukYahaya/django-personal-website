# myapp/models.py - COMPLETE FILE
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from datetime import timedelta
import re


# ===== EXISTING PUBLICATION MODEL =====
class Publication(models.Model):
    # Original fields
    bibtex_entry = models.TextField()
    featured = models.BooleanField(default=False)

    # Parsed BibTeX fields - these should be automatically populated
    title = models.CharField(max_length=500, blank=True)
    authors = models.CharField(max_length=1000, blank=True)
    year = models.IntegerField(null=True, blank=True)
    journal = models.CharField(max_length=300, blank=True)
    booktitle = models.CharField(max_length=300, blank=True)
    organization = models.CharField(max_length=300, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    volume = models.CharField(max_length=20, blank=True)
    number = models.CharField(max_length=20, blank=True)
    doi = models.CharField(max_length=100, blank=True)
    url = models.URLField(blank=True)
    abstract = models.TextField(blank=True)

    # Citation fields
    citation_count = models.IntegerField(default=0, help_text="Number of citations from Google Scholar")
    last_citation_update = models.DateTimeField(null=True, blank=True, help_text="When citations were last updated")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return self.title or f"Publication {self.id}"

    def save(self, *args, **kwargs):
        """Parse BibTeX entry when saving"""
        if self.bibtex_entry:
            self.parse_bibtex()
        super().save(*args, **kwargs)

    def parse_bibtex(self):
        """Parse BibTeX entry and populate fields"""
        entry = self.bibtex_entry.strip()

        # Parse title
        title_match = re.search(r'title\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if title_match:
            self.title = self.clean_bibtex_field(title_match.group(1))

        # Parse authors
        author_match = re.search(r'author\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if author_match:
            self.authors = self.clean_bibtex_field(author_match.group(1))

        # Parse year
        year_match = re.search(r'year\s*=\s*\{?(\d{4})\}?', entry, re.IGNORECASE)
        if year_match:
            self.year = int(year_match.group(1))

        # Parse journal
        journal_match = re.search(r'journal\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if journal_match:
            self.journal = self.clean_bibtex_field(journal_match.group(1))

        # Parse booktitle
        booktitle_match = re.search(r'booktitle\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if booktitle_match:
            self.booktitle = self.clean_bibtex_field(booktitle_match.group(1))

        # Parse organization
        org_match = re.search(r'organization\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if org_match:
            self.organization = self.clean_bibtex_field(org_match.group(1))

        # Parse publisher
        pub_match = re.search(r'publisher\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if pub_match:
            self.publisher = self.clean_bibtex_field(pub_match.group(1))

        # Parse pages
        pages_match = re.search(r'pages\s*=\s*\{([^{}]*)\}', entry, re.IGNORECASE)
        if pages_match:
            self.pages = self.clean_bibtex_field(pages_match.group(1))

        # Parse volume
        volume_match = re.search(r'volume\s*=\s*\{([^{}]*)\}', entry, re.IGNORECASE)
        if volume_match:
            self.volume = self.clean_bibtex_field(volume_match.group(1))

        # Parse number
        number_match = re.search(r'number\s*=\s*\{([^{}]*)\}', entry, re.IGNORECASE)
        if number_match:
            self.number = self.clean_bibtex_field(number_match.group(1))

        # Parse DOI
        doi_match = re.search(r'doi\s*=\s*\{([^{}]*)\}', entry, re.IGNORECASE)
        if doi_match:
            self.doi = self.clean_bibtex_field(doi_match.group(1))

        # Parse URL
        url_match = re.search(r'url\s*=\s*\{([^{}]*)\}', entry, re.IGNORECASE)
        if url_match:
            self.url = self.clean_bibtex_field(url_match.group(1))

        # Parse abstract
        abstract_match = re.search(r'abstract\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}', entry, re.IGNORECASE)
        if abstract_match:
            self.abstract = self.clean_bibtex_field(abstract_match.group(1))

    def clean_bibtex_field(self, field):
        """Clean BibTeX field by removing extra spaces and LaTeX commands"""
        if not field:
            return ""

        # Remove common LaTeX commands
        field = re.sub(r'\\[a-zA-Z]+\{([^{}]*)\}', r'\1', field)
        field = re.sub(r'\\[a-zA-Z]+', '', field)

        # Replace special characters
        field = field.replace('\\"a', 'ä').replace('\\"o', 'ö').replace('\\"u', 'ü')
        field = field.replace('\\`a', 'à').replace('\\`e', 'è').replace('\\`i', 'ì')
        field = field.replace("\\'a", 'á').replace("\\'e", 'é').replace("\\'i", 'í')
        field = field.replace('\\^a', 'â').replace('\\^e', 'ê').replace('\\^i', 'î')
        field = field.replace('\\~n', 'ñ')
        field = field.replace('\\c{c}', 'ç').replace('\\c{C}', 'Ç')

        # Clean up extra whitespace
        field = re.sub(r'\s+', ' ', field).strip()

        return field

    def update_citations(self):
        """Update citation count for this publication"""
        from .utils import get_citations_for_publication

        if self.title and self.authors:
            try:
                citation_count = get_citations_for_publication(self.title, self.authors)
                self.citation_count = citation_count
                self.last_citation_update = timezone.now()
                self.save()
                return citation_count
            except Exception as e:
                print(f"Error updating citations for {self.title}: {e}")
                return self.citation_count
        return 0

    @property
    def needs_citation_update(self):
        """Check if citation count needs updating (older than 7 days)"""
        if not self.last_citation_update:
            return True

        return timezone.now() - self.last_citation_update > timedelta(days=7)

    @property
    def publication_type(self):
        """Determine the type of publication"""
        if self.journal:
            return "Journal Article"
        elif self.booktitle:
            if any(word in self.booktitle.lower() for word in ['conference', 'symposium', 'workshop', 'congress']):
                return "Conference Paper"
            elif 'thesis' in self.booktitle.lower() or 'dissertation' in self.booktitle.lower():
                return "Thesis"
            else:
                return "Proceedings"
        elif self.organization:
            return "Technical Report"
        else:
            return "Publication"

    @property
    def short_authors(self):
        """Return abbreviated author list for display"""
        if not self.authors:
            return ""

        authors = [author.strip() for author in self.authors.split(' and ')]
        if len(authors) <= 3:
            return self.authors
        else:
            return f"{authors[0]} et al."

    @property
    def citation_text(self):
        """Generate a formatted citation"""
        parts = []

        if self.authors:
            parts.append(self.short_authors)

        if self.title:
            parts.append(f'"{self.title}"')

        if self.journal:
            parts.append(self.journal)
        elif self.booktitle:
            parts.append(self.booktitle)

        if self.year:
            parts.append(f"({self.year})")

        return ", ".join(parts)


# ===== NEW MODELS FOR NEWS & POSTS =====
class Tag(models.Model):
    """Model for post tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    """Model for news and posts"""

    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('post', 'Post'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    # Basic fields
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='post')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    # Content
    excerpt = models.TextField(max_length=500, help_text="Brief description for listings")
    content = models.TextField(help_text="Main content (HTML allowed)")

    # Metadata
    tags = models.ManyToManyField(Tag, blank=True)
    read_time = models.PositiveIntegerField(null=True, blank=True, help_text="Estimated read time in minutes")
    featured = models.BooleanField(default=False, help_text="Feature this post on homepage")

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Author (optional - you can set a default user ID)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    # SEO fields
    meta_description = models.CharField(max_length=160, blank=True, help_text="For search engines")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Auto-generate slug from title
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Ensure unique slug
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Auto-calculate read time if not set
        if not self.read_time and self.content:
            # Rough estimate: 200 words per minute
            word_count = len(self.content.split())
            self.read_time = max(1, round(word_count / 200))

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('publications:post_detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        return self.status == 'published'

    @property
    def is_news(self):
        return self.category == 'news'

    @property
    def is_post(self):
        return self.category == 'post'

    def get_next_post(self):
        """Get the next published post"""
        return Post.objects.filter(
            status='published',
            created_at__gt=self.created_at
        ).order_by('created_at').first()

    def get_previous_post(self):
        """Get the previous published post"""
        return Post.objects.filter(
            status='published',
            created_at__lt=self.created_at
        ).order_by('-created_at').first()

    @classmethod
    def get_published(cls):
        """Get all published posts"""
        return cls.objects.filter(status='published')

    @classmethod
    def get_latest(cls, count=3):
        """Get latest published posts"""
        return cls.get_published().order_by('-created_at')[:count]

    @classmethod
    def get_featured(cls):
        """Get featured posts"""
        return cls.get_published().filter(featured=True)

    @classmethod
    def get_by_category(cls, category):
        """Get posts by category"""
        return cls.get_published().filter(category=category)


# Add this to your models.py file

class HomePage(models.Model):
    """Model for home page content - editable via Django admin"""

    # Biography Section
    biography_title = models.CharField(max_length=100, default="Biography")
    biography_content = models.TextField(
        help_text="Main biography text. You can use HTML tags for formatting like <span class='highlight'>text</span>"
    )

    # Contact Information
    email = models.EmailField(default="faroukyahayaco@gmail.com")
    phone = models.CharField(max_length=20, default="+33 66 6 69 69 19")
    address = models.TextField(default="37 cours de Quebec\nBordeaux, France")

    # Research Interests
    research_interests_title = models.CharField(max_length=100, default="Research Interests")
    research_interests_content = models.TextField(
        default="Inverse filtering, Source Separation, Array signal processing, High-dimensional data analysis, Matrix/Tensor decomposition, Compressive learning, Randomized methods, Sensor calibration, Low-rank approximations, Medical image analysis (2D MRI, fMRI modalities)"
    )

    # Social Media Links
    linkedin_url = models.URLField(default="https://fr.linkedin.com/in/faroya", blank=True)
    scholar_url = models.URLField(default="https://scholar.google.com/citations?user=p8zrh5gAAAAJ&hl=en", blank=True)
    orcid_url = models.URLField(default="https://orcid.org/0000-0003-4147-2453", blank=True)
    researchgate_url = models.URLField(default="https://www.researchgate.net/profile/Farouk-Yahaya", blank=True)
    github_url = models.URLField(default="https://github.com/FaroukYahaya", blank=True)

    # Professional Experience Section
    experience_title = models.CharField(max_length=100, default="Professional Experience")
    show_experience = models.BooleanField(default=True, help_text="Show/hide the professional experience section")

    # Education Section
    education_title = models.CharField(max_length=100, default="Education")
    show_education = models.BooleanField(default=True, help_text="Show/hide the education section")

    # Latest News Section
    news_title = models.CharField(max_length=100, default="Latest News")
    show_news = models.BooleanField(default=True, help_text="Show/hide the latest news section")
    news_count = models.PositiveIntegerField(default=3, help_text="Number of latest posts to show")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Page"

    def __str__(self):
        return "Home Page Content"

    @classmethod
    def get_content(cls):
        """Get or create the home page content"""
        content, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'biography_content': '''I am an <span class="highlight">AI/ML Research Engineer</span> with expertise in machine learning, artificial intelligence, and computational research. My research interests include inverse filtering, source separation, array signal processing, high-dimensional data analysis, matrix/tensor decomposition, compressive learning, randomized methods, sensor calibration, low-rank approximations and medical image analysis.

Currently working as an AI/ML Engineer at <span class="highlight">Expleo</span> in Mérignac, France, where I lead a team developing AI-powered smart tooling for aerospace clients. I completed my Ph.D. in Computer Science at <span class="highlight">Université du Littoral Côte d'Opale (ULCO)</span> focusing on compressive informed non-negative matrix factorization methods for incomplete and large-scale data.

My work spans across various domains including computer vision, predictive analytics, neurodegenerative disease classification, and bio-signal processing. I have experience in both academic research and industrial applications, with a strong background in teaching and student supervision.'''
            }
        )
        return content


# Add separate models for timeline items to make them editable
class ProfessionalExperience(models.Model):
    """Model for professional experience timeline items"""

    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    start_date = models.CharField(max_length=20, help_text="e.g., 'Feb 2024', 'Jul 2022'")
    end_date = models.CharField(max_length=20, help_text="e.g., 'Present', 'Jan 2024'")
    description = models.TextField(blank=True, help_text="Optional description of the role")
    order = models.PositiveIntegerField(default=0, help_text="Order in timeline (0 = most recent)")

    class Meta:
        ordering = ['order']
        verbose_name = "Professional Experience"
        verbose_name_plural = "Professional Experiences"

    def __str__(self):
        return f"{self.position} at {self.company}"

    @property
    def date_range(self):
        return f"{self.start_date} - {self.end_date}"


class Education(models.Model):
    """Model for education timeline items"""

    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    start_year = models.CharField(max_length=10, help_text="e.g., '2018'")
    end_year = models.CharField(max_length=10, help_text="e.g., '2021'")
    description = models.TextField(blank=True, help_text="Optional description or thesis title")
    order = models.PositiveIntegerField(default=0, help_text="Order in timeline (0 = most recent)")

    class Meta:
        ordering = ['order']
        verbose_name = "Education"
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree} at {self.institution}"

    @property
    def date_range(self):
        return f"{self.start_year} - {self.end_year}"

    # This is how the END of your models.py should look:

    # ... (all your existing models above) ...




    # TEACHING MODELS START HERE - MAKE SURE THEY'RE AT THE SAME LEVEL AS Education, NOT INSIDE IT!

class TeachingPage(models.Model):
    """Model for teaching page content"""

    # Page content
    page_title = models.CharField(max_length=100, default="Teaching")
    introduction = models.TextField(
        default="I enjoy teaching computer science and AI concepts, from basic programming to advanced machine learning. My approach focuses on practical learning and real-world applications.",
        help_text="Main introduction text for the teaching page"
    )

    # Page settings
    show_statistics = models.BooleanField(default=True, help_text="Show teaching statistics")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Teaching Page"
        verbose_name_plural = "Teaching Page"

    def __str__(self):
        return "Teaching Page Content"

    @classmethod
    def get_content(cls):
        """Get or create the teaching page content"""
        content, created = cls.objects.get_or_create(pk=1)
        return content


class AcademicYear(models.Model):
    """Model for academic years"""

    year_start = models.IntegerField(help_text="Starting year (e.g., 2021)")
    year_end = models.IntegerField(help_text="Ending year (e.g., 2022)")
    description = models.TextField(blank=True, help_text="Optional description for this academic year")
    is_active = models.BooleanField(default=True, help_text="Show this academic year on the page")

    class Meta:
        ordering = ['-year_start']
        unique_together = ['year_start', 'year_end']

    def __str__(self):
        return f"{self.year_start} — {self.year_end}"

    @property
    def year_display(self):
        return f"{self.year_start} — {self.year_end}"


class Course(models.Model):
    """Model for individual courses"""

    SEMESTER_CHOICES = [
        ('1', 'Semester 1'),
        ('2', 'Semester 2'),
        ('full', 'Full Year'),
        ('other', 'Other'),
    ]

    INSTITUTION_CHOICES = [
        ('ULCO', 'ULCO'),
        ('EIL', 'EIL'),
        ('IUT', 'IUT'),
        ('other', 'Other'),
    ]

    # Basic course information
    title = models.CharField(max_length=200)
    credits = models.CharField(max_length=20, blank=True, help_text="e.g., '3 ECTS'")
    description = models.TextField(blank=True, help_text="Course description")

    # Academic placement
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='courses')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='1')
    institution = models.CharField(max_length=50, choices=INSTITUTION_CHOICES, default='ULCO')
    custom_institution = models.CharField(max_length=100, blank=True, help_text="If 'Other' is selected above")

    # Teaching details
    hours_per_week = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Hours per week")
    total_hours = models.IntegerField(null=True, blank=True, help_text="Total hours for the course")
    student_count = models.IntegerField(null=True, blank=True, help_text="Number of students")

    # Additional information
    co_teachers = models.CharField(max_length=200, blank=True, help_text="Co-teachers (e.g., 'A. Ahmad')")
    topics_covered = models.TextField(blank=True, help_text="Main topics covered (comma-separated)")
    technologies_used = models.CharField(max_length=200, blank=True, help_text="Technologies/tools used (e.g., 'Python, scikit-learn')")

    # Metadata
    order = models.PositiveIntegerField(default=0, help_text="Order within semester (0 = first)")
    is_featured = models.BooleanField(default=False, help_text="Highlight this course")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['academic_year', 'semester', 'order', 'title']

    def __str__(self):
        return f"{self.title} ({self.academic_year})"

    @property
    def institution_display(self):
        """Get the display name for institution"""
        if self.institution == 'other' and self.custom_institution:
            return self.custom_institution
        return self.get_institution_display()

    @property
    def credits_display(self):
        """Format credits for display"""
        return f"({self.credits})" if self.credits else ""

    @property
    def co_teachers_display(self):
        """Format co-teachers for display"""
        if self.co_teachers:
            return f"(co-taught with {self.co_teachers})"
        return ""


class TeachingStatistic(models.Model):
    """Model for teaching statistics"""

    STAT_TYPES = [
        ('total_courses', 'Total Courses Taught'),
        ('total_students', 'Total Students Taught'),
        ('total_hours', 'Total Teaching Hours'),
        ('years_experience', 'Years of Teaching Experience'),
    ]

    stat_type = models.CharField(max_length=20, choices=STAT_TYPES, unique=True)
    value = models.CharField(max_length=20, help_text="e.g., '15', '500+', '3 years'")
    description = models.CharField(max_length=100, blank=True)
    show_on_page = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'stat_type']

    def __str__(self):
        return f"{self.get_stat_type_display()}: {self.value}"