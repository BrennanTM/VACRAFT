"""
Parse the config.js file to extract the complete course structure
"""

import re
import pandas as pd
import json

def parse_config_js():
    """Parse config.js to extract course structure"""

    with open('config.js', 'r') as f:
        content = f.read()

    # Extract all lesson.push lines
    lesson_pattern = r'lesson\.push\(\{\s*menuEntryData:\s*\[(.*?)\]\s*\}\);'
    matches = re.findall(lesson_pattern, content, re.DOTALL)

    lessons = []
    page_counter = 1  # Start from page 1

    print("=" * 80)
    print("PARSING CONFIG.JS - COMPLETE COURSE STRUCTURE")
    print("=" * 80)

    for i, match in enumerate(matches, 1):
        # Clean up the match
        match = match.strip()

        # Parse the components
        # Format: [ page_count, ["001","002",...], "assessment", "#", "Title", "lesson00/00_001.htm", group ]

        # Extract page count (first number)
        page_count_match = re.match(r'(\d+)', match)
        if page_count_match:
            page_count = int(page_count_match.group(1))
        else:
            page_count = 1

        # Extract page array
        page_array_match = re.search(r'\[(\"[^]]+\")\]', match)
        if page_array_match:
            page_array_str = page_array_match.group(1)
            page_numbers = re.findall(r'"(\d+)"', page_array_str)
        else:
            page_numbers = []

        # Extract title
        title_match = re.search(r'"([^"]*(?:Section|Lesson|Welcome)[^"]*)"', match)
        if title_match:
            title = title_match.group(1)
        else:
            # Try to get any quoted string that looks like a title
            all_strings = re.findall(r'"([^"]+)"', match)
            # Filter out URLs, "none", "#", and short strings
            title_candidates = [s for s in all_strings
                               if len(s) > 5
                               and not s.startswith('lesson')
                               and s not in ['none', '#']
                               and not s.endswith('.htm')]
            title = title_candidates[0] if title_candidates else f"Section {i}"

        # Extract lesson URL
        url_match = re.search(r'lesson\d+/\d+_\d+\.htm', match)
        if url_match:
            lesson_url = url_match.group(0)
            # Extract lesson number from URL
            lesson_num_match = re.search(r'lesson(\d+)', lesson_url)
            lesson_num = int(lesson_num_match.group(1)) if lesson_num_match else None
        else:
            lesson_url = None
            lesson_num = None

        # Extract lesson/section number from title
        section_match = re.search(r'Section\s+(\d+)', title)
        lesson_in_title = re.search(r'Lesson\s+(\d+)', title)

        if section_match:
            section_num = int(section_match.group(1))
        else:
            section_num = None

        print(f"\nEntry {i}:")
        print(f"  Title: {title}")
        print(f"  Page count: {page_count}")
        print(f"  Page numbers in array: {page_numbers}")
        print(f"  Lesson URL: {lesson_url}")
        print(f"  Section: {section_num}, Lesson: {lesson_in_title.group(1) if lesson_in_title else 'N/A'}")
        print(f"  Maps to pages: {page_counter} to {page_counter + page_count - 1}")

        # Create entries for each page in this section
        for j in range(page_count):
            page_id = page_counter + j

            # Determine if this is the last page of the section
            is_last_page = (j == page_count - 1)

            # Create more specific page titles based on position
            if j == 0:
                page_title = title  # First page gets the section title
            elif is_last_page and 'Lesson' in title:
                page_title = f"{title} - Summary"
            else:
                page_title = f"{title} - Page {j+1}"

            lessons.append({
                'Page_ID': page_id,
                'Title': page_title,
                'Section': f"Section {section_num}" if section_num else None,
                'Lesson': lesson_in_title.group(0) if lesson_in_title else None,
                'Lesson_Number': int(lesson_in_title.group(1)) if lesson_in_title else lesson_num,
                'Page_in_Lesson': j + 1,
                'Total_Pages_in_Lesson': page_count,
                'Is_First_Page': j == 0,
                'Is_Last_Page': is_last_page,
                'Lesson_URL': lesson_url if j == 0 else None,
                'Content_Type': determine_content_type(title, j, page_count)
            })

        page_counter += page_count

    # Add menu page
    lessons.append({
        'Page_ID': 'menu',
        'Title': 'Navigation Menu',
        'Section': None,
        'Lesson': None,
        'Lesson_Number': None,
        'Page_in_Lesson': None,
        'Total_Pages_in_Lesson': None,
        'Is_First_Page': False,
        'Is_Last_Page': False,
        'Lesson_URL': None,
        'Content_Type': 'Navigation'
    })

    return pd.DataFrame(lessons)

def determine_content_type(title, page_num, total_pages):
    """Determine content type based on title and position"""

    title_lower = title.lower()

    if page_num == 0:
        if 'welcome' in title_lower:
            return 'Welcome'
        elif 'introduction' in title_lower:
            return 'Introduction'
        elif 'section' in title_lower:
            return 'Section Introduction'
        else:
            return 'Lesson Start'
    elif page_num == total_pages - 1:
        return 'Lesson Summary'
    else:
        if 'safety' in title_lower:
            return 'Safety Content'
        elif 'ptsd' in title_lower:
            return 'PTSD Education'
        elif 'communication' in title_lower:
            return 'Communication Skills'
        elif 'treatment' in title_lower:
            return 'Treatment Information'
        elif 'problem solving' in title_lower:
            return 'Problem Solving'
        elif 'stress' in title_lower or 'sleep' in title_lower:
            return 'Stress Management'
        elif 'reward' in title_lower or 'positive' in title_lower:
            return 'Positive Reinforcement'
        else:
            return 'Educational Content'

if __name__ == "__main__":
    # Parse the config file
    df = parse_config_js()

    print("\n" + "=" * 80)
    print("PARSING COMPLETE - SUMMARY")
    print("=" * 80)

    print(f"\nTotal pages mapped: {len(df[df['Page_ID'] != 'menu'])}")
    print(f"Total sections: {df['Section'].nunique() - 1}")  # -1 for None
    print(f"Total lessons: {df['Lesson_Number'].nunique() - 1}")  # -1 for None

    print("\nSections found:")
    sections = df[df['Is_First_Page'] == True]['Section'].dropna().unique()
    for section in sorted(sections):
        section_df = df[df['Section'] == section]
        print(f"  {section}: {len(section_df)} pages")

    print("\nLessons found:")
    lessons = df[df['Is_First_Page'] == True][['Lesson_Number', 'Title']].dropna(subset=['Lesson_Number'])
    for _, lesson in lessons.iterrows():
        print(f"  Lesson {int(lesson['Lesson_Number'])}: {lesson['Title']}")

    print("\nContent type distribution:")
    print(df['Content_Type'].value_counts())

    # Save the complete mapping
    df.to_csv('course_structure_complete.csv', index=False)
    print(f"\nComplete course structure saved to: course_structure_complete.csv")

    # Verify coverage
    print("\n" + "=" * 80)
    print("COVERAGE VERIFICATION")
    print("=" * 80)

    # Check which pages from user data are covered
    user_pages = list(range(1, 192))  # Pages 1-191 from user data
    covered_pages = df[df['Page_ID'] != 'menu']['Page_ID'].tolist()

    missing_pages = [p for p in user_pages if p not in covered_pages]

    print(f"\nPages in user data: 1-191")
    print(f"Pages mapped from config.js: {min(covered_pages)}-{max(covered_pages)}")
    print(f"Coverage: {len(covered_pages)}/191 = {len(covered_pages)/191*100:.1f}%")

    if missing_pages:
        print(f"\nMissing pages: {missing_pages}")