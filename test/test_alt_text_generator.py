#!/usr/bin/env python3
"""
Tests for the Alt Text Generator
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from alt_text_generator import AltTextGenerator


class TestAltTextGenerator(unittest.TestCase):
    """Test cases for the AltTextGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock OpenAI client
        self.mock_openai_client = Mock()
        self.generator = AltTextGenerator(self.mock_openai_client)

        # Sample object for testing
        self.sample_object = {
            "objectid": "test001",
            "title": "Test Image",
            "description": "A test image for unit testing",
            "subject": ["testing", "metadata"],
            "coverage": "modern",
            "creator": ["Test Author"],
            "date": "2024",
            "isPartOf": ["Test Collection"],
            "relation": ["test-relation"],
            "language": "de",
            "object_thumb": "https://forschung.stadtgeschichtebasel.ch/objects/test.jpg",
        }

    def test_get_metadata_for_prompt(self):
        """Test metadata extraction for prompt generation."""
        result = self.generator.get_metadata_for_prompt(self.sample_object)

        # Check that all expected keys are present
        expected_keys = [
            "objectid",
            "title",
            "description",
            "subject",
            "coverage",
            "creator",
            "date",
            "isPartOf",
            "relation",
            "language",
            "object_thumb",
        ]

        for key in expected_keys:
            self.assertIn(key, result)

        # Check specific values
        self.assertEqual(result["objectid"], "test001")
        self.assertEqual(result["title"], "Test Image")
        self.assertEqual(result["subject"], ["testing", "metadata"])

    def test_build_prompt(self):
        """Test prompt building functionality."""
        metadata = self.generator.get_metadata_for_prompt(self.sample_object)
        prompt = self.generator.build_prompt(metadata)

        # Check that prompt contains expected elements
        self.assertIn("WCAG", prompt)
        self.assertIn("forschung.stadtgeschichtebasel.ch", prompt)
        self.assertIn("Test Image", prompt)
        self.assertIn("testing, metadata", prompt)
        self.assertIn("objectid", prompt)
        self.assertIn("JSON", prompt)

    def test_build_prompt_handles_empty_fields(self):
        """Test that prompt building handles empty or missing fields gracefully."""
        minimal_metadata = {"objectid": "test002"}
        prompt = self.generator.build_prompt(minimal_metadata)

        # Should not crash and should contain the objectid
        self.assertIn("test002", prompt)
        self.assertIn("WCAG", prompt)

    def test_build_prompt_handles_string_lists(self):
        """Test that prompt building handles both string and list values."""
        # Test with string instead of list
        metadata_with_strings = {
            "objectid": "test003",
            "subject": "single subject",
            "creator": "single creator",
            "isPartOf": "single collection",
            "relation": "single relation",
        }

        prompt = self.generator.build_prompt(metadata_with_strings)
        self.assertIn("single subject", prompt)
        self.assertIn("single creator", prompt)

    @patch("requests.get")
    def test_get_image_bytes(self, mock_get):
        """Test image downloading."""
        # Mock image response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.generator.get_image_bytes("https://example.com/test.jpg")

        self.assertEqual(result, b"fake_image_data")
        mock_get.assert_called_once_with("https://example.com/test.jpg")

    def test_generate_alt_text_no_client(self):
        """Test alt text generation when no OpenAI client is provided."""
        generator_no_client = AltTextGenerator(None)

        with self.assertRaises(ValueError) as cm:
            generator_no_client.generate_alt_text({}, b"image_data")

        self.assertIn("OpenAI client is required", str(cm.exception))

    def test_generate_alt_text_with_mock_client(self):
        """Test alt text generation with mock OpenAI client."""
        # Mock OpenAI response
        mock_choice = Mock()
        mock_choice.message.content = (
            '{"objectid": "test001", "alt_text": "Test alt text"}'
        )

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        self.mock_openai_client.chat.completions.create.return_value = mock_response

        metadata = self.generator.get_metadata_for_prompt(self.sample_object)
        result = self.generator.generate_alt_text(metadata, b"fake_image_data")

        self.assertEqual(result["objectid"], "test001")
        self.assertEqual(result["alt_text"], "Test alt text")

    @patch("requests.get")
    def test_generate_for_object(self, mock_get):
        """Test complete object processing."""
        # Mock image download
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Mock OpenAI response
        mock_choice = Mock()
        mock_choice.message.content = (
            '{"objectid": "test001", "alt_text": "Generated alt text"}'
        )

        mock_openai_response = Mock()
        mock_openai_response.choices = [mock_choice]
        mock_openai_response.id = "test_response_id"
        mock_openai_response.model = "gpt-5"
        mock_openai_response.usage = Mock()

        self.mock_openai_client.chat.completions.create.return_value = (
            mock_openai_response
        )

        result = self.generator.generate_for_object(self.sample_object)

        self.assertEqual(result["objectid"], "test001")
        self.assertEqual(result["alt_text"], "Generated alt text")

    def test_generate_for_object_no_image_url(self):
        """Test error handling when object has no image URL."""
        obj_without_image = {"objectid": "test002", "title": "Test without image"}

        with self.assertRaises(ValueError) as cm:
            self.generator.generate_for_object(obj_without_image)

        self.assertIn("No image URL found", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
