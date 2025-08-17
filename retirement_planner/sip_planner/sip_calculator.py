"""
Enhanced SIP (Systematic Investment Plan) Calculator

This module provides functions to calculate SIP returns with step-up SIPs and initial investments.
"""
from typing import List, Dict, Union
import pandas as pd
from datetime import datetime

def calculate_sip(
    monthly_investment: float,
    tenure_years: int,
    rate_of_return: float,
    yearly_step_up: float = 0.0,
    initial_investment: float = 0.0,
    tenure_months: int = 0,
    step_up_type: str = 'compounded',  # 'compounded' or 'fixed'
) -> Dict[str, Union[float, pd.DataFrame]]:
    """
    Calculate SIP returns with step-up and initial investment.
    
    Args:
        monthly_investment: Initial monthly investment amount
        tenure_years: Investment period in years
        rate_of_return: Expected annual rate of return (in percentage)
        yearly_step_up: Yearly percentage increase in SIP amount (default: 0%)
        initial_investment: Initial lump sum investment (default: 0)
        tenure_months: Additional months to the tenure (0-11)
        
    Returns:
        Dictionary containing:
        - 'final_amount': Total corpus at the end of tenure
        - 'total_invested': Total amount invested
        - 'total_returns': Total returns generated
        - 'projection': DataFrame with year-by-year projection
    """
    # Convert annual rate to monthly and percentage to decimal
    monthly_rate = (rate_of_return / 100) / 12
    total_months = (tenure_years * 12) + tenure_months
    
    # Initialize variables
    current_investment = monthly_investment
    total_invested = initial_investment
    corpus = initial_investment
    
    # Track yearly projections
    projections = []
    
    # Track the monthly investment for display
    display_investment = current_investment
    
    # Add initial projection (at the start of the investment)
    if initial_investment > 0:
        projections.append({
            'year': 0,
            'monthly_investment': monthly_investment,  # Show the original starting amount
            'total_invested': total_invested,
            'corpus': corpus,
            'returns': 0.0
        })
    
    # Track the current year and initial investment
    current_year = 1
    initial_sip = monthly_investment
    current_investment = monthly_investment
    
    # Track step-up type
    is_compounded_stepup = step_up_type.lower() == 'compounded'
    
    for month in range(1, total_months + 1):
        # Add monthly investment at the beginning of the month
        corpus += current_investment
        total_invested += current_investment
        
        # Apply monthly return at the end of the month
        corpus *= (1 + monthly_rate)
        
        # Check if it's the end of a year
        if month % 12 == 0 and month < total_months:
            year = month // 12
            
            # Record yearly projection with the current investment amount
            projections.append({
                'year': year,
                'monthly_investment': current_investment,
                'total_invested': total_invested,
                'corpus': corpus,
                'returns': corpus - total_invested
            })
            
            # Apply step-up for the next year starting from the second year
            if current_year >= 1:  # Start step-up from the second year
                if is_compounded_stepup:
                    # Compounded: step-up is applied to previous year's SIP
                    current_investment *= (1 + (yearly_step_up / 100))
                else:
                    # Fixed: step-up is always applied to initial SIP
                    current_investment = initial_sip * (1 + (yearly_step_up / 100) * (current_year))
            
            current_year += 1
    
    # Add final projection for partial years if needed
    if total_months % 12 != 0 or not projections:
        year = (total_months // 12) + (1 if total_months % 12 > 0 else 0)
        # If we have projections, the last one is for the full year, so we need to adjust the year
        if projections:
            year = projections[-1]['year'] + (1 if total_months % 12 > 0 else 0)
        
        # For the final projection, use the current investment amount
        projections.append({
            'year': year,
            'monthly_investment': current_investment,
            'total_invested': total_invested,
            'corpus': corpus,
            'returns': corpus - total_invested
        })
    
    # Create DataFrame from projections
    df = pd.DataFrame(projections)
    
    return {
        'final_amount': corpus,
        'total_invested': total_invested,
        'total_returns': corpus - total_invested,
        'projection': df
    }

def calculate_sip_required(
    target_amount: float,
    tenure_years: int,
    rate_of_return: float,
    yearly_step_up: float = 0.0,
    initial_investment: float = 0.0,
    tenure_months: int = 0,
) -> Dict[str, Union[float, pd.DataFrame]]:
    """
    Calculate the monthly SIP required to reach a target amount.
    
    Args:
        target_amount: Desired corpus amount
        tenure_years: Investment period in years
        rate_of_return: Expected annual rate of return (in percentage)
        yearly_step_up: Yearly percentage increase in SIP amount (default: 0%)
        initial_investment: Initial lump sum investment (default: 0)
        tenure_months: Additional months to the tenure (0-11)
        
    Returns:
        Dictionary containing the required monthly SIP and projection details
    """
    # Use binary search to find the required monthly investment
    low = 0.0
    high = target_amount
    result = None
    
    # Set a tolerance level for the binary search
    tolerance = 0.01
    
    while high - low > tolerance:
        mid = (low + high) / 2
        calc = calculate_sip(
            monthly_investment=mid,
            tenure_years=tenure_years,
            rate_of_return=rate_of_return,
            yearly_step_up=yearly_step_up,
            initial_investment=initial_investment,
            tenure_months=tenure_months
        )
        
        if calc['final_amount'] < target_amount:
            low = mid
        else:
            high = mid
            result = calc
    
    return result if result else calculate_sip(
        monthly_investment=high,
        tenure_years=tenure_years,
        rate_of_return=rate_of_return,
        yearly_step_up=yearly_step_up,
        initial_investment=initial_investment,
        tenure_months=tenure_months
    )
