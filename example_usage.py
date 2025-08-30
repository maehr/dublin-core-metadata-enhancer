#!/usr/bin/env python3
"""
Example usage of the Dublin Core Metadata Enhancer

This example demonstrates how to use the metadata enhancement pipeline
to generate alternative text for Dublin Core metadata objects.
"""

import json
import os

from src.metadata_enhancer import MetadataEnhancer


def example_usage():
    """Example demonstrating the metadata enhancement workflow."""

    # Example metadata object (you would normally load this from a JSON file)
    sample_metadata = {
        "objects": [
            {
                "objectid": "example001",
                "title": "Stadtplan von Basel",
                "description": "Historischer Stadtplan von Basel aus dem 16. Jh.",
                "subject": ["Karten", "Basel", "Stadtgeschichte"],
                "coverage": "16. Jahrhundert",
                "creator": ["Unbekannter Kartograph"],
                "date": "1550-1600",
                "isPartOf": ["Kartensammlung Basel"],
                "relation": ["Stadtgeschichte Basel"],
                "language": "de",
                "object_thumb": "https://example.com/sample-map.jpg",
            }
        ]
    }

    print("Dublin Core Metadata Enhancer - Example Usage")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  No OpenAI API key found.")
        print("   Set OPENAI_API_KEY environment variable to run with real API calls.")
        print("   This example will show the workflow without making API calls.")
        print()

        # Demonstrate the workflow without API calls
        enhancer = MetadataEnhancer("dummy-key")

        for obj in sample_metadata["objects"]:
            print(f"Processing object: {obj['objectid']}")

            # Extract metadata for prompt
            metadata_for_prompt = enhancer.get_metadata_for_prompt(obj)
            print(f"✓ Extracted metadata: {list(metadata_for_prompt.keys())}")

            # Build prompt (this doesn't require API)
            prompt = enhancer.build_prompt(metadata_for_prompt)
            print(f"✓ Built prompt (length: {len(prompt)} characters)")
            print("Sample prompt preview:")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
            print()

            # Show what the output would look like
            example_output = {
                "objectid": obj["objectid"],
                "alt_text": "Historischer Stadtplan von Basel mit Befestigungsanlagen",
                "longdesc": "",
            }
            print("Example output format:")
            print(json.dumps(example_output, indent=2, ensure_ascii=False))
            print()

        print("To run with real API calls:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("2. Run: python enhance_metadata.py")

    else:
        print("✓ OpenAI API key found - ready for enhancement!")
        print("Note: This example uses sample data, not the real metadata URL.")
        print("Use enhance_metadata.py for the full pipeline.")


if __name__ == "__main__":
    example_usage()
