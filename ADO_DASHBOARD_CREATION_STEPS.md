# Azure DevOps Hackathon Dashboard - Creation Steps

## Overview
This document outlines the complete steps to create an interactive dashboard that connects to Azure DevOps, searches for items tagged with 'hackathon', and displays comprehensive test data from the specified test plan.

## Prerequisites
- Python 3.8+
- Azure DevOps access with Personal Access Token (PAT)
- Flask and requests libraries
- Access to the specified ADO organization and project

## Step-by-Step Creation Process

### Step 1: Project Setup
```bash
# Create project directory
mkdir "ADO Dashboard"
cd "ADO Dashboard"

# Create directory structure
mkdir static templates config data reports
```

### Step 2: Configuration Setup
Create `config/ado_config.txt` with Azure DevOps credentials:
```ini
# Azure DevOps Configuration
PAT=2JsNtHM6ACM6ozSKnM2QolTJ2HXc4vl5WMowcSQGibyb5BLh9ir3JQQJ99BIACAAAAAtF2WOAAASAZDO3ihq
ORG=CSGDevOpsAutomation
PROJECT=DWMS

# ADO API Settings
BASE_URL=https://dev.azure.com
API_VERSION=7.0
SEARCH_TAG=hackathon
TEST_PLAN_ID=108014
TEST_SUITE_ID=108015

# Dashboard Settings
DASHBOARD_PORT=5001
DASHBOARD_HOST=0.0.0.0
```

### Step 3: Azure DevOps Client Implementation
Create `ado_client.py` with the following capabilities:

#### 3.1 Authentication Setup
```python
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
```

#### 3.2 Test Plans Retrieval
```python
def get_test_plans(self) -> List[Dict[str, Any]]:
    """Get test plans from ADO"""
    url = f"{self.base_url}/_apis/test/plans"
    params = {'api-version': self.config['API_VERSION']}
    
    response = self.session.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data.get('value', [])
```

#### 3.3 Test Results Retrieval
```python
def get_test_results(self, plan_id: str = None) -> List[Dict[str, Any]]:
    """Get test results from specific test plan"""
    url = f"{self.base_url}/_apis/test/Runs"
    params = {
        'api-version': self.config['API_VERSION'],
        'planId': plan_id or self.config['TEST_PLAN_ID'],
        'includeRunDetails': 'true'
    }
    
    response = self.session.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data.get('value', [])
```

#### 3.4 Hackathon Items Search
```python
def search_work_items_by_tag(self, tag: str = 'hackathon') -> List[Dict[str, Any]]:
    """Search work items by tag using WIQL"""
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
    
    response = self.session.post(url, json=wiql_query, params=params)
    response.raise_for_status()
    
    data = response.json()
    work_items = data.get('workItems', [])
    
    # Get detailed information for each work item
    if work_items:
        item_ids = [str(item['id']) for item in work_items]
        return self.get_work_items_details(item_ids)
    
    return []
```

### Step 4: Flask Dashboard Application
Create `app.py` with the following components:

#### 4.1 Data Management
```python
class ADODashboard:
    def __init__(self):
        self.ado_client = ADOClient()
        self.dashboard_data = {}
        
    def refresh_data(self) -> Dict[str, Any]:
        """Refresh data from ADO"""
        self.dashboard_data = self.ado_client.get_dashboard_data()
        return self.dashboard_data
```

#### 4.2 API Endpoints
```python
@app.route('/api/summary')
def api_summary():
    """Summary statistics"""
    
@app.route('/api/test-results')
def api_test_results():
    """Test results from ADO"""
    
@app.route('/api/hackathon-items')
def api_hackathon_items():
    """Work items tagged with hackathon"""
    
@app.route('/api/test-plans')
def api_test_plans():
    """Test plans information"""
    
@app.route('/api/search')
def api_search():
    """Search functionality across all data"""
```

### Step 5: Dashboard Frontend
Create `templates/ado_dashboard.html` with:

#### 5.1 Header Section
- CSG logo integration
- Organization/Project information
- Search tag display
- Real-time statistics

#### 5.2 Summary Cards
- Total Test Plans
- Total Test Results
- Test Pass Rate
- Total Hackathon Items

#### 5.3 Interactive Charts
- Test Outcomes Distribution (Passed/Failed)
- Work Item Types Distribution
- Priority Distribution
- State Distribution

#### 5.4 Tabbed Content
- **Test Results Tab**: Shows all test executions with hackathon tag
- **Hackathon Items Tab**: Shows work items (tasks, bugs, user stories) with hackathon tag
- **Test Plans Tab**: Shows relevant test plans

#### 5.5 Search & Filter Functionality
- Text search across titles and descriptions
- Filter by item type (tests, work items, all)
- Real-time filtering and updates

### Step 6: Data Integration Points

#### 6.1 ADO REST API Endpoints Used
```
# Test Plans
GET https://dev.azure.com/{org}/{project}/_apis/test/plans?api-version=7.0

# Test Results
GET https://dev.azure.com/{org}/{project}/_apis/test/Runs?api-version=7.0&planId={planId}

# Work Items Search (WIQL)
POST https://dev.azure.com/{org}/{project}/_apis/wit/wiql?api-version=7.0

# Work Items Details
GET https://dev.azure.com/{org}/{project}/_apis/wit/workitems?ids={ids}&api-version=7.0
```

