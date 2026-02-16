import pandas as pd
import json
from collections import Counter
import os

# Load the diagnosis data
print("Loading diagnosis data...")
try:
    df = pd.read_excel(diagnosis_cs.xlsx')
except FileNotFoundError:
    print("Error: '../diagnosis_cs.xlsx' not found.")
    exit(1)

print(f"Total records: {len(df)}")
cols = df.columns.tolist()
print(f"Columns: {cols}")

# Calculate key metrics
total_diagnoses = int(df['count'].sum())
unique_facilities = int(df['facility_code'].nunique())
unique_diagnoses = int(df['diagnosis_name'].nunique())
avg_per_facility = round(total_diagnoses / unique_facilities, 2) if unique_facilities > 0 else 0

# Get top diagnoses
top_diagnoses = df.groupby('diagnosis_name')['count'].sum().sort_values(ascending=False).head(15)

# Get top facilities
top_facilities = df.groupby('facility_name')['count'].sum().sort_values(ascending=False).head(10)

# Get diagnosis type breakdown
if 'type' in df.columns:
    type_breakdown = df.groupby('type')['count'].sum().to_dict()
else:
    type_breakdown = {}

# Get Category breakdown
if 'Category' in df.columns:
    category_breakdown = df.groupby('Category')['count'].sum().sort_values(ascending=False).head(10)
else:
    category_breakdown = pd.Series(dtype='int64')

# Get Sub_category breakdown (top 15)
if 'Sub_category' in df.columns:
    subcategory_breakdown = df.groupby('Sub_category')['count'].sum().sort_values(ascending=False).head(15)
else:
    subcategory_breakdown = pd.Series(dtype='int64')

# Get facility distribution by state/region (if available)
facility_stats = df.groupby('facility_name').agg({
    'count': 'sum',
    'diagnosis_name': 'nunique'
}).reset_index()
facility_stats.columns = ['facility_name', 'total_count', 'unique_diagnoses']
facility_stats = facility_stats.sort_values('total_count', ascending=False).head(20)

# Pre-calculate data for each category
category_data = {}
if 'Category' in df.columns:
    unique_categories = df['Category'].dropna().unique()
    print(f"Processing {len(unique_categories)} categories...")
    
    for category in unique_categories:
        cat_df = df[df['Category'] == category]
        
        # Metrics
        cat_total = int(cat_df['count'].sum())
        cat_facilities = int(cat_df['facility_code'].nunique())
        cat_diagnoses = int(cat_df['diagnosis_name'].nunique())
        cat_avg = round(cat_total / cat_facilities, 2) if cat_facilities > 0 else 0
        
        # Top 10 Diagnoses
        cat_top_diag = cat_df.groupby('diagnosis_name')['count'].sum().sort_values(ascending=False).head(10)
        
        # Top 10 Sub-categories
        if 'Sub_category' in cat_df.columns:
            cat_top_sub = cat_df.groupby('Sub_category')['count'].sum().sort_values(ascending=False).head(10)
        else:
            cat_top_sub = pd.Series(dtype='int64')
            
        # Top 10 Facilities
        cat_top_fac = cat_df.groupby('facility_name')['count'].sum().sort_values(ascending=False).head(10)
        
        # Type Breakdown
        if 'type' in cat_df.columns:
            cat_type = cat_df.groupby('type')['count'].sum().to_dict()
        else:
            cat_type = {}
            
        # Facility Stats for Table
        cat_facility_stats = cat_df.groupby('facility_name').agg({
            'count': 'sum',
            'diagnosis_name': 'nunique'
        }).reset_index()
        cat_facility_stats.columns = ['facility_name', 'total_count', 'unique_diagnoses']
        cat_facility_stats = cat_facility_stats.sort_values('total_count', ascending=False).head(10)
            
        category_data[category] = {
            'metrics': {
                'total_diagnoses': cat_total,
                'unique_facilities': cat_facilities,
                'unique_diagnosis_types': cat_diagnoses,
                'avg_per_facility': cat_avg
            },
            'top_diagnoses': {
                'labels': cat_top_diag.index.tolist(),
                'values': cat_top_diag.values.tolist()
            },
            'subcategory_breakdown': {
                'labels': cat_top_sub.index.tolist(),
                'values': cat_top_sub.values.tolist()
            },
            'top_facilities': {
                'labels': cat_top_fac.index.tolist(),
                'values': cat_top_fac.values.tolist()
            },
            'type_breakdown': cat_type,
            'facility_details': cat_facility_stats.to_dict('records')
        }

# Create comprehensive data structure
dashboard_data = {
    'metrics': {
        'total_diagnoses': total_diagnoses,
        'unique_facilities': unique_facilities,
        'unique_diagnosis_types': unique_diagnoses,
        'avg_per_facility': avg_per_facility
    },
    'top_diagnoses': {
        'labels': top_diagnoses.index.tolist(),
        'values': top_diagnoses.values.tolist()
    },
    'top_facilities': {
        'labels': top_facilities.index.tolist(),
        'values': top_facilities.values.tolist()
    },
    'type_breakdown': type_breakdown,
    'category_breakdown': {
        'labels': category_breakdown.index.tolist(),
        'values': category_breakdown.values.tolist()
    },
    'subcategory_breakdown': {
        'labels': subcategory_breakdown.index.tolist(),
        'values': subcategory_breakdown.values.tolist()
    },
    'facility_details': facility_stats.to_dict('records'),
    'category_data': category_data
}

# Save to JSON
output_file = 'data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, indent=2, ensure_ascii=False)

print(f"\nData processing complete!")
print(f"Output saved to: {output_file}")
print(f"\nKey Metrics:")
print(f"  Total Diagnoses: {total_diagnoses:,}")
print(f"  Unique Facilities: {unique_facilities:,}")
print(f"  Unique Diagnosis Types: {unique_diagnoses:,}")
print(f"  Average per Facility: {avg_per_facility:,.2f}")

