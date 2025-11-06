"""
VA CRAFT PTSD Engagement Data Processing and Analysis
Phases 2-4: Complete data processing, sessionization, metrics calculation, and reporting
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("VA CRAFT PTSD USER ENGAGEMENT ANALYSIS")
print("=" * 80)
print(f"Analysis Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# =====================================================================
# PHASE 2A: LOAD AND CLEAN DATA
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 2A: LOADING AND CLEANING DATA")
print("=" * 80)

# Load page views
print("\nLoading Page_Views.xlsx...")
page_views = pd.read_excel('Page_Views.xlsx')
print(f"  Raw records: {len(page_views):,}")

# Remove placeholder rows
page_views = page_views[page_views['UserId'] != 'UserName']
page_views = page_views[~page_views['Date / Time'].astype(str).str.startswith('0000')]
print(f"  After cleaning: {len(page_views):,} records")

# Convert datetime
page_views['DateTime'] = pd.to_datetime(page_views['Date / Time'])
page_views = page_views.sort_values(['UserId', 'DateTime'])

# Load login history (optional - for reference)
print("\nLoading Login_History.xlsx...")
login_history = pd.read_excel('Login_History.xlsx')
print(f"  Login records: {len(login_history):,}")

# Load data dictionary
print("\nLoading Data Dictionary...")
data_dict = pd.read_csv('Data_Dictionary_FINAL.csv')
print(f"  Pages in dictionary: {len(data_dict)}")

# Basic statistics
print(f"\nUser Activity Overview:")
print(f"  Unique users: {page_views['UserId'].nunique()}")
print(f"  Date range: {page_views['DateTime'].min().date()} to {page_views['DateTime'].max().date()}")
print(f"  Total page views: {len(page_views):,}")

# =====================================================================
# PHASE 2B: SESSIONIZATION AND DWELL TIME CALCULATION
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 2B: SESSIONIZATION AND DWELL TIME CALCULATION")
print("=" * 80)

# Define session timeout (30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

print(f"\nSession timeout: {SESSION_TIMEOUT.total_seconds()/60:.0f} minutes")

# Sort data for sessionization
df = page_views.copy()
df = df.sort_values(['UserId', 'DateTime'])

# Calculate time difference to previous event
df['TimeDiff'] = df.groupby('UserId')['DateTime'].diff()

# Identify new sessions
df['NewSession'] = (
    (df['TimeDiff'] > SESSION_TIMEOUT) |  # Timeout exceeded
    (df['UserId'] != df['UserId'].shift())  # New user
)

# Assign session IDs
df['SessionId'] = df['NewSession'].cumsum()

# Calculate dwell time (time until next event)
df['NextDateTime'] = df.groupby('UserId')['DateTime'].shift(-1)
df['DwellTime'] = df['NextDateTime'] - df['DateTime']

# Cap dwell time at session timeout for last page of session
df['IsLastInSession'] = df.groupby('SessionId')['DateTime'].transform('max') == df['DateTime']
df.loc[df['IsLastInSession'], 'DwellTime'] = pd.Timedelta(seconds=0)

# For non-last pages, cap at timeout
df.loc[df['DwellTime'] > SESSION_TIMEOUT, 'DwellTime'] = SESSION_TIMEOUT

# Convert to seconds
df['DwellTimeSeconds'] = df['DwellTime'].dt.total_seconds()

print(f"\nSessionization complete:")
print(f"  Total sessions: {df['SessionId'].nunique():,}")
print(f"  Avg pages per session: {len(df) / df['SessionId'].nunique():.1f}")
print(f"  Avg session duration: {df.groupby('SessionId')['DwellTimeSeconds'].sum().mean()/60:.1f} minutes")

# =====================================================================
# PHASE 2C: MERGE WITH DATA DICTIONARY
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 2C: MERGING WITH DATA DICTIONARY")
print("=" * 80)

# Merge page views with dictionary
df['Page'] = df['Page'].astype(str)
data_dict['Page_ID'] = data_dict['Page_ID'].astype(str)

df_enriched = df.merge(
    data_dict,
    left_on='Page',
    right_on='Page_ID',
    how='left'
)

print(f"\nMerge results:")
print(f"  Records with content info: {df_enriched['Title'].notna().sum():,} ({df_enriched['Title'].notna().sum()/len(df_enriched)*100:.1f}%)")
print(f"  Records without content info: {df_enriched['Title'].isna().sum():,}")

# =====================================================================
# PHASE 3A: CALCULATE ENGAGEMENT METRICS
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 3A: CALCULATING ENGAGEMENT METRICS")
print("=" * 80)

# Calculate metrics per user
user_metrics = []

for user_id in df_enriched['UserId'].unique():
    user_data = df_enriched[df_enriched['UserId'] == user_id]

    # Basic metrics
    total_visits = user_data['SessionId'].nunique()
    total_pages = len(user_data)
    total_time_seconds = user_data['DwellTimeSeconds'].sum()
    total_time_minutes = total_time_seconds / 60

    # Date range
    first_activity = user_data['DateTime'].min()
    last_activity = user_data['DateTime'].max()
    days_active = (last_activity - first_activity).days + 1

    # Content engagement
    sections_visited = user_data['Section'].dropna().unique()
    lessons_visited = user_data['Lesson'].dropna().unique()

    # Calculate completion - based on seeing lesson summary pages
    summary_pages = user_data[user_data['Is_Last_Page'] == True]['Lesson'].dropna().unique()
    lessons_completed = len(summary_pages)

    # Furthest progression
    furthest_page = user_data['Page'].astype(float).max()
    furthest_content = user_data[user_data['Page'].astype(float) == furthest_page]['Title'].iloc[0] if not user_data[user_data['Page'].astype(float) == furthest_page].empty else 'Unknown'

    # Time by section
    section_time = user_data.groupby('Section')['DwellTimeSeconds'].sum() / 60  # in minutes

    user_metrics.append({
        'Invite_Code': user_id,  # Using UserId as Invite_Code
        'Total_Visits': total_visits,
        'Total_Pages_Viewed': total_pages,
        'Total_Time_Minutes': round(total_time_minutes, 1),
        'Total_Time_Hours': round(total_time_minutes / 60, 2),
        'First_Activity': first_activity.strftime('%Y-%m-%d %H:%M'),
        'Last_Activity': last_activity.strftime('%Y-%m-%d %H:%M'),
        'Days_Active': days_active,
        'Sections_Visited': len(sections_visited),
        'Lessons_Started': len(lessons_visited),
        'Lessons_Completed': lessons_completed,
        'Completion_Rate': round(lessons_completed / 12 * 100, 1),  # 12 total lessons
        'Furthest_Page': int(furthest_page) if not pd.isna(furthest_page) else 0,
        'Furthest_Content': furthest_content[:50] if furthest_content else 'Unknown',
        'Avg_Pages_Per_Visit': round(total_pages / total_visits, 1),
        'Avg_Minutes_Per_Visit': round(total_time_minutes / total_visits, 1)
    })

# Convert to DataFrame
metrics_df = pd.DataFrame(user_metrics)
metrics_df = metrics_df.sort_values('Total_Time_Minutes', ascending=False)

print(f"\nMetrics calculated for {len(metrics_df)} users")
print(f"\nEngagement Overview:")
print(f"  Average time spent: {metrics_df['Total_Time_Hours'].mean():.1f} hours")
print(f"  Average visits: {metrics_df['Total_Visits'].mean():.1f}")
print(f"  Average pages viewed: {metrics_df['Total_Pages_Viewed'].mean():.1f}")
print(f"  Average completion rate: {metrics_df['Completion_Rate'].mean():.1f}%")

# =====================================================================
# PHASE 3B: EXPORT METRICS TO EXCEL
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 3B: EXPORTING METRICS")
print("=" * 80)

# Create Excel writer
with pd.ExcelWriter('CRAFT_PTSD_Engagement_Metrics.xlsx', engine='xlsxwriter') as writer:
    # Sheet 1: User Metrics
    metrics_df.to_excel(writer, sheet_name='User_Metrics', index=False)

    # Sheet 2: Summary Statistics
    summary_stats = pd.DataFrame({
        'Metric': [
            'Total Users',
            'Total Page Views',
            'Total Sessions',
            'Average Time per User (hours)',
            'Average Visits per User',
            'Average Pages per User',
            'Average Completion Rate (%)',
            'Users Who Completed All Lessons',
            'Users Who Started But Didn\'t Complete'
        ],
        'Value': [
            len(metrics_df),
            len(df_enriched),
            df_enriched['SessionId'].nunique(),
            round(metrics_df['Total_Time_Hours'].mean(), 2),
            round(metrics_df['Total_Visits'].mean(), 1),
            round(metrics_df['Total_Pages_Viewed'].mean(), 1),
            round(metrics_df['Completion_Rate'].mean(), 1),
            len(metrics_df[metrics_df['Completion_Rate'] == 100]),
            len(metrics_df[(metrics_df['Lessons_Started'] > 0) & (metrics_df['Completion_Rate'] < 100)])
        ]
    })
    summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)

    # Sheet 3: Section Engagement
    section_stats = df_enriched.groupby('Section').agg({
        'UserId': 'nunique',
        'DwellTimeSeconds': 'sum',
        'Page': 'count'
    }).reset_index()
    section_stats.columns = ['Section', 'Unique_Users', 'Total_Time_Seconds', 'Total_Views']
    section_stats['Total_Time_Hours'] = round(section_stats['Total_Time_Seconds'] / 3600, 2)
    section_stats.to_excel(writer, sheet_name='Section_Engagement', index=False)

print("✓ Metrics exported to: CRAFT_PTSD_Engagement_Metrics.xlsx")

# =====================================================================
# PHASE 4A: GENERATE INDIVIDUAL SUMMARIES
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 4A: GENERATING INDIVIDUAL USER SUMMARIES")
print("=" * 80)

individual_summaries = []

for _, user in metrics_df.head(50).iterrows():  # Top 50 users by engagement
    summary = f"""User {user['Invite_Code']} (Invite Code {user['Invite_Code']}):
  • Engaged in {user['Total_Visits']} sessions totaling {user['Total_Time_Hours']} hours
  • Activity span: {user['First_Activity']} to {user['Last_Activity']} ({user['Days_Active']} days)
  • Viewed {user['Total_Pages_Viewed']} pages across {user['Sections_Visited']}/6 sections
  • Completed {user['Lessons_Completed']}/12 lessons ({user['Completion_Rate']}% completion)
  • Furthest progression: {user['Furthest_Content']}"""

    individual_summaries.append(summary)

# =====================================================================
# PHASE 4B: GENERATE AGGREGATE SUMMARY
# =====================================================================
print("\n" + "=" * 80)
print("PHASE 4B: GENERATING AGGREGATE SUMMARY")
print("=" * 80)

# Calculate additional aggregate statistics
high_engagement_users = metrics_df[metrics_df['Total_Time_Hours'] > metrics_df['Total_Time_Hours'].median()]
completers = metrics_df[metrics_df['Completion_Rate'] == 100]
dropoffs = metrics_df[(metrics_df['Lessons_Started'] > 0) & (metrics_df['Lessons_Completed'] == 0)]

# Identify common dropout points
last_pages = df_enriched.groupby('UserId')['Page'].last()
dropout_sections = df_enriched[df_enriched['Page'].isin(last_pages)]['Section'].value_counts()

aggregate_summary = f"""
VA CRAFT PTSD INTERVENTION - ENGAGEMENT ANALYSIS SUMMARY
{'=' * 70}

