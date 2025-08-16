#!/usr/bin/env python3
"""
Retirement Planning Calculator

This application helps users plan their retirement by projecting their financial future
based on current savings, expected returns, inflation, and major life expenses.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from retirement_planner.io_handlers import (
    load_config, parse_config, get_user_input, save_results
)
from retirement_planner.calculations import generate_yearly_projections
from retirement_planner.visualization import (
    plot_retirement_projections, plot_expense_breakdown
)

def main():
    """Main entry point for the retirement planning application."""
    parser = argparse.ArgumentParser(description='Retirement Planning Calculator')
    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to configuration file (JSON or YAML)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='output',
        help='Directory to save output files (default: output/)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        if args.config:
            config = load_config(args.config)
            params = parse_config(config)
        else:
            print("\n=== Retirement Planning Calculator ===")
            print("No configuration file provided. Please enter your details manually.\n")
            user_data = get_user_input()
            params = parse_config(user_data)
        
        # Generate projections
        print("\nGenerating retirement projections...")
        projections = generate_yearly_projections(params)
        
        if not projections:
            print("Error: No projections were generated.")
            return 1
        
        # Save results
        print("Saving results...")
        output_files = save_results(projections, args.output_dir)
        
        # Generate visualizations
        print("Generating visualizations...")
        plot_retirement_projections(projections, args.output_dir)
        plot_expense_breakdown(projections, args.output_dir)
        
        # Print summary
        print("\n=== Retirement Planning Complete ===")
        print(f"Projections saved to: {output_files['csv']}")
        print(f"Excel file: {output_files['excel']}")
        print(f"Visualizations saved in: {args.output_dir}")
        
        # Print key metrics
        final_year = projections[-1]
        print(f"\nFinal Corpus at Age {final_year['age']}: ₹{final_year['corpus_end']:,.2f}")
        
        # Check for potential shortfall
        if final_year['corpus_end'] <= 0 and final_year['age'] < params.life_expectancy:
            print("\n⚠️  WARNING: Your corpus is projected to be depleted before life expectancy!")
            print(f"   Shortfall occurs at age {final_year['age']} (expected to live until {params.life_expectancy})")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
