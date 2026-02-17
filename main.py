import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import os

# Set page configuration
st.set_page_config(
    page_title="Healthcare Diagnosis Analytics Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling (inspired by original design)
st.markdown("""
<style>
    /* Global Theme Overrides */
    .stApp {
        background-color: #0f111a;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e2130 0%, #161824 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="metric-container"] > label {
        color: #a0aec0 !important;
        font-size: 0.9rem !important;
    }
    div[data-testid="metric-container"] > div[data-testid="stMetricValue"] {
        color: #fff !important;
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    
    /* Category Badges Styling (if used via markdown) */
    .cat-header {
        background: linear-gradient(90deg, #1e2130 0%, rgba(30, 33, 48, 0) 100%);
        padding: 10px 20px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Helper for consistent chart styling
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#a0aec0'),
        coloraxis_showscale=False,  # Hide the color legend bar
        margin=dict(l=10, r=10, t=30, b=10),
    )
    fig.update_xaxes(showgrid=False, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
    return fig

# Load data
@st.cache_data
def load_data():
    try:
        # Check current directory first, then parent
        if os.path.exists('diagnosis_cs.xlsx'):
            file_path = 'diagnosis_cs.xlsx'
        elif os.path.exists('../diagnosis_cs.xlsx'):
            file_path = '../diagnosis_cs.xlsx'
        else:
            return None
        
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    # Header
    st.title("🏥 Healthcare Diagnosis Analytics")
    st.markdown("### Comprehensive EHR Insights Dashboard")
    st.markdown("---")

    with st.spinner('Loading data...'):
        df = load_data()

    if df is None:
        st.error("Could not find 'diagnosis_cs.xlsx'. Please ensure the file is in the correct directory.")
        return

    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Category Filter
    if 'Category' in df.columns:
        categories = ['All'] + sorted(df['Category'].dropna().unique().tolist())
        selected_category = st.sidebar.selectbox("Select Diagnosis Category", categories)
    else:
        selected_category = 'All'

    # Filter Data based on selection
    if selected_category != 'All':
        filtered_df = df[df['Category'] == selected_category]
        st.subheader(f"Analysis for: {selected_category}")
    else:
        filtered_df = df
        st.subheader("Global Overview")

    # --- Metrics Section ---
    total_diagnoses = int(filtered_df['count'].sum())
    unique_facilities = int(filtered_df['facility_code'].nunique())
    unique_diagnoses = int(filtered_df['diagnosis_name'].nunique())
    avg_per_facility = round(total_diagnoses / unique_facilities, 2) if unique_facilities > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Diagnoses", f"{total_diagnoses:,}", help="Total number of diagnosis cases")
    c2.metric("Healthcare Facilities", f"{unique_facilities:,}", help="Number of unique facilities")
    c3.metric("Unique Diagnoses", f"{unique_diagnoses:,}", help="Distinct diagnosis types")
    c4.metric("Avg per Facility", f"{avg_per_facility:,.2f}", help="Average cases per facility")

    st.markdown("---")

    # --- Charts Section ---
    
    # Row 1: Top Diagnoses and Top Facilities
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 15 Diagnoses")
        top_diagnoses = filtered_df.groupby('diagnosis_name')['count'].sum().sort_values(ascending=False).head(15).reset_index()
        fig_diag = px.bar(top_diagnoses, x='count', y='diagnosis_name', orientation='h', 
                          color='count', color_continuous_scale='Viridis',
                          labels={'count': 'Cases', 'diagnosis_name': 'Diagnosis'})
        fig_diag.update_layout(yaxis={'categoryorder':'total ascending'})
        fig_diag = style_chart(fig_diag)
        st.plotly_chart(fig_diag, use_container_width=True)

    with col2:
        st.subheader("Top 10 Healthcare Facilities")
        top_facilities = filtered_df.groupby('facility_name')['count'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_fac = px.bar(top_facilities, x='facility_name', y='count',
                         color='count', color_continuous_scale='Magma',
                         labels={'count': 'Total Cases', 'facility_name': 'Facility'})
        fig_fac.update_layout(xaxis_tickangle=-45)
        fig_fac = style_chart(fig_fac)
        st.plotly_chart(fig_fac, use_container_width=True)

    # Row 2: Type Breakdown and Categories (if viewing All)
    col3, col4 = st.columns(2)

    with col3:
        if 'type' in filtered_df.columns:
            st.subheader("Diagnosis Type Distribution")
            type_counts = filtered_df.groupby('type')['count'].sum().reset_index()
            fig_type = px.pie(type_counts, values='count', names='type', hole=0.4, 
                              color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_type.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_type, use_container_width=True)

    with col4:
        if selected_category == 'All' and 'Category' in filtered_df.columns:
            st.subheader("Top 10 Diagnosis Categories")
            cat_counts = filtered_df.groupby('Category')['count'].sum().sort_values(ascending=False).head(10).reset_index()
            fig_cat = px.bar(cat_counts, x='count', y='Category', orientation='h',
                             color='count', color_continuous_scale='Plasma')
            fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
            fig_cat = style_chart(fig_cat)
            st.plotly_chart(fig_cat, use_container_width=True)
        elif 'Sub_category' in filtered_df.columns:
             st.subheader("Top 15 Diagnosis Sub-categories")
             sub_counts = filtered_df.groupby('Sub_category')['count'].sum().sort_values(ascending=False).head(15).reset_index()
             fig_sub = px.bar(sub_counts, x='count', y='Sub_category', orientation='h',
                              color='count', color_continuous_scale='Plasma')
             fig_sub.update_layout(yaxis={'categoryorder':'total ascending'})
             fig_sub = style_chart(fig_sub)
             st.plotly_chart(fig_sub, use_container_width=True)

    # Row 3: Data Table
    st.markdown("---")
    st.subheader("Facility Performance Details")
    
    facility_stats = filtered_df.groupby('facility_name').agg({
        'count': 'sum',
        'diagnosis_name': 'nunique'
    }).reset_index()
    facility_stats.columns = ['Facility', 'Total Cases', 'Unique Diagnoses']
    facility_stats = facility_stats.sort_values('Total Cases', ascending=False)
    
    st.dataframe(facility_stats, use_container_width=True, hide_index=True)

    # --- Category Details Sections (Only when "All" is selected) ---
    if selected_category == 'All' and 'Category' in df.columns:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("## Detailed Category Analysis")
        st.markdown("---")
        
        # Get all unique categories
        categories_list = sorted(df['Category'].dropna().unique().tolist())
        
        for cat in categories_list:
            # Styled Header for Category
            st.markdown(f"""
            <div class="cat-header">
                <h3 style="margin:0; color:white;">{cat}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            cat_df = df[df['Category'] == cat]
            
            # Metrics for this category
            cat_total = int(cat_df['count'].sum())
            cat_facilities = int(cat_df['facility_code'].nunique())
            cat_diagnoses = int(cat_df['diagnosis_name'].nunique())
            
            m1, m2, m3 = st.columns(3)
            # Using standard metrics but they will be styled by the CSS above
            m1.metric("Cases", f"{cat_total:,}")
            m2.metric("Facilities", f"{cat_facilities:,}")
            m3.metric("Unique Diagnoses", f"{cat_diagnoses:,}")
            
            # Charts for this category
            d1, d2 = st.columns(2)
            
            with d1:
                st.markdown("**Top 5 Diagnoses**")
                cat_top_diag = cat_df.groupby('diagnosis_name')['count'].sum().sort_values(ascending=False).head(5).reset_index()
                fig_cat_diag = px.bar(cat_top_diag, x='count', y='diagnosis_name', orientation='h',
                                      color='count', color_continuous_scale='Viridis')
                fig_cat_diag.update_layout(yaxis={'categoryorder':'total ascending'}, 
                                           margin=dict(l=0, r=10, t=10, b=0), height=250)
                fig_cat_diag = style_chart(fig_cat_diag)
                st.plotly_chart(fig_cat_diag, use_container_width=True)
                
            with d2:
                st.markdown("**Top 5 Facilities**")
                cat_top_fac = cat_df.groupby('facility_name')['count'].sum().sort_values(ascending=False).head(5).reset_index()
                fig_cat_fac = px.bar(cat_top_fac, x='facility_name', y='count',
                                     color='count', color_continuous_scale='Magma')
                fig_cat_fac.update_layout(xaxis_tickangle=-45, 
                                          margin=dict(l=0, r=10, t=10, b=0), height=250)
                fig_cat_fac = style_chart(fig_cat_fac)
                st.plotly_chart(fig_cat_fac, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 20px;">
        <p>Healthcare Diagnosis Analytics Dashboard © 2026 | Data-driven insights for better healthcare outcomes</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