OVERALL PARTICIPATION
{'-' * 30}
• Total participants: {len(metrics_df)} users
• Total engagement: {df_enriched['SessionId'].nunique():,} sessions
• Total page views: {len(df_enriched):,} pages
• Date range: {df_enriched['DateTime'].min().date()} to {df_enriched['DateTime'].max().date()}

ENGAGEMENT METRICS
{'-' * 30}
• Average time per user: {metrics_df['Total_Time_Hours'].mean():.1f} hours
• Median time per user: {metrics_df['Total_Time_Hours'].median():.1f} hours
• Average visits per user: {metrics_df['Total_Visits'].mean():.1f} sessions
• Average pages per visit: {metrics_df['Avg_Pages_Per_Visit'].mean():.1f} pages

COURSE COMPLETION
{'-' * 30}
• Full course completion rate: {len(completers)/len(metrics_df)*100:.1f}% ({len(completers)} users)
• Partial completion (started lessons): {len(metrics_df[metrics_df['Lessons_Started'] > 0])/len(metrics_df)*100:.1f}%
• Average lessons completed: {metrics_df['Lessons_Completed'].mean():.1f}/12
• Never started lessons: {len(metrics_df[metrics_df['Lessons_Started'] == 0])} users

SECTION ENGAGEMENT
{'-' * 30}
Most engaged sections:
{df_enriched.groupby('Section')['UserId'].nunique().sort_values(ascending=False).head().to_string()}

