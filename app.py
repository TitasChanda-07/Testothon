from flask import Flask, render_template, request, jsonify
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from collections import Counter, defaultdict
import re

app = Flask(__name__)

class TestFailureDashboard:
    def __init__(self):
        self.training_data = []
        self.test_data = []
        self.combined_data = []
        self.load_data()
        
    def load_data(self):
        """Load training and test data from JSONL files"""
        try:
            print(f"Current working directory: {os.getcwd()}")
            print(f"Looking for data files in: {os.path.abspath('data')}")
            
            # Load training data
            training_file = 'data/TrainingData.jsonl'
            if os.path.exists(training_file):
                print(f"Found training file: {training_file}")
                with open(training_file, 'r', encoding='utf-8') as f:
                    self.training_data = [json.loads(line.strip()) for line in f if line.strip()]
                print(f"Loaded {len(self.training_data)} training records")
            else:
                print(f"Training file not found: {training_file}")
            
            # Load test data
            test_file = 'data/TestData.jsonl'
            if os.path.exists(test_file):
                print(f"Found test file: {test_file}")
                with open(test_file, 'r', encoding='utf-8') as f:
                    self.test_data = [json.loads(line.strip()) for line in f if line.strip()]
                print(f"Loaded {len(self.test_data)} test records")
            else:
                print(f"Test file not found: {test_file}")
            
            # Combine all data for analysis
            self.combined_data = self.training_data + self.test_data
            print(f"Combined data: {len(self.combined_data)} total records")
            
            if self.combined_data:
                # Print sample data for debugging
                sample = self.combined_data[0]
                print(f"Sample record keys: {list(sample.keys())}")
                print(f"Sample environment: {sample.get('environment', 'N/A')}")
                print(f"Sample module: {sample.get('module', 'N/A')}")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            import traceback
            traceback.print_exc()
    
    def get_summary_stats(self):
        """Get summary statistics for the dashboard"""
        if not self.combined_data:
            return {}
        
        # Basic counts
        total_failures = len(self.combined_data)
        training_count = len(self.training_data)
        test_count = len(self.test_data)
        
        # Environment distribution
        environments = Counter(record.get('environment', 'Unknown') for record in self.combined_data)
        
        # Module distribution
        modules = Counter(record.get('module', 'Unknown') for record in self.combined_data)
        
        # Failure type distribution
        failure_types = Counter(record.get('failure_type', 'Unknown') for record in self.combined_data)
        
        # Status distribution
        status_dist = Counter(record.get('status', 'Unknown') for record in self.combined_data)
        
        # Time-based analysis
        timestamps = [record.get('timestamp') for record in self.combined_data if record.get('timestamp')]
        date_range = self.get_date_range(timestamps)
        
        return {
            'total_failures': total_failures,
            'training_count': training_count,
            'test_count': test_count,
            'environments': dict(environments),
            'modules': dict(modules),
            'failure_types': dict(failure_types),
            'status_distribution': dict(status_dist),
            'date_range': date_range
        }
    
    def get_date_range(self, timestamps):
        """Calculate date range from timestamps"""
        if not timestamps:
            return {'start': 'No Data', 'end': 'No Data', 'days': 0}
        
        try:
            dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps if ts]
            if dates:
                start_date = min(dates)
                end_date = max(dates)
                days_diff = (end_date - start_date).days
                return {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d'),
                    'days': days_diff
                }
        except Exception as e:
            print(f"Error parsing dates: {e}")
        
        return {'start': 'No Data', 'end': 'No Data', 'days': 0}
    
    def search_failures(self, query='', test_id='', environment='', module='', failure_type='', error_message=''):
        """Search and filter failures based on criteria"""
        filtered_data = self.combined_data.copy()
        
        # Apply filters
        if test_id and test_id != 'All':
            filtered_data = [r for r in filtered_data if r.get('test_id', '').lower() == test_id.lower()]
        
        if environment and environment != 'All':
            filtered_data = [r for r in filtered_data if r.get('environment', '').lower() == environment.lower()]
        
        if module and module != 'All':
            filtered_data = [r for r in filtered_data if r.get('module', '').lower() == module.lower()]
        
        if failure_type and failure_type != 'All':
            filtered_data = [r for r in filtered_data if r.get('failure_type', '').lower() == failure_type.lower()]
        
        if error_message and error_message != 'All':
            # For error message, do a partial match
            filtered_data = [r for r in filtered_data if error_message.lower() in r.get('error_message', '').lower()]
        
        # Apply text search
        if query:
            query_lower = query.lower()
            filtered_data = [
                r for r in filtered_data
                if any(query_lower in str(r.get(field, '')).lower() 
                      for field in ['test_id', 'error_message', 'expected_behavior', 'actual_behavior', 'correlation_id'])
            ]
        
        return filtered_data
    
    def get_failure_trends(self, days=30):
        """Get failure trends over time"""
        if not self.combined_data:
            return {}
        
        # Group failures by date
        daily_failures = defaultdict(int)
        failure_type_trends = defaultdict(lambda: defaultdict(int))
        
        for record in self.combined_data:
            timestamp = record.get('timestamp')
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    daily_failures[date.isoformat()] += 1
                    
                    failure_type = record.get('failure_type', 'Unknown')
                    failure_type_trends[date.isoformat()][failure_type] += 1
                except Exception:
                    continue
        
        return {
            'daily_failures': dict(daily_failures),
            'failure_type_trends': dict(failure_type_trends)
        }
    
    def get_defect_correlation_stats(self):
        """Get statistics about defect correlations"""
        correlated_count = 0
        correlation_scores = []
        
        for record in self.combined_data:
            if record.get('correlation_id'):
                correlated_count += 1
            
            # Check if there are correlated defects (from historical analysis)
            correlated_defects = record.get('correlated_defects', [])
            if correlated_defects:
                for defect in correlated_defects:
                    score = defect.get('similarity_score', 0)
                    if score > 0:
                        correlation_scores.append(score)
        
        avg_correlation = sum(correlation_scores) / len(correlation_scores) if correlation_scores else 0
        
        return {
            'total_records': len(self.combined_data),
            'correlated_count': correlated_count,
            'correlation_rate': (correlated_count / len(self.combined_data) * 100) if self.combined_data else 0,
            'avg_correlation_score': avg_correlation,
            'high_correlation_count': sum(1 for score in correlation_scores if score >= 0.8)
        }

