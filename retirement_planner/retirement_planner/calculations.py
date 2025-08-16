from typing import List, Dict, Any, Tuple
from dataclasses import asdict
import datetime
import math
from .models import RetirementParams, Child, YearlyProjection

def calculate_inflated_amount(amount: float, inflation: float, years: int) -> float:
    """Calculate the future value of an amount considering inflation."""
    return amount * ((1 + inflation) ** years)

def calculate_school_fees(
    child: Child, 
    current_year: int, 
    inflation: float,
    child_age: int
) -> float:
    """Calculate school fees for a child in a given year."""
    if child_age < 5 or child_age > 17:  # Assuming school age is 5-17
        return 0.0
    
    # Calculate number of fee increases
    years_since_start = child_age - 5  # Assuming school starts at age 5
    num_increases = years_since_start // child.fee_increase_frequency
    
    # Calculate current year's fee with increases
    current_fee = child.school_fee * ((1 + child.school_fee_increase) ** num_increases)
    
    # Adjust for inflation from today
    return calculate_inflated_amount(current_fee, inflation, current_year)

def calculate_graduation_fees(
    child: Child,
    current_year: int,
    inflation: float,
    child_age: int
) -> float:
    """Calculate annual graduation fees for a child (spread over 4 years)."""
    if 18 <= child_age <= 21:  # Assuming 4 years of graduation
        # Spread the total graduation fee over 4 years and adjust for inflation
        annual_fee = child.graduation_fee / 4
        return calculate_inflated_amount(annual_fee, inflation, current_year)
    return 0.0

def calculate_marriage_expense(
    child: Child,
    current_year: int,
    inflation: float,
    child_age: int
) -> float:
    """Calculate marriage expense if the child is getting married this year."""
    if child_age == child.marriage_age:
        return calculate_inflated_amount(child.marriage_cost, inflation, current_year)
    return 0.0

def generate_yearly_projections(params: RetirementParams) -> List[Dict[str, Any]]:
    """Generate year-by-year retirement projections."""
    projections = []
    current_corpus = params.current_corpus
    
    for year in range(params.current_age, params.life_expectancy + 1):
        # Determine return rate based on retirement status
        is_retired = year >= params.retirement_age
        return_rate = params.post_ret_return if is_retired else params.pre_ret_return
        
        # Calculate household expenses (increasing with inflation each year)
        years_elapsed = year - params.current_age
        household_expense = calculate_inflated_amount(
            params.monthly_expenses * 12, 
            params.inflation, 
            years_elapsed
        )
        
        # Initialize expense trackers
        total_school_fees = 0.0
        total_graduation_fees = 0.0
        total_marriage_expense = 0.0
        
        # Calculate child-related expenses
        for child in params.children:
            child_age = child.current_age + years_elapsed
            
            # School fees (ages 5-17)
            total_school_fees += calculate_school_fees(
                child, years_elapsed, params.inflation, child_age
            )
            
            # Graduation fees (ages 18-21)
            total_graduation_fees += calculate_graduation_fees(
                child, years_elapsed, params.inflation, child_age
            )
            
            # Marriage expense
            total_marriage_expense += calculate_marriage_expense(
                child, years_elapsed, params.inflation, child_age
            )
        
        # Create projection for the year
        projection = YearlyProjection(
            year=datetime.datetime.now().year + years_elapsed,
            age=year,
            corpus_start=current_corpus,
            household_expense=household_expense,
            school_fees=total_school_fees,
            graduation_fees=total_graduation_fees,
            marriage_expense=total_marriage_expense
        )
        
        # Calculate corpus at the end of the year
        current_corpus = projection.corpus_end(return_rate=return_rate)
        
        # Check for negative corpus
        if current_corpus < 0:
            current_corpus = 0  # Prevent negative corpus in projections
        
        # Convert to dict and add corpus_end
        projection_dict = asdict(projection)
        projection_dict['corpus_end'] = current_corpus
        projections.append(projection_dict)
        
        # Stop if corpus is depleted
        if current_corpus <= 0 and year < params.life_expectancy:
            break
    
    return projections
