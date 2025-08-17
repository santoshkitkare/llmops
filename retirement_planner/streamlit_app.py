import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64
from datetime import datetime
import os
import sys

# Import the retirement planning modules
from retirement_planner.calculations import generate_yearly_projections
from retirement_planner.io_handlers import parse_config
from retirement_planner.models import RetirementParams, Child

# Import SIP modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sip_planner.sip_calculator import calculate_sip
from sip_planner import calculate_required_sip, get_sip_plan

# Page configuration
st.set_page_config(
    page_title="Financial Planner",
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

# Initialize session state for form data and results
if 'projections' not in st.session_state:
    st.session_state.projections = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

def get_table_download_link(df, filename, link_text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'

# Create main tabs
tab1, tab2 = st.tabs(["Retirement Planner", "SIP Planner"])

# SIP Planner Tab
with tab2:
    st.markdown("<h1 class='main-header'>SIP Planner</h1>", unsafe_allow_html=True)
    
    # Create sub-tabs for SIP Calculator and SIP Planner
    sip_tab1, sip_tab2 = st.tabs(["SIP Calculator", "SIP Planner"])
    
    # SIP Calculator Tab
    with sip_tab1:
        st.markdown("### Calculate Returns on Your SIP")
        
        with st.form(key='sip_calculator_form'):
            col1, col2 = st.columns(2)
            
            with col1:
                monthly_investment = st.number_input(
                    'Monthly Investment (₹)',
                    min_value=1000.0,
                    step=1000.0,
                    value=10000.0,
                    format='%.2f'
                )
                
                tenure_years = st.number_input(
                    'Investment Tenure (Years)',
                    min_value=1,
                    max_value=50,
                    value=10,
                    step=1
                )
                
                initial_investment = st.number_input(
                    'Initial Investment (₹)',
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    format='%.2f'
                )
            
            with col2:
                rate_of_return = st.number_input(
                    'Expected Annual Return (%)',
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.1,
                    format='%.1f'
                )
                
                yearly_step_up = st.number_input(
                    'Yearly Step-up (%)',
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0,
                    format='%.1f'
                )
                
                # Add step-up type selection
                step_up_type = st.radio(
                    'Step-up Type',
                    ['Compounded', 'Fixed'],
                    help='Compounded: Step-up is applied to previous year\'s SIP amount\nFixed: Step-up is always applied to initial SIP amount'
                )
                
                tenure_months = st.number_input(
                    'Additional Months',
                    min_value=0,
                    max_value=11,
                    value=0,
                    step=1
                )
            
            submitted_calc = st.form_submit_button("Calculate SIP Returns")
        
        if submitted_calc:
            # Calculate SIP returns
            result = calculate_sip(
                monthly_investment=monthly_investment,
                tenure_years=tenure_years,
                rate_of_return=rate_of_return,
                yearly_step_up=yearly_step_up,
                initial_investment=initial_investment,
                tenure_months=tenure_months,
                step_up_type=step_up_type.lower()
            )
            
            # Display results
            st.markdown("## Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Final Corpus", f"₹{result['final_amount']:,.2f}")
            with col2:
                st.metric("Total Invested", f"₹{result['total_invested']:,.2f}")
            with col3:
                st.metric("Total Returns", f"₹{result['total_returns']:,.2f}")
            
            # Create projection chart
            st.markdown("### Investment Growth Over Time")
            
            df_sip = result['projection']
            
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=df_sip['year'],
                y=df_sip['total_invested'],
                name='Total Invested',
                mode='lines+markers',
                line=dict(color='#1f77b4')
            ))
            
            fig.add_trace(go.Scatter(
                x=df_sip['year'],
                y=df_sip['corpus'],
                name='Expected Corpus',
                mode='lines+markers',
                line=dict(color='#2ca02c')
            ))
            
            fig.update_layout(
                xaxis_title='Years',
                yaxis_title='Amount (₹)',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.markdown("### Yearly Projection")
            
            # Format the DataFrame for display with new column order
            display_df = df_sip.rename(columns={
                'year': 'Year',
                'monthly_investment': 'Monthly SIP (₹)',
                'total_invested': 'Total Investment (₹)',
                'returns': 'Returns (₹)',
                'corpus': 'Corpus (₹)'
            })
            
            # Add Yearly Investment column (12 * monthly_investment)
            display_df['Yearly Investment (₹)'] = df_sip['monthly_investment'] * 12
            
            # Reorder columns
            display_df = display_df[[
                'Year',
                'Monthly SIP (₹)',
                'Yearly Investment (₹)',
                'Total Investment (₹)',
                'Returns (₹)',
                'Corpus (₹)'
            ]]
            
            # Format numbers with commas
            for col in ['Monthly SIP (₹)', 'Yearly Investment (₹)', 'Total Investment (₹)', 'Returns (₹)', 'Corpus (₹)']:
                display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df_sip.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Projection as CSV",
                data=csv,
                file_name=f"sip_calculator_projection_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # SIP Planner Tab
    with sip_tab2:
        st.markdown("### Plan Your SIP to Reach Your Financial Goals")
        
        with st.form("sip_planner_form"):
            st.markdown("#### Financial Goal Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                target_amount = st.number_input(
                    "Target Amount (₹)",
                    min_value=10000,
                    value=1000000,
                    step=10000,
                    key="sip_plan_target"
                )
                
                years = st.number_input(
                    "Investment Period (Years)",
                    min_value=1,
                    max_value=50,
                    value=10,
                    step=1,
                    key="sip_plan_years"
                )
                
                months = st.number_input(
                    "Additional Months",
                    min_value=0,
                    max_value=11,
                    value=0,
                    step=1,
                    key="sip_plan_months"
                )
            
            with col2:
                expected_return = st.number_input(
                    "Expected Annual Return (%)",
                    min_value=1.0,
                    max_value=30.0,
                    value=12.0,
                    step=0.5,
                    key="sip_plan_ror"
                )
                
                yearly_step_up = st.number_input(
                    "Yearly Step-up in SIP (%)",
                    min_value=0.0,
                    max_value=50.0,
                    value=10.0,
                    step=0.5,
                    key="sip_plan_stepup"
                )
                
                initial_investment = st.number_input(
                    "Initial Investment (₹) - Optional",
                    min_value=0,
                    value=0,
                    step=10000,
                    key="sip_plan_initial"
                )
            
            submitted_plan = st.form_submit_button("Calculate Required SIP")
        
        if submitted_plan:
            # Calculate required SIP
            plan = calculate_required_sip(
                target_amount=target_amount,
                years=years,
                expected_return_rate=expected_return,
                yearly_step_up=yearly_step_up,
                initial_investment=initial_investment,
                tenure_months=months
            )
            
            # Display results
            st.markdown("## SIP Plan")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Required Monthly SIP", f"₹{plan['monthly_sip']:,.2f}")
            with col2:
                st.metric("Total Investment", f"₹{plan['total_invested']:,.2f}")
            with col3:
                st.metric("Final Corpus", f"₹{plan['final_amount']:,.2f}")
            
            # Create projection chart
            st.markdown("### Investment Growth Projection")
            
            df_plan = pd.DataFrame(plan['projection'])
            
            fig = go.Figure()
            
            # Add traces
            fig.add_trace(go.Scatter(
                x=df_plan['year'],
                y=df_plan['total_invested'],
                name='Total Invested',
                mode='lines+markers',
                line=dict(color='#1f77b4')
            ))
            
            fig.add_trace(go.Scatter(
                x=df_plan['year'],
                y=df_plan['corpus'],
                name='Projected Corpus',
                mode='lines+markers',
                line=dict(color='#2ca02c')
            ))
            
            fig.add_trace(go.Scatter(
                x=df_plan['year'],
                y=df_plan['monthly_sip'],
                name='Monthly SIP',
                mode='lines+markers',
                line=dict(color='#ff7f0e'),
                yaxis='y2'
            ))
            
            fig.update_layout(
                xaxis_title='Years',
                yaxis_title='Amount (₹)',
                yaxis2=dict(
                    title='Monthly SIP (₹)',
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                hovermode='x unified',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.markdown("### Yearly Projection")
            
            # Format the DataFrame for display with new column order
            display_df = df_plan.rename(columns={
                'year': 'Year',
                'monthly_sip': 'Monthly SIP (₹)',
                'yearly_investment': 'Yearly Investment (₹)',
                'total_invested': 'Total Investment (₹)',
                'returns': 'Returns (₹)',
                'corpus': 'Corpus (₹)'
            })
            
            # Reorder columns
            display_df = display_df[[
                'Year',
                'Monthly SIP (₹)',
                'Yearly Investment (₹)',
                'Total Investment (₹)',
                'Returns (₹)',
                'Corpus (₹)'
            ]]
            
            # Format numbers with commas
            for col in ['Monthly SIP (₹)', 'Yearly Investment (₹)', 'Total Investment (₹)', 'Returns (₹)', 'Corpus (₹)']:
                display_df[col] = display_df[col].apply(lambda x: f"₹{x:,.2f}" if pd.notnull(x) else "")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df_plan.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Plan as CSV",
                data=csv,
                file_name=f"sip_planner_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Retirement Planner Tab
with tab1:
    st.markdown("<h1 class='main-header'>Retirement Planning Tool</h1>", unsafe_allow_html=True)
    
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
        
        if 'num_children' not in st.session_state:
            st.session_state.num_children = 1
        
        num_children = st.number_input("Number of Children", min_value=0, max_value=5, value=0, step=1, 
                                     key="num_children")
        
        children = []
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
        
        # Submit button at the end of the form
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


# Display retirement results if available
if st.session_state.show_results and st.session_state.projections and 'df' in st.session_state:
    with tab1:
        df = st.session_state.df
        
        # Check if required columns exist in the DataFrame
        if not all(col in df.columns for col in ['corpus_start', 'age', 'household_expense']):
            st.error("Error: Missing required data columns in the results.")
        else:
            # Key Metrics
            st.markdown("## Retirement Plan Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                corpus_value = df['corpus_start'].iloc[-1] if not df.empty else 0
                st.markdown("<div class='result-card'><div class='metric-label'>Retirement Corpus Required</div>"
                          f"<div class='metric-value'>₹{corpus_value:,.0f}</div></div>", 
                          unsafe_allow_html=True)
            
            with col2:
                retirement_expenses = df[df['age'] == retirement_age]['household_expense']
                expense_value = retirement_expenses.values[0] if not retirement_expenses.empty else 0
                st.markdown("<div class='result-card'><div class='metric-label'>Annual Expenses at Retirement</div>"
                          f"<div class='metric-value'>₹{expense_value:,.0f}</div></div>", 
                          unsafe_allow_html=True)
            
            with col3:
                st.markdown("<div class='result-card'><div class='metric-label'>Corpus at Life Expectancy</div>"
                          f"<div class='metric-value'>₹{df['corpus_start'].iloc[-1]:,.0f}</div></div>", 
                          unsafe_allow_html=True)
            
            with col4:
                years_after_retirement = life_expectancy - retirement_age if 'retirement_age' in locals() else 0
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
            expense_cols = [col for col in ['household_expense', 'school_fees', 'graduation_fees', 'marriage_expense'] 
                          if col in df.columns]
            
            if expense_cols:
                expense_df = df[['age'] + expense_cols].melt(id_vars='age', var_name='Expense Type', value_name='Amount')
                
                fig2 = px.area(expense_df, x='age', y='Amount', color='Expense Type',
                              title="Expense Breakdown Over Time",
                              labels={'Amount': 'Amount (₹)', 'age': 'Age'},
                              height=500)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Data Table
            st.markdown("### Yearly Projections")
            display_cols = ['year', 'age', 'corpus_start', 'household_expense']
            display_cols.extend([col for col in ['school_fees', 'graduation_fees', 'marriage_expense'] 
                               if col in df.columns])
            
            st.dataframe(df[display_cols].round(2), 
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
                excel_file = "retirement_plan.xlsx"
                df.to_excel(excel_file, index=False)
                with open(excel_file, "rb") as f:
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
