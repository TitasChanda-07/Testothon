from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from typing import Dict, List, Any
from ado_defects_client import ADODefectsClient
from config.ado_config import *

app = Flask(__name__)

class DefectsDashboard:
    """Azure DevOps Defects Dashboard for 'hack' tag analysis"""
    
    def __init__(self):
        self.ado_client = ADODefectsClient()
        self.dashboard_data = {}
        self.last_refresh = None
        
    def refresh_data(self) -> Dict[str, Any]:
        """Refresh data from ADO"""
        print("Refreshing defects data from ADO...")
        try:
            self.dashboard_data = self.ado_client.get_dashboard_data()
            self.last_refresh = datetime.now()
            
            # Save data locally for faster access
            os.makedirs('data', exist_ok=True)
            with open('data/defects_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.dashboard_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Refreshed data: {self.dashboard_data['metadata']['total_analyzed']} items")
            return self.dashboard_data
            
        except Exception as e:
            print(f"Error refreshing data: {e}")
            return self.load_cached_data()
    
    def load_cached_data(self) -> Dict[str, Any]:
        """Load cached data if available"""
        try:
            if os.path.exists('data/defects_data.json'):
                with open('data/defects_data.json', 'r', encoding='utf-8') as f:
                    self.dashboard_data = json.load(f)
                print("Loaded cached defects data")
                return self.dashboard_data
        except Exception as e:
            print(f"Error loading cached data: {e}")
        
        # Return sample data if no cache available
        return self.get_sample_dashboard_data()
    
    def get_sample_dashboard_data(self) -> Dict[str, Any]:
        """Generate sample dashboard data for demonstration"""
        sample_defects = [
            {
                'id': '3001',
                'fields': {
                    'System.Id': '3001',
                    'System.Title': 'Login authentication fails with hack tag implementation',
                    'System.State': 'Active',
                    'System.WorkItemType': 'Bug',
                    'System.Tags': 'hack; authentication; security; login',
                    'System.Priority': 'High',
                    'Microsoft.VSTS.Common.Severity': '2 - High',
                    'System.CreatedDate': '2025-09-15T10:30:00Z',
                    'System.ChangedDate': '2025-09-18T09:15:00Z',
                    'System.AssignedTo': {'displayName': 'Security Team'},
                    'System.Description': 'Authentication module fails when hack tag is processed'
                }
            },
            {
                'id': '3002',
                'fields': {
                    'System.Id': '3002',
                    'System.Title': 'Data validation error in hack feature',
                    'System.State': 'Resolved',
                    'System.WorkItemType': 'Bug',
                    'System.Tags': 'hack; data; validation; resolved',
                    'System.Priority': 'Medium',
                    'Microsoft.VSTS.Common.Severity': '3 - Medium',
                    'System.CreatedDate': '2025-09-10T14:20:00Z',
                    'System.ChangedDate': '2025-09-16T11:45:00Z',
                    'Microsoft.VSTS.Common.ResolvedDate': '2025-09-16T11:45:00Z',
                    'System.AssignedTo': {'displayName': 'Development Team'}
                }
            },
            {
                'id': '3003',
                'fields': {
                    'System.Id': '3003',
                    'System.Title': 'Implement hack tag filtering in dashboard',
                    'System.State': 'Active',
                    'System.WorkItemType': 'Task',
                    'System.Tags': 'hack; dashboard; filtering; enhancement',
                    'System.Priority': 'High',
                    'System.CreatedDate': '2025-09-17T16:00:00Z',
                    'System.ChangedDate': '2025-09-18T10:30:00Z',
                    'System.AssignedTo': {'displayName': 'UI Team'}
                }
            },
            {
                'id': '3004',
                'fields': {
                    'System.Id': '3004',
                    'System.Title': 'Performance issue with hack tag search',
                    'System.State': 'New',
                    'System.WorkItemType': 'Bug',
                    'System.Tags': 'hack; performance; search; optimization',
                    'System.Priority': 'Medium',
                    'Microsoft.VSTS.Common.Severity': '3 - Medium',
                    'System.CreatedDate': '2025-09-18T08:45:00Z',
                    'System.ChangedDate': '2025-09-18T08:45:00Z',
                    'System.AssignedTo': {'displayName': 'Performance Team'}
                }
            }
        ]
        
        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'organization': ORG,
                'project': PROJECT,
                'search_tag': SEARCH_TAG,
                'query_url': QUERY_URL,
                'total_analyzed': 4
            },
            'defects': sample_defects,
            'analysis': self.ado_client.analyze_defects(sample_defects),
            'metrics': self.ado_client.get_defect_metrics(sample_defects),
            'trends': self.ado_client.get_defect_trends(sample_defects)
        }
    
    def get_data(self) -> Dict[str, Any]:
        """Get dashboard data (cached or fresh)"""
        if not self.dashboard_data:
            self.dashboard_data = self.load_cached_data()
        
        return self.dashboard_data
    
    def search_defects(self, query: str = '', defect_type: str = '', state: str = '', priority: str = '') -> List[Dict[str, Any]]:
        """Search and filter defects"""
        data = self.get_data()
        defects = data.get('defects', [])
        
        filtered_defects = []
        
        for defect in defects:
            fields = defect.get('fields', {})
            
            # Apply filters
            if defect_type and defect_type != 'All':
                if fields.get('System.WorkItemType', '').lower() != defect_type.lower():
                    continue
            
            if state and state != 'All':
                if fields.get('System.State', '').lower() != state.lower():
                    continue
            
            if priority and priority != 'All':
                if fields.get('System.Priority', '').lower() != priority.lower():
                    continue
            
            # Apply text search
            if query:
                query_lower = query.lower()
                searchable_text = ' '.join([
                    str(fields.get('System.Title', '')),
                    str(fields.get('System.Description', '')),
                    str(fields.get('System.Tags', '')),
                    str(fields.get('System.Id', ''))
                ]).lower()
                
                if query_lower not in searchable_text:
                    continue
            
            filtered_defects.append(defect)
        
        return filtered_defects

