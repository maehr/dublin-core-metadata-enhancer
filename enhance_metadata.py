#!/usr/bin/env python3
"""
CLI interface for the Dublin Core Metadata Enhancer

This script provides a command-line interface to enhance Dublin Core metadata
by generating alternative text for images using OpenAI's newest GPT-5 model.
"""

import argparse
import os
import sys

from src.metadata_enhancer import MetadataEnhancer


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code: 0 for success, 1 for error
    """
    parser = argparse.ArgumentParser(
        description="Enhance Dublin Core metadata with AI-generated alt text"
    )

    parser.add_argument(
        "--metadata-url",
        default="https://forschung.stadtgeschichtebasel.ch/assets/data/metadata.json",
        help="Path to local JSON file or URL to the metadata JSON file "
        "(default: %(default)s)",
    )

    parser.add_argument(
        "--output",
        default="alttexte_automatisch.json",
        help="Output file for enhanced metadata (default: %(default)s)",
    )

    parser.add_argument(
        "--api-key",
        help="OpenAI API key (alternatively set OPENAI_API_KEY environment variable)",
    )

    args = parser.parse_args()

    # Get API key from argument or environment
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required")
        print(
            "Either use --api-key argument or set OPENAI_API_KEY environment variable"
        )
        return 1

    try:
        enhancer = MetadataEnhancer(api_key)
        results = enhancer.enhance_metadata(args.metadata_url, args.output)
        print(f"✓ Successfully enhanced {len(results)} metadata objects")
        print(f"✓ Results saved to {args.output}")
        return 0
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
