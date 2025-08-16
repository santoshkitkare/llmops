import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import base64
from datetime import datetime
import os

# Import the retirement planning modules
from retirement_planner.calculations import generate_yearly_projections
from retirement_planner.io_handlers import parse_config
from retirement_planner.models import RetirementParams, Child

# Page configuration
st.set_page_config(
    page_title="Retirement Planner",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 1rem;}
    .section-header {font-size: 1.5rem; color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 0.3rem; margin-top: 1.5rem;}
    .stButton>button {background-color: #1f77b4; color: white; border-radius: 5px; padding: 0.5rem 1rem;}
    .stButton>button:hover {background-color: #0d5a8a;}
    .result-card {background-color: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
    .metric-value {font-size: 1.5rem; font-weight: bold; color: #1f77b4;}
    .metric-label {font-size: 0.9rem; color: #666;}
    </style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Retirement Planning Tool</h1>", unsafe_allow_html=True)

# Initialize session state for form data and results
if 'projections' not in st.session_state:
    st.session_state.projections = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

def get_table_download_link(df, filename, link_text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Input form with expandable sections
with st.form("retirement_form"):
    st.markdown("### Basic Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_age = st.number_input("Current Age", min_value=18, max_value=100, value=35, step=1)
        retirement_age = st.number_input("Planned Retirement Age", min_value=18, max_value=100, value=60, step=1)
        life_expectancy = st.number_input("Life Expectancy", min_value=60, max_value=120, value=85, step=1)
    
    with col2:
        current_corpus = st.number_input("Current Savings (₹)", min_value=0, value=1000000, step=100000)
        monthly_expenses = st.number_input("Current Monthly Expenses (₹)", min_value=0, value=50000, step=5000)
        inflation = st.number_input("Expected Inflation Rate (%)", min_value=0.0, max_value=20.0, value=6.0, step=0.1) / 100
    
    with col3:
        pre_ret_return = st.number_input("Pre-retirement Return (% p.a.)", min_value=0.0, max_value=30.0, value=10.0, step=0.1) / 100
        post_ret_return = st.number_input("Post-retirement Return (% p.a.)", min_value=0.0, max_value=30.0, value=8.0, step=0.1) / 100
    
    # Children section
    st.markdown("### Children's Information (Optional)")
    children = []
    
    if 'num_children' not in st.session_state:
        st.session_state.num_children = 1
    
    num_children = st.number_input("Number of Children", min_value=0, max_value=5, value=0, step=1, 
                                 key="num_children")
    
    for i in range(num_children):
        with st.expander(f"Child {i+1} Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                child_age = st.number_input(f"Child {i+1} Age", min_value=0, max_value=30, value=5, key=f"child_{i}_age")
                school_fee = st.number_input(f"Current Annual School Fee (₹)", min_value=0, value=50000, 
                                           step=10000, key=f"child_{i}_school_fee")
                school_fee_increase = st.number_input("Annual School Fee Increase (%)", min_value=0.0, 
                                                    max_value=50.0, value=10.0, step=0.5, 
                                                    key=f"child_{i}_fee_increase") / 100
            with col2:
                graduation_fee = st.number_input("Total Graduation Cost (₹)", min_value=0, value=500000, 
                                               step=10000, key=f"child_{i}_grad_fee")
                marriage_cost = st.number_input("Expected Marriage Cost (₹)", min_value=0, value=500000, 
                                              step=50000, key=f"child_{i}_marriage_cost")
                marriage_age = st.number_input("Expected Marriage Age", min_value=18, max_value=50, 
                                             value=25, key=f"child_{i}_marriage_age")
            
            children.append({
                'current_age': child_age,
                'school_fee': school_fee,
                'school_fee_increase': school_fee_increase,
                'fee_increase_frequency': 1,  # Annual increase
                'graduation_fee': graduation_fee,
                'marriage_cost': marriage_cost,
                'marriage_age': marriage_age
            })
    
    # Submit button
    submitted = st.form_submit_button("Generate Retirement Plan")
    
    if submitted:
        # Prepare parameters
        params = {
            'current_age': current_age,
            'retirement_age': retirement_age,
            'life_expectancy': life_expectancy,
            'current_corpus': current_corpus,
            'pre_retirement_return': pre_ret_return * 100,  # Convert to percentage for parsing
            'post_retirement_return': post_ret_return * 100,
            'inflation': inflation * 100,
            'monthly_expenses': monthly_expenses,
            'children': children
        }
        
        try:
            # Generate projections
            retirement_params = parse_config(params)
            projections = generate_yearly_projections(retirement_params)
            
            # Store results in session state
            st.session_state.projections = projections
            st.session_state.show_results = True
            
            # Convert to DataFrame for display
            df = pd.DataFrame(projections)
            
            # Add year column if not exists
            if 'year' not in df.columns and 'age' in df.columns:
                current_year = datetime.now().year
                df['year'] = df['age'].apply(lambda x: current_year + (x - current_age))
            
            st.session_state.df = df
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.show_results = False

# Display results if available
if st.session_state.show_results and st.session_state.projections:
    df = st.session_state.df
    
    # Key Metrics
    st.markdown("## Retirement Plan Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='result-card'><div class='metric-label'>Retirement Corpus Required</div>"
                   f"<div class='metric-value'>₹{df['corpus_start'].iloc[-1]:,.0f}</div></div>", 
                   unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='result-card'><div class='metric-label'>Annual Expenses at Retirement</div>"
                   f"<div class='metric-value'>₹{df[df['age'] == retirement_age]['household_expense'].values[0]:,.0f}</div></div>", 
                   unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='result-card'><div class='metric-label'>Corpus at Life Expectancy</div>"
                   f"<div class='metric-value'>₹{df['corpus_start'].iloc[-1]:,.0f}</div></div>", 
                   unsafe_allow_html=True)
    
    with col4:
        years_after_retirement = life_expectancy - retirement_age
        st.markdown(f"<div class='result-card'><div class='metric-label'>Years in Retirement</div>"
                   f"<div class='metric-value'>{years_after_retirement} years</div></div>", 
                   unsafe_allow_html=True)
    
    # Charts
    st.markdown("## Projections")
    
    # Corpus vs Expenses Over Time
    fig1 = px.line(df, x='age', y=['corpus_start', 'household_expense'],
                  title="Corpus vs Expenses Over Time",
                  labels={'value': 'Amount (₹)', 'age': 'Age'},
                  height=500)
    fig1.update_layout(legend_title_text='')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Expense Breakdown
    st.markdown("### Expense Breakdown")
    
    # Prepare data for stacked area chart
    expense_cols = ['household_expense', 'school_fees', 'graduation_fees', 'marriage_expense']
    expense_df = df[['age'] + expense_cols].melt(id_vars='age', var_name='Expense Type', value_name='Amount')
    
    fig2 = px.area(expense_df, x='age', y='Amount', color='Expense Type',
                  title="Expense Breakdown Over Time",
                  labels={'Amount': 'Amount (₹)', 'age': 'Age'},
                  height=500)
    st.plotly_chart(fig2, use_container_width=True)
    
    # Data Table
    st.markdown("### Yearly Projections")
    st.dataframe(df[['year', 'age', 'corpus_start', 'household_expense', 'school_fees', 
                    'graduation_fees', 'marriage_expense']].round(2), 
                height=400, use_container_width=True)
    
    # Download buttons
    st.markdown("### Download Results")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"retirement_plan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        excel = df.to_excel("retirement_plan.xlsx", index=False)
        with open("retirement_plan.xlsx", "rb") as f:
            excel_data = f.read()
        st.download_button(
            label="Download as Excel",
            data=excel_data,
            file_name=f"retirement_plan_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Instructions
with st.sidebar:
    st.markdown("## How to Use")
    st.markdown("""
    1. Fill in your basic financial information
    2. Add details about your children (if any)
    3. Click 'Generate Retirement Plan'
    4. Review the projections and download results
    
    ### Tips:
    - Be realistic about investment returns
    - Consider inflation in your calculations
    - Review and update your plan annually
    - Consult a financial advisor for personalized advice
    """)
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This retirement planning tool helps you project your financial future 
    based on your current savings, expenses, and investment returns.
    
    *Note: This is for informational purposes only and not financial advice.*
    """)
