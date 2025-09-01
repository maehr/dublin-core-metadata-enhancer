#!/usr/bin/env python3
"""
Tests for the Iconclass Classifier
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from iconclass_classifier import IconclassClassifier


class TestIconclassClassifier(unittest.TestCase):
    """Test cases for the IconclassClassifier class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenAI client
        self.mock_openai_client = Mock()
        self.classifier = IconclassClassifier(self.mock_openai_client)

        # Sample object for testing
        self.sample_object = {
            "objectid": "test001",
            "title": "Basel Stadtansicht",
            "description": "Eine historische Karte von Basel",
            "subject": ["Stadt", "Karte"],
            "coverage": "1500-1600",
            "creator": ["Merian"],
            "date": "1615",
            "language": "de",
        }

    def test_extract_keywords(self):
        """Test keyword extraction from metadata."""
        keywords = self.classifier.extract_keywords(self.sample_object)

        self.assertIn("basel", keywords)
        self.assertIn("stadtansicht", keywords)
        self.assertIn("karte", keywords)
        self.assertIn("stadt", keywords)

    def test_build_iconclass_prompt(self):
        """Test prompt building for Iconclass classification."""
        prompt = self.classifier.build_iconclass_prompt(self.sample_object)

        self.assertIn("Basel Stadtansicht", prompt)
        self.assertIn("Stadt, Karte", prompt)
        self.assertIn("Iconclass", prompt)
        self.assertIn("JSON array", prompt)

    @patch("requests.get")
    def test_validate_notation_success(self, mock_get):
        """Test successful notation validation."""
        # Mock successful Iconclass API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prefLabel": {"de": "Stadtansicht", "en": "city view"}
        }
        mock_get.return_value = mock_response

        result = self.classifier.validate_notation("25F")

        self.assertEqual(result["notation"], "25F")
        self.assertEqual(result["label_de"], "Stadtansicht")
        self.assertEqual(result["label_en"], "city view")
        self.assertEqual(result["uri"], "https://iconclass.org/25F")

    @patch("requests.get")
    def test_validate_notation_failure(self, mock_get):
        """Test notation validation with invalid notation."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.classifier.validate_notation("INVALID")

        self.assertEqual(result, {})

    def test_get_llm_candidates_no_client(self):
        """Test LLM candidates when no OpenAI client is provided."""
        classifier_no_client = IconclassClassifier(None)
        prompt = "test prompt"

        result = classifier_no_client.get_llm_candidates(prompt)

        self.assertEqual(result, [])

    def test_get_llm_candidates_with_mock_client(self):
        """Test LLM candidates with mock OpenAI client."""
        # Mock OpenAI response
        mock_choice = Mock()
        mock_choice.message.content = (
            '[{"notation":"25F","label_de":"Stadtansicht",'
            '"label_en":"city view","why":"Shows city view"}]'
        )

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        self.mock_openai_client.chat.completions.create.return_value = mock_response

        prompt = self.classifier.build_iconclass_prompt(self.sample_object)
        result = self.classifier.get_llm_candidates(prompt)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["notation"], "25F")
        self.assertEqual(result[0]["label_de"], "Stadtansicht")

    @patch.dict(os.environ, {"ICONCLASS_VALIDATE": "false"})
    def test_classify_object_without_validation(self):
        """Test object classification without notation validation."""
        # Mock LLM response
        mock_choice = Mock()
        mock_choice.message.content = (
            '[{"notation":"25F","label_de":"Stadtansicht",'
            '"label_en":"city view","why":"City view"}]'
        )

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        self.mock_openai_client.chat.completions.create.return_value = mock_response

        # Create classifier with validation disabled
        classifier = IconclassClassifier(self.mock_openai_client)

        result = classifier.classify_object(self.sample_object)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["valueURI"], "https://iconclass.org/25F")
        self.assertEqual(result[0]["notation"], "25F")
        self.assertEqual(result[0]["scheme"], "Iconclass")
        self.assertIsInstance(result[0]["confidence"], float)

    def test_configuration_environment_variables(self):
        """Test that configuration is read from environment variables."""
        with patch.dict(
            os.environ,
            {
                "ICONCLASS_TOP_K": "3",
                "ICONCLASS_LANG": "en",
                "ICONCLASS_VALIDATE": "false",
            },
        ):
            classifier = IconclassClassifier()

            self.assertEqual(classifier.top_k, 3)
            self.assertEqual(classifier.lang, "en")
            self.assertFalse(classifier.validate)


if __name__ == "__main__":
    unittest.main()
