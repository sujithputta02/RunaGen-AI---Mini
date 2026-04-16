import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ml.model_1_skill_extraction import SkillExtractor
from ml.certificate_validator import CertificateValidator

def test_full_validation_flow():
    print("🚀 Testing Resume Certificate Validation Flow")
    print("-" * 50)
    
    # 1. Setup components
    extractor = SkillExtractor(use_ollama=False) # Use heuristic for speed in test
    validator = CertificateValidator()
    
    # 2. Sample resume with various certificate types
    test_resume = """
    John Doe - Cloud Architect
    
    SKILLS: Python, AWS, SQL, Docker, Kubernetes
    
    CERTIFICATIONS:
    - AWS Certified Solutions Architect Professional (ID: AWS-SOL-9922)
    - Google Professional Cloud Architect, 2023
    - Microsoft Azure Fundamentals (AZ-900)
    - Professional Certificate in Data Science, Coursera, 2022
    - Complete Python Bootcamp, Udemy (ID: UD-PYTHON-101)
    - Certified Ethical Hacker (CEH)
    - Master's Degree in Hacking, Anonymous Institute
    """
    
    print("📝 Extracting certificates and skills from test resume...")
    extracted_data = extractor.extract_all(test_resume)
    certs = extracted_data.get('certifications', [])
    skills = extracted_data.get('skills', [])
    
    print(f"✅ Extracted {len(certs)} certifications and {len(skills)} skills.")
    
    print("\n⚖️  Validating certifications with skill cross-referencing...")
    validated_certs = validator.validate(certs, skills=skills)
    
    print("\n📊 Validation Results:")
    print("-" * 50)
    for v_cert in validated_certs:
        status_icon = "✅" if v_cert['status'] == "Verified" else "⚠️" if v_cert['status'] == "Likely Authentic" else "❓" if v_cert['status'] == "Unverified" else "🚫"
        print(f"{status_icon} {v_cert['name']}")
        print(f"   Status: {v_cert['status']}")
        print(f"   Issuer: {v_cert['issuer']}")
        print(f"   Score:  {v_cert['score']}")
        print(f"   ID:     {v_cert['verification_id']}")
        print("-" * 30)

    # Simple assertions
    assert len(validated_certs) > 0, "No certs validated"
    print("\n✨ FULL FLOW VERIFIED SUCCESSFULLY")

if __name__ == "__main__":
    try:
        test_full_validation_flow()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
