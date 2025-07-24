# myapp/views.py - COMPLETE FILE - Replace your current views.py with this

import random
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Publication, Post

from django.shortcuts import render
from .models import Post, HomePage, ProfessionalExperience, Education

from .models import TeachingPage, AcademicYear, Course, TeachingStatistic

from django.db.models import Count, Sum
def home_view(request):
    # Get the home page content
    home_content = HomePage.get_content()

    # Get timeline data
    experiences = ProfessionalExperience.objects.all()
    education = Education.objects.all()

    # Get latest posts for news section
    latest_posts = Post.get_latest(count=home_content.news_count) if home_content.show_news else []

    context = {
        'home_content': home_content,
        'experiences': experiences,
        'education': education,
        'latest_posts': latest_posts,
    }

    return render(request, 'home.html', context)


def publications_list(request):
    """Display all publications in a simple Google Scholar-like format with sorting"""

    # Get search query
    search_query = request.GET.get('search', '')

    # Get sorting parameters
    sort_by = request.GET.get('sort', 'year')  # Default sort by year
    direction = request.GET.get('direction', 'desc')  # Default descending

    # Debug: Print the parameters received
    print("=== SORTING DEBUG ===")
    print(f"Sort by: {sort_by}")
    print(f"Direction: {direction}")
    print(f"Search query: {search_query}")
    print("====================")

    # Start with all publications
    publications = Publication.objects.all()

    # Apply search filter
    if search_query:
        publications = publications.filter(
            Q(title__icontains=search_query) |
            Q(authors__icontains=search_query) |
            Q(journal__icontains=search_query) |
            Q(booktitle__icontains=search_query) |
            Q(organization__icontains=search_query)
        )

    # Apply sorting
    if sort_by == 'citations':
        # Sort by citation count
        sort_field = 'citation_count'
    elif sort_by == 'year':
        # Sort by year
        sort_field = 'year'
    elif sort_by == 'title':
        # Sort by title alphabetically
        sort_field = 'title'
    else:
        # Default to year
        sort_field = 'year'

    # Apply direction
    if direction == 'desc':
        sort_field = f'-{sort_field}'

    # Add secondary sorting for consistency
    if sort_by == 'citations':
        publications = publications.order_by(sort_field, '-year', 'title')
    elif sort_by == 'year':
        publications = publications.order_by(sort_field, 'title')
    else:
        publications = publications.order_by(sort_field, '-year')

    # Get statistics
    total_publications = Publication.objects.count()
    featured_publications = Publication.objects.filter(featured=True).count()
    journal_publications = Publication.objects.filter(journal__isnull=False).exclude(journal='').count()

    # Calculate years active
    years = Publication.objects.filter(year__isnull=False).values_list('year', flat=True).distinct()
    years_active = len(years) if years else 0

    # Debug: Print first few publications to verify sorting
    print("=== PUBLICATIONS DEBUG ===")
    for i, pub in enumerate(publications[:3]):
        print(f"{i + 1}. {pub.title[:50]}...")
        print(f"   Year: {pub.year}")
        print(f"   Citations: {pub.citation_count}")
        print("---")

    context = {
        'publications': publications,
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_direction': direction,
        'total_publications': total_publications,
        'featured_publications': featured_publications,
        'journal_publications': journal_publications,
        'years_active': years_active,
    }

    return render(request, 'publications.html', context)


def publication_detail(request, pk):
    """Display a single publication with full details"""
    publication = get_object_or_404(Publication, pk=pk)

    # Get related publications (same year or similar authors)
    related_publications = Publication.objects.filter(
        Q(year=publication.year) |
        Q(authors__icontains=publication.authors.split(',')[0] if publication.authors else '')
    ).exclude(pk=publication.pk)[:5]

    context = {
        'publication': publication,
        'related_publications': related_publications,
    }

    return render(request, 'publications/detail.html', context)


