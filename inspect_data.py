#!/usr/bin/env python3
"""
Inspect the Page_Views data to understand what page IDs exist
"""

import pandas as pd

def inspect_page_views():
    """Load and inspect the Page_Views data"""
    print("="*80)
    print("INSPECTING PAGE_VIEWS.XLSX")
    print("="*80)

    # Load the data
    df = pd.read_excel('/home/user/VACRAFT/Page_Views.xlsx')

    print("\n1. Dataset Shape:")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")

    print("\n2. Column Names:")
    for col in df.columns:
        print(f"   - {col}")

    print("\n3. First few rows:")
    print(df.head(10))

    print("\n4. Data types:")
    print(df.dtypes)

    print("\n5. Page column analysis:")
    if 'Page' in df.columns:
        # Get unique page IDs
        unique_pages = df['Page'].unique()
        print(f"   Total unique pages: {len(unique_pages)}")

        # Sort and display
        print("\n   Unique Page IDs (sorted):")
        try:
            # Try to convert to numeric for sorting
            numeric_pages = []
            non_numeric_pages = []

            for page in unique_pages:
                try:
                    numeric_pages.append(int(page))
                except:
                    non_numeric_pages.append(str(page))

            numeric_pages.sort()
            non_numeric_pages.sort()

            print(f"\n   Numeric Page IDs ({len(numeric_pages)} total):")
            print(f"   Range: {min(numeric_pages) if numeric_pages else 'N/A'} to {max(numeric_pages) if numeric_pages else 'N/A'}")
            print(f"   First 20: {numeric_pages[:20]}")
            print(f"   Last 20: {numeric_pages[-20:]}")

            if non_numeric_pages:
                print(f"\n   Non-numeric Page IDs ({len(non_numeric_pages)} total):")
                for page in non_numeric_pages[:50]:
                    print(f"     - {page}")

        except Exception as e:
            print(f"   Could not analyze page IDs: {e}")
            print(f"   All unique values: {sorted(unique_pages)[:50]}")

    print("\n6. Sample of data (first 20 rows):")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df.head(20).to_string())

    return df

if __name__ == "__main__":
    df = inspect_page_views()
