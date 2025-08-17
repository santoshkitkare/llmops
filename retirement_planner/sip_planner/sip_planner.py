"""
SIP Planner Module

This module provides functionality to calculate the monthly SIP amount needed to reach
a target corpus based on expected returns and investment period, with support for step-up SIPs.
"""

def calculate_required_sip(
    target_amount: float,
    years: int,
    expected_return_rate: float,
    yearly_step_up: float = 0.0,
    initial_investment: float = 0.0,
    tenure_months: int = 0
) -> dict:
    """
    Calculate the required monthly SIP amount to reach a target corpus.
    
    Args:
        target_amount: Target corpus amount to achieve (in INR)
        years: Investment period in years
        expected_return_rate: Expected annual rate of return (in percentage, e.g., 12 for 12%)
        yearly_step_up: Yearly percentage increase in SIP amount (default: 0%)
        initial_investment: Initial lump sum investment (default: 0)
        tenure_months: Additional months to the tenure (0-11)
        
    Returns:
        dict: Dictionary containing:
            - 'monthly_sip': Required monthly SIP amount
            - 'total_invested': Total amount invested over the period
            - 'final_amount': Projected final amount
            - 'projection': List of yearly projections
    """
    # Use binary search to find the required monthly SIP amount
    low = 0.0
    high = target_amount  # Upper bound for binary search
    result = None
    tolerance = 0.01  # 1 paisa tolerance
    
    def calculate_final_amount(sip_amount):
        """Helper function to calculate final amount for a given SIP"""
        monthly_rate = (expected_return_rate / 100) / 12
        total_months = (years * 12) + tenure_months
        
        corpus = initial_investment
        current_sip = sip_amount
        
        for month in range(1, total_months + 1):
            # Add monthly SIP at the beginning of the month
            corpus += current_sip
            
            # Apply monthly return at the end of the month
            corpus *= (1 + monthly_rate)
            
            # Apply yearly step-up
            if month % 12 == 0 and month < total_months:
                current_sip *= (1 + (yearly_step_up / 100))
        
        return corpus
    
    # Binary search to find the required SIP amount
    while high - low > tolerance:
        mid = (low + high) / 2
        final_amount = calculate_final_amount(mid)
        
        if final_amount < target_amount:
            low = mid
        else:
            high = mid
            result = mid
    
    # Generate projection for the final result
    if result is None:
        result = high
    
    # Calculate final projection with the found SIP amount
    monthly_rate = (expected_return_rate / 100) / 12
    total_months = (years * 12) + tenure_months
    
    corpus = initial_investment
    current_sip = result
    total_invested = initial_investment
    projections = []
    
    for year in range(1, years + 1):
        year_investment = 0
        
        for month in range(1, 13):
            # Skip if we've reached total months (for partial last year)
            if (year - 1) * 12 + month > total_months:
                break
                
            # Add monthly SIP at the beginning of the month
            corpus += current_sip
            year_investment += current_sip
            total_invested += current_sip
            
            # Apply monthly return at the end of the month
            corpus *= (1 + monthly_rate)
            
            # Apply yearly step-up after 12 months
            if month % 12 == 0 and (year * 12) < total_months:
                current_sip *= (1 + (yearly_step_up / 100))
        
        # For the first year, use the initial SIP amount (before any step-ups)
        # For subsequent years, use the stepped-up amount
        monthly_sip_for_display = result if year == 1 else current_sip
        
        # Add yearly projection
        projections.append({
            'year': year,
            'monthly_sip': monthly_sip_for_display,
            'yearly_investment': year_investment,
            'total_invested': total_invested,
            'corpus': corpus,
            'returns': corpus - total_invested
        })
    
    # Handle additional months in the last year
    remaining_months = tenure_months % 12
    if remaining_months > 0:
        year_investment = 0
        
        for month in range(1, remaining_months + 1):
            # Add monthly SIP at the beginning of the month
            corpus += current_sip
            year_investment += current_sip
            total_invested += current_sip
            
            # Apply monthly return at the end of the month
            corpus *= (1 + monthly_rate)
        
        # Add projection for partial year
        projections.append({
            'year': years + (tenure_months / 12),
            'monthly_sip': current_sip,
            'yearly_investment': year_investment,
            'total_invested': total_invested,
            'corpus': corpus,
            'returns': corpus - total_invested
        })
    
    return {
        'monthly_sip': result,
        'total_invested': total_invested,
        'final_amount': corpus,
        'projection': projections
    }

def get_sip_plan(
    target_amount: float,
    years: int,
    expected_return_rate: float,
    yearly_step_up: float = 0.0,
    initial_investment: float = 0.0,
    tenure_months: int = 0
) -> dict:
    """
    Get a comprehensive SIP plan to reach the target amount.
    
    Args:
        target_amount: Target corpus amount to achieve (in INR)
        years: Investment period in years
        expected_return_rate: Expected annual rate of return (in percentage, e.g., 12 for 12%)
        yearly_step_up: Yearly percentage increase in SIP amount (default: 0%)
        initial_investment: Initial lump sum investment (default: 0)
        tenure_months: Additional months to the tenure (0-11)
        
    Returns:
        dict: Dictionary containing the SIP plan with projections
    """
    return calculate_required_sip(
        target_amount=target_amount,
        years=years,
        expected_return_rate=expected_return_rate,
        yearly_step_up=yearly_step_up,
        initial_investment=initial_investment,
        tenure_months=tenure_months
    )

# Example usage
if __name__ == "__main__":
    # Example: Calculate SIP needed for 1 crore in 15 years with 12% return
    plan = get_sip_plan(
        target_amount=1_00_00_000,  # 1 crore
        years=15,
        expected_return_rate=12.0,
        yearly_step_up=10.0,  # 10% yearly step-up
        initial_investment=0
    )
    
    print(f"Monthly SIP needed: ₹{plan['monthly_sip']:,.2f}")
    print(f"Total invested: ₹{plan['total_invested']:,.2f}")
    print(f"Final corpus: ₹{plan['final_amount']:,.2f}")
    
    # Print yearly projections
    print("\nYearly Projections:")
    print("Year | Monthly SIP    | Yearly Investment | Total Invested | Corpus")
    print("-" * 80)
    
    for proj in plan['projection']:
        print(f"{proj['year']:4.1f} | "
              f"₹{proj['monthly_sip']:>10,.2f} | "
              f"₹{proj['yearly_investment']:>13,.0f} | "
              f"₹{proj['total_invested']:>12,.0f} | "
              f"₹{proj['corpus']:>10,.0f}")
