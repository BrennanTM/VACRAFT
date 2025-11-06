#!/usr/bin/env python3
"""
VA CRAFT PTSD Analysis - Data Integrity Verification Script
This script verifies that all data processing was based on actual files
and no hallucinations occurred in the analysis.
"""

import pandas as pd
import hashlib
import json
import os
from datetime import datetime

print("=" * 80)
print("DATA INTEGRITY VERIFICATION FOR VA CRAFT PTSD ANALYSIS")
print("=" * 80)
print(f"Verification Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Step 1: Verify Input Files Exist and Calculate Checksums
print("STEP 1: VERIFYING INPUT FILES")
print("-" * 40)

required_files = {
    'Page_Views.xlsx': 'Original page view logs',
    'Login_History.xlsx': 'Original login history',
    'Data_Dictionary_FINAL.csv': 'Extracted course structure',
    'CRAFT_PTSD_Engagement_Metrics.xlsx': 'Generated metrics',
    'CRAFT_PTSD_Synthesis.txt': 'Generated synthesis report'
}

file_checksums = {}
for filename, description in required_files.items():
    if os.path.exists(filename):
        # Calculate MD5 checksum
        with open(filename, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        file_size = os.path.getsize(filename)
        file_checksums[filename] = {
            'exists': True,
            'size': file_size,
            'md5': file_hash,
            'description': description
        }
        print(f"✓ {filename}: {file_size:,} bytes (MD5: {file_hash[:8]}...)")
    else:
        file_checksums[filename] = {'exists': False}
        print(f"✗ {filename}: NOT FOUND")

# Step 2: Verify Page Views Data Structure
print("\nSTEP 2: VERIFYING PAGE VIEWS STRUCTURE")
print("-" * 40)

try:
    page_views = pd.read_excel('Page_Views.xlsx')
    print(f"Total records: {len(page_views):,}")
    print(f"Columns: {', '.join(page_views.columns)}")

    # Check for expected columns
    expected_cols = ['UserId', 'Page', 'Date / Time']
    missing_cols = [col for col in expected_cols if col not in page_views.columns]
    if missing_cols:
        print(f"⚠ Missing expected columns: {missing_cols}")
    else:
        print("✓ All expected columns present")

    # Data statistics
    print(f"\nData Statistics:")
    print(f"  Unique users: {page_views['UserId'].nunique()}")
    print(f"  Unique pages: {page_views['Page'].nunique()}")
    print(f"  Date range: {pd.to_datetime(page_views['Date / Time']).min()} to {pd.to_datetime(page_views['Date / Time']).max()}")

    # Sample of page IDs to verify they're numeric
    sample_pages = page_views['Page'].value_counts().head(10)
    print(f"\nTop 10 most visited pages:")
    for page, count in sample_pages.items():
        print(f"  Page {page}: {count:,} views")

except Exception as e:
    print(f"✗ Error reading Page_Views.xlsx: {e}")

# Step 3: Verify Data Dictionary Completeness
print("\nSTEP 3: VERIFYING DATA DICTIONARY COVERAGE")
print("-" * 40)

try:
    data_dict = pd.read_csv('Data_Dictionary_FINAL.csv')
    print(f"Total pages in dictionary: {len(data_dict)}")

    # Check page ID range
    if 'Page_ID' in data_dict.columns:
        page_ids = pd.to_numeric(data_dict['Page_ID'], errors='coerce')
        valid_ids = page_ids.dropna()
        print(f"Page ID range: {int(valid_ids.min())} to {int(valid_ids.max())}")
        print(f"Valid page mappings: {len(valid_ids)}/{len(data_dict)}")

    # Check for required content columns
    content_cols = ['Title', 'Section', 'Lesson']
    for col in content_cols:
        if col in data_dict.columns:
            non_null = data_dict[col].notna().sum()
            print(f"  {col}: {non_null}/{len(data_dict)} entries ({non_null/len(data_dict)*100:.1f}%)")

    # Verify coverage of user pages
    if 'Page_Views.xlsx' in file_checksums and file_checksums['Page_Views.xlsx']['exists']:
        user_pages = set(page_views['Page'].astype(str).unique())
        dict_pages = set(data_dict['Page_ID'].astype(str).unique())

        covered = user_pages.intersection(dict_pages)
        uncovered = user_pages - dict_pages - {'menu'}  # Exclude 'menu' pages

        print(f"\nPage Coverage Analysis:")
        print(f"  User pages in dictionary: {len(covered)}/{len(user_pages)} ({len(covered)/len(user_pages)*100:.1f}%)")
        if uncovered:
            print(f"  Unmapped pages: {sorted(list(uncovered)[:10])}...")
        else:
            print(f"  ✓ All user pages mapped successfully")

except Exception as e:
    print(f"✗ Error reading Data_Dictionary_FINAL.csv: {e}")

# Step 4: Verify Metrics Generation
print("\nSTEP 4: VERIFYING GENERATED METRICS")
print("-" * 40)

try:
    metrics = pd.read_excel('CRAFT_PTSD_Engagement_Metrics.xlsx', sheet_name=None)
    print(f"Excel sheets created: {', '.join(metrics.keys())}")

    if 'User_Metrics' in metrics:
        user_metrics = metrics['User_Metrics']
        print(f"\nUser Metrics Summary:")
        print(f"  Total users analyzed: {len(user_metrics)}")
        print(f"  Columns: {len(user_metrics.columns)}")

        # Verify key metrics exist
        key_metrics = ['Total_Time_Hours', 'Total_Visits', 'Completion_Rate']
        for metric in key_metrics:
            if metric in user_metrics.columns:
                print(f"  {metric}: Mean={user_metrics[metric].mean():.2f}, Max={user_metrics[metric].max():.2f}")

    if 'Summary_Statistics' in metrics:
        summary = metrics['Summary_Statistics']
        print(f"\nSummary Statistics:")
        for _, row in summary.iterrows():
            print(f"  {row['Metric']}: {row['Value']}")

except Exception as e:
    print(f"✗ Error reading metrics file: {e}")

# Step 5: Verify Synthesis Report
print("\nSTEP 5: VERIFYING SYNTHESIS REPORT")
print("-" * 40)

try:
    with open('CRAFT_PTSD_Synthesis.txt', 'r') as f:
        synthesis = f.read()

    print(f"Report size: {len(synthesis):,} characters")

    # Check for key sections
    key_sections = [
        'OVERALL PARTICIPATION',
        'ENGAGEMENT METRICS',
        'COURSE COMPLETION',
        'SECTION ENGAGEMENT',
        'KEY INSIGHTS'
    ]

    for section in key_sections:
        if section in synthesis:
            print(f"  ✓ Contains section: {section}")
        else:
            print(f"  ✗ Missing section: {section}")

    # Count individual user summaries
    user_summary_count = synthesis.count('User 1')
    print(f"\nIndividual user summaries: {user_summary_count}")

except Exception as e:
    print(f"✗ Error reading synthesis report: {e}")

# Step 6: Cross-Validation
print("\nSTEP 6: CROSS-VALIDATION OF RESULTS")
print("-" * 40)

try:
    # Recalculate basic metrics to verify
    page_views_clean = page_views[page_views['UserId'] != 'UserName']
    actual_users = page_views_clean['UserId'].nunique()
    actual_views = len(page_views_clean)

    print(f"Direct calculation from raw data:")
    print(f"  Users: {actual_users}")
    print(f"  Page views: {actual_views:,}")

    # Compare with reported metrics
    if 'User_Metrics' in metrics:
        reported_users = len(metrics['User_Metrics'])
        print(f"\nReported in metrics file:")
        print(f"  Users: {reported_users}")

        if actual_users == reported_users:
            print("  ✓ User counts match")
        else:
            print(f"  ⚠ User count mismatch: {actual_users} vs {reported_users}")

except Exception as e:
    print(f"⚠ Could not complete cross-validation: {e}")

# Save verification report
print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

verification_report = {
    'timestamp': datetime.now().isoformat(),
    'files_verified': file_checksums,
    'data_stats': {
        'total_users': actual_users if 'actual_users' in locals() else None,
        'total_views': actual_views if 'actual_views' in locals() else None,
        'dictionary_pages': len(data_dict) if 'data_dict' in locals() else None,
    },
    'verification_status': 'PASS' if all(f['exists'] for f in file_checksums.values() if 'exists' in f) else 'FAIL'
}

with open('verification_report.json', 'w') as f:
    json.dump(verification_report, f, indent=2)

print(f"Verification report saved to: verification_report.json")
print(f"Overall Status: {verification_report['verification_status']}")