DROPOUT ANALYSIS
{'-' * 30}
Common last sections before dropout:
{dropout_sections.head().to_string()}

HIGH ENGAGEMENT GROUP ({len(high_engagement_users)} users, >{metrics_df['Total_Time_Hours'].median():.1f} hours)
{'-' * 30}
• Average time: {high_engagement_users['Total_Time_Hours'].mean():.1f} hours
• Average completion: {high_engagement_users['Completion_Rate'].mean():.1f}%
• Average visits: {high_engagement_users['Total_Visits'].mean():.1f}

KEY INSIGHTS
{'-' * 30}
1. The intervention shows moderate engagement with users spending an average of {metrics_df['Total_Time_Hours'].mean():.1f} hours.

2. Completion rates are {metrics_df['Completion_Rate'].mean():.1f}%, suggesting opportunities to improve retention.

3. Section {dropout_sections.index[0] if len(dropout_sections) > 0 else 'Unknown'} shows the highest dropout rate, indicating a potential barrier.

4. Highly engaged users (>{metrics_df['Total_Time_Hours'].median():.1f} hours) show {high_engagement_users['Completion_Rate'].mean():.1f}% completion,
   suggesting that sustained engagement correlates with completion.

5. The most visited content relates to {df_enriched['Section'].mode()[0] if not df_enriched['Section'].mode().empty else 'core topics'},
   indicating high interest in these areas.

