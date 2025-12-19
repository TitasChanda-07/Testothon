import requests
import json
import base64
from typing import Dict, List, Any, Optional
from urllib.parse import quote
import logging
from datetime import datetime, timedelta

class ADOClient:
    """Azure DevOps client for fetching test data"""
    
    def __init__(self, config_path: str = "config/ado_config.txt"):
        self.config = self._load_config(config_path)
        self.session = self._create_session()
        self.base_url = f"{self.config['BASE_URL']}/{quote(self.config['ORG'])}/{quote(self.config['PROJECT'])}"
        
    def _load_config(self, config_path: str) -> Dict[str, str]:
        """Load configuration from file"""
        config = {}
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.strip().startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        return config
    
    def _create_session(self) -> requests.Session:
        """Create authenticated requests session"""
        session = requests.Session()
        
        # Create basic auth header
        pat_token = self.config['PAT']
        auth_string = f":{pat_token}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        session.headers.update({
            'Authorization': f'Basic {encoded_auth}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        return session
    
    def get_test_plans(self) -> List[Dict[str, Any]]:
        """Get test plans from ADO"""
        url = f"{self.base_url}/_apis/test/plans"
        params = {'api-version': self.config['API_VERSION']}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            test_plans = data.get('value', [])
            
            print(f"Retrieved {len(test_plans)} test plans")
            return test_plans
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test plans: {e}")
            return []
    
    def get_test_suites(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get test suites for a specific plan"""
        url = f"{self.base_url}/_apis/test/Plans/{plan_id}/suites"
        params = {'api-version': self.config['API_VERSION']}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            test_suites = data.get('value', [])
            
            print(f"Retrieved {len(test_suites)} test suites for plan {plan_id}")
            return test_suites
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test suites: {e}")
            return []
    
    def get_test_cases_by_tag(self, tag: str = None) -> List[Dict[str, Any]]:
        """Get test cases filtered by tag"""
        if not tag:
            tag = self.config.get('SEARCH_TAG', 'hackathon')
        
        # First, get all test cases
        url = f"{self.base_url}/_apis/test/testcases"
        params = {'api-version': self.config['API_VERSION']}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            all_test_cases = data.get('value', [])
            
            # Filter by tag (this is a simplified approach)
            tagged_cases = []
            for test_case in all_test_cases:
                tags = test_case.get('tags', [])
                if any(tag.lower() in str(t).lower() for t in tags):
                    tagged_cases.append(test_case)
            
            print(f"Found {len(tagged_cases)} test cases with tag '{tag}' out of {len(all_test_cases)} total")
            return tagged_cases
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test cases: {e}")
            return []
    
    def get_test_results(self, plan_id: str = None, suite_id: str = None) -> List[Dict[str, Any]]:
        """Get test results from ADO"""
        if not plan_id:
            plan_id = self.config.get('TEST_PLAN_ID', '108014')
        if not suite_id:
            suite_id = self.config.get('TEST_SUITE_ID', '108015')
        
        url = f"{self.base_url}/_apis/test/Runs"
        params = {
            'api-version': self.config['API_VERSION'],
            'planId': plan_id,
            'includeRunDetails': 'true'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            test_runs = data.get('value', [])
            
            # Get detailed results for each run
            all_results = []
            for run in test_runs:
                run_id = run.get('id')
                if run_id:
                    run_results = self.get_test_run_results(run_id)
                    for result in run_results:
                        result['run_info'] = {
                            'run_id': run_id,
                            'run_name': run.get('name', ''),
                            'run_state': run.get('state', ''),
                            'start_date': run.get('startedDate', ''),
                            'completed_date': run.get('completedDate', '')
                        }
                    all_results.extend(run_results)
            
            print(f"Retrieved {len(all_results)} test results from {len(test_runs)} runs")
            return all_results
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching test results: {e}")
            return []
    
    def get_test_run_results(self, run_id: str) -> List[Dict[str, Any]]:
        """Get results for a specific test run"""
        url = f"{self.base_url}/_apis/test/Runs/{run_id}/results"
        params = {
            'api-version': self.config['API_VERSION'],
            'includeIterationDetails': 'true'
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('value', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching results for run {run_id}: {e}")
            return []
    
    def search_work_items_by_tag(self, tag: str = None) -> List[Dict[str, Any]]:
        """Search work items (test cases, bugs) by tag using WIQL"""
        if not tag:
            tag = self.config.get('SEARCH_TAG', 'hackathon')
        
        # WIQL query to find work items with specific tag
        wiql_query = {
            "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType], 
                       [System.Tags], [System.CreatedDate], [System.ChangedDate]
                FROM WorkItems 
                WHERE [System.Tags] CONTAINS '{tag}'
                ORDER BY [System.ChangedDate] DESC
            """
        }
        
        url = f"{self.base_url}/_apis/wit/wiql"
        params = {'api-version': self.config['API_VERSION']}
        
        try:
            response = self.session.post(url, json=wiql_query, params=params)
            response.raise_for_status()
            
            data = response.json()
            work_items = data.get('workItems', [])
            
            # Get detailed information for each work item
            detailed_items = []
            if work_items:
                item_ids = [str(item['id']) for item in work_items]
                detailed_items = self.get_work_items_details(item_ids)
            
            print(f"Found {len(detailed_items)} work items with tag '{tag}'")
            return detailed_items
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching work items by tag: {e}")
            return []
    
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
                'api-version': self.config['API_VERSION'],
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
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        print("Fetching ADO dashboard data...")
        
        # Get test plans
        test_plans = self.get_test_plans()
        
        # Get test results
        test_results = self.get_test_results()
        
        # Search for hackathon-tagged items
        hackathon_items = self.search_work_items_by_tag()
        
        # Process and structure the data
        dashboard_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'organization': self.config['ORG'],
                'project': self.config['PROJECT'],
                'search_tag': self.config.get('SEARCH_TAG', 'hackathon')
            },
            'test_plans': test_plans,
            'test_results': test_results,
            'hackathon_items': hackathon_items,
            'summary': self._generate_summary(test_plans, test_results, hackathon_items)
        }
        
        return dashboard_data
    
    def _generate_summary(self, test_plans: List, test_results: List, hackathon_items: List) -> Dict[str, Any]:
        """Generate summary statistics"""
        # Test results analysis
        passed_tests = sum(1 for r in test_results if r.get('outcome', '').lower() == 'passed')
        failed_tests = sum(1 for r in test_results if r.get('outcome', '').lower() == 'failed')
        
        # Work items analysis
        work_item_types = {}
        for item in hackathon_items:
            work_type = item.get('fields', {}).get('System.WorkItemType', 'Unknown')
            work_item_types[work_type] = work_item_types.get(work_type, 0) + 1
        
        # State analysis
        work_item_states = {}
        for item in hackathon_items:
            state = item.get('fields', {}).get('System.State', 'Unknown')
            work_item_states[state] = work_item_states.get(state, 0) + 1
        
        return {
            'total_test_plans': len(test_plans),
            'total_test_results': len(test_results),
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'test_pass_rate': round((passed_tests / len(test_results) * 100), 2) if test_results else 0,
            'total_hackathon_items': len(hackathon_items),
            'work_item_types': work_item_types,
            'work_item_states': work_item_states
        }

if __name__ == "__main__":
    # Test the ADO client
    client = ADOClient()
    
    print("Testing ADO connection...")
    try:
        # Test basic connectivity
        test_plans = client.get_test_plans()
        print(f"✓ Successfully connected to ADO")
        print(f"✓ Found {len(test_plans)} test plans")
        
        # Test hackathon search
        hackathon_items = client.search_work_items_by_tag('hackathon')
        print(f"✓ Found {len(hackathon_items)} items with 'hackathon' tag")
        
    except Exception as e:
        print(f"✗ ADO connection failed: {e}") 