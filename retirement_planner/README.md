# Retirement Planning Calculator

A comprehensive web-based application for generating detailed retirement projections based on your financial situation, expected returns, and major life expenses.

## Features

- Modern, interactive web interface
- Real-time visualization of retirement projections
- Detailed year-by-year financial projections
- Interactive charts for corpus growth and expense breakdowns
- Support for multiple children with customizable education and marriage expenses
- Accounts for inflation and different pre/post-retirement returns
- Export results to CSV and Excel formats
- Mobile-responsive design

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

## Running the Web Application

To start the Streamlit web application, run:

```bash
streamlit run streamlit_app.py
```

This will start a local web server and open the application in your default web browser. If it doesn't open automatically, you can access it at `http://localhost:8501`.

## Using the Application

1. **Basic Information**: Fill in your current age, planned retirement age, life expectancy, current savings, and monthly expenses.
2. **Investment Returns**: Set your expected pre-retirement and post-retirement returns, and the expected inflation rate.
3. **Children's Information** (Optional): Add details about your children's education and future expenses.
4. **Generate Plan**: Click the "Generate Retirement Plan" button to see your projections.
5. **Review & Download**: View the interactive charts and download the results as CSV or Excel.

## Features in Detail

### Interactive Visualizations
- **Corpus vs Expenses**: See how your retirement corpus grows over time compared to your expenses.
- **Expense Breakdown**: Visualize how different expense categories contribute to your total expenses.

### Detailed Projections
- Year-by-year breakdown of your financial situation
- Detailed expense categorization
- Corpus growth projections

### Export Options
- Download your retirement plan as CSV or Excel
- Save visualizations for offline review

## Running Tests

To run the test suite:

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Project Structure

```
retirement_planner/
├── __init__.py
├── calculations.py    # Core retirement calculation logic
├── models.py         # Data models and classes
├── io_handlers.py    # Input/output handling
├── visualization.py  # Visualization functions
└── streamlit_app.py  # Streamlit web application
```

## Running the Application

1. First, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Streamlit application:
   ```bash
   streamlit run streamlit_app.py
   ```

3. Open your web browser and navigate to `http://localhost:8501`

4. Fill in your financial details and click "Generate Retirement Plan" to see the projections.

## Output

The application will generate interactive visualizations directly in the browser, and you can download the following:

- **CSV/Excel Exports**: Detailed year-by-year projections
- **Interactive Charts**: Visualize corpus growth and expense breakdowns
- **Summary Metrics**: Key financial metrics at a glance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
