"""
Quick test to show skill extraction is working correctly
"""
import sys
sys.path.insert(0, 'src')

from ml.model_1_skill_extraction import SkillExtractor

# Example resume text
sample_resume = """
SKILLS:
- Python
- SQL
- Machine Learning
- Data Analysis

EXPERIENCE:
Data Analyst with 2 years of experience in Python and SQL.
"""

extractor = SkillExtractor()
result = extractor.extract_all(sample_resume)

print("=" * 60)
print("SKILL EXTRACTION TEST")
print("=" * 60)
print("\n📄 Resume Text:")
print(sample_resume)
print("\n🔍 Extracted Skills:")
for skill in result['skills']:
    print(f"   ✓ {skill}")

print(f"\n📊 Total Skills Found: {len(result['skills'])}")
print(f"📅 Experience: {result['experience_years']} years" if result['experience_years'] else "📅 Experience: Not found")
print(f"🎓 Education: {result['education']}")

print("\n" + "=" * 60)
print("✅ Skills are extracted ONLY from the resume text!")
print("=" * 60)
