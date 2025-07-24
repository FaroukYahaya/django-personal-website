# First, install django-summernote for rich text editing
# Run: pip install django-summernote Pygments

# Then add 'django_summernote' to your INSTALLED_APPS in settings.py
# INSTALLED_APPS = [
#     ...
#     'django_summernote',
#     ...
# ]

# Add this to your main urls.py (not your app urls.py):
# from django.urls import path, include
# urlpatterns = [
#     ...
#     path('summernote/', include('django_summernote.urls')),
#     ...
# ]

# Updated admin.py with rich text editor and code support
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from django_summernote.admin import SummernoteModelAdmin
from .models import Publication, Post, Tag

# Add this to your admin.py file

from .models import HomePage, ProfessionalExperience, Education

# Add these to your myapp/admin.py file

from .models import TeachingPage, AcademicYear, Course, TeachingStatistic


@admin.register(TeachingPage)
class TeachingPageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Page Content', {
            'fields': ('page_title', 'introduction'),
        }),
        ('Settings', {
            'fields': ('show_statistics',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return not TeachingPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year_display', 'course_count', 'is_active')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    ordering = ['-year_start']

    def course_count(self, obj):
        return obj.courses.count()

    course_count.short_description = 'Courses'


class CourseInline(admin.TabularInline):
    model = Course
    extra = 0
    fields = ('title', 'semester', 'credits', 'order', 'is_featured')
    ordering = ['semester', 'order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'academic_year', 'semester', 'institution_display', 'credits', 'is_featured')
    list_filter = ('academic_year', 'semester', 'institution', 'is_featured')
    search_fields = ('title', 'description', 'topics_covered')
    list_editable = ('is_featured',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'credits', 'description')
        }),
        ('Academic Placement', {
            'fields': ('academic_year', 'semester', 'institution', 'custom_institution')
        }),
        ('Teaching Details', {
            'fields': ('hours_per_week', 'total_hours', 'student_count', 'co_teachers'),
            'classes': ('collapse',)
        }),
        ('Course Content', {
            'fields': ('topics_covered', 'technologies_used'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('order', 'is_featured'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('academic_year')


@admin.register(TeachingStatistic)
class TeachingStatisticAdmin(admin.ModelAdmin):
    list_display = ('get_stat_type_display', 'value', 'show_on_page', 'order')
    list_editable = ('value', 'show_on_page', 'order')
    list_filter = ('stat_type', 'show_on_page')
    ordering = ['order']


@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Biography Section', {
            'fields': ('biography_title', 'biography_content'),
            'description': 'Edit the main biography section'
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address'),
            'description': 'Update your contact details'
        }),
        ('Research Interests', {
            'fields': ('research_interests_title', 'research_interests_content'),
            'description': 'Edit your research interests'
        }),
        ('Social Media Links', {
            'fields': ('linkedin_url', 'scholar_url', 'orcid_url', 'researchgate_url', 'github_url'),
            'description': 'Update your social media and academic profile links'
        }),
        ('Section Visibility', {
            'fields': (
                ('experience_title', 'show_experience'),
                ('education_title', 'show_education'),
                ('news_title', 'show_news', 'news_count')
            ),
            'description': 'Control which sections are displayed and their titles'
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        # Prevent adding multiple instances - only allow one home page
        return not HomePage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of home page content
        return False

    def changelist_view(self, request, extra_context=None):
        # If no home page exists, redirect to add form
        if not HomePage.objects.exists():
            return self.add_view(request, extra_context=extra_context)
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ProfessionalExperience)
class ProfessionalExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'date_range', 'order')
    list_editable = ('order',)
    list_filter = ('company',)
    search_fields = ('position', 'company', 'location')

    fieldsets = (
        (None, {
            'fields': ('position', 'company', 'location')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'order'),
            'description': 'Set the timeline order (0 = most recent position)'
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',),
            'description': 'Optional description of the role'
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'date_range', 'order')
    list_editable = ('order',)
    list_filter = ('institution',)
    search_fields = ('degree', 'institution', 'location')

    fieldsets = (
        (None, {
            'fields': ('degree', 'institution', 'location')
        }),
        ('Timeline', {
            'fields': ('start_year', 'end_year', 'order'),
            'description': 'Set the timeline order (0 = most recent degree)'
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',),
            'description': 'Optional description or thesis title'
        }),
    )


# ===== PUBLICATION ADMIN (KEEP AS IS) =====
class PublicationTypeFilter(admin.SimpleListFilter):
    """Custom filter for publication type"""
    title = 'publication type'
    parameter_name = 'pub_type'

    def lookups(self, request, model_admin):
        return (
            ('journal', 'Journal Articles'),
            ('conference', 'Conference Papers'),
            ('thesis', 'Thesis/Dissertation'),
            ('report', 'Technical Reports'),
            ('other', 'Other'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'journal':
            return queryset.filter(journal__isnull=False).exclude(journal='')
        elif self.value() == 'conference':
            return queryset.filter(booktitle__isnull=False).exclude(booktitle='')
        elif self.value() == 'thesis':
            return queryset.filter(organization__isnull=False).exclude(organization='')
        elif self.value() == 'report':
            return queryset.filter(
                journal__isnull=True,
                booktitle__isnull=True,
                organization__isnull=True
            )
        elif self.value() == 'other':
            return queryset.filter(
                journal__exact='',
                booktitle__exact='',
                organization__exact=''
            )
        return queryset


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = [
        'get_title_display',
        'short_authors',
        'year',
        'get_publication_type',
        'get_citation_display',
        'featured',
        'created_at'
    ]

    list_filter = [
        'featured',
        PublicationTypeFilter,
        'year',
        ('created_at', admin.DateFieldListFilter),
        ('last_citation_update', admin.DateFieldListFilter),
    ]

    search_fields = [
        'title',
        'authors',
        'journal',
        'booktitle',
        'organization',
        'bibtex_entry'
    ]

    list_editable = ['featured']
    list_per_page = 25
    ordering = ['-created_at']

    fieldsets = (
        ('📝 Quick Add - Just Paste BibTeX', {
            'fields': ('bibtex_entry', 'featured'),
            'description': '''
                <div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h4>📋 How to Add a Publication:</h4>
                    <ol>
                        <li><strong>Get BibTeX:</strong> Go to Google Scholar, search your paper, click "Cite" → "BibTeX"</li>
                        <li><strong>Copy & Paste:</strong> Copy the BibTeX entry and paste it below</li>
                        <li><strong>Save:</strong> Click "Save" - all fields will auto-populate!</li>
                        <li><strong>Optional:</strong> Check "Featured" to highlight on homepage</li>
                    </ol>
                    <p><strong>💡 Tip:</strong> You can also get BibTeX from journal websites, Zotero, Mendeley, etc.</p>
                </div>
            '''
        }),
        ('📄 Parsed Information (Auto-filled)', {
            'fields': (
                ('title', 'year'),
                'authors',
                ('journal', 'booktitle', 'organization'),
                ('volume', 'number', 'pages'),
                ('doi', 'url'),
                'publisher',
                'abstract'
            ),
            'classes': ('collapse',),
            'description': 'These fields are automatically populated from your BibTeX entry. You can edit them manually if needed.'
        }),
        ('📊 Citation Data', {
            'fields': (
                ('citation_count', 'last_citation_update'),
            ),
            'classes': ('collapse',),
            'description': 'Citation data is automatically updated. Use the "Update Citations" action to refresh.'
        }),
        ('🔧 Advanced', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System timestamps - automatically managed.'
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'last_citation_update']

    actions = [
        'mark_as_featured',
        'mark_as_not_featured',
        'update_citations_action',
        'refresh_bibtex_parsing'
    ]

    def get_title_display(self, obj):
        if len(obj.title) > 60:
            return format_html(
                '<span title="{}">{}</span>',
                obj.title,
                obj.title[:60] + "..."
            )
        return obj.title

    get_title_display.short_description = 'Title'
    get_title_display.admin_order_field = 'title'

    def get_publication_type(self, obj):
        type_map = {
            'Journal Article': '📰',
            'Conference Paper': '🎤',
            'Technical Report': '📋',
            'Thesis': '🎓',
            'Publication': '📄'
        }
        pub_type = obj.publication_type
        icon = type_map.get(pub_type, '📄')
        return format_html('{} {}', icon, pub_type)

    get_publication_type.short_description = 'Type'

    def get_citation_display(self, obj):
        if obj.citation_count > 0:
            color = '#28a745' if obj.citation_count >= 10 else '#ffc107' if obj.citation_count >= 5 else '#6c757d'
            return format_html(
                '<span style="color: {}; font-weight: bold;">📊 {}</span>',
                color,
                obj.citation_count
            )
        return format_html('<span style="color: #6c757d;">📊 0</span>')

    get_citation_display.short_description = 'Citations'
    get_citation_display.admin_order_field = 'citation_count'

    def short_authors(self, obj):
        return obj.short_authors

    short_authors.short_description = 'Authors'

    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'✅ {updated} publication(s) marked as featured.')

    mark_as_featured.short_description = "⭐ Mark selected as featured"

    def mark_as_not_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f'✅ {updated} publication(s) unmarked as featured.')

    mark_as_not_featured.short_description = "☆ Remove featured status"

    def update_citations_action(self, request, queryset):
        """Update citation counts for selected publications"""
        count = 0
        errors = 0

        for pub in queryset:
            try:
                old_count = pub.citation_count
                new_count = pub.update_citations()
                count += 1

                if new_count != old_count:
                    self.message_user(
                        request,
                        f'📊 Updated "{pub.title[:50]}..." citations: {old_count} → {new_count}'
                    )
            except Exception as e:
                errors += 1
                self.message_user(
                    request,
                    f'❌ Error updating "{pub.title[:50]}...": {e}',
                    level='ERROR'
                )

        if count > 0:
            self.message_user(request, f'✅ Successfully updated citations for {count} publication(s).')
        if errors > 0:
            self.message_user(request, f'⚠️ {errors} publication(s) had errors.', level='WARNING')

    update_citations_action.short_description = "📊 Update citation counts"

    def refresh_bibtex_parsing(self, request, queryset):
        """Re-parse BibTeX entries for selected publications"""
        count = 0
        for pub in queryset:
            if pub.bibtex_entry:
                pub.parse_bibtex()
                pub.save()
                count += 1

        self.message_user(request, f'✅ Re-parsed {count} publication(s).')

    refresh_bibtex_parsing.short_description = "🔄 Re-parse BibTeX entries"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'bibtex_entry' in form.base_fields:
            form.base_fields['bibtex_entry'].help_text = format_html(
                '''
                <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 10px;">
                    <strong>📋 Example BibTeX Entry:</strong><br>
                    <code style="display: block; white-space: pre; font-family: monospace; margin-top: 5px;">
@article{{yahaya2024,
  title={{A framework for compressed weighted nonnegative matrix factorization}},
  author={{Yahaya, Farouk and Puigt, Matthieu and Delmaire, Gilles}},
  journal={{IEEE Transactions on Signal Processing}},
  volume={{72}},
  pages={{123--145}},
  year={{2024}},
  publisher={{IEEE}}
}}
                    </code>
                </div>
                '''
            )

        return form

    class Media:
        css = {
            'all': ('admin/css/custom.css',)
        }


# ===== TAG ADMIN =====
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        """Count of posts using this tag"""
        count = obj.post_set.count()
        if count > 0:
            url = reverse('admin:publications_post_changelist') + f'?tags__id__exact={obj.id}'
            return format_html('<a href="{}">{} posts</a>', url, count)
        return '0 posts'

    post_count.short_description = 'Posts using this tag'


# ===== POST ADMIN WITH RICH TEXT EDITOR AND CODE SUPPORT =====
@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):  # Changed to SummernoteModelAdmin for rich text
    summernote_fields = ('content',)  # Enable rich editor for content field

    # Custom Summernote configuration with code support
    summernote_config = {
        'iframe': True,
        'summernote': {
            'airMode': False,
            'width': '100%',
            'height': '500',
            'toolbar': [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'strikethrough', 'superscript', 'subscript', 'clear']],
                ['fontname', ['fontname']],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['height', ['height']],
                ['table', ['table']],
                ['insert', ['link', 'picture', 'video', 'hr']],
                ['view', ['fullscreen', 'codeview']],
                ['help', ['help']],
                ['misc', ['codeblock']],  # Code block button
            ],
            'codeblock': {
                'languages': [
                    {'name': 'Python', 'value': 'python'},
                    {'name': 'JavaScript', 'value': 'javascript'},
                    {'name': 'HTML', 'value': 'html'},
                    {'name': 'CSS', 'value': 'css'},
                    {'name': 'SQL', 'value': 'sql'},
                    {'name': 'Bash', 'value': 'bash'},
                    {'name': 'JSON', 'value': 'json'},
                    {'name': 'XML', 'value': 'xml'},
                    {'name': 'Django Template', 'value': 'django'},
                    {'name': 'YAML', 'value': 'yaml'},
                    {'name': 'PHP', 'value': 'php'},
                    {'name': 'Java', 'value': 'java'},
                    {'name': 'C++', 'value': 'cpp'},
                    {'name': 'TypeScript', 'value': 'typescript'},
                ]
            },
            'codemirror': {
                'theme': 'monokai',
                'lineNumbers': True,
                'lineWrapping': True,
            }
        },
        'css': (
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/codemirror.min.css',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/theme/monokai.min.css',
            '//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/github-dark.min.css',
        ),
        'js': (
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/codemirror.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/python/python.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/javascript/javascript.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/xml/xml.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/css/css.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/sql/sql.min.js',
            '//cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.0/mode/shell/shell.min.js',
        ),
        'lazy': False,
    }

    list_display = [
        'get_title_display',
        'category',
        'status',
        'featured',
        'created_at',
        'read_time',
        'view_link'
    ]
    list_filter = [
        'status',
        'category',
        'featured',
        'created_at',
        'tags'
    ]
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'created_at'
    list_editable = ['featured', 'status']

    fieldsets = (
        ('📝 Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'featured')
        }),
        ('📄 Content', {
            'fields': ('excerpt', 'content'),
            'description': '''
                <div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h4>📝 Writing Tips with Code Support:</h4>
                    <ul>
                        <li><strong>Code Blocks:</strong> Use the "Code Block" button in the toolbar for syntax-highlighted code</li>
                        <li><strong>Inline Code:</strong> Select text and use the code button for inline code</li>
                        <li><strong>Languages:</strong> Python, JavaScript, HTML, CSS, SQL, Bash, JSON, and more!</li>
                        <li><strong>Line Numbers:</strong> Automatically added to code blocks</li>
                        <li><strong>Themes:</strong> Dark theme for better code readability</li>
                    </ul>
                    <p><strong>💡 Tip:</strong> You can also paste code directly and it will be auto-detected!</p>
                </div>
            '''
        }),
        ('🏷️ Metadata', {
            'fields': ('tags', 'read_time', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('📅 Publishing', {
            'fields': ('created_at', 'published_at'),
            'classes': ('collapse',),
            'description': 'Published date is automatically set when status changes to published'
        }),
    )

    readonly_fields = ['updated_at', 'published_at']

    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured']

    def get_title_display(self, obj):
        """Display title with truncation and icon"""
        icons = {'news': '📰', 'post': '📝'}
        icon = icons.get(obj.category, '📄')

        if len(obj.title) > 50:
            return format_html(
                '{} <span title="{}">{}</span>',
                icon,
                obj.title,
                obj.title[:50] + "..."
            )
        return format_html('{} {}', icon, obj.title)

    get_title_display.short_description = 'Title'
    get_title_display.admin_order_field = 'title'

    def view_link(self, obj):
        """Link to view the post on the site"""
        if obj.status == 'published':
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">👁️ View</a>', url)
        return '⏳ Draft'

    view_link.short_description = 'View'

    def make_published(self, request, queryset):
        """Bulk action to publish posts"""
        updated = 0
        for post in queryset:
            post.status = 'published'
            if not post.published_at:
                post.published_at = timezone.now()
            post.save()
            updated += 1

        self.message_user(request, f'✅ {updated} posts marked as published.')

    make_published.short_description = '📢 Mark selected as published'

    def make_draft(self, request, queryset):
        """Bulk action to make posts draft"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'📝 {updated} posts marked as draft.')

    make_draft.short_description = '📝 Mark selected as draft'

    def make_featured(self, request, queryset):
        """Bulk action to feature posts"""
        updated = queryset.update(featured=True)
        self.message_user(request, f'⭐ {updated} posts marked as featured.')

    make_featured.short_description = '⭐ Mark selected as featured'

    def remove_featured(self, request, queryset):
        """Bulk action to remove featured status"""
        updated = queryset.update(featured=False)
        self.message_user(request, f'☆ {updated} posts removed from featured.')

    remove_featured.short_description = '☆ Remove featured status'

    def get_queryset(self, request):
        """Optimize queryset with prefetch_related for tags"""
        return super().get_queryset(request).prefetch_related('tags')

    class Media:
        css = {
            'all': (
                'admin/css/custom.css',
                '//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/github-dark.min.css',
            )
        }
        js = (
            '//cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js',
            'admin/js/code-highlighting.js',
        )


# Make the admin site more user-friendly
admin.site.site_header = "📚 Publications & News Management"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the Administration Portal"