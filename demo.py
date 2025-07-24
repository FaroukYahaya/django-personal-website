#!/usr/bin/env python3
"""
Script to populate teaching page with your original content
Run this from your project root: python populate_teaching_data.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perswebsite.settings')
django.setup()

from myapp.models import TeachingPage, AcademicYear, Course, TeachingStatistic


def populate_original_teaching_data():
    print("🚀 Populating teaching page with your original content...")

    # 1. Create/Update Teaching Page
    teaching_page, created = TeachingPage.objects.get_or_create(
        pk=1,
        defaults={
            'page_title': 'Teaching',
            'introduction': 'I enjoy teaching computer science and AI concepts, from basic programming to advanced machine learning. My approach focuses on <span class="highlight">practical learning</span> and real-world applications.',
            'show_statistics': True
        }
    )
    print("✅ Created/Updated Teaching Page")

    # 2. Create Academic Years
    year_2021_2022, created = AcademicYear.objects.get_or_create(
        year_start=2021,
        year_end=2022,
        defaults={'is_active': True}
    )
    if created:
        print("✅ Created Academic Year 2021-2022")

    year_2020_2021, created = AcademicYear.objects.get_or_create(
        year_start=2020,
        year_end=2021,
        defaults={'is_active': True}
    )
    if created:
        print("✅ Created Academic Year 2020-2021")

    # 3. Create Courses from your original content
    semester_1_courses = [
        {
            'title': 'Advanced Algorithms',
            'credits': '3 ECTS',
            'description': 'Computational thinking, complexity, NP-completeness, dynamic programming, greedy algorithms',
            'academic_year': year_2021_2022,
            'semester': '1',
            'institution': 'ULCO',
            'order': 0,
            'topics_covered': 'Computational thinking, complexity, NP-completeness, dynamic programming, greedy algorithms'
        },
        {
            'title': 'Synthesis Project',
            'credits': '2 ECTS',
            'description': 'Research project with LISIC: literature review and research article writing',
            'academic_year': year_2021_2022,
            'semester': '1',
            'institution': 'ULCO',
            'order': 1
        },
        {
            'title': 'Algorithms 1',
            'credits': '3 ECTS',
            'description': 'Programming fundamentals with Python: variables, functions, loops, arrays',
            'academic_year': year_2021_2022,
            'semester': '1',
            'institution': 'ULCO',
            'order': 2,
            'technologies_used': 'Python'
        },
        {
            'title': 'Web 1',
            'credits': '3 ECTS',
            'description': 'Web development basics: HTML and CSS',
            'academic_year': year_2021_2022,
            'semester': '1',
            'institution': 'ULCO',
            'order': 3,
            'technologies_used': 'HTML, CSS'
        }
    ]

    semester_2_courses = [
        {
            'title': 'Algorithms 2 (C++)',
            'credits': '3 ECTS',
            'description': 'C++ fundamentals: variables, functions, pointers, control structures',
            'academic_year': year_2021_2022,
            'semester': '2',
            'institution': 'ULCO',
            'order': 0,
            'technologies_used': 'C++'
        },
        {
            'title': 'Algorithms 3 (Advanced C++)',
            'credits': '3 ECTS',
            'description': 'Advanced topics: recursion, data structures, linked lists, final project',
            'academic_year': year_2021_2022,
            'semester': '2',
            'institution': 'ULCO',
            'order': 1,
            'technologies_used': 'C++',
            'is_featured': True  # Mark as featured since it's advanced
        },
        {
            'title': 'Database 1',
            'credits': '3 ECTS',
            'description': 'Database design: UML, conceptual models, normalization',
            'academic_year': year_2021_2022,
            'semester': '2',
            'institution': 'ULCO',
            'order': 2,
            'co_teachers': 'A. Ahmad',
            'topics_covered': 'UML, conceptual models, normalization'
        },
        {
            'title': 'Digital Tools',
            'credits': '3 ECTS',
            'description': 'Essential digital skills: Word, PowerPoint, Excel for certification preparation',
            'academic_year': year_2021_2022,
            'semester': '2',
            'institution': 'ULCO',
            'order': 3,
            'technologies_used': 'Microsoft Office, Word, PowerPoint, Excel'
        }
    ]

    # 2020-2021 courses
    year_2020_courses = [
        {
            'title': 'Machine Learning',
            'description': 'Supervised & unsupervised learning, reinforcement learning with Python (scikit-learn) & C++',
            'academic_year': year_2020_2021,
            'semester': 'full',
            'institution': 'ULCO',
            'order': 0,
            'technologies_used': 'Python, scikit-learn, C++',
            'topics_covered': 'Supervised learning, unsupervised learning, reinforcement learning',
            'is_featured': True  # Mark as featured since it's a specialized course
        }
    ]

    # Other courses (without specific academic year)
    other_courses = [
        {
            'title': 'Multidimensional Data Analysis',
            'academic_year': year_2021_2022,  # Assign to recent year
            'semester': 'other',
            'institution': 'EIL',
            'order': 0
        },
        {
            'title': 'Big Data & Sensor Calibration',
            'academic_year': year_2021_2022,
            'semester': 'other',
            'institution': 'EIL',
            'order': 1
        },
        {
            'title': 'Data Analysis in Excel',
            'academic_year': year_2021_2022,
            'semester': 'other',
            'institution': 'IUT',
            'order': 2,
            'technologies_used': 'Excel'
        },
        {
            'title': 'Semester Projects',
            'description': 'Student project supervision and guidance',
            'academic_year': year_2021_2022,
            'semester': 'other',
            'institution': 'EIL',
            'order': 3,
            'custom_institution': 'EIL, IUT'  # Multiple institutions
        }
    ]

    # Combine all courses
    all_courses = semester_1_courses + semester_2_courses + year_2020_courses + other_courses

    course_count = 0
    for course_data in all_courses:
        course, created = Course.objects.get_or_create(
            title=course_data['title'],
            academic_year=course_data['academic_year'],
            semester=course_data['semester'],
            defaults=course_data
        )
        if created:
            course_count += 1
            print(f"✅ Created course: {course.title}")
        else:
            print(f"📄 Course already exists: {course.title}")

    print(f"📚 Added {course_count} new courses")

    # 4. Create Teaching Statistics
    stats_data = [
        {
            'stat_type': 'total_courses',
            'value': '15+',
            'description': 'Courses taught across different institutions',
            'order': 0
        },
        {
            'stat_type': 'total_students',
            'value': '300+',
            'description': 'Students taught and mentored',
            'order': 1
        },
        {
            'stat_type': 'total_hours',
            'value': '500+',
            'description': 'Hours of teaching experience',
            'order': 2
        },
        {
            'stat_type': 'years_experience',
            'value': '3+',
            'description': 'Years of teaching experience',
            'order': 3
        }
    ]

    stat_count = 0
    for stat_data in stats_data:
        stat, created = TeachingStatistic.objects.get_or_create(
            stat_type=stat_data['stat_type'],
            defaults=stat_data
        )
        if created:
            stat_count += 1
            print(f"📊 Created statistic: {stat.get_stat_type_display()}")

    if stat_count > 0:
        print(f"📊 Added {stat_count} teaching statistics")

    print("\n🎉 Your original teaching content has been imported successfully!")
    print("\n📋 Summary:")
    print(f"   • 2021-2022: {len(semester_1_courses + semester_2_courses)} courses")
    print(f"   • 2020-2021: {len(year_2020_courses)} courses")
    print(f"   • Other courses: {len(other_courses)} courses")
    print(f"   • Total: {len(all_courses)} courses")
    print(f"   • Featured courses: {sum(1 for c in all_courses if c.get('is_featured', False))}")

    print("\n🌐 Next steps:")
    print("1. Visit http://localhost:8000/teaching/ to see your modern teaching page")
    print("2. Visit http://localhost:8000/admin/ to edit courses, add student counts, hours, etc.")
    print("3. You can now filter by year, semester, and institution!")
    print("4. Featured courses (Machine Learning & Advanced C++) are highlighted with stars ⭐")


if __name__ == "__main__":
    populate_original_teaching_data()