#!/usr/bin/env python3
"""
Tests for the Dublin Core Metadata Enhancer
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from metadata_enhancer import MetadataEnhancer


class TestMetadataEnhancer(unittest.TestCase):
    """Test cases for the MetadataEnhancer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = MetadataEnhancer("test-api-key")

        # Sample metadata object for testing
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
            "object_thumb": "https://upload.wikimedia.org/wikipedia/en/a/a9/Example.jpg",
        }

    def test_get_metadata_for_prompt(self):
        """Test metadata extraction for prompt generation."""
        result = self.enhancer.get_metadata_for_prompt(self.sample_object)

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
        metadata = self.enhancer.get_metadata_for_prompt(self.sample_object)
        prompt = self.enhancer.build_prompt(metadata)

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
        prompt = self.enhancer.build_prompt(minimal_metadata)

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

        prompt = self.enhancer.build_prompt(metadata_with_strings)
        self.assertIn("single subject", prompt)
        self.assertIn("single creator", prompt)

    @patch("requests.get")
    def test_load_metadata(self, mock_get):
        """Test metadata loading from URL."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"objects": [self.sample_object]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.enhancer.load_metadata("https://forschung.stadtgeschichtebasel.ch/assets/data/metadata.json")

        self.assertEqual(result["objects"], [self.sample_object])
        mock_get.assert_called_once_with("https://forschung.stadtgeschichtebasel.ch/assets/data/metadata.json")

    @patch("requests.get")
    def test_get_image_bytes(self, mock_get):
        """Test image downloading."""
        # Mock image response
        mock_response = Mock()
        mock_response.content = b"fake_image_data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.enhancer.get_image_bytes("https://example.com/test.jpg")

        self.assertEqual(result, b"fake_image_data")
        mock_get.assert_called_once_with("https://example.com/test.jpg")

    def test_main_function_no_api_key(self):
        """Test main function behavior when no API key is provided."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove OPENAI_API_KEY if it exists
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]

            from metadata_enhancer import main

            result = main()
            self.assertEqual(result, 1)  # Should return error code


if __name__ == "__main__":
    unittest.main()
