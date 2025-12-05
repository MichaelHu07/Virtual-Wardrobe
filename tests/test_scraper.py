import unittest
from app.services.scraper.parsers.heuristics import ContentParser

class TestHeuristics(unittest.TestCase):
    def test_material_extraction(self):
        text = "This shirt is made of 100% Cotton and feels great."
        result = ContentParser.extract_materials(text)
        self.assertEqual(result, "100% Cotton")
        
        text_mixed = "Blend: 50% Polyester / 50% Cotton"
        result_mixed = ContentParser.extract_materials(text_mixed)
        # Regex might return list, joined by comma
        self.assertTrue("50% Polyester" in result_mixed)
        self.assertTrue("50% Cotton" in result_mixed)

    def test_size_normalization(self):
        raw = [" Small ", "XL", "42"]
        normalized = ContentParser.normalize_sizes(raw)
        self.assertIn("S", normalized)
        self.assertIn("XL", normalized)
        self.assertIn("42", normalized)

    def test_stretchiness(self):
        high = "Contains 5% Spandex"
        self.assertEqual(ContentParser.estimate_stretchiness(high), 0.8)
        
        low = "100% Cotton rigid denim"
        self.assertEqual(ContentParser.estimate_stretchiness(low), 0.1)

if __name__ == '__main__':
    unittest.main()

