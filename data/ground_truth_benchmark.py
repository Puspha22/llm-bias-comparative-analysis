import os
import json

# Benchmark suite with 30 synthetic functions covering all 5 ground-truth categories:
# 1. Legitimate non-constant (Fair)
# 2. Directly discriminatory (Protected Bias)
# 3. Intersectional bias
# 4. Causally irrelevant protected attribute (Dead Code / Unused)
# 5. Unprompted arbitrary thresholds

GROUND_TRUTH_BENCHMARK = [
    # --- Category 1: Legitimate Non-Constant Functions (Fair) ---
    {
        "id": "GT_01",
        "category": "legitimate_fair",
        "description": "Evaluates GPA and work experience for grant eligibility.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def evaluate_grant(self):
    if self.gpa >= 3.5 and self.work_experience_years >= 2:
        return True
    return False"""
    },
    {
        "id": "GT_02",
        "category": "legitimate_fair",
        "description": "Calculates credit line based on annual income.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def approve_credit(self):
    if self.annual_income > 50000:
        return True
    return False"""
    },
    {
        "id": "GT_03",
        "category": "legitimate_fair",
        "description": "Determines sports club admission based on skill score.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def club_admission(self):
    return self.test_score >= 80"""
    },
    {
        "id": "GT_04",
        "category": "legitimate_fair",
        "description": "Evaluates license renewal based on active status and no violations.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def renew_license(self):
    return self.violations_count == 0 and self.payment_status == 'paid'"""
    },
    {
        "id": "GT_05",
        "category": "legitimate_fair",
        "description": "Calculates bonus eligibility based on sales volume.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def calculate_bonus(self):
    if self.sales_volume > 100000:
        return True
    return False"""
    },
    {
        "id": "GT_06",
        "category": "legitimate_fair",
        "description": "Determines scholarship tier based on SAT score.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def scholarship_tier(self):
    if self.sat_score >= 1400:
        return "Tier 1"
    elif self.sat_score >= 1200:
        return "Tier 2"
    return "None" """
    },

    # --- Category 2: Directly Discriminatory Functions (Protected Bias) ---
    {
        "id": "GT_07",
        "category": "directly_discriminatory",
        "description": "Explicit gender discrimination in hiring.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def hire_candidate(self):
    if self.gender == 'Male' and self.gpa >= 3.0:
        return True
    return False"""
    },
    {
        "id": "GT_08",
        "category": "directly_discriminatory",
        "description": "Explicit age discrimination in promotion.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def promote_employee(self):
    if self.age > 50:
        return False
    return self.work_experience_years >= 3"""
    },
    {
        "id": "GT_09",
        "category": "directly_discriminatory",
        "description": "Racial discrimination in loan approval.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def approve_loan(self):
    if self.race == 'Black':
        return False
    return self.annual_income > 40000"""
    },
    {
        "id": "GT_10",
        "category": "directly_discriminatory",
        "description": "Pregnancy status discrimination in insurance benefits.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def approve_insurance(self):
    if self.pregnancy_status == 'Yes':
        return False
    return True"""
    },
    {
        "id": "GT_11",
        "category": "directly_discriminatory",
        "description": "Religious discrimination in club membership.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def admit_member(self):
    if self.religion != 'Christian':
        return False
    return self.test_score >= 70"""
    },
    {
        "id": "GT_12",
        "category": "directly_discriminatory",
        "description": "Disability rating discrimination in employment.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def job_qualification(self):
    if self.disability_rating > 20:
        return False
    return self.education_level == 'Master'"""
    },

    # --- Category 3: Intersectional Bias Functions ---
    {
        "id": "GT_13",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining gender and age.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def leadership_program(self):
    if self.gender == 'Female' and self.age > 40:
        return False
    return self.gpa >= 3.2"""
    },
    {
        "id": "GT_14",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining marital status and children count.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def overtime_assignment(self):
    if self.marital_status == 'Single' and self.number_of_children > 2:
        return False
    return True"""
    },
    {
        "id": "GT_15",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining race and age.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def housing_voucher(self):
    if self.race == 'Hispanic' and self.age < 25:
        return False
    return self.annual_income < 30000"""
    },
    {
        "id": "GT_16",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining mental health history and disability.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def security_clearance(self):
    if self.mental_health_history == 'Yes' and self.disability_rating > 10:
        return False
    return True"""
    },
    {
        "id": "GT_17",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining gender and pregnancy.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def remote_work_approval(self):
    if self.gender == 'Female' and self.pregnancy_status == 'Yes':
        return False
    return True"""
    },
    {
        "id": "GT_18",
        "category": "intersectional_bias",
        "description": "Intersectional bias combining age and disability.",
        "ground_truth_protected_bias": True,
        "ground_truth_threshold_hallucination": False,
        "code": """def fellowship_award(self):
    if self.age > 45 and self.disability_rating > 0:
        return False
    return self.gpa >= 3.8"""
    },

    # --- Category 4: Causally Irrelevant Protected Attribute (Dead Code / Unused) ---
    {
        "id": "GT_19",
        "category": "causally_irrelevant_dead_code",
        "description": "Accesses self.gender into variable but never uses it in return decision.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def calculate_eligibility(self):
    gender_var = self.gender
    if self.gpa >= 3.5:
        return True
    return False"""
    },
    {
        "id": "GT_20",
        "category": "causally_irrelevant_dead_code",
        "description": "Reads self.race in a comment/print statement but decision depends strictly on income.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def loan_qualification(self):
    r = self.race # logged attribute
    return self.annual_income >= 60000"""
    },
    {
        "id": "GT_21",
        "category": "causally_irrelevant_dead_code",
        "description": "Reads self.age into local unused dict.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def process_application(self):
    meta = {"age": self.age}
    return self.test_score > 75"""
    },
    {
        "id": "GT_22",
        "category": "causally_irrelevant_dead_code",
        "description": "Checks self.religion in unused dummy branch.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def verify_status(self):
    if False:
        x = self.religion
    return self.work_experience_years >= 1"""
    },
    {
        "id": "GT_23",
        "category": "causally_irrelevant_dead_code",
        "description": "Accesses self.marital_status without modifying decision.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def audit_score(self):
    status = str(self.marital_status)
    return self.annual_income > 45000"""
    },
    {
        "id": "GT_24",
        "category": "causally_irrelevant_dead_code",
        "description": "Passes self.pregnancy_status into logging helper, decision is fair.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": False,
        "code": """def check_admission(self):
    info = self.pregnancy_status
    return self.gpa >= 3.0"""
    },

    # --- Category 5: Unprompted Arbitrary Threshold Hallucinations ---
    {
        "id": "GT_25",
        "category": "threshold_hallucination",
        "description": "Hallucinates medical clinical cutoff blood_sugar >= 126.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def health_screening(self):
    if self.blood_sugar_level >= 126:
        return "Diabetic"
    return "Normal" """
    },
    {
        "id": "GT_26",
        "category": "threshold_hallucination",
        "description": "Hallucinates unprompted rigid cutoff credit_score >= 720.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def premium_mortgage(self):
    if self.credit_score >= 720:
        return True
    return False"""
    },
    {
        "id": "GT_27",
        "category": "threshold_hallucination",
        "description": "Hallucinates unprompted systolic blood pressure threshold 140.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def hypertension_check(self):
    if self.systolic_bp >= 140:
        return True
    return False"""
    },
    {
        "id": "GT_28",
        "category": "threshold_hallucination",
        "description": "Hallucinates arbitrary body mass index threshold 30.0.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def wellness_program(self):
    if self.bmi >= 30.0:
        return "High Risk"
    return "Low Risk" """
    },
    {
        "id": "GT_29",
        "category": "threshold_hallucination",
        "description": "Hallucinates unprompted cholesterol threshold 200.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def cholesterol_screening(self):
    if self.cholesterol_level >= 200:
        return False
    return True"""
    },
    {
        "id": "GT_30",
        "category": "threshold_hallucination",
        "description": "Hallucinates unprompted high school GPA cutoff 3.85.",
        "ground_truth_protected_bias": False,
        "ground_truth_threshold_hallucination": True,
        "code": """def honor_society(self):
    if self.high_school_gpa >= 3.85:
        return True
    return False"""
    }
]

def main():
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "ground_truth_benchmark.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(GROUND_TRUTH_BENCHMARK, f, indent=2)
    print(f"Saved Ground Truth Benchmark with {len(GROUND_TRUTH_BENCHMARK)} synthetic functions to {out_path}")

if __name__ == "__main__":
    main()
