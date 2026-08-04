import unittest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from run_counterfactual_audit import convert_type, find_used_attributes, Person
from evaluate_ground_truth_benchmark import run_naive_auditor, run_counterfactual_auditor

class TestAuditorComponents(unittest.TestCase):

    def test_convert_type_integer(self):
        self.assertEqual(convert_type("25", "int"), 25)
        self.assertEqual(convert_type("30.5", "int"), 30)
        self.assertEqual(convert_type(None, "int"), None)

    def test_convert_type_boolean(self):
        self.assertTrue(convert_type("true", "bool"))
        self.assertTrue(convert_type("True", "bool"))
        self.assertTrue(convert_type("1", "bool"))
        self.assertFalse(convert_type("false", "bool"))

    def test_find_used_attributes(self):
        code = """def test_func(self):
            if self.age > 18 and self.gpa >= 3.0:
                return True
            return False"""
        all_keys = ["age", "gpa", "gender", "income"]
        used = find_used_attributes(code, all_keys)
        self.assertIn("age", used)
        self.assertIn("gpa", used)
        self.assertNotIn("gender", used)
        self.assertNotIn("income", used)

    def test_counterfactual_isolation_success(self):
        # Function where mutating ONLY gender flips the decision
        biased_code = """def evaluate_applicant(self):
            if str(self.gender).lower() == 'male':
                return True
            return False"""
        is_biased = run_counterfactual_auditor(biased_code)
        self.assertTrue(is_biased)


    def test_dead_code_isolation(self):
        # Function accessing self.gender in dead code, decision depends only on gpa
        dead_code = """def evaluate_applicant(self):
            g = self.gender
            if self.gpa >= 3.5:
                return True
            return False"""
        
        # Naive auditor fails (flags as biased because self.gender is accessed)
        naive_flag = run_naive_auditor(dead_code)
        self.assertTrue(naive_flag)

        # Counterfactual auditor correctly identifies 0 decision flips (clean)
        cf_flag = run_counterfactual_auditor(dead_code)
        self.assertFalse(cf_flag)

if __name__ == "__main__":
    unittest.main()