# ===== NEW VIEWS FOR POSTS =====
def posts_list(request):
    """View for the posts listing page"""
    posts = Post.get_published().order_by('-created_at')

    # Handle search
    search_query = request.GET.get('search', '')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    # Handle category filter
    category = request.GET.get('category', '')
    if category in ['news', 'post']:
        posts = posts.filter(category=category)

    # Pagination
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    context = {
        'posts': posts_page,
        'search_query': search_query,
        'current_category': category,
        'total_posts': posts.count(),
    }

    return render(request, 'posts_list.html', context)


def post_detail(request, slug):
    """View for individual post detail"""
    post = get_object_or_404(Post, slug=slug, status='published')

    # Get next and previous posts
    next_post = post.get_next_post()
    previous_post = post.get_previous_post()

    # Get related posts (same category or tags)
    related_posts = Post.get_published().filter(
        Q(category=post.category) | Q(tags__in=post.tags.all())
    ).exclude(id=post.id).distinct()[:3]

    context = {
        'post': post,
        'next_post': next_post,
        'previous_post': previous_post,
        'related_posts': related_posts,
    }

    return render(request, 'post_detail.html', context)


# ===== UPDATED POSTS VIEW =====
def posts(request):
    """Redirect to the new posts_list view"""
    return posts_list(request)


# Update your teaching view in myapp/views.py

# Replace your teaching view in myapp/views.py with this fixed version:

def teaching(request):
    """Teaching page with filtering capabilities"""
    # Get page content
    teaching_content = TeachingPage.get_content()

    # Get filter parameters
    selected_year = request.GET.get('year', 'all')
    selected_semester = request.GET.get('semester', 'all')
    selected_institution = request.GET.get('institution', 'all')

    # Get all academic years for filter dropdown
    academic_years = AcademicYear.objects.filter(is_active=True).annotate(
        course_count=Count('courses')
    ).filter(course_count__gt=0)

    # Start with all courses
    courses = Course.objects.select_related('academic_year').filter(
        academic_year__is_active=True
    )

    # Apply filters
    if selected_year != 'all':
        try:
            year_id = int(selected_year)
            courses = courses.filter(academic_year__id=year_id)
        except (ValueError, TypeError):
            pass

    if selected_semester != 'all':
        courses = courses.filter(semester=selected_semester)

    if selected_institution != 'all':
        courses = courses.filter(institution=selected_institution)

    # Group courses by academic year and semester
    courses_by_year = {}
    for course in courses:
        year_key = course.academic_year.id
        if year_key not in courses_by_year:
            courses_by_year[year_key] = {
                'year': course.academic_year,
                'semesters': {}
            }

        semester = course.semester
        if semester not in courses_by_year[year_key]['semesters']:
            courses_by_year[year_key]['semesters'][semester] = []

        courses_by_year[year_key]['semesters'][semester].append(course)

    # Get teaching statistics
    statistics = TeachingStatistic.objects.filter(show_on_page=True) if teaching_content.show_statistics else []

    # Calculate dynamic statistics
    total_courses = courses.count()
    total_students = courses.aggregate(total=Sum('student_count'))['total'] or 0
    total_hours = courses.aggregate(total=Sum('total_hours'))['total'] or 0

    # Get unique institutions and semesters for filters - FIXED
    institutions = Course.objects.filter(academic_year__is_active=True).values_list('institution', flat=True).distinct().order_by('institution')
    semesters = Course.objects.filter(academic_year__is_active=True).values_list('semester', flat=True).distinct().order_by('semester')

    # Semester choices for display
    semester_choices = dict(Course.SEMESTER_CHOICES)
    institution_choices = dict(Course.INSTITUTION_CHOICES)

    context = {
        'teaching_content': teaching_content,
        'courses_by_year': dict(sorted(courses_by_year.items(), key=lambda x: x[1]['year'].year_start, reverse=True)),
        'statistics': statistics,
        'academic_years': academic_years,
        'selected_year': selected_year,
        'selected_semester': selected_semester,
        'selected_institution': selected_institution,
        'institutions': institutions,
        'semesters': semesters,
        'semester_choices': semester_choices,
        'institution_choices': institution_choices,
        'total_courses': total_courses,
        'total_students': total_students,
        'total_hours': total_hours,
    }

    return render(request, 'teaching.html', context)