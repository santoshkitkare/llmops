from pathlib import Path
from typing import List, Dict, Any, Tuple
import math

def _format_amount(amount: float) -> str:
    """Format amount as string with commas and 2 decimal places."""
    return f"₹{amount:,.2f}"

def _create_text_chart(x_values, y_values, width=60, height=20):
    """Create a simple text-based bar chart."""
    if not x_values or not y_values:
        return "No data to display"
    
    # Find min and max values
    min_val = min(y_values)
    max_val = max(y_values)
    range_val = max_val - min_val if max_val > min_val else 1
    
    # Scale values to fit the chart height
    scale = (height - 4) / range_val if range_val > 0 else 1
    
    # Create chart rows
    chart_rows = []
    for i in range(height, 0, -1):
        row = []
        threshold = min_val + (i / scale)
        for val in y_values:
            if val >= threshold:
                row.append('█')
            else:
                row.append(' ')
        chart_rows.append(''.join(row))
    
    # Add x-axis labels
    x_labels = [str(x) for x in x_values]
    if len(x_labels) > 20:  # Only show some labels if there are many points
        step = len(x_labels) // 10
        x_labels = [label if i % step == 0 else '' for i, label in enumerate(x_labels)]
    
    # Add y-axis scale
    y_scale = [f"{min_val + (i * range_val / 3):,.0f}" for i in range(4)]
    
    # Combine everything
    chart = '\n'.join(chart_rows)
    chart += '\n' + '-' * width
    chart += '\n' + ' '.join(x_labels)
    chart += '\n\nY-scale: ' + ' | '.join(y_scale)
    
    return chart

def plot_retirement_projections(projections: List[Dict[str, Any]], output_dir: str = 'output') -> str:
    """
    Generate and save a plot of the retirement projections.
    
    Args:
        projections: List of yearly projection dictionaries
        output_dir: Directory to save the plot
        
    Returns:
        Path to the saved plot image
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract data from projections
    ages = [p['age'] for p in projections]
    corpus = [float(p['corpus_start']) for p in projections]
    expenses = [float(p['household_expense']) for p in projections]
    
    # Create a simple text-based chart
    chart = "=== Retirement Projection ===\n"
    chart += "\nCorpus Over Time:\n"
    chart += _create_text_chart(ages, corpus) + "\n\n"
    
    chart += "Expenses Over Time:\n"
    chart += _create_text_chart(ages, expenses) + "\n\n"
    
    # Add retirement age info
    if projections and 'retirement_age' in projections[0]:
        retirement_age = projections[0]['retirement_age']
        chart += f"Retirement Age: {retirement_age}\n"
    
    # Add some key metrics
    if projections:
        final_proj = projections[-1]
        chart += f"\nFinal Projection at Age {final_proj['age']}:\n"
        chart += f"- Final Corpus: {_format_amount(final_proj['corpus_start'])}\n"
        chart += f"- Annual Expenses: {_format_amount(final_proj['household_expense'])}\n"
    
    # Print to console
    print("\n" + "="*60)
    print(chart)
    print("="*60 + "\n")
    
    # Save to file
    plot_path = output_path / 'retirement_projection.txt'
    with open(plot_path, 'w') as f:
        f.write(chart)
    
    return str(plot_path)

def plot_expense_breakdown(projections: List[Dict[str, Any]], output_dir: str = 'output') -> str:
    """
    Generate and save a text-based visualization of the expense breakdown.
    
    Args:
        projections: List of yearly projection dictionaries
        output_dir: Directory to save the plot
        
    Returns:
        Path to the saved text file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Extract data from projections
    ages = [p['age'] for p in projections]
    household = [float(p['household_expense']) for p in projections]
    school = [float(p['school_fees']) for p in projections]
    graduation = [float(p['graduation_fees']) for p in projections]
    marriage = [float(p['marriage_expense']) for p in projections]
    
    # Create a simple text-based chart for each category
    chart = "=== Expense Breakdown by Category ===\n\n"
    
    chart += "Household Expenses:\n"
    chart += _create_text_chart(ages, household) + "\n\n"
    
    if any(school):
        chart += "School Fees:\n"
        chart += _create_text_chart(ages, school) + "\n\n"
    
    if any(graduation):
        chart += "Graduation Fees:\n"
        chart += _create_text_chart(ages, graduation) + "\n\n"
    
    if any(marriage):
        chart += "Marriage Expenses:\n"
        chart += _create_text_chart(ages, marriage) + "\n\n"
    
    # Add total expenses chart
    total_expenses = [h + s + g + m for h, s, g, m in zip(household, school, graduation, marriage)]
    chart += "Total Annual Expenses:\n"
    chart += _create_text_chart(ages, total_expenses) + "\n"
    
    # Print to console
    print("\n" + "="*60)
    print(chart)
    print("="*60 + "\n")
    
    # Save to file
    plot_path = output_path / 'expense_breakdown.txt'
    with open(plot_path, 'w') as f:
        f.write(chart)
    
    return str(plot_path)
