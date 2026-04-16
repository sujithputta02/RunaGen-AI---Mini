"""
BI Dashboard Generator
Creates interactive visualizations for career analytics
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta

class DashboardGenerator:
    def __init__(self, output_dir="dashboards/html"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all_dashboards(self, data=None):
        """Generate all 4 dashboards"""
        print("Generating BI Dashboards...")
        print("="*60)
        
        # Use mock data if not provided
        if data is None:
            data = self._generate_mock_data()
        
        # Generate each dashboard
        self.dashboard_1_career_transitions(data)
        self.dashboard_2_skill_gaps(data)
        self.dashboard_3_salary_insights(data)
        self.dashboard_4_market_trends(data)
        
        # Generate index page
        self._generate_index()
        
        print("\n" + "="*60)
        print("✅ All dashboards generated successfully!")
        print(f"📁 Location: {self.output_dir.absolute()}")
        print(f"🌐 Open: {self.output_dir.absolute()}/index.html")
    
    def dashboard_1_career_transitions(self, data):
        """Dashboard 1: Career Transition Graph"""
        print("\n📊 Generating Dashboard 1: Career Transitions...")
        
        # Create Sankey diagram for career transitions
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=data['career_transitions']['labels'],
                color=data['career_transitions']['colors']
            ),
            link=dict(
                source=data['career_transitions']['source'],
                target=data['career_transitions']['target'],
                value=data['career_transitions']['value'],
                color=data['career_transitions']['link_colors']
            )
        )])
        
        fig.update_layout(
            title="Career Transition Pathways",
            font=dict(size=12),
            height=600
        )
        
        # Save
        output_file = self.output_dir / "dashboard_1_career_transitions.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
        
        return fig
    
    def dashboard_2_skill_gaps(self, data):
        """Dashboard 2: Skill Gap & Priority Skills"""
        print("\n📊 Generating Dashboard 2: Skill Gaps...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Top Priority Skills',
                'Skill Frequency Heatmap',
                'Salary Premium vs Demand',
                'Skill Gap Distribution'
            ),
            specs=[
                [{"type": "bar"}, {"type": "heatmap"}],
                [{"type": "scatter"}, {"type": "pie"}]
            ]
        )
        
        # 1. Top Priority Skills (Bar Chart)
        skills_df = data['skill_gaps']
        fig.add_trace(
            go.Bar(
                x=skills_df['skill'],
                y=skills_df['priority_score'],
                marker_color=skills_df['priority_score'],
                marker_colorscale='Viridis',
                name='Priority Score'
            ),
            row=1, col=1
        )
        
        # 2. Skill Frequency Heatmap
        heatmap_data = data['skill_heatmap']
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data['values'],
                x=heatmap_data['skills'],
                y=heatmap_data['roles'],
                colorscale='YlOrRd',
                name='Frequency'
            ),
            row=1, col=2
        )
        
        # 3. Salary Premium vs Demand (Scatter)
        fig.add_trace(
            go.Scatter(
                x=skills_df['demand_frequency'],
                y=skills_df['salary_premium'],
                mode='markers+text',
                text=skills_df['skill'],
                textposition='top center',
                marker=dict(
                    size=skills_df['priority_score'] * 20,
                    color=skills_df['priority_score'],
                    colorscale='Viridis',
                    showscale=True
                ),
                name='Skills'
            ),
            row=2, col=1
        )
        
        # 4. Skill Gap Distribution (Pie)
        gap_dist = data['gap_distribution']
        fig.add_trace(
            go.Pie(
                labels=gap_dist['categories'],
                values=gap_dist['values'],
                hole=0.3
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Skill Gap Analysis Dashboard",
            showlegend=False,
            height=800
        )
        
        # Save
        output_file = self.output_dir / "dashboard_2_skill_gaps.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
        
        return fig
    
    def dashboard_3_salary_insights(self, data):
        """Dashboard 3: Salary Insights"""
        print("\n📊 Generating Dashboard 3: Salary Insights...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Salary Distribution by Role',
                'Salary Trends Over Time',
                'Experience vs Salary',
                'Skill Impact on Salary'
            ),
            specs=[
                [{"type": "box"}, {"type": "scatter"}],
                [{"type": "scatter"}, {"type": "bar"}]
            ]
        )
        
        # 1. Salary Distribution by Role (Box Plot)
        salary_data = data['salary_by_role']
        for role in salary_data['roles']:
            fig.add_trace(
                go.Box(
                    y=salary_data['salaries'][role],
                    name=role,
                    boxmean='sd'
                ),
                row=1, col=1
            )
        
        # 2. Salary Trends Over Time (Line Chart)
        trends = data['salary_trends']
        for role in trends['roles']:
            fig.add_trace(
                go.Scatter(
                    x=trends['dates'],
                    y=trends['salaries'][role],
                    mode='lines+markers',
                    name=role
                ),
                row=1, col=2
            )
        
        # 3. Experience vs Salary (Scatter)
        exp_salary = data['experience_salary']
        fig.add_trace(
            go.Scatter(
                x=exp_salary['experience'],
                y=exp_salary['salary'],
                mode='markers',
                marker=dict(
                    size=10,
                    color=exp_salary['experience'],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=exp_salary['roles'],
                name='Salary vs Experience'
            ),
            row=2, col=1
        )
        
        # 4. Skill Impact on Salary (Bar Chart)
        skill_impact = data['skill_salary_impact']
        fig.add_trace(
            go.Bar(
                x=skill_impact['skills'],
                y=skill_impact['impact'],
                marker_color=skill_impact['impact'],
                marker_colorscale='RdYlGn',
                name='Salary Impact'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Salary Insights Dashboard",
            showlegend=True,
            height=800
        )
        
        fig.update_xaxes(title_text="Role", row=1, col=1)
        fig.update_yaxes(title_text="Salary ($)", row=1, col=1)
        fig.update_xaxes(title_text="Date", row=1, col=2)
        fig.update_yaxes(title_text="Salary ($)", row=1, col=2)
        fig.update_xaxes(title_text="Years of Experience", row=2, col=1)
        fig.update_yaxes(title_text="Salary ($)", row=2, col=1)
        fig.update_xaxes(title_text="Skill", row=2, col=2)
        fig.update_yaxes(title_text="Salary Impact ($)", row=2, col=2)
        
        # Save
        output_file = self.output_dir / "dashboard_3_salary_insights.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
        
        return fig
    
    def dashboard_4_market_trends(self, data):
        """Dashboard 4: Market Trends"""
        print("\n📊 Generating Dashboard 4: Market Trends...")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Job Posting Volume Over Time',
                'Job Distribution by Industry',
                'Top Growing Skills',
                'Role Demand Trends'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # 1. Job Posting Volume (Line Chart)
        volume = data['job_volume']
        fig.add_trace(
            go.Scatter(
                x=volume['dates'],
                y=volume['volume'],
                mode='lines+markers',
                fill='tozeroy',
                name='Job Postings',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # 2. Job Distribution by Industry (Pie Chart)
        industry = data['industry_distribution']
        fig.add_trace(
            go.Pie(
                labels=industry['industries'],
                values=industry['counts'],
                hole=0.3
            ),
            row=1, col=2
        )
        
        # 3. Top Growing Skills (Bar Chart)
        growing_skills = data['growing_skills']
        fig.add_trace(
            go.Bar(
                x=growing_skills['skills'],
                y=growing_skills['growth_rate'],
                marker_color=growing_skills['growth_rate'],
                marker_colorscale='Greens',
                name='Growth Rate'
            ),
            row=2, col=1
        )
        
        # 4. Role Demand Trends (Multi-line)
        role_trends = data['role_demand_trends']
        for role in role_trends['roles']:
            fig.add_trace(
                go.Scatter(
                    x=role_trends['dates'],
                    y=role_trends['demand'][role],
                    mode='lines',
                    name=role
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="Job Market Trends Dashboard",
            showlegend=True,
            height=800
        )
        
        fig.update_xaxes(title_text="Date", row=1, col=1)
        fig.update_yaxes(title_text="Number of Postings", row=1, col=1)
        fig.update_xaxes(title_text="Skill", row=2, col=1)
        fig.update_yaxes(title_text="Growth Rate (%)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=2)
        fig.update_yaxes(title_text="Demand Index", row=2, col=2)
        
        # Save
        output_file = self.output_dir / "dashboard_4_market_trends.html"
        fig.write_html(str(output_file))
        print(f"✓ Saved: {output_file.name}")
        
        return fig
    
    def _generate_index(self):
        """Generate index page with links to all dashboards"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RunaGen AI - BI Dashboards</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 20px;
            font-size: 2.5em;
        }
        .subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 40px;
            font-size: 1.2em;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }
        .dashboard-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        .dashboard-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }
        .dashboard-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 10px;
        }
        .dashboard-description {
            color: #666;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .dashboard-link {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: opacity 0.3s;
        }
        .dashboard-link:hover {
            opacity: 0.9;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 RunaGen AI - BI Dashboards</h1>
        <p class="subtitle">Interactive Career Analytics & Market Intelligence</p>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="dashboard-icon">🔄</div>
                <h2 class="dashboard-title">Career Transitions</h2>
                <p class="dashboard-description">
                    Visualize career pathways and transition probabilities using interactive Sankey diagrams.
                </p>
                <a href="dashboard_1_career_transitions.html" class="dashboard-link">View Dashboard →</a>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-icon">📊</div>
                <h2 class="dashboard-title">Skill Gap Analysis</h2>
                <p class="dashboard-description">
                    Identify priority skills, analyze demand patterns, and understand salary premiums.
                </p>
                <a href="dashboard_2_skill_gaps.html" class="dashboard-link">View Dashboard →</a>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-icon">💰</div>
                <h2 class="dashboard-title">Salary Insights</h2>
                <p class="dashboard-description">
                    Explore salary distributions, trends, and the impact of skills on compensation.
                </p>
                <a href="dashboard_3_salary_insights.html" class="dashboard-link">View Dashboard →</a>
            </div>
            
            <div class="dashboard-card">
                <div class="dashboard-icon">📈</div>
                <h2 class="dashboard-title">Market Trends</h2>
                <p class="dashboard-description">
                    Track job market dynamics, industry distribution, and emerging skill demands.
                </p>
                <a href="dashboard_4_market_trends.html" class="dashboard-link">View Dashboard →</a>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated on """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <p>RunaGen AI - ML-Powered Career Intelligence Platform</p>
        </div>
    </div>
</body>
</html>
"""
        
        output_file = self.output_dir / "index.html"
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        print(f"\n✓ Generated index page: {output_file.name}")
    
    def _generate_mock_data(self):
        """Generate mock data for dashboards"""
        np.random.seed(42)
        
        # Career transitions data
        career_transitions = {
            'labels': [
                'Data Analyst', 'Data Engineer', 'Data Scientist', 
                'ML Engineer', 'Software Engineer', 'Senior Data Scientist',
                'Lead ML Engineer', 'Principal Engineer'
            ],
            'source': [0, 0, 1, 1, 2, 2, 3, 3, 4],
            'target': [2, 1, 2, 3, 5, 3, 6, 5, 7],
            'value': [30, 20, 40, 25, 35, 20, 30, 25, 15],
            'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f'],
            'link_colors': ['rgba(31,119,180,0.4)'] * 9
        }
        
        # Skill gaps data
        skills = ['Python', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning', 
                 'Deep Learning', 'Spark', 'Airflow', 'Terraform']
        skill_gaps = pd.DataFrame({
            'skill': skills,
            'priority_score': np.random.rand(len(skills)) * 0.5 + 0.5,
            'demand_frequency': np.random.rand(len(skills)) * 0.5 + 0.5,
            'salary_premium': np.random.rand(len(skills)) * 0.5 + 0.5
        })
        
        # Skill heatmap
        roles = ['Data Scientist', 'Data Engineer', 'ML Engineer', 'Software Engineer']
        skill_heatmap = {
            'skills': skills[:8],
            'roles': roles,
            'values': np.random.rand(len(roles), 8) * 100
        }
        
        # Gap distribution
        gap_distribution = {
            'categories': ['High Priority', 'Medium Priority', 'Low Priority'],
            'values': [35, 45, 20]
        }
        
        # Salary by role
        roles_list = ['Data Analyst', 'Data Engineer', 'Data Scientist', 'ML Engineer']
        salary_by_role = {
            'roles': roles_list,
            'salaries': {
                role: np.random.normal(80000 + i*20000, 15000, 100)
                for i, role in enumerate(roles_list)
            }
        }
        
        # Salary trends
        dates = pd.date_range(start='2024-01-01', end='2026-03-01', freq='ME')
        salary_trends = {
            'dates': dates,
            'roles': roles_list,
            'salaries': {
                role: 70000 + i*15000 + np.cumsum(np.random.randn(len(dates)) * 1000)
                for i, role in enumerate(roles_list)
            }
        }
        
        # Experience vs Salary
        n_points = 50
        experience_salary = {
            'experience': np.random.randint(0, 20, n_points),
            'salary': 50000 + np.random.randint(0, 20, n_points) * 5000 + np.random.randn(n_points) * 10000,
            'roles': np.random.choice(roles_list, n_points)
        }
        
        # Skill salary impact
        skill_salary_impact = {
            'skills': skills[:8],
            'impact': np.random.randint(5000, 25000, 8)
        }
        
        # Job volume
        job_dates = pd.date_range(start='2024-01-01', end='2026-03-01', freq='W-MON')
        job_volume = {
            'dates': job_dates,
            'volume': 1000 + np.cumsum(np.random.randn(len(job_dates)) * 50)
        }
        
        # Industry distribution
        industry_distribution = {
            'industries': ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing', 'Other'],
            'counts': [350, 200, 150, 100, 80, 120]
        }
        
        # Growing skills
        growing_skills = {
            'skills': ['AI/ML', 'Cloud', 'DevOps', 'Data Science', 'Cybersecurity', 'Blockchain'],
            'growth_rate': [45, 38, 35, 32, 28, 25]
        }
        
        # Role demand trends
        role_demand_trends = {
            'dates': job_dates,
            'roles': roles_list,
            'demand': {
                role: 100 + np.cumsum(np.random.randn(len(job_dates)) * 5)
                for role in roles_list
            }
        }
        
        return {
            'career_transitions': career_transitions,
            'skill_gaps': skill_gaps,
            'skill_heatmap': skill_heatmap,
            'gap_distribution': gap_distribution,
            'salary_by_role': salary_by_role,
            'salary_trends': salary_trends,
            'experience_salary': experience_salary,
            'skill_salary_impact': skill_salary_impact,
            'job_volume': job_volume,
            'industry_distribution': industry_distribution,
            'growing_skills': growing_skills,
            'role_demand_trends': role_demand_trends
        }

if __name__ == "__main__":
    generator = DashboardGenerator()
    generator.generate_all_dashboards()
