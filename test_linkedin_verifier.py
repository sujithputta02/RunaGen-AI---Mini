#!/usr/bin/env python3
"""
Test LinkedIn Verifier
"""
import sys
sys.path.insert(0, 'src')

from features.linkedin_verifier import get_linkedin_verifier

# Sample resume text with LinkedIn URL
resume_text = """
SUJITH PUTTA
Software Engineer

Contact:
Email: sujith@example.com
LinkedIn: linkedin.com/in/sujithputta
GitHub: github.com/sujithputta

CERTIFICATIONS:
- AWS Certified Solutions Architect (2023)
- Google Cloud Professional (2022)

EXPERIENCE:
Software Engineer at Tech Corp (2020-2023)
- Developed web applications
- Worked with Python and React
"""

# Sample certifications
certifications = [
    {
        'name': 'AWS Certified Solutions Architect',
        'issuer': 'Amazon Web Services',
        'year': '2023',
        'verification_id': 'ABC123'
    },
    {
        'name': 'Google Cloud Professional',
        'issuer': 'Google',
        'year': '2022',
        'verification_id': None
    }
]

def test_linkedin_verifier():
    print("\n" + "="*70)
    print("Testing LinkedIn Verifier")
    print("="*70)
    
    verifier = get_linkedin_verifier()
    
    # Test 1: Extract social links
    print("\n📋 Test 1: Extract Social Links")
    social_links = verifier.extract_social_links(resume_text)
    print(f"LinkedIn: {social_links.get('linkedin')}")
    print(f"GitHub: {social_links.get('github')}")
    print(f"Portfolio: {social_links.get('portfolio')}")
    
    # Test 2: Get verification summary
    print("\n📋 Test 2: Get Verification Summary")
    result = verifier.get_verification_summary(resume_text, certifications)
    
    print(f"\n✅ Results:")
    print(f"  - LinkedIn Available: {result['linkedin_available']}")
    print(f"  - GitHub Available: {result['github_available']}")
    print(f"  - Portfolio Available: {result['portfolio_available']}")
    print(f"  - LinkedIn Certs Found: {result['linkedin_certifications_found']}")
    print(f"  - Verified Certifications: {len(result['verified_certifications'])}")
    print(f"  - Recommendations: {len(result['profile_recommendations'])}")
    
    print(f"\n💡 Recommendations:")
    for rec in result['profile_recommendations']:
        print(f"  - {rec}")
    
    print(f"\n📜 Verified Certifications:")
    for cert in result['verified_certifications']:
        linkedin_status = "✓ LinkedIn" if cert.get('linkedin_verified') else "Resume Only"
        print(f"  - {cert['name']} [{linkedin_status}]")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_linkedin_verifier()
