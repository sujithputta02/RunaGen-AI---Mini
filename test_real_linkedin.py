#!/usr/bin/env python3
"""
Test LinkedIn Scraper with Real Profile
"""
import sys
sys.path.insert(0, 'src')

from features.linkedin_scraper_selenium import get_selenium_scraper

# Test with a real public LinkedIn profile
# Using Satya Nadella's public profile as example
linkedin_url = "https://www.linkedin.com/in/satyanadella"

print("\n" + "="*70)
print("Testing LinkedIn Selenium Scraper with Real Profile")
print("="*70)
print(f"\nProfile: {linkedin_url}")
print("\n🔍 Starting scrape...")

try:
    scraper = get_selenium_scraper(headless=True)
    profile_data = scraper.scrape_public_profile(linkedin_url)
    
    print("\n✅ Scraping Complete!")
    print("="*70)
    
    print(f"\n👤 Name: {profile_data.get('name', 'Not found')}")
    print(f"💼 Headline: {profile_data.get('headline', 'Not found')}")
    
    print(f"\n📜 Certifications ({len(profile_data.get('certifications', []))}):")
    for cert in profile_data.get('certifications', [])[:5]:
        print(f"  - {cert.get('name')} ({cert.get('issuer')})")
    
    print(f"\n🛠️ Skills ({len(profile_data.get('skills', []))}):")
    for skill in profile_data.get('skills', [])[:10]:
        print(f"  - {skill}")
    
    print(f"\n💼 Experience ({len(profile_data.get('experience', []))}):")
    for exp in profile_data.get('experience', [])[:3]:
        print(f"  - {exp.get('title')} at {exp.get('company')}")
    
    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70 + "\n")
    
    scraper.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
