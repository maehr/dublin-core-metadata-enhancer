#!/usr/bin/env python3
"""
Common utilities for Dublin Core metadata enhancement modules.

This module provides shared functionality used by both alt text generation
and Iconclass classification modules.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


class MetadataLoaderMixin:
    """Mixin class providing metadata loading functionality."""

    def load_metadata(self, source: str) -> dict[str, Any]:
        """
        Load metadata from a JSON file or URL.

        Args:
            source: Path to local JSON file or URL to the JSON metadata file

        Returns:
            Dictionary containing the loaded metadata
        """
        # Check if source is a local file path
        if self._is_local_file(source):
            try:
                with open(source, encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Local file not found: {source}") from e
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in local file {source}: {e}") from e
        else:
            # Treat as URL
            try:
                response = requests.get(source)
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                raise ValueError(
                    f"Failed to load metadata from URL {source}: {e}"
                ) from e
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON from URL {source}: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("Expected JSON object, got different type")
        return data

    def _is_local_file(self, source: str) -> bool:
        """
        Determine if source is a local file path or URL.

        Args:
            source: Source string to check

        Returns:
            True if it's a local file path, False if it's a URL
        """
        # Parse as URL and check if it has a scheme (http/https)
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            return False

        # Check if it's a valid file path
        path = Path(source)
        return path.exists() or not parsed.scheme


class LoggingMixin:
    """Mixin class providing logging functionality."""

    def _setup_logging(self, log_filename: str) -> logging.Logger:
        """
        Set up logging configuration.

        Args:
            log_filename: Name of the log file

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Remove any existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger


class FilenameGenerator:
    """Utility class for generating output and log filenames."""

    @staticmethod
    def generate_filenames(
        metadata_source: str, suffix: str = "enhanced"
    ) -> tuple[str, str]:
        """
        Generate output and log filenames based on input source and timestamp.

        Args:
            metadata_source: Source of metadata (file path or URL)
            suffix: Suffix to add to the output filename

        Returns:
            Tuple of (output_filename, log_filename)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract base name from source
        if FilenameGenerator._is_local_file(metadata_source):
            base_name = Path(metadata_source).stem
        else:
            # For URLs, use the last part of the path or 'metadata'
            parsed_url = urlparse(metadata_source)
            path_parts = parsed_url.path.strip("/").split("/")
            base_name = Path(path_parts[-1]).stem if path_parts[-1] else "metadata"

        output_filename = (
            f"{base_name}_{suffix}_{timestamp}.jsonld"  # Use .jsonld extension
        )
        log_filename = f"{base_name}_processing_{timestamp}.log"

        return output_filename, log_filename

    @staticmethod
    def _is_local_file(source: str) -> bool:
        """
        Determine if source is a local file path or URL.

        Args:
            source: Source string to check

        Returns:
            True if it's a local file path, False if it's a URL
        """
        # Parse as URL and check if it has a scheme (http/https)
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            return False

        # Check if it's a valid file path
        path = Path(source)
        return path.exists() or not parsed.scheme


class JSONLDFormatter:
    """Utility class for formatting output as JSON-LD with Dublin Core terms."""

    @staticmethod
    def format_enhanced_object(obj_data: dict[str, Any]) -> dict[str, Any]:
        """
        Format enhanced object data as JSON-LD with Dublin Core terms.

        Args:
            obj_data: Enhanced object data

        Returns:
            JSON-LD formatted object
        """
        # Create JSON-LD object with Dublin Core context
        jsonld_obj = {
            "@context": {
                "dc": "http://purl.org/dc/terms/",
                "dcmitype": "http://purl.org/dc/dcmitype/",
                "edm": "http://www.europeana.eu/schemas/edm/",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@type": "edm:ProvidedCHO",
            "dc:identifier": obj_data.get("objectid"),
        }

        # Add alt text as alternative description
        alt_text = obj_data.get("alt_text")
        if alt_text:
            jsonld_obj["dc:description"] = {
                "@type": "edm:AltText",
                "@value": alt_text,
                "@language": "de",
            }

        # Add long description if present
        longdesc = obj_data.get("longdesc")
        if longdesc and longdesc.strip():
            jsonld_obj["edm:isNextInSequence"] = {
                "@type": "edm:LongDescription",
                "@value": longdesc,
                "@language": "de",
            }

        # Add Iconclass subjects if present
        subjects = obj_data.get("subjects", [])
        if subjects:
            dc_subjects = []
            for subject in subjects:
                dc_subject = {
                    "@id": subject.get("valueURI"),
                    "skos:notation": subject.get("notation"),
                    "skos:prefLabel": [],
                    "edm:confidence": subject.get("confidence"),
                    "skos:inScheme": {
                        "@id": "https://iconclass.org/",
                        "skos:prefLabel": "Iconclass",
                    },
                }

                # Add multilingual labels
                pref_labels = subject.get("prefLabel", {})
                if pref_labels.get("de"):
                    dc_subject["skos:prefLabel"].append(
                        {"@value": pref_labels["de"], "@language": "de"}
                    )
                if pref_labels.get("en"):
                    dc_subject["skos:prefLabel"].append(
                        {"@value": pref_labels["en"], "@language": "en"}
                    )

                dc_subjects.append(dc_subject)

            jsonld_obj["dc:subject"] = dc_subjects

        return jsonld_obj

    @staticmethod
    def format_output(enhanced_objects: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Format complete output as timestamped JSON-LD.

        Args:
            enhanced_objects: List of enhanced objects

        Returns:
            Complete JSON-LD document
        """
        timestamp = datetime.now().isoformat()

        # Format each object
        formatted_objects = [
            JSONLDFormatter.format_enhanced_object(obj) for obj in enhanced_objects
        ]

        # Create container document
        return {
            "@context": {
                "dc": "http://purl.org/dc/terms/",
                "dcmitype": "http://purl.org/dc/dcmitype/",
                "edm": "http://www.europeana.eu/schemas/edm/",
                "foaf": "http://xmlns.com/foaf/0.1/",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@type": "edm:DataSet",
            "dc:created": {"@value": timestamp, "@type": "xsd:dateTime"},
            "dc:creator": {
                "@id": "https://github.com/maehr/dublin-core-metadata-enhancer",
                "foaf:name": "Dublin Core Metadata Enhancer",
            },
            "dc:description": (
                "Enhanced Dublin Core metadata with AI-generated alt text "
                "and Iconclass subject classification"
            ),
            "edm:providedCHO": formatted_objects,
        }
