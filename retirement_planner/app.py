from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import os
import json
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename

# Import the retirement planning modules
from retirement_planner.calculations import generate_yearly_projections
from retirement_planner.io_handlers import parse_config, save_results
from retirement_planner.visualization import plot_retirement_projections, plot_expense_breakdown
from retirement_planner.models import RetirementParams, Child

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Add MIME type for .js files
@app.after_request
def add_header(response):
    if response.mimetype == 'application/javascript':
        response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        
        # Parse input data
        params = {
            'current_age': int(data['currentAge']),
            'retirement_age': int(data['retirementAge']),
            'life_expectancy': int(data['lifeExpectancy']),
            'current_corpus': float(data['currentCorpus']),
            'pre_retirement_return': float(data['preRetReturn']),
            'post_retirement_return': float(data['postRetReturn']),
            'inflation': float(data['inflation']),
            'monthly_expenses': float(data['monthlyExpenses']),
            'children': []
        }
        
        # Add children data if any
        for child_data in data.get('children', []):
            child = {
                'current_age': int(child_data['age']),
                'school_fee': float(child_data.get('schoolFee', 0)),
                'school_fee_increase': float(child_data.get('schoolFeeIncrease', 0)),
                'fee_increase_frequency': int(child_data.get('feeIncreaseFreq', 1)),
                'graduation_fee': float(child_data.get('graduationFee', 0)),
                'marriage_cost': float(child_data.get('marriageCost', 0)),
                'marriage_age': int(child_data.get('marriageAge', 25))
            }
            params['children'].append(child)
        
        # Generate projections
        retirement_params = parse_config(params)
        projections = generate_yearly_projections(retirement_params)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_files = save_results(projections, app.config['OUTPUT_FOLDER'])
        
        # Generate visualizations
        plot_retirement_projections(projections, app.config['OUTPUT_FOLDER'])
        plot_expense_breakdown(projections, app.config['OUTPUT_FOLDER'])
        
        return jsonify({
            'status': 'success',
            'projections': projections,
            'downloads': {
                'csv': url_for('download_file', filename=os.path.basename(output_files['csv'])),
                'excel': url_for('download_file', filename=os.path.basename(output_files['excel'])),
                'chart': url_for('static', filename='images/chart.png')
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['OUTPUT_FOLDER'],
        filename,
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)
