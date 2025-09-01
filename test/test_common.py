#!/usr/bin/env python3
"""
Tests for the Common module utilities
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from common import FilenameGenerator, JSONLDFormatter, MetadataLoaderMixin


class TestMetadataLoaderMixin(unittest.TestCase):
    """Test cases for the MetadataLoaderMixin class."""

    def setUp(self):
        """Set up test fixtures."""

        class TestClass(MetadataLoaderMixin):
            pass

        self.loader = TestClass()

    @patch("requests.get")
    def test_load_metadata_from_url(self, mock_get):
        """Test metadata loading from URL."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {"objects": [{"objectid": "test001"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.loader.load_metadata("https://example.com/metadata.json")

        self.assertEqual(result["objects"], [{"objectid": "test001"}])
        mock_get.assert_called_once_with("https://example.com/metadata.json")

    def test_load_metadata_from_local_file(self):
        """Test metadata loading from local file."""
        # Use the sample file
        test_file_path = os.path.join(os.path.dirname(__file__), "sample_metadata.json")

        result = self.loader.load_metadata(test_file_path)

        self.assertIn("objects", result)
        self.assertEqual(len(result["objects"]), 1)
        self.assertEqual(result["objects"][0]["objectid"], "local_test001")

    def test_is_local_file(self):
        """Test the _is_local_file helper method."""
        # Test URLs
        self.assertFalse(self.loader._is_local_file("https://example.com/file.json"))
        self.assertFalse(self.loader._is_local_file("http://example.com/file.json"))

        # Test local paths
        test_file_path = os.path.join(os.path.dirname(__file__), "sample_metadata.json")
        self.assertTrue(self.loader._is_local_file(test_file_path))

        # Test non-existent file (should still be considered local path)
        self.assertTrue(self.loader._is_local_file("/some/local/path.json"))


class TestFilenameGenerator(unittest.TestCase):
    """Test cases for the FilenameGenerator class."""

    def test_generate_filenames_url(self):
        """Test filename generation from URL."""
        url = "https://example.com/path/to/metadata.json"
        output_file, log_file = FilenameGenerator.generate_filenames(url)

        self.assertTrue(output_file.startswith("metadata_enhanced_"))
        self.assertTrue(output_file.endswith(".jsonld"))
        self.assertTrue(log_file.startswith("metadata_processing_"))
        self.assertTrue(log_file.endswith(".log"))

    def test_generate_filenames_local_file(self):
        """Test filename generation from local file."""
        file_path = "/path/to/my_data.json"
        output_file, log_file = FilenameGenerator.generate_filenames(file_path)

        self.assertTrue(output_file.startswith("my_data_enhanced_"))
        self.assertTrue(output_file.endswith(".jsonld"))
        self.assertTrue(log_file.startswith("my_data_processing_"))
        self.assertTrue(log_file.endswith(".log"))

    def test_generate_filenames_with_suffix(self):
        """Test filename generation with custom suffix."""
        url = "https://example.com/test.json"
        output_file, log_file = FilenameGenerator.generate_filenames(url, "custom")

        self.assertTrue(output_file.startswith("test_custom_"))
        self.assertTrue(output_file.endswith(".jsonld"))


class TestJSONLDFormatter(unittest.TestCase):
    """Test cases for the JSONLDFormatter class."""

    def test_format_enhanced_object_basic(self):
        """Test basic object formatting to JSON-LD."""
        obj_data = {"objectid": "test001", "alt_text": "Test alt text"}

        result = JSONLDFormatter.format_enhanced_object(obj_data)

        self.assertEqual(result["@type"], "edm:ProvidedCHO")
        self.assertEqual(result["dc:identifier"], "test001")
        self.assertEqual(result["dc:description"]["@value"], "Test alt text")
        self.assertEqual(result["dc:description"]["@type"], "edm:AltText")

    def test_format_enhanced_object_with_subjects(self):
        """Test object formatting with Iconclass subjects."""
        obj_data = {
            "objectid": "test001",
            "alt_text": "Test alt text",
            "subjects": [
                {
                    "valueURI": "https://iconclass.org/25F",
                    "notation": "25F",
                    "prefLabel": {"de": "Stadtansicht", "en": "city view"},
                    "confidence": 0.86,
                    "scheme": "Iconclass",
                }
            ],
        }

        result = JSONLDFormatter.format_enhanced_object(obj_data)

        self.assertIn("dc:subject", result)
        subjects = result["dc:subject"]
        self.assertEqual(len(subjects), 1)
        self.assertEqual(subjects[0]["@id"], "https://iconclass.org/25F")
        self.assertEqual(subjects[0]["skos:notation"], "25F")
        self.assertEqual(subjects[0]["edm:confidence"], 0.86)

    def test_format_output(self):
        """Test complete output formatting."""
        enhanced_objects = [
            {"objectid": "test001", "alt_text": "Test alt text 1"},
            {"objectid": "test002", "alt_text": "Test alt text 2"},
        ]

        result = JSONLDFormatter.format_output(enhanced_objects)

        self.assertEqual(result["@type"], "edm:DataSet")
        self.assertIn("dc:created", result)
        self.assertIn("dc:creator", result)
        self.assertIn("edm:providedCHO", result)
        self.assertEqual(len(result["edm:providedCHO"]), 2)


if __name__ == "__main__":
    unittest.main()
