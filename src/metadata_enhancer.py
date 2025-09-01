#!/usr/bin/env python3
"""
Dublin Core Metadata Enhancer

This module provides functionality to enhance Dublin Core metadata records
by generating WCAG 2.2-compliant alternative text for images and Iconclass
subject classifications using OpenAI's GPT-5 model.
"""

import json
import os
from typing import Any

# Import modules with proper path handling
try:
    from .alt_text_generator import AltTextGenerator
    from .common import (
        FilenameGenerator,
        JSONLDFormatter,
        LoggingMixin,
        MetadataLoaderMixin,
    )
    from .iconclass_classifier import IconclassClassifier
except ImportError:
    # Fallback for direct execution
    from alt_text_generator import AltTextGenerator
    from common import (
        FilenameGenerator,
        JSONLDFormatter,
        LoggingMixin,
        MetadataLoaderMixin,
    )
    from iconclass_classifier import IconclassClassifier


class MetadataEnhancer(MetadataLoaderMixin, LoggingMixin):
    """Main class for enhancing Dublin Core metadata with AI-generated content."""

    def __init__(self, openai_api_key: str):
        """
        Initialize the metadata enhancer.

        Args:
            openai_api_key: OpenAI API key for GPT-5 access
        """
        self.openai_api_key = openai_api_key
        self.logger = None
        self.iconclass_enabled = os.getenv("ICONCLASS_ENABLE", "true").lower() == "true"

        # Initialize OpenAI client
        try:
            import openai

            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        except ImportError as err:
            raise ImportError(
                "OpenAI package is required. Install with: pip install openai"
            ) from err

        # Initialize generators
        self.alt_text_generator = None
        self.iconclass_classifier = None

    def _get_generators(self):
        """Initialize generators if not already done."""
        if self.alt_text_generator is None:
            self.alt_text_generator = AltTextGenerator(self.openai_client, self.logger)

        if self.iconclass_enabled and self.iconclass_classifier is None:
            self.iconclass_classifier = IconclassClassifier(
                self.openai_client, self.logger
            )

    def enhance_metadata(
        self, metadata_source: str, output_file: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Main method to enhance metadata for all objects.

        Args:
            metadata_source: Path to local JSON file or URL to the metadata JSON file
            output_file: Optional output file name. If None, generated automatically.

        Returns:
            List of enhanced metadata objects
        """
        # Generate filenames if not provided
        if output_file is None:
            output_file, log_file = FilenameGenerator.generate_filenames(
                metadata_source
            )
        else:
            # Still generate log filename based on output file
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            from pathlib import Path

            base_name = Path(output_file).stem
            log_file = f"{base_name}_processing_{timestamp}.log"

        # Setup logging
        self.logger = self._setup_logging(log_file)

        self.logger.info(f"Loading metadata from {metadata_source}...")
        data = self.load_metadata(metadata_source)
        objects = data.get("objects", [])

        # Initialize generators
        self._get_generators()

        results = []

        for i, obj in enumerate(objects):
            obj_id = obj.get("objectid", "unknown")
            self.logger.info(f"Processing object {i + 1}/{len(objects)}: {obj_id}")

            try:
                # Generate alt text
                self.logger.info("Generating alt text...")
                alt_text_result = self.alt_text_generator.generate_for_object(obj)

                # Check for empty response
                if not alt_text_result or "alt_text" not in alt_text_result:
                    raise ValueError("Alt text generation failed")

                # Add Iconclass subject classification if enabled
                if self.iconclass_enabled and self.iconclass_classifier:
                    self.logger.info("Generating Iconclass subjects...")
                    try:
                        subjects = self.iconclass_classifier.classify_object(obj)
                        alt_text_result["subjects"] = subjects
                        self.logger.info(
                            f"Generated {len(subjects)} Iconclass subjects"
                        )
                    except Exception as e:
                        self.logger.warning(f"Iconclass classification failed: {e}")
                        # Continue without subjects - don't fail the entire process

                results.append(alt_text_result)
                alt_preview = alt_text_result.get("alt_text", "")[:50]
                self.logger.info(f"Generated alt text: {alt_preview}...")

            except Exception as e:
                self.logger.error(f"Error processing object: {e}")
                continue

        # Format as JSON-LD and save results
        self.logger.info(f"Formatting {len(results)} enhanced objects as JSON-LD")
        formatted_output = JSONLDFormatter.format_output(results)

        self.logger.info(f"Saving enhanced metadata to {output_file}")
        with open(output_file, "w", encoding="utf8") as f:
            json.dump(formatted_output, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Processing complete. Log saved to {log_file}")
        return results

    # Backward compatibility methods for existing tests
    def get_metadata_for_prompt(self, obj: dict[str, Any]) -> dict[str, Any]:
        """Backward compatibility wrapper."""
        self._get_generators()
        return self.alt_text_generator.get_metadata_for_prompt(obj)

    def build_prompt(self, metadata: dict[str, Any]) -> str:
        """Backward compatibility wrapper."""
        self._get_generators()
        return self.alt_text_generator.build_prompt(metadata)

    def get_image_bytes(self, url: str) -> bytes:
        """Backward compatibility wrapper."""
        self._get_generators()
        return self.alt_text_generator.get_image_bytes(url)


def main() -> int:
    """Main entry point for the metadata enhancer.

    Returns:
        Exit code: 0 for success, 1 for error
    """
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key as an environment variable:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1

    # Default metadata source from the issue
    metadata_source = (
        "https://forschung.stadtgeschichtebasel.ch/assets/data/metadata.json"
    )

    enhancer = MetadataEnhancer(api_key)

    try:
        results = enhancer.enhance_metadata(metadata_source)
        print(f"✓ Successfully enhanced {len(results)} metadata objects")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
