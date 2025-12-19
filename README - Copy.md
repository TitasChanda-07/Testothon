# Azure DevOps Defects Dashboard - 'Hack' Tag Analysis

## Overview

This interactive dashboard connects to Azure DevOps to analyze all defects and work items tagged with 'hack'. It provides comprehensive insights, metrics, and visualizations for defect management and tracking.

## 🔗 **ADO Integration Details**

### **Source Information:**
- **Organization**: CSGDevOpsAutomation
- **Project**: DWMS
- **Query URL**: 
- **Search Tag**: `hack`
- **PAT Token**: Configured for authentication
- **Query ID**: `13c1df67-8876-424e-aedd-d72c717097e4`

## 📋 **Complete Dashboard Creation Steps**

### **Step 1: Project Setup**
```bash
# Create project directory
mkdir "ADO_Dashboard_Defects"
cd "ADO_Dashboard_Defects"

# Create directory structure
mkdir static templates config data reports
```

### **Step 2: Configuration Setup**
Create `config/ado_config.py` with:
```python
# ADO Credentials
PAT = ""
ORG = ""
PROJECT = "DWMS"

# Search Configuration
SEARCH_TAG = "hack"
QUERY_URL = 
```

### **Step 3: ADO Client Implementation**
Create `ado_defects_client.py` with:

#### **3.1 Authentication Setup**
```python
def _create_session(self) -> requests.Session:
    session = requests.Session()
    auth_string = f":{PAT}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()
    
    session.headers.update({
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    return session
```

#### **3.2 WIQL Query for 'Hack' Tagged Defects**
```python
def search_defects_by_tag(self, tag: str = "hack") -> List[Dict[str, Any]]:
    wiql_query = {
        "query": f"""
            SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
                   [System.Tags], [System.CreatedDate], [System.ChangedDate],
                   [System.AssignedTo], [System.Priority], [Microsoft.VSTS.Common.Severity],
                   [System.Reason], [System.Description]
            FROM WorkItems 
            WHERE [System.Tags] CONTAINS '{tag}'
            AND [System.WorkItemType] IN ('Bug', 'Task', 'User Story', 'Feature')
            ORDER BY [System.ChangedDate] DESC
        """
    }
```

#### **3.3 Defects Analysis Functions**
```python
def analyze_defects(self, defects: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Analyze by type, state, priority, severity, assignee
    # Calculate trends and metrics
    # Identify critical defects
    # Generate insights
```

### **Step 4: Flask Dashboard Application**
Create `defects_dashboard.py` with:

#### **4.1 API Endpoints**
```python
@app.route('/api/summary')        # Summary metrics
@app.route('/api/analysis')       # Detailed analysis
@app.route('/api/defects')        # All defects data
@app.route('/api/search')         # Search and filter
@app.route('/api/filters')        # Filter options
@app.route('/api/refresh')        # Refresh from ADO
@app.route('/api/export')         # Export data
```

#### **4.2 Data Management**
```python
class DefectsDashboard:
    def refresh_data(self):        # Fetch fresh data from ADO
    def load_cached_data(self):    # Load cached data
    def search_defects(self):      # Search and filter functionality
```

### **Step 5: Interactive Frontend**
Create `templates/defects_dashboard.html` with:

#### **5.1 Header Section**
- CSG logo integration
- Organization/Project display
- Search tag indicator
- Direct link to ADO query

#### **5.2 Summary Cards**
- Total Defects count
- Total Bugs count
- Resolution Rate percentage
- Average Resolution Time
- Critical Bugs count
- Recent Defects (30 days)

#### **5.3 Search & Filter Controls**
- Work Item Type filter (Bug, Task, User Story, Feature)
- State filter (Active, New, Resolved, Closed)
- Priority filter (High, Medium, Low)
- Assignee filter (by team/person)
- Text search across title, description, tags

#### **5.4 Interactive Charts**
- **Defects by Type**: Pie chart showing Bug vs Task vs User Story distribution
- **Defects by State**: Bar chart of Active, Resolved, New, etc.
- **Priority Distribution**: Doughnut chart of High, Medium, Low priorities
- **Assignee Distribution**: Horizontal bar chart of defects per assignee

#### **5.5 Detailed Defects View**
- Defect cards with all information
- Color-coded badges for type, state, priority
- Direct links to ADO work items
- Description and tags display
- Created/Updated timestamps

### **Step 6: Data Processing Features**

#### **6.1 Defect Metrics Calculation**
```python
def get_defect_metrics(self, defects):
    return {
        'total_defects': len(defects),
        'total_bugs': count_bugs,
        'resolution_rate': percentage_resolved,
        'avg_resolution_time_days': average_days,
        'critical_bugs': high_priority_count,
        'recent_defects_30_days': recent_count
    }
```

#### **6.2 Trend Analysis**
```python
def get_defect_trends(self, defects, days=90):
    return {
        'daily_creation': creation_by_date,
        'daily_resolution': resolution_by_date,
        'creation_trend': "increasing/decreasing/stable",
        'resolution_trend': "increasing/decreasing/stable"
    }
```

### **Step 7: ADO Query Integration**