# Initialize dashboard
dashboard = TestFailureDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    summary = dashboard.get_summary_stats()
    return render_template('dashboard.html', summary=summary)

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary statistics"""
    return jsonify(dashboard.get_summary_stats())

@app.route('/api/search')
def api_search():
    """API endpoint for searching and filtering failures"""
    query = request.args.get('query', '')
    test_id = request.args.get('test_id', '')
    environment = request.args.get('environment', '')
    module = request.args.get('module', '')
    failure_type = request.args.get('failure_type', '')
    error_message = request.args.get('error_message', '')
    
    results = dashboard.search_failures(query, test_id, environment, module, failure_type, error_message)
    return jsonify(results)

@app.route('/api/trends')
def api_trends():
    """API endpoint for failure trends"""
    days = request.args.get('days', 30, type=int)
    trends = dashboard.get_failure_trends(days)
    return jsonify(trends)

@app.route('/api/correlations')
def api_correlations():
    """API endpoint for defect correlation statistics"""
    return jsonify(dashboard.get_defect_correlation_stats())

@app.route('/api/filters')
def api_filters():
    """API endpoint to get available filter options"""
    # Force reload data if empty
    if not dashboard.combined_data:
        dashboard.load_data()
    
    # If still no data, return sample data to demonstrate functionality
    if not dashboard.combined_data:
        print("No data loaded, returning sample values for demonstration")
        return jsonify({
            'test_ids': ['_Test_1', '_Test_2', '_Test_3', 'test_checkout_creates_order', 'test_search_results_valid_keyword'],
            'environments': ['QA', 'UAT', 'PreProd', 'Staging'],
            'modules': ['Analytics & Reporting', 'Order Management', 'Notifications & Messaging', 'Product Catalog', 'Promotions & Discounts'],
            'failure_types': ['Backend Service Bug', 'Configuration Error', 'Authentication Failure', 'Data Integrity Issue', 'Integration Timeout'],
            'error_messages': ['Simulated symptom related to Backend Service Bug', 'Unhandled exception in request handler', 'Feature flag misconfigured for environment', 'OAuth flow completed but user not authorized', 'Mismatched schema caused invalid record']
        })
    
    # Get all unique values from the combined data
    test_ids = sorted(set(r.get('test_id', 'Unknown') for r in dashboard.combined_data))
    environments = sorted(set(r.get('environment', 'Unknown') for r in dashboard.combined_data if r.get('environment')))
    modules = sorted(set(r.get('module', 'Unknown') for r in dashboard.combined_data if r.get('module')))
    failure_types = sorted(set(r.get('failure_type', 'Unknown') for r in dashboard.combined_data if r.get('failure_type')))
    error_messages = sorted(set(r.get('error_message', '')[:100] + '...' if len(r.get('error_message', '')) > 100 else r.get('error_message', '') 
                               for r in dashboard.combined_data if r.get('error_message')))[:20]  # Limit to top 20 error messages
    
    return jsonify({
        'test_ids': test_ids,
        'environments': environments,
        'modules': modules,
        'failure_types': failure_types,
        'error_messages': error_messages
    })

@app.route('/api/export')
def api_export():
    """API endpoint to export filtered data as JSON"""
    query = request.args.get('query', '')
    test_id = request.args.get('test_id', '')
    environment = request.args.get('environment', '')
    module = request.args.get('module', '')
    failure_type = request.args.get('failure_type', '')
    error_message = request.args.get('error_message', '')
    
    results = dashboard.search_failures(query, test_id, environment, module, failure_type, error_message)
    
    # Save to reports directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'filtered_failures_{timestamp}.json'
    filepath = os.path.join('reports', filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'status': 'success',
        'filename': filename,
        'count': len(results),
        'filepath': filepath
    })

if __name__ == '__main__':
    print("="*60)
    print("TEST FAILURE ANALYSIS DASHBOARD")
    print("="*60)
    
    # Force reload data
    dashboard.load_data()
    
    print(f"Training data: {len(dashboard.training_data)} records")
    print(f"Test data: {len(dashboard.test_data)} records")
    print(f"Total failures: {len(dashboard.combined_data)} records")
    
    if dashboard.combined_data:
        # Show sample unique values
        environments = set(r.get('environment') for r in dashboard.combined_data if r.get('environment'))
        modules = set(r.get('module') for r in dashboard.combined_data if r.get('module'))
        print(f"Sample environments: {sorted(list(environments))[:5]}")
        print(f"Sample modules: {sorted(list(modules))[:5]}")
    
    print("="*60)
    print("Starting dashboard server...")
    print("Dashboard available at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 