#### 6.2 Authentication
- Uses Personal Access Token (PAT) authentication
- Basic authentication header: `Authorization: Basic {base64(:{PAT})}`

### Step 7: Dashboard Features Implementation

#### 7.1 Real-time Data Display
- **Test Plan Information**: ID, Name, State, Description
- **Test Results**: Test case titles, outcomes, durations, error messages
- **Work Items**: ID, Title, Type, State, Assigned To, Tags
- **Links**: Direct links to ADO items for detailed view

#### 7.2 Interactive Elements
- **Search Box**: Full-text search across all content
- **Filter Dropdowns**: Filter by item type
- **Tabs**: Switch between different data views
- **Refresh Button**: Update data from ADO
- **Export Functionality**: Download filtered results

#### 7.3 Visual Analytics
- **Pie Charts**: Test outcome distribution
- **Bar Charts**: Work item types and states
- **Summary Cards**: Key metrics and KPIs
- **Color Coding**: Visual status indicators

### Step 8: Sample Data Structure

#### 8.1 Test Results Format
```json
{
  "id": "1001",
  "testCaseTitle": "Login Functionality Test - Hackathon",
  "outcome": "Passed",
  "state": "Completed",
  "priority": "High",
  "automatedTestName": "test_login_hackathon",
  "startedDate": "2025-09-18T10:00:00Z",
  "completedDate": "2025-09-18T10:05:00Z",
  "tags": ["hackathon", "login", "authentication"],
  "duration": "5m 23s",
  "errorMessage": "Optional error details"
}
```

#### 8.2 Work Items Format
```json
{
  "id": "2001",
  "fields": {
    "System.Id": "2001",
    "System.Title": "Implement hackathon dashboard",
    "System.State": "Active",
    "System.WorkItemType": "Task",
    "System.Tags": "hackathon; dashboard; development",
    "System.CreatedDate": "2025-09-15T09:00:00Z",
    "System.ChangedDate": "2025-09-18T11:00:00Z",
    "System.AssignedTo": "Developer Team",
    "System.Priority": "High"
  }
}
```

### Step 9: Deployment Steps

#### 9.1 Install Dependencies
```bash
pip install Flask requests urllib3
```

#### 9.2 Run Dashboard
```bash
python app.py
```

#### 9.3 Access Dashboard
- URL: `http://localhost:5001`
- Features: Interactive filtering, search, charts, direct ADO links

### Step 10: Integration with ADO Test Plan

#### 10.1 Test Plan URL Integration
- **Direct Link**: https://dev.azure.com/CSGDevOpsAutomation/DWMS/_testPlans/define?planId=108014&suiteId=108015
- **API Integration**: Fetches data from the specified test plan
- **Tag Filtering**: Searches for 'hackathon' tagged items
- **Real-time Updates**: Refresh data from ADO on demand

#### 10.2 Work Item Correlation
- Links test results to related work items
- Shows associated bugs, tasks, and user stories
- Provides direct navigation to ADO items
- Displays work item relationships and dependencies

### Step 11: Dashboard Capabilities

#### 11.1 Data Display
✅ **Test Plans**: Shows test plan 108014 details and status
✅ **Test Results**: Displays all test executions with hackathon tag
✅ **Work Items**: Shows tasks, bugs, user stories tagged with hackathon
✅ **Summary Statistics**: Pass rates, counts, distributions

#### 11.2 Interactive Features
✅ **Search**: Full-text search across all content
✅ **Filtering**: Filter by item type and status
✅ **Charts**: Visual representation of data
✅ **Navigation**: Direct links to ADO items
✅ **Export**: Download filtered data
✅ **Refresh**: Update data from ADO

#### 11.3 Visual Design
✅ **CSG Logo**: Company branding in header
✅ **Modern UI**: Azure-themed color scheme
✅ **Responsive**: Works on all screen sizes
✅ **Professional**: Clean, corporate appearance

## Technical Architecture

### Backend Components
1. **ADO Client** (`ado_client.py`): Handles all Azure DevOps API interactions
2. **Flask App** (`app.py`): Web server and API endpoints
3. **Configuration** (`config/ado_config.txt`): Credentials and settings

### Frontend Components
1. **HTML Template** (`templates/ado_dashboard.html`): Main dashboard interface
2. **CSS Styling**: Azure-themed responsive design
3. **JavaScript**: Interactive functionality and AJAX calls
4. **Charts**: Chart.js integration for data visualization

### Data Flow
1. **Authentication**: PAT-based authentication with ADO
2. **Data Retrieval**: REST API calls to ADO endpoints
3. **Processing**: Data transformation and summary calculation
4. **Visualization**: Interactive charts and tables
5. **User Interaction**: Search, filter, and navigation features

## Security Considerations
- PAT token stored securely in configuration file
- HTTPS communication with Azure DevOps
- Input validation for search queries
- Rate limiting for API calls

## Performance Optimization
- Data caching for faster response times
- Lazy loading of chart data
- Efficient API calls with minimal data transfer
- Client-side filtering for better user experience

## Troubleshooting
1. **Authentication Issues**: Verify PAT token permissions
2. **API Errors**: Check ADO service status and API version
3. **Data Loading**: Verify organization and project names
4. **Search Issues**: Ensure proper tag formatting in work items

This comprehensive ADO dashboard provides a complete solution for monitoring hackathon-related test activities and work items with direct integration to the specified Azure DevOps test plan. 