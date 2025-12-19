from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from ado_client import ADOClient

app = Flask(__name__)

class ADODashboard:
    """Azure DevOps Dashboard for hackathon test data"""
    
    def __init__(self):
        self.ado_client = ADOClient()
        self.dashboard_data = {}
        self.last_refresh = None
        
    def refresh_data(self) -> Dict[str, Any]:
        """Refresh data from ADO"""
        print("Refreshing ADO data...")
        try:
            self.dashboard_data = self.ado_client.get_dashboard_data()
            self.last_refresh = datetime.now()
            
            # Save data locally for faster access
            with open('data/ado_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.dashboard_data, f, indent=2, ensure_ascii=False)
            
            return self.dashboard_data
            
        except Exception as e:
            print(f"Error refreshing ADO data: {e}")
            # Try to load from cache
            return self.load_cached_data()
    
    def load_cached_data(self) -> Dict[str, Any]:
        """Load cached data if available"""
        try:
            if os.path.exists('data/ado_data.json'):
                with open('data/ado_data.json', 'r', encoding='utf-8') as f:
                    self.dashboard_data = json.load(f)
                print("Loaded cached ADO data")
                return self.dashboard_data
        except Exception as e:
            print(f"Error loading cached data: {e}")
        
        # Return sample data if no cache available
        return self.get_sample_data()
    
    def get_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for demonstration"""
        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'organization': 'CSGDevOpsAutomation',
                'project': 'DWMS',
                'search_tag': 'hackathon'
            },
            'test_plans': [
                {
                    'id': '108014',
                    'name': 'Hackathon Test Plan',
                    'state': 'Active',
                    'description': 'Test plan for hackathon projects'
                }
            ],
            'test_results': [
                {
                    'id': '1001',
                    'testCaseTitle': 'Login Functionality Test',
                    'outcome': 'Passed',
                    'state': 'Completed',
                    'priority': 'High',
                    'automatedTestName': 'test_login_hackathon',
                    'startedDate': '2025-09-18T10:00:00Z',
                    'completedDate': '2025-09-18T10:05:00Z',
                    'tags': ['hackathon', 'login', 'authentication']
                },
                {
                    'id': '1002',
                    'testCaseTitle': 'Data Validation Test',
                    'outcome': 'Failed',
                    'state': 'Completed',
                    'priority': 'Medium',
                    'automatedTestName': 'test_data_validation_hackathon',
                    'startedDate': '2025-09-18T10:10:00Z',
                    'completedDate': '2025-09-18T10:15:00Z',
                    'tags': ['hackathon', 'data', 'validation'],
                    'errorMessage': 'Data validation failed for user input'
                },
                {
                    'id': '1003',
                    'testCaseTitle': 'API Integration Test',
                    'outcome': 'Passed',
                    'state': 'Completed',
                    'priority': 'High',
                    'automatedTestName': 'test_api_integration_hackathon',
                    'startedDate': '2025-09-18T10:20:00Z',
                    'completedDate': '2025-09-18T10:25:00Z',
                    'tags': ['hackathon', 'api', 'integration']
                }
            ],
            'hackathon_items': [
                {
                    'id': '2001',
                    'fields': {
                        'System.Id': '2001',
                        'System.Title': 'Implement hackathon dashboard',
                        'System.State': 'Active',
                        'System.WorkItemType': 'Task',
                        'System.Tags': 'hackathon; dashboard; development',
                        'System.CreatedDate': '2025-09-15T09:00:00Z',
                        'System.ChangedDate': '2025-09-18T11:00:00Z'
                    }
                },
                {
                    'id': '2002',
                    'fields': {
                        'System.Id': '2002',
                        'System.Title': 'Fix authentication bug in hackathon app',
                        'System.State': 'Resolved',
                        'System.WorkItemType': 'Bug',
                        'System.Tags': 'hackathon; authentication; bug',
                        'System.CreatedDate': '2025-09-16T14:30:00Z',
                        'System.ChangedDate': '2025-09-17T16:45:00Z'
                    }
                }
            ],
            'summary': {
                'total_test_plans': 1,
                'total_test_results': 3,
                'passed_tests': 2,
                'failed_tests': 1,
                'test_pass_rate': 66.67,
                'total_hackathon_items': 2,
                'work_item_types': {'Task': 1, 'Bug': 1},
                'work_item_states': {'Active': 1, 'Resolved': 1}
            }
        }
    
    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data (cached or fresh)"""
        if not self.dashboard_data:
            # Try to load cached data first
            self.dashboard_data = self.load_cached_data()
        
        return self.dashboard_data
    
    def get_test_results_summary(self) -> Dict[str, Any]:
        """Get test results summary for charts"""
        data = self.get_data()
        test_results = data.get('test_results', [])
        
        # Outcome distribution
        outcomes = {}
        priorities = {}
        states = {}
        
        for result in test_results:
            outcome = result.get('outcome', 'Unknown')
            priority = result.get('priority', 'Unknown')
            state = result.get('state', 'Unknown')
            
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            priorities[priority] = priorities.get(priority, 0) + 1
            states[state] = states.get(state, 0) + 1
        
        return {
            'outcomes': outcomes,
            'priorities': priorities,
            'states': states,
            'total_tests': len(test_results)
        }
    
    def get_hackathon_items_summary(self) -> Dict[str, Any]:
        """Get hackathon work items summary"""
        data = self.get_data()
        hackathon_items = data.get('hackathon_items', [])
        
        work_types = {}
        states = {}
        
        for item in hackathon_items:
            fields = item.get('fields', {})
            work_type = fields.get('System.WorkItemType', 'Unknown')
            state = fields.get('System.State', 'Unknown')
            
            work_types[work_type] = work_types.get(work_type, 0) + 1
            states[state] = states.get(state, 0) + 1
        
        return {
            'work_types': work_types,
            'states': states,
            'total_items': len(hackathon_items)
        }

# Initialize dashboard
ado_dashboard = ADODashboard()

@app.route('/')
def index():
    """Main ADO dashboard page"""
    data = ado_dashboard.get_data()
    summary = data.get('summary', {})
    return render_template('ado_dashboard.html', 
                         summary=summary, 
                         metadata=data.get('metadata', {}))

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary statistics"""
    data = ado_dashboard.get_data()
    return jsonify(data.get('summary', {}))

@app.route('/api/test-plans')
def api_test_plans():
    """API endpoint for test plans"""
    data = ado_dashboard.get_data()
    return jsonify(data.get('test_plans', []))

@app.route('/api/test-results')
def api_test_results():
    """API endpoint for test results"""
    data = ado_dashboard.get_data()
    return jsonify(data.get('test_results', []))

@app.route('/api/hackathon-items')
def api_hackathon_items():
    """API endpoint for hackathon work items"""
    data = ado_dashboard.get_data()
    return jsonify(data.get('hackathon_items', []))

@app.route('/api/test-results-summary')
def api_test_results_summary():
    """API endpoint for test results summary"""
    return jsonify(ado_dashboard.get_test_results_summary())

@app.route('/api/hackathon-summary')
def api_hackathon_summary():
    """API endpoint for hackathon items summary"""
    return jsonify(ado_dashboard.get_hackathon_items_summary())

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh data from ADO"""
    try:
        data = ado_dashboard.refresh_data()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'summary': data.get('summary', {})
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/search')
def api_search():
    """API endpoint for searching items"""
    query = request.args.get('query', '').lower()
    item_type = request.args.get('type', 'all')
    
    data = ado_dashboard.get_data()
    results = []
    
    # Search test results
    if item_type in ['all', 'tests']:
        for result in data.get('test_results', []):
            if query in str(result.get('testCaseTitle', '')).lower() or \
               query in str(result.get('automatedTestName', '')).lower():
                results.append({**result, 'item_type': 'test_result'})
    
    # Search hackathon items
    if item_type in ['all', 'workitems']:
        for item in data.get('hackathon_items', []):
            fields = item.get('fields', {})
            title = fields.get('System.Title', '')
            if query in title.lower():
                results.append({**item, 'item_type': 'work_item'})
    
    return jsonify(results)

if __name__ == '__main__':
    print("="*60)
    print("AZURE DEVOPS HACKATHON DASHBOARD")
    print("="*60)
    print(f"Organization: {ado_dashboard.ado_client.config['ORG']}")
    print(f"Project: {ado_dashboard.ado_client.config['PROJECT']}")
    print(f"Search Tag: {ado_dashboard.ado_client.config.get('SEARCH_TAG', 'hackathon')}")
    print("="*60)
    print("Loading initial data...")
    
    # Load initial data
    data = ado_dashboard.get_data()
    summary = data.get('summary', {})
    
    print(f"Test Plans: {summary.get('total_test_plans', 0)}")
    print(f"Test Results: {summary.get('total_test_results', 0)}")
    print(f"Hackathon Items: {summary.get('total_hackathon_items', 0)}")
    print(f"Test Pass Rate: {summary.get('test_pass_rate', 0)}%")
    
    print("="*60)
    print("Starting ADO dashboard server...")
    print("Dashboard available at: http://localhost:5001")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 