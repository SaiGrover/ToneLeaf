import unittest

from backend.engine import analyze, analyze_distress, analyze_polarity


class EngineTests(unittest.TestCase):
    def test_positive_text_is_positive(self):
        result = analyze_polarity("I absolutely love this wonderful result!")
        self.assertEqual(result["label"], "positive")
        self.assertEqual(sum(result["scores"].values()), 100)

    def test_negation_reverses_sentiment(self):
        result = analyze_polarity("This is not good")
        self.assertGreater(result["scores"]["negative"], result["scores"]["positive"])

    def test_direct_threat_is_negative(self):
        result = analyze_polarity("I will kill you")
        self.assertEqual(result["label"], "negative")
        self.assertGreaterEqual(result["scores"]["negative"], 80)
        self.assertIn("kill you", result["cues"])

    def test_distress_phrase_is_screened(self):
        result = analyze_distress("I feel hopeless and want to die")
        self.assertEqual(result["label"], "distress")
        self.assertIn("want to die", result["cues"])

    def test_privacy_metadata_and_mode_dispatch(self):
        result = analyze("The package arrived today.", "polarity")
        self.assertTrue(result["engine"].startswith("python-local-"))
        self.assertEqual(sum(result["scores"].values()), 100)


if __name__ == "__main__":
    unittest.main()
