"""
Comprehensive Job Roles Taxonomy
Covers all major career categories and roles
"""

# Comprehensive job role queries for data collection
JOB_ROLES_TAXONOMY = {
    "Technology & Engineering": [
        # Software Development
        "software engineer",
        "software developer",
        "full stack developer",
        "frontend developer",
        "backend developer",
        "mobile developer",
        "ios developer",
        "android developer",
        "web developer",
        "game developer",
        "embedded systems engineer",
        
        # Data & AI
        "data scientist",
        "data analyst",
        "data engineer",
        "machine learning engineer",
        "ml engineer",
        "ai engineer",
        "deep learning engineer",
        "nlp engineer",
        "computer vision engineer",
        "research scientist",
        "data architect",
        "business intelligence analyst",
        "analytics engineer",
        
        # DevOps & Infrastructure
        "devops engineer",
        "site reliability engineer",
        "cloud engineer",
        "infrastructure engineer",
        "platform engineer",
        "systems engineer",
        "network engineer",
        "security engineer",
        "cybersecurity analyst",
        
        # Specialized Tech
        "blockchain developer",
        "qa engineer",
        "test automation engineer",
        "solutions architect",
        "technical architect",
        "database administrator",
        "system administrator",
    ],
    
    "Product & Design": [
        "product manager",
        "product owner",
        "technical product manager",
        "ux designer",
        "ui designer",
        "ux researcher",
        "product designer",
        "graphic designer",
        "visual designer",
        "interaction designer",
        "service designer",
    ],
    
    "Business & Management": [
        "business analyst",
        "management consultant",
        "strategy consultant",
        "operations manager",
        "project manager",
        "program manager",
        "scrum master",
        "agile coach",
        "business development manager",
        "account manager",
        "relationship manager",
    ],
    
    "Sales & Marketing": [
        "sales representative",
        "account executive",
        "sales engineer",
        "sales manager",
        "marketing manager",
        "digital marketing specialist",
        "content marketing manager",
        "seo specialist",
        "social media manager",
        "brand manager",
        "growth hacker",
        "marketing analyst",
    ],
    
    "Finance & Accounting": [
        "financial analyst",
        "accountant",
        "auditor",
        "tax consultant",
        "investment banker",
        "financial advisor",
        "risk analyst",
        "compliance officer",
        "controller",
        "treasurer",
        "quantitative analyst",
    ],
    
    "Healthcare & Medical": [
        "registered nurse",
        "physician",
        "surgeon",
        "pharmacist",
        "medical technologist",
        "physical therapist",
        "occupational therapist",
        "radiologist",
        "dentist",
        "healthcare administrator",
        "clinical research coordinator",
    ],
    
    "Education & Training": [
        "teacher",
        "professor",
        "instructor",
        "tutor",
        "curriculum developer",
        "instructional designer",
        "training specialist",
        "education consultant",
    ],
    
    "Human Resources": [
        "hr manager",
        "recruiter",
        "talent acquisition specialist",
        "hr business partner",
        "compensation analyst",
        "learning and development specialist",
        "organizational development consultant",
    ],
    
    "Legal & Compliance": [
        "lawyer",
        "attorney",
        "legal counsel",
        "paralegal",
        "compliance manager",
        "contract manager",
        "legal analyst",
    ],
    
    "Creative & Media": [
        "content writer",
        "copywriter",
        "technical writer",
        "editor",
        "journalist",
        "video editor",
        "photographer",
        "animator",
        "illustrator",
    ],
    
    "Operations & Logistics": [
        "operations analyst",
        "supply chain manager",
        "logistics coordinator",
        "warehouse manager",
        "procurement specialist",
        "inventory manager",
    ],
    
    "Customer Service & Support": [
        "customer service representative",
        "customer success manager",
        "technical support specialist",
        "help desk technician",
        "support engineer",
    ],
    
    "Research & Science": [
        "research analyst",
        "laboratory technician",
        "scientist",
        "biomedical engineer",
        "chemical engineer",
        "mechanical engineer",
        "civil engineer",
        "electrical engineer",
    ],
    
    "Administrative & Office": [
        "administrative assistant",
        "executive assistant",
        "office manager",
        "receptionist",
        "data entry specialist",
    ],
}

# Flatten all roles into a single list
ALL_JOB_ROLES = []
for category, roles in JOB_ROLES_TAXONOMY.items():
    ALL_JOB_ROLES.extend(roles)

# Priority roles (most common/important)
PRIORITY_ROLES = [
    # Tech
    "software engineer", "data scientist", "data engineer", "data analyst",
    "machine learning engineer", "devops engineer", "frontend developer",
    "backend developer", "full stack developer", "cloud engineer",
    
    # Business
    "product manager", "business analyst", "project manager",
    "account manager", "sales representative",
    
    # Finance
    "financial analyst", "accountant",
    
    # Other
    "marketing manager", "hr manager", "customer service representative",
]

# Get role count
TOTAL_ROLES = len(ALL_JOB_ROLES)
TOTAL_CATEGORIES = len(JOB_ROLES_TAXONOMY)

def get_roles_by_category(category):
    """Get all roles for a specific category"""
    return JOB_ROLES_TAXONOMY.get(category, [])

def get_all_categories():
    """Get all category names"""
    return list(JOB_ROLES_TAXONOMY.keys())

def get_priority_roles():
    """Get priority roles for quick collection"""
    return PRIORITY_ROLES

def get_all_roles():
    """Get all roles across all categories"""
    return ALL_JOB_ROLES

if __name__ == "__main__":
    print(f"Total Categories: {TOTAL_CATEGORIES}")
    print(f"Total Roles: {TOTAL_ROLES}")
    print("\nCategories:")
    for category, roles in JOB_ROLES_TAXONOMY.items():
        print(f"  {category}: {len(roles)} roles")
