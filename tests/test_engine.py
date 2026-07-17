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

    def test_jump_and_self_harm_language_is_screened(self):
        result = analyze_distress("I will jump from the building and hit myself")
        self.assertEqual(result["label"], "distress")
        self.assertGreaterEqual(result["scores"]["distress"], 80)
        self.assertIn("jump from the building", result["cues"])
        self.assertIn("hit myself", result["cues"])

    def test_kill_me_language_is_screened(self):
        result = analyze_distress("Hello kill me")
        self.assertEqual(result["label"], "distress")
        self.assertIn("kill me", result["cues"])

    def test_poison_ingestion_is_negative_and_distress(self):
        samples = (
            "I will eat poison",
            "I will eat rat poison",
            "I will eat healthy good quality poison so that I die very quickly",
        )
        for text in samples:
            with self.subTest(text=text):
                polarity = analyze_polarity(text)
                distress = analyze_distress(text)
                self.assertEqual(polarity["label"], "negative")
                self.assertEqual(distress["label"], "distress")
                self.assertGreaterEqual(distress["scores"]["distress"], 50)

    def test_poison_storage_context_is_not_flagged(self):
        text = "The rat poison is stored in a locked cabinet."
        self.assertEqual(analyze_polarity(text)["label"], "neutral")
        self.assertEqual(analyze_distress(text)["label"], "supportive")

    def test_first_person_self_deprecation_and_runaway_intent_are_screened(self):
        for text in ("I am a complete loser", "I will run away from my family"):
            with self.subTest(text=text):
                self.assertEqual(analyze_distress(text)["label"], "distress")

    def test_context_controls_do_not_trigger_distress(self):
        for text in ("He called the movie a complete loser", "I will run away from the sprinkler"):
            with self.subTest(text=text):
                self.assertEqual(analyze_distress(text)["label"], "supportive")

    def test_common_loser_misspelling_is_negative(self):
        self.assertEqual(analyze_polarity("I am a looser")["label"], "negative")

    def test_privacy_metadata_and_mode_dispatch(self):
        result = analyze("The package arrived today.", "polarity")
        self.assertTrue(result["engine"].startswith("python-local-"))
        self.assertEqual(sum(result["scores"].values()), 100)


if __name__ == "__main__":
    unittest.main()
