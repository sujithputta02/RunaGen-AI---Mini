import re

class CertificateValidator:
    def __init__(self):
        # Trusted issuers with their baseline reliability scores
        self.TRUSTED_ISSUERS = {
            'Amazon Web Services': 0.95,
            'AWS': 0.95,
            'Google': 0.95,
            'GCP': 0.95,
            'Microsoft': 0.95,
            'Azure': 0.95,
            'IBM': 0.90,
            'Oracle': 0.85,
            'Cisco': 0.90,
            'Udemy': 0.40,  # Lower, as they are often unproctored
            'Coursera': 0.70, # Higher for professional certificates
            'LinkedIn': 0.40,
            'EdX': 0.70,
            'Pluralsight': 0.60,
            'PMP': 0.95,
            'Project Management Institute': 0.95,
            'Scrum.org': 0.90,
            'CompTIA': 0.90,
            'Salesforce': 0.95,
            'Red Hat': 0.95,
            'HashiCorp': 0.90
        }

    def validate(self, certificates, skills=None):
        """
        Evaluate extracted certificates and assign a validation status.
        Args:
            certificates (list): List of certificate objects
            skills (list, optional): List of extracted skills for cross-verification
        """
        validated_certs = []
        if not certificates:
            return validated_certs
        
        user_skills_lower = [s.lower() for s in skills] if skills else []

        for cert in certificates:
            if not isinstance(cert, dict):
                continue

            name = cert.get('name', 'Unknown Certificate')
            issuer = cert.get('issuer', 'Unknown')
            year = cert.get('year')
            v_id = cert.get('verification_id')
            
            # Default reliability score
            score = 0.5 
            
            # 1. Authority/Issuer Check
            issuer_match = False
            for trusted_issuer, base_score in self.TRUSTED_ISSUERS.items():
                if trusted_issuer.lower() in issuer.lower() or trusted_issuer.lower() in name.lower():
                    score = max(score, base_score)
                    issuer_match = True
            
            # 2. Skill Alignment Bonus (New: Cross-verification)
            # If the certificate name matches a skill they already have, it's more plausible
            if user_skills_lower:
                cert_words = set(re.findall(r'\w+', name.lower()))
                matching_skills = [s for s in user_skills_lower if s in cert_words]
                if matching_skills:
                    score += 0.1 # Plausibility bonus
            
            # 3. Verification ID bonus
            if v_id and len(str(v_id)) > 5:
                score += 0.15
            
            # 4. Plausibility Check (Heuristic)
            if any(term in name.lower() for term in ['phd', 'doctorate', 'degree']) and issuer_match:
                if not any(edu in issuer.lower() for edu in ['university', 'college', 'institute']):
                     score -= 0.3
            
            # 5. Active Link Check
            if v_id and ('http' in str(v_id) or '.com' in str(v_id)):
                score += 0.1
            
            # Ensure score stays in bounds
            score = max(0.1, min(0.99, score))
            
            # 6. Status Determination
            if score >= 0.85:
                status = "Verified"
                color = "green"
            elif score >= 0.65: # Adjusted threshold for Likelihood
                status = "Likely Authentic"
                color = "yellow"
            elif score >= 0.40:
                status = "Unverified"
                color = "gray"
            else:
                status = "Flagged/Suspicious"
                color = "red"
            
            validated_certs.append({
                "name": name,
                "issuer": issuer,
                "year": year,
                "verification_id": v_id,
                "score": round(score, 2),
                "status": status,
                "status_color": color
            })
            
        return validated_certs

if __name__ == "__main__":
    # Test validator
    validator = CertificateValidator()
    test_certs = [
        {"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "year": "2023", "verification_id": "ABC-123"},
        {"name": "Python for Everybody", "issuer": "Coursera", "year": "2022", "verification_id": None},
        {"name": "Complete Web Dev", "issuer": "Udemy", "year": "2021", "verification_id": "UD-999"},
        {"name": "PhD in Hacking", "issuer": "Anonymous", "year": "2025", "verification_id": "FAKE-ID"}
    ]
    results = validator.validate(test_certs)
    import json
    print(json.dumps(results, indent=2))
