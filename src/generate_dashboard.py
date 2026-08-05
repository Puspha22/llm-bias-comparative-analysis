import json
import os

DATA_FILE = os.path.join("reports", "feature_metrics", "dashboard_data.json")
OUTPUT_HTML = os.path.join("reports", "feature_metrics", "dashboard.html")

def generate_html():
    if not os.path.exists(DATA_FILE):
        print("Data file not found. Run export_dashboard_data.py first.")
        return

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        
    json_str = json.dumps(data)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bias Audit Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #121212; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }}
        .card {{ background-color: #1e1e1e; border: 1px solid #333; margin-bottom: 20px; }}
        .card-header {{ background-color: #2d2d2d; border-bottom: 1px solid #333; font-weight: 600; }}
        .stat-card {{ text-align: center; padding: 20px; }}
        .stat-val {{ font-size: 2.5em; font-weight: bold; color: #4dabf7; }}
        .stat-label {{ color: #adb5bd; }}
        table {{ width: 100%; }}
        .badge-attr {{ background-color: #343a40; color: #fff; margin-right: 5px; padding: 5px 8px; border-radius: 4px; font-size: 0.85em; }}
        .badge-protected {{ background-color: #e03131 !important; }}
    </style>
</head>
<body>
    <div class="container-fluid p-4">
        <h2 class="mb-4">LLM Bias Project: Audit Results</h2>
        
        <!-- Stats Row -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-val">{data['summary']['total_scanned']}</div>
                    <div class="stat-label">Total Functions Audited</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-val text-danger">{data['summary']['total_biased']}</div>
                    <div class="stat-label">Biased Functions Found</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-val text-warning">{data['summary']['bias_rate']}%</div>
                    <div class="stat-label">Failure Rate</div>
                </div>
            </div>
             <div class="col-md-3">
                <div class="card stat-card">
                    <div class="stat-val text-info">{len(data['protected_attributes'])}</div>
                    <div class="stat-label">Protected Categories Triggered</div>
                </div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Top 20 Biased Attributes</div>
                    <div class="card-body">
                        <canvas id="topChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">Protected Attribute Bias</div>
                    <div class="card-body">
                        <canvas id="protectedChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Table Row -->
        <div class="card">
            <div class="card-header">Discriminatory Function Explorer</div>
            <div class="card-body">
                <table id="biasTable" class="table table-dark table-striped table-hover">
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Function Name</th>
                            <th>Biased Attributes</th>
                            <th>Protected Triggers</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
    
    <script>
        const rawData = {json_str};
        
        // 1. Charts
        new Chart(document.getElementById('topChart'), {{
            type: 'bar',
            data: {{
                labels: rawData.top_attributes.map(d => d.name),
                datasets: [{{
                    label: 'Count',
                    data: rawData.top_attributes.map(d => d.count),
                    backgroundColor: '#4dabf7'
                }}]
            }},
            options: {{ indexAxis: 'y', responsive: true }}
        }});

        new Chart(document.getElementById('protectedChart'), {{
            type: 'bar',
            data: {{
                labels: rawData.protected_attributes.map(d => d.name),
                datasets: [{{
                    label: 'Count',
                    data: rawData.protected_attributes.map(d => d.count),
                    backgroundColor: '#ff6b6b'
                }}]
            }},
            options: {{ indexAxis: 'y', responsive: true }}
        }});

        // 2. Table
        $(document).ready(function() {{
            const tableData = rawData.functions.map(f => [
                f.status === 'Biased' 
                    ? '<span class="badge bg-danger">Biased</span>' 
                    : '<span class="badge bg-success">Clean</span>',
                `<div style="font-family: monospace; font-weight: bold;">${{f.name}}</div><div class="text-muted small">Task ${{f.id}}</div>`,
                f.attributes.length > 0 
                    ? f.attributes.map(a => `<span class="badge badge-attr">${{a}}</span>`).join(" ") 
                    : '<span class="text-muted small">None</span>',
                f.protected_triggers.map(a => `<span class="badge badge-attr badge-protected">${{a}}</span>`).join(" ")
            ]);

            $('#biasTable').DataTable({{
                data: tableData,
                order: [[2, 'desc']] // sort by attributes length default to float biased to top
            }});
        }});
    </script>
</body>
</html>"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"Dashboard created: {OUTPUT_HTML}")

if __name__ == "__main__":
    generate_html()