#### **7.1 WIQL Query Structure**
Based on the ADO query URL, the dashboard uses:
```sql
SELECT [System.Id], [System.Title], [System.State], [System.WorkItemType],
       [System.Tags], [System.CreatedDate], [System.ChangedDate],
       [System.AssignedTo], [System.Priority], [Microsoft.VSTS.Common.Severity]
FROM WorkItems 
WHERE [System.Tags] CONTAINS 'hack'
ORDER BY [System.ChangedDate] DESC
```

#### **7.2 Work Item Fields Retrieved**
- **System.Id**: Work item identifier
- **System.Title**: Defect title/summary
- **System.State**: Current state (Active, Resolved, etc.)
- **System.WorkItemType**: Type (Bug, Task, User Story)
- **System.Tags**: All tags including 'hack'
- **System.Priority**: Priority level
- **Microsoft.VSTS.Common.Severity**: Severity level
- **System.AssignedTo**: Assigned team/person
- **System.Description**: Detailed description

### **Step 8: Dashboard Features Implementation**

#### **8.1 Real-time ADO Integration**
- Connects to live ADO instance
- Fetches current defect data
- Updates dashboard with latest information
- Provides direct navigation to ADO items

#### **8.2 Advanced Analytics**
- **Resolution Rate**: Percentage of resolved defects
- **Average Resolution Time**: Days from creation to resolution
- **Critical Defects Alert**: Highlights high-priority bugs
- **Trend Analysis**: Creation vs resolution trends
- **Team Performance**: Defects by assignee

#### **8.3 Interactive Filtering**
- **Multi-criteria Filtering**: Combine multiple filters
- **Real-time Search**: Instant results as you type
- **Dynamic Updates**: Charts update with filtered data
- **Export Functionality**: Download filtered results

### **Step 9: Deployment Instructions**

#### **9.1 Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **9.2 Run Dashboard**
```bash
python defects_dashboard.py
```

#### **9.3 Access Dashboard**
- **URL**: http://localhost:5002
- **Features**: Full ADO integration, real-time data, interactive charts

### **Step 10: Sample Data Structure**

#### **10.1 Defect Record Example**
```json
{
  "id": "3001",
  "fields": {
    "System.Id": "3001",
    "System.Title": "Login authentication fails with hack tag implementation",
    "System.State": "Active",
    "System.WorkItemType": "Bug",
    "System.Tags": "hack; authentication; security; login",
    "System.Priority": "High",
    "Microsoft.VSTS.Common.Severity": "2 - High",
    "System.CreatedDate": "2025-09-15T10:30:00Z",
    "System.AssignedTo": {"displayName": "Security Team"},
    "System.Description": "Authentication module fails when hack tag is processed"
  }
}
```

#### **10.2 Analysis Output Example**
```json
{
  "total_defects": 4,
  "by_type": {"Bug": 3, "Task": 1},
  "by_state": {"Active": 2, "Resolved": 1, "New": 1},
  "by_priority": {"High": 2, "Medium": 2},
  "critical_defects": 2,
  "resolution_rate": 25.0,
  "avg_resolution_time_days": 6.2
}
```

## 🎯 **Key Dashboard Capabilities**

### **Defect Analysis:**
- ✅ **Total Count**: All defects with 'hack' tag
- ✅ **Type Breakdown**: Bugs, Tasks, User Stories, Features
- ✅ **State Analysis**: Active, Resolved, New, Closed
- ✅ **Priority Distribution**: High, Medium, Low priorities
- ✅ **Severity Tracking**: Critical, High, Medium, Low severity
- ✅ **Team Assignment**: Defects by assignee/team

### **Interactive Features:**
- ✅ **Real-time Search**: Find specific defects instantly
- ✅ **Multi-filter Support**: Combine multiple criteria
- ✅ **Direct ADO Links**: Navigate to work items in ADO
- ✅ **Export Capability**: Download analysis results
- ✅ **Refresh Data**: Get latest information from ADO
- ✅ **Visual Charts**: Interactive data visualization

### **Alerts & Insights:**
- ✅ **Critical Defects Alert**: Highlights urgent bugs
- ✅ **Trend Analysis**: Creation vs resolution patterns
- ✅ **Performance Metrics**: Resolution rates and times
- ✅ **Team Workload**: Distribution of defects by assignee

## 🚀 **Technical Implementation**

### **Backend Architecture:**
- **Flask Web Server**: Serves dashboard and API endpoints
- **ADO REST Client**: Handles all Azure DevOps interactions
- **Data Caching**: Local storage for performance
- **Real-time Updates**: On-demand refresh from ADO

### **Frontend Architecture:**
- **Responsive Design**: Works on all devices
- **Interactive Charts**: Chart.js integration
- **Modern UI**: Azure-themed design with CSG branding
- **AJAX Functionality**: Dynamic content loading

### **Security Features:**
- **PAT Authentication**: Secure token-based access
- **Input Validation**: Prevents injection attacks
- **Error Handling**: Graceful failure management
- **Data Sanitization**: Clean data display

## 📊 **Dashboard Sections**

1. **Header**: Logo, organization info, query link
2. **Summary Cards**: Key metrics and KPIs
3. **Critical Alerts**: High-priority defect notifications
4. **Search Controls**: Advanced filtering options
5. **Analytics Charts**: Visual data representation
6. **Defects List**: Detailed defect information with ADO links

This comprehensive ADO Defects Dashboard provides complete visibility into all defects tagged with 'hack' from the specified Azure DevOps query, enabling effective defect management and analysis. 