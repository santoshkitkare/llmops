import json
import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Union
from .models import RetirementParams, Child

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file."""
    path = Path(config_path)
    with open(path, 'r') as f:
        if path.suffix.lower() == '.json':
            return json.load(f)
        elif path.suffix.lower() in ('.yaml', '.yml'):
            return yaml.safe_load(f)
        else:
            raise ValueError("Unsupported file format. Use .json, .yaml, or .yml")

def parse_config(config: Dict[str, Any]) -> RetirementParams:
    """Parse configuration dictionary into RetirementParams object."""
    children = []
    for child_data in config.get('children', []):
        children.append(Child(
            current_age=child_data['current_age'],
            school_fee=child_data.get('school_fee', 0),
            school_fee_increase=child_data.get('school_fee_increase', 0) / 100,  # Convert % to decimal
            fee_increase_frequency=child_data.get('fee_increase_frequency', 1),
            graduation_fee=child_data.get('graduation_fee', 0),
            marriage_cost=child_data.get('marriage_cost', 0),
            marriage_age=child_data.get('marriage_age', 25)  # Default marriage age 25
        ))
    
    return RetirementParams(
        current_age=config['current_age'],
        retirement_age=config['retirement_age'],
        life_expectancy=config['life_expectancy'],
        current_corpus=config['current_corpus'],
        pre_ret_return=config['pre_retirement_return'] / 100,  # Convert % to decimal
        post_ret_return=config['post_retirement_return'] / 100,
        inflation=config['inflation'] / 100,
        monthly_expenses=config['monthly_expenses'],
        children=children
    )

def save_results(projections: list, output_dir: str = 'output') -> Dict[str, str]:
    """Save projections to CSV and Excel files."""
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create DataFrame
    df = pd.DataFrame(projections)
    
    # Generate filenames with timestamp
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    csv_path = output_path / f'retirement_plan_{timestamp}.csv'
    excel_path = output_path / f'retirement_plan_{timestamp}.xlsx'
    
    # Save files
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False, engine='openpyxl')
    
    return {
        'csv': str(csv_path),
        'excel': str(excel_path)
    }

def get_user_input() -> Dict[str, Any]:
    """Get user input interactively."""
    print("\n=== Retirement Planning Input ===")
    
    # Basic information
    current_age = int(input("Current age: "))
    retirement_age = int(input("Expected retirement age: "))
    life_expectancy = int(input("Life expectancy age: "))
    current_corpus = float(input("Current corpus (savings/investments): "))
    
    # Financial parameters
    pre_ret_return = float(input("Expected pre-retirement return (% p.a.): "))
    post_ret_return = float(input("Expected post-retirement return (% p.a.): "))
    inflation = float(input("Expected inflation (% p.a.): "))
    monthly_expenses = float(input("Current monthly household expenses: "))
    
    # Children information
    children = []
    while True:
        add_child = input("\nAdd a child? (y/n): ").lower()
        if add_child != 'y':
            break
            
        print(f"\nChild {len(children) + 1} Details:")
        child = {
            'current_age': int(input("  Current age: ")),
            'school_fee': float(input("  Annual school fee today: ")),
            'school_fee_increase': float(input("  Expected annual school fee increase (%): ")),
            'fee_increase_frequency': int(input("  Frequency of fee increase (years): ")),
            'graduation_fee': float(input("  Total graduation fee today: ")),
            'marriage_cost': float(input("  Expected marriage cost today: ")),
            'marriage_age': int(input("  Expected marriage age: "))
        }
        children.append(child)
    
    return {
        'current_age': current_age,
        'retirement_age': retirement_age,
        'life_expectancy': life_expectancy,
        'current_corpus': current_corpus,
        'pre_retirement_return': pre_ret_return,
        'post_retirement_return': post_ret_return,
        'inflation': inflation,
        'monthly_expenses': monthly_expenses,
        'children': children
    }