# Initialize dashboard
defects_dashboard = DefectsDashboard()

@app.route('/')
def index():
    """Main defects dashboard page"""
    data = defects_dashboard.get_data()
    summary = data.get('metrics', {})
    metadata = data.get('metadata', {})
    return render_template('defects_dashboard.html', 
                         summary=summary, 
                         metadata=metadata)

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary metrics"""
    data = defects_dashboard.get_data()
    return jsonify(data.get('metrics', {}))

@app.route('/api/analysis')
def api_analysis():
    """API endpoint for defects analysis"""
    data = defects_dashboard.get_data()
    return jsonify(data.get('analysis', {}))

@app.route('/api/defects')
def api_defects():
    """API endpoint for defects data"""
    data = defects_dashboard.get_data()
    return jsonify(data.get('defects', []))

@app.route('/api/trends')
def api_trends():
    """API endpoint for defect trends"""
    data = defects_dashboard.get_data()
    return jsonify(data.get('trends', {}))

@app.route('/api/search')
def api_search():
    """API endpoint for searching defects"""
    query = request.args.get('query', '')
    defect_type = request.args.get('type', '')
    state = request.args.get('state', '')
    priority = request.args.get('priority', '')
    
    results = defects_dashboard.search_defects(query, defect_type, state, priority)
    return jsonify(results)

@app.route('/api/filters')
def api_filters():
    """API endpoint for filter options"""
    data = defects_dashboard.get_data()
    defects = data.get('defects', [])
    
    if not defects:
        return jsonify({
            'types': ['Bug', 'Task', 'User Story', 'Feature'],
            'states': ['Active', 'New', 'Resolved', 'Closed', 'Committed'],
            'priorities': ['High', 'Medium', 'Low'],
            'assignees': ['Security Team', 'Development Team', 'UI Team', 'Performance Team']
        })
    
    types = sorted(set(d.get('fields', {}).get('System.WorkItemType', '') for d in defects if d.get('fields', {}).get('System.WorkItemType')))
    states = sorted(set(d.get('fields', {}).get('System.State', '') for d in defects if d.get('fields', {}).get('System.State')))
    priorities = sorted(set(d.get('fields', {}).get('System.Priority', '') for d in defects if d.get('fields', {}).get('System.Priority')))
    
    assignees = []
    for d in defects:
        assignee = d.get('fields', {}).get('System.AssignedTo')
        if isinstance(assignee, dict):
            assignees.append(assignee.get('displayName', ''))
        elif assignee:
            assignees.append(str(assignee))
    assignees = sorted(set(a for a in assignees if a))
    
    return jsonify({
        'types': types,
        'states': states,
        'priorities': priorities,
        'assignees': assignees
    })

@app.route('/api/refresh')
def api_refresh():
    """API endpoint to refresh data from ADO"""
    try:
        data = defects_dashboard.refresh_data()
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'total_items': data['metadata']['total_analyzed'],
            'message': f"Refreshed {data['metadata']['total_analyzed']} defects with '{SEARCH_TAG}' tag"
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/api/export')
def api_export():
    """API endpoint to export defects data"""
    try:
        data = defects_dashboard.get_data()
        
        # Save export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'hack_defects_export_{timestamp}.json'
        filepath = os.path.join('reports', filename)
        
        os.makedirs('reports', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'filepath': filepath,
            'total_items': len(data.get('defects', [])),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("="*70)
    print("AZURE DEVOPS DEFECTS DASHBOARD - HACK TAG ANALYSIS")
    print("="*70)
    print(f"Organization: {ORG}")
    print(f"Project: {PROJECT}")
    print(f"Search Tag: {SEARCH_TAG}")
    print(f"Query URL: {QUERY_URL}")
    print("="*70)
    print("Loading defects data...")
    
    # Load initial data
    data = defects_dashboard.get_data()
    metadata = data.get('metadata', {})
    metrics = data.get('metrics', {})
    
    print(f"Total Defects: {metrics.get('total_defects', 0)}")
    print(f"Total Bugs: {metrics.get('total_bugs', 0)}")
    print(f"Critical Bugs: {metrics.get('critical_bugs', 0)}")
    print(f"Resolution Rate: {metrics.get('resolution_rate', 0)}%")
    print(f"Recent Defects (30 days): {metrics.get('recent_defects_30_days', 0)}")
    
    print("="*70)
    print("Starting defects dashboard server...")
    print(f"Dashboard available at: http://localhost:{DASHBOARD_PORT}")
    print("Press Ctrl+C to stop")
    
    app.run(debug=True, host=DASHBOARD_HOST, port=DASHBOARD_PORT) 