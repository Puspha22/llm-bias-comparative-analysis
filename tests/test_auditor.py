import unittest
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from logic_auditing.helper_functions import convert_type, find_used_attributes, Person, PROTECTED_ATTRIBUTES

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

    def test_protected_attribute_list(self):
        self.assertIn("age", PROTECTED_ATTRIBUTES)
        self.assertIn("gender", PROTECTED_ATTRIBUTES)
        self.assertEqual(len(PROTECTED_ATTRIBUTES), 15)

if __name__ == "__main__":
    unittest.main()
