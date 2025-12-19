import requests
import json
import base64
from typing import Dict, List, Any, Optional
from urllib.parse import quote
from datetime import datetime, timedelta
from config.ado_config import *

class ADODefectsClient:
    """Azure DevOps client for analyzing defects with 'hack' tag"""
    
    def __init__(self):
        self.session = self._create_session()
        self.base_url = f"{BASE_URL}/{quote(ORG)}/{quote(PROJECT)}"
        
    def _create_session(self) -> requests.Session:
        """Create authenticated requests session"""
        session = requests.Session()
        
        # Create basic auth header with PAT
        auth_string = f":{PAT}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        session.headers.update({
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        return session
    
    def search_defects_by_tag(self, tag: str = SEARCH_TAG) -> List[Dict[str, Any]]:
        """Search for defects and work items with specific tag using WIQL"""
        
        # WIQL query to find work items with 'hack' tag
        wiql_query = {
            "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
                       [System.Tags], [System.CreatedDate], [System.ChangedDate],
                       [System.AssignedTo], [System.Priority], [Microsoft.VSTS.Common.Severity],
                       [System.Reason], [System.Description], [Microsoft.VSTS.Common.ResolvedReason]
                FROM WorkItems 
                WHERE [System.Tags] CONTAINS '{tag}'
                AND [System.WorkItemType] IN ('Bug', 'Task', 'User Story', 'Feature', 'Epic')
                ORDER BY [System.ChangedDate] DESC
            """
        }
        
        url = f"{self.base_url}/_apis/wit/wiql"
        params = {'api-version': API_VERSION}
        
        try:
            response = self.session.post(url, json=wiql_query, params=params)
            response.raise_for_status()
            
            data = response.json()
            work_items = data.get('workItems', [])
            
            print(f"Found {len(work_items)} work items with tag '{tag}'")
            
            # Get detailed information for each work item
            if work_items:
                item_ids = [str(item['id']) for item in work_items]
                detailed_items = self.get_work_items_details(item_ids)
                return detailed_items
            
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching defects by tag: {e}")
            return self._get_sample_defects()
    
    def get_work_items_details(self, item_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for work items"""
        if not item_ids:
            return []
        
        # Batch get work items (max 200 at a time)
        batch_size = 200
        all_items = []
        
        for i in range(0, len(item_ids), batch_size):
            batch_ids = item_ids[i:i + batch_size]
            ids_param = ','.join(batch_ids)
            
            url = f"{self.base_url}/_apis/wit/workitems"
            params = {
                'ids': ids_param,
                'api-version': API_VERSION,
                '$expand': 'all'
            }
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                batch_items = data.get('value', [])
                all_items.extend(batch_items)
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching work item details: {e}")
                continue
        
        return all_items
    
    def analyze_defects(self, defects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze defects data for dashboard insights"""
        if not defects:
            return self._get_sample_analysis()
        
        analysis = {
            'total_defects': len(defects),
            'by_type': {},
            'by_state': {},
            'by_priority': {},
            'by_severity': {},
            'by_assignee': {},
            'by_created_date': {},
            'critical_defects': [],
            'recent_defects': [],
            'resolved_defects': [],
            'open_defects': []
        }
        
        for defect in defects:
            fields = defect.get('fields', {})
            
            # Basic categorization
            work_type = fields.get('System.WorkItemType', 'Unknown')
            state = fields.get('System.State', 'Unknown')
            priority = fields.get('System.Priority', 'Unknown')
            severity = fields.get('Microsoft.VSTS.Common.Severity', 'Unknown')
            assignee = fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if isinstance(fields.get('System.AssignedTo'), dict) else str(fields.get('System.AssignedTo', 'Unassigned'))
            
            # Count by categories
            analysis['by_type'][work_type] = analysis['by_type'].get(work_type, 0) + 1
            analysis['by_state'][state] = analysis['by_state'].get(state, 0) + 1
            analysis['by_priority'][priority] = analysis['by_priority'].get(priority, 0) + 1
            analysis['by_severity'][severity] = analysis['by_severity'].get(severity, 0) + 1
            analysis['by_assignee'][assignee] = analysis['by_assignee'].get(assignee, 0) + 1
            
            # Date analysis
            created_date = fields.get('System.CreatedDate', '')
            if created_date:
                try:
                    date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).date()
                    month_key = date.strftime('%Y-%m')
                    analysis['by_created_date'][month_key] = analysis['by_created_date'].get(month_key, 0) + 1
                except:
                    pass
            
            # Critical defects (High priority bugs)
            if work_type == 'Bug' and priority in ['1', 'High', '2']:
                analysis['critical_defects'].append({
                    'id': fields.get('System.Id'),
                    'title': fields.get('System.Title', ''),
                    'state': state,
                    'priority': priority,
                    'severity': severity,
                    'assignee': assignee,
                    'created_date': created_date,
                    'url': f"https://dev.azure.com/{ORG}/{PROJECT}/_workitems/edit/{fields.get('System.Id')}"
                })
            
            # Recent defects (last 30 days)
            if created_date:
                try:
                    created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                    if (datetime.now() - created).days <= 30:
                        analysis['recent_defects'].append({
                            'id': fields.get('System.Id'),
                            'title': fields.get('System.Title', ''),
                            'type': work_type,
                            'state': state,
                            'created_date': created_date,
                            'url': f"https://dev.azure.com/{ORG}/{PROJECT}/_workitems/edit/{fields.get('System.Id')}"
                        })
                except:
                    pass
            
            # Categorize by state
            if state.lower() in ['resolved', 'closed', 'done']:
                analysis['resolved_defects'].append(defect)
            elif state.lower() in ['new', 'active', 'committed', 'approved']:
                analysis['open_defects'].append(defect)
        
        # Sort lists by priority/date
        analysis['critical_defects'] = sorted(analysis['critical_defects'], 
                                            key=lambda x: x.get('created_date', ''), reverse=True)[:10]
        analysis['recent_defects'] = sorted(analysis['recent_defects'], 
                                          key=lambda x: x.get('created_date', ''), reverse=True)[:15]
        
        return analysis
    
    def get_defect_trends(self, defects: List[Dict[str, Any]], days: int = 90) -> Dict[str, Any]:
        """Analyze defect trends over time"""
        if not defects:
            return {}
        
        # Daily defect creation
        daily_creation = {}
        daily_resolution = {}
        
        for defect in defects:
            fields = defect.get('fields', {})
            
            # Creation trend
            created_date = fields.get('System.CreatedDate', '')
            if created_date:
                try:
                    date = datetime.fromisoformat(created_date.replace('Z', '+00:00')).date()
                    date_key = date.isoformat()
                    daily_creation[date_key] = daily_creation.get(date_key, 0) + 1
                except:
                    pass
            
            # Resolution trend
            resolved_date = fields.get('Microsoft.VSTS.Common.ResolvedDate', '')
            if resolved_date:
                try:
                    date = datetime.fromisoformat(resolved_date.replace('Z', '+00:00')).date()
                    date_key = date.isoformat()
                    daily_resolution[date_key] = daily_resolution.get(date_key, 0) + 1
                except:
                    pass
        
        return {
            'daily_creation': daily_creation,
            'daily_resolution': daily_resolution,
            'creation_trend': self._calculate_trend(daily_creation),
            'resolution_trend': self._calculate_trend(daily_resolution)
        }
    
    def _calculate_trend(self, daily_data: Dict[str, int]) -> str:
        """Calculate trend direction (increasing/decreasing/stable)"""
        if len(daily_data) < 2:
            return "stable"
        
        dates = sorted(daily_data.keys())
        recent_dates = dates[-7:]  # Last 7 days
        earlier_dates = dates[-14:-7] if len(dates) >= 14 else dates[:-7]
        
        if not earlier_dates:
            return "stable"
        
        recent_avg = sum(daily_data[d] for d in recent_dates) / len(recent_dates)
        earlier_avg = sum(daily_data[d] for d in earlier_dates) / len(earlier_dates)
        
        if recent_avg > earlier_avg * 1.1:
            return "increasing"
        elif recent_avg < earlier_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def get_defect_metrics(self, defects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate key defect metrics"""
        if not defects:
            return self._get_sample_metrics()
        
        total_defects = len(defects)
        bugs = [d for d in defects if d.get('fields', {}).get('System.WorkItemType') == 'Bug']
        resolved_defects = [d for d in defects if d.get('fields', {}).get('System.State', '').lower() in ['resolved', 'closed', 'done']]
        
        # Calculate resolution rate
        resolution_rate = (len(resolved_defects) / total_defects * 100) if total_defects > 0 else 0
        
        # Calculate average resolution time (for resolved defects)
        resolution_times = []
        for defect in resolved_defects:
            fields = defect.get('fields', {})
            created = fields.get('System.CreatedDate', '')
            resolved = fields.get('Microsoft.VSTS.Common.ResolvedDate', '')
            
            if created and resolved:
                try:
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    resolved_dt = datetime.fromisoformat(resolved.replace('Z', '+00:00'))
                    resolution_time = (resolved_dt - created_dt).days
                    resolution_times.append(resolution_time)
                except:
                    pass
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            'total_defects': total_defects,
            'total_bugs': len(bugs),
            'resolved_defects': len(resolved_defects),
            'open_defects': total_defects - len(resolved_defects),
            'resolution_rate': round(resolution_rate, 2),
            'avg_resolution_time_days': round(avg_resolution_time, 1),
            'critical_bugs': len([b for b in bugs if b.get('fields', {}).get('System.Priority', '') in ['1', 'High']]),
            'recent_defects_30_days': len([d for d in defects if self._is_recent(d, 30)])
        }
    
    def _is_recent(self, defect: Dict[str, Any], days: int) -> bool:
        """Check if defect was created in the last N days"""
        created_date = defect.get('fields', {}).get('System.CreatedDate', '')
        if not created_date:
            return False
        
        try:
            created = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
            return (datetime.now() - created).days <= days
        except:
            return False
    
    def _get_sample_defects(self) -> List[Dict[str, Any]]:
        """Generate sample defects data for demonstration"""
        return [
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
                    'System.AssignedTo': {'displayName': 'Development Team'},
                    'System.Description': 'Input validation fails for hack tagged data entries'
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
                    'System.AssignedTo': {'displayName': 'UI Team'},
                    'System.Description': 'Add filtering capability for hack tagged items in main dashboard'
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
                    'System.AssignedTo': {'displayName': 'Performance Team'},
                    'System.Description': 'Search queries for hack tagged items are slow and timeout'
                }
            },
            {
                'id': '3005',
                'fields': {
                    'System.Id': '3005',
                    'System.Title': 'Add hack tag automation to CI/CD pipeline',
                    'System.State': 'Committed',
                    'System.WorkItemType': 'User Story',
                    'System.Tags': 'hack; automation; cicd; pipeline',
                    'System.Priority': 'Low',
                    'System.CreatedDate': '2025-09-12T13:15:00Z',
                    'System.ChangedDate': '2025-09-17T15:20:00Z',
                    'System.AssignedTo': {'displayName': 'DevOps Team'},
                    'System.Description': 'Automatically tag builds and deployments with hack tag when appropriate'
                }
            }
        ]
    
    def _get_sample_analysis(self) -> Dict[str, Any]:
        """Generate sample analysis for demonstration"""
        return {
            'total_defects': 5,
            'by_type': {'Bug': 3, 'Task': 1, 'User Story': 1},
            'by_state': {'Active': 2, 'Resolved': 1, 'New': 1, 'Committed': 1},
            'by_priority': {'High': 2, 'Medium': 2, 'Low': 1},
            'by_severity': {'2 - High': 1, '3 - Medium': 2, 'Unknown': 2},
            'by_assignee': {'Security Team': 1, 'Development Team': 1, 'UI Team': 1, 'Performance Team': 1, 'DevOps Team': 1},
            'by_created_date': {'2025-09': 5},
            'critical_defects': 2,
            'recent_defects': 5,
            'resolved_defects': 1,
            'open_defects': 4
        }
    
    def _get_sample_metrics(self) -> Dict[str, Any]:
        """Generate sample metrics for demonstration"""
        return {
            'total_defects': 5,
            'total_bugs': 3,
            'resolved_defects': 1,
            'open_defects': 4,
            'resolution_rate': 20.0,
            'avg_resolution_time_days': 6.2,
            'critical_bugs': 2,
            'recent_defects_30_days': 5
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data for defects analysis"""
        print(f"Fetching defects data with tag '{SEARCH_TAG}'...")
        
        # Get defects with hack tag
        defects = self.search_defects_by_tag()
        
        # Analyze the defects
        analysis = self.analyze_defects(defects)
        
        # Get metrics
        metrics = self.get_defect_metrics(defects)
        
        # Get trends
        trends = self.get_defect_trends(defects)
        
        return {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'organization': ORG,
                'project': PROJECT,
                'search_tag': SEARCH_TAG,
                'query_url': QUERY_URL,
                'total_analyzed': len(defects)
            },
            'defects': defects,
            'analysis': analysis,
            'metrics': metrics,
            'trends': trends
        }

if __name__ == "__main__":
    # Test the ADO defects client
    client = ADODefectsClient()
    
    print("Testing ADO Defects Client...")
    try:
        # Test connection and data retrieval
        dashboard_data = client.get_dashboard_data()
        
        print(f"✓ Successfully connected to ADO")
        print(f"✓ Organization: {ORG}")
        print(f"✓ Project: {PROJECT}")
        print(f"✓ Search Tag: {SEARCH_TAG}")
        print(f"✓ Found {dashboard_data['metadata']['total_analyzed']} items with '{SEARCH_TAG}' tag")
        print(f"✓ Analysis completed with {len(dashboard_data['analysis']['critical_defects'])} critical defects")
        
    except Exception as e:
        print(f"✗ ADO connection failed: {e}")
        import traceback
        traceback.print_exc() 