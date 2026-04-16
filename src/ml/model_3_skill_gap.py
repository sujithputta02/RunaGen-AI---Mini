"""
MODEL 3: Skill Gap Prioritization
Ranking model to prioritize missing skills
"""
import pandas as pd
import numpy as np

class SkillGapAnalyzer:
    def __init__(self):
        self.weights = {
            'demand_weight': 0.4,
            'salary_impact': 0.3,
            'growth_rate': 0.2,
            'skill_centrality': 0.1
        }
    
    def calculate_priority_score(self, skill_data):
        """
        Calculate priority score for each missing skill
        
        Score = (0.4 × Demand) + (0.3 × Salary Impact) + 
                (0.2 × Growth Rate) + (0.1 × Centrality)
        """
        score = (
            self.weights['demand_weight'] * skill_data['demand_frequency'] +
            self.weights['salary_impact'] * skill_data['salary_premium'] +
            self.weights['growth_rate'] * skill_data['market_growth'] +
            self.weights['skill_centrality'] * skill_data['centrality_score']
        )
        return score
    
    def analyze_gaps(self, current_skills, target_role_skills, market_data):
        """
        Identify and prioritize skill gaps
        
        Args:
            current_skills: List of user's current skills
            target_role_skills: Required skills for target role
            market_data: DataFrame with skill market metrics
        """
        # Find missing skills
        missing_skills = set(target_role_skills) - set(current_skills)
        
        # Calculate priority for each missing skill
        gap_analysis = []
        
        for skill in missing_skills:
            if skill in market_data.index:
                skill_info = market_data.loc[skill]
                priority_score = self.calculate_priority_score(skill_info)
                
                gap_analysis.append({
                    'skill': skill,
                    'priority_score': priority_score,
                    'demand_frequency': skill_info['demand_frequency'],
                    'salary_impact': skill_info['salary_premium'],
                    'growth_rate': skill_info['market_growth']
                })
        
        # Sort by priority score
        gap_df = pd.DataFrame(gap_analysis)
        gap_df = gap_df.sort_values('priority_score', ascending=False)
        
        return gap_df
    
    def get_learning_recommendations(self, gap_analysis, top_n=5):
        """Generate learning recommendations for top priority skills"""
        top_skills = gap_analysis.head(top_n)
        
        recommendations = []
        for _, row in top_skills.iterrows():
            recommendations.append({
                'skill': row['skill'],
                'priority': 'High' if row['priority_score'] > 0.7 else 'Medium',
                'estimated_salary_boost': f"${row['salary_impact']*10000:.0f}",
                'market_demand': f"{row['demand_frequency']*100:.0f}%"
            })
        
        return recommendations

if __name__ == "__main__":
    analyzer = SkillGapAnalyzer()
    
    # Mock data
    current_skills = ['Python', 'SQL', 'Pandas']
    target_role_skills = ['Python', 'SQL', 'Pandas', 'AWS', 'Spark', 'Docker']
    
    market_data = pd.DataFrame({
        'demand_frequency': [0.85, 0.92, 0.78],
        'salary_premium': [0.75, 0.88, 0.65],
        'market_growth': [0.80, 0.85, 0.70],
        'centrality_score': [0.70, 0.82, 0.68]
    }, index=['AWS', 'Spark', 'Docker'])
    
    # Analyze gaps
    gaps = analyzer.analyze_gaps(current_skills, target_role_skills, market_data)
    print("\nSkill Gap Analysis:")
    print(gaps)
    
    # Get recommendations
    recommendations = analyzer.get_learning_recommendations(gaps)
    print("\nLearning Recommendations:")
    for rec in recommendations:
        print(f"- {rec['skill']}: {rec['priority']} priority, "
              f"Salary boost: {rec['estimated_salary_boost']}")
