# Retirement Planning Calculator

A comprehensive Python application for generating detailed retirement projections based on your financial situation, expected returns, and major life expenses.

## Features

- Interactive command-line interface for easy input
- Support for JSON/YAML configuration files
- Detailed year-by-year financial projections
- Multiple output formats (CSV, Excel)
- Visualizations of corpus growth and expense breakdowns
- Handles multiple children with customizable education and marriage expenses
- Accounts for inflation and different pre/post-retirement returns

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/RetirementPlanner.git
   cd RetirementPlanner
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Interactive Mode

Run the application without any arguments to use the interactive mode:

```bash
python main.py
```

The application will prompt you for all the necessary inputs.

### Using a Configuration File

You can also provide a configuration file in JSON or YAML format:

```bash
python main.py -c config.json
```

Example `config.json`:

```json
{
    "current_age": 35,
    "retirement_age": 60,
    "life_expectancy": 90,
    "current_corpus": 5000000,
    "pre_retirement_return": 10.0,
    "post_retirement_return": 7.0,
    "inflation": 6.0,
    "monthly_expenses": 50000,
    "children": [
        {
            "current_age": 5,
            "school_fee": 150000,
            "school_fee_increase": 8.0,
            "fee_increase_frequency": 2,
            "graduation_fee": 1000000,
            "marriage_cost": 5000000,
            "marriage_age": 28
        }
    ]
}
```

### Output

The application will generate the following files in the `output` directory (or a custom directory specified with `-o`):

- `retirement_plan_YYYYMMDD_HHMMSS.csv` - Detailed year-by-year projections
- `retirement_plan_YYYYMMDD_HHMMSS.xlsx` - Same data in Excel format
- `retirement_projection.png` - Visualization of corpus vs. expenses
- `expense_breakdown.png` - Stacked area chart of expense categories

## Project Structure

- `main.py` - Command-line interface and main entry point
- `retirement_planner/` - Core package
  - `__init__.py` - Package initialization
  - `models.py` - Data models and classes
  - `calculations.py` - Core calculation logic
  - `io_handlers.py` - Input/output operations
  - `visualization.py` - Plotting functions
- `requirements.txt` - Python dependencies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
