"""
SIP Calculator Module

This module provides functions to calculate the monthly SIP amount needed to reach
a target corpus based on expected returns and investment period.
"""

def calculate_sip_amount(
    target_amount: float,
    years: int,
    expected_return_rate: float
) -> float:
    """
    Calculate the monthly SIP amount needed to reach a target corpus.
    
    Args:
        target_amount: The desired corpus amount at the end of the investment period
        years: Investment period in years
        expected_return_rate: Expected annual rate of return (in percentage, e.g., 12 for 12%)
        
    Returns:
        float: Monthly SIP amount needed
    """
    # Convert annual rate to monthly and percentage to decimal
    monthly_rate = (expected_return_rate / 100) / 12
    total_months = years * 12
    
    # Formula: SIP = FV * r / ((1 + r)^n - 1) * (1 + r)
    # Where FV is future value, r is monthly rate, n is number of months
    if monthly_rate == 0:
        return target_amount / total_months
    
    sip_amount = (target_amount * monthly_rate) / ((1 + monthly_rate) ** total_months - 1)
    return sip_amount

def calculate_sip_projection(
    monthly_sip: float,
    years: int,
    expected_return_rate: float,
    initial_investment: float = 0
) -> list:
    """
    Generate year-by-year SIP projection.
    
    Args:
        monthly_sip: Monthly SIP amount
        years: Investment period in years
        expected_return_rate: Expected annual rate of return (in percentage)
        initial_investment: Initial investment amount (default: 0)
        
    Returns:
        list: List of dictionaries containing year-by-year projection
    """
    monthly_rate = (expected_return_rate / 100) / 12
    total_months = years * 12
    
    corpus = initial_investment
    projections = []
    
    for year in range(1, years + 1):
        for month in range(1, 13):
            # Add monthly SIP at the beginning of the month
            corpus += monthly_sip
            # Apply monthly return at the end of the month
            corpus *= (1 + monthly_rate)
        
        # Record yearly projection
        total_invested = (year * 12 * monthly_sip) + initial_investment
        returns = corpus - total_invested
        
        projections.append({
            'year': year,
            'total_invested': total_invested,
            'corpus': corpus,
            'returns': returns,
            'xirr': expected_return_rate
        })
    
    return projections