RECOMMENDATIONS
{'-' * 30}
1. Focus retention efforts on early sections where dropout is highest
2. Investigate barriers in sections with low completion
3. Consider adding engagement prompts or reminders after periods of inactivity
4. Highlight success stories from users who completed the program
5. Optimize content length in sections with highest time investment

{'=' * 70}
Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

# Save synthesis report
with open('CRAFT_PTSD_Synthesis.txt', 'w') as f:
    f.write(aggregate_summary)
    f.write("\n\n")
    f.write("=" * 70)
    f.write("\nINDIVIDUAL USER SUMMARIES (Top 50 by Engagement)\n")
    f.write("=" * 70)
    f.write("\n\n")
    for summary in individual_summaries:
        f.write(summary)
        f.write("\n\n")

print("✓ Synthesis report saved to: CRAFT_PTSD_Synthesis.txt")

# =====================================================================
# FINAL SUMMARY
# =====================================================================
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print("\nGenerated Files:")
print("  1. CRAFT_PTSD_Engagement_Metrics.xlsx - Detailed user metrics")
print("  2. CRAFT_PTSD_Synthesis.txt - Written summaries and insights")
print("  3. Data_Dictionary_FINAL.csv - Complete page mappings")
print("\nKey Findings:")
print(f"  • {len(metrics_df)} users analyzed")
print(f"  • {metrics_df['Total_Time_Hours'].sum():.1f} total hours of engagement")
print(f"  • {metrics_df['Completion_Rate'].mean():.1f}% average completion rate")
print(f"  • {len(completers)} users completed all 12 lessons")
print(f"\nAnalysis End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")