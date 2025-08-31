#!/usr/bin/env python3
"""
Dublin Core Metadata Enhancer

This module provides functionality to enhance Dublin Core metadata records
by generating WCAG 2.2-compliant alternative text for images using OpenAI's
newest GPT-5 model.
"""

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


class MetadataEnhancer:
    """Main class for enhancing Dublin Core metadata with AI-generated alt text."""

    def __init__(self, openai_api_key: str):
        """
        Initialize the metadata enhancer.

        Args:
            openai_api_key: OpenAI API key for GPT-5 access
        """
        self.openai_api_key = openai_api_key

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

    def get_metadata_for_prompt(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Extract relevant metadata fields for prompt generation.

        Args:
            obj: Object from the metadata JSON

        Returns:
            Dictionary with relevant metadata fields
        """
        keys = [
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
        return {k: obj.get(k, "") for k in keys}

    def build_prompt(self, metadata: dict[str, Any]) -> str:
        """
        Build the prompt for OpenAI API based on metadata.

        Args:
            metadata: Dictionary containing object metadata

        Returns:
            Formatted prompt string
        """
        # Handle list fields safely
        subject = metadata.get("subject", [])
        if isinstance(subject, list):
            subject_str = ", ".join(subject)
        else:
            subject_str = str(subject) if subject else ""

        creator = metadata.get("creator", [])
        if isinstance(creator, list):
            creator_str = ", ".join(creator)
        else:
            creator_str = str(creator) if creator else ""

        is_part_of = metadata.get("isPartOf", [])
        if isinstance(is_part_of, list):
            is_part_of_str = ", ".join(is_part_of)
        else:
            is_part_of_str = str(is_part_of) if is_part_of else ""

        relation = metadata.get("relation", [])
        if isinstance(relation, list):
            relation_str = ", ".join(relation)
        else:
            relation_str = str(relation) if relation else ""

        prompt = f"""Du bist ein Spezialist für barrierefreie Alternativtexte (WCAG).
Das folgende Bild stammt von „forschung.stadtgeschichtebasel.ch" und diese Metadaten:

Titel: {metadata.get("title", "")}
Beschreibung: {metadata.get("description", "")}
Thema: {subject_str}
Zeitraum: {metadata.get("coverage", "")}
Schöpfer: {creator_str}
Datum: {metadata.get("date", "")}
Teil von: {is_part_of_str}
Verweise: {relation_str}
Sprache: {metadata.get("language", "")}

Analysiere das Bild (siehe separate Bildübertragung) zusammen mit den Metadaten.

1. Identifiziere: Bildtyp – *Informativ*, **Komplex (Diagramm/Karte)** oder
   *Bild von Text*.
2. Erstelle:
   • Bei *Informativ*: 1–2 Sätze, keine Wiederholung der Metadaten, Fokus
     auf Relevanz.
   • Bei *Komplex* (Diagramm/Karte): Alt-Text mit Typ + Kernaussage, ggf.
     Langbeschreibung.
   • Bei *Bild von Text*: Text als Alt-Text (bei Kurztext) oder Hinweis +
     exakter OCR-Text.
Allgemein: Keine Formate wie „Bild von…", keine Emojis, Alt-Text auf Deutsch,
maximal 120 Zeichen (informativ/Text), maximal 200 Zeichen (komplex).

Antworte **nur** als JSON wie im Beispiel:
{{
  "objectid": "{metadata.get("objectid", "")}",
  "alt_text": "…",
  "longdesc": "…"  // optional, nur falls nötig
}}"""
        return prompt

    def get_image_bytes(self, url: str) -> bytes:
        """
        Download image for OpenAI API.

        Note: Image resizing is handled by omeka, so we use images as-is.

        Args:
            url: URL to the image (should be object_thumb field)

        Returns:
            Image data as bytes
        """
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def generate_alttext(self, metadata: dict[str, Any], image_bytes: bytes) -> str:
        """
        Generate alt text using OpenAI API.

        Args:
            metadata: Object metadata
            image_bytes: Image data as bytes

        Returns:
            JSON string with alt text and optional long description
        """
        try:
            import openai
        except ImportError as err:
            raise ImportError(
                "OpenAI package is required. Install with: uv add openai"
            ) from err

        prompt = self.build_prompt(metadata)

        client = openai.OpenAI(api_key=self.openai_api_key)

        # Convert bytes to base64 for API
        import base64

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model="gpt-5",  # Updated to newest OpenAI model (GPT-5)
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein Experte für Alternativtexte.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high",
                            },
                        },
                    ],
                },
            ],
            max_completion_tokens=1000
        )

        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI API returned empty response")
        return content

    def enhance_metadata(
        self, metadata_source: str, output_file: str = "alttexte_automatisch.json"
    ) -> list[dict[str, Any]]:
        """
        Main method to enhance metadata for all objects.

        Args:
            metadata_source: Path to local JSON file or URL to the metadata JSON file
            output_file: Output file name for enhanced metadata

        Returns:
            List of enhanced metadata objects
        """
        print(f"Loading metadata from {metadata_source}...")
        data = self.load_metadata(metadata_source)
        objects = data.get("objects", [])

        results = []

        for i, obj in enumerate(objects):
            print(
                f"Processing object {i + 1}/{len(objects)}: "
                f"{obj.get('objectid', 'unknown')}"
            )

            metadata = self.get_metadata_for_prompt(obj)
            image_url = metadata.get("object_thumb")

            if not image_url:
                print("  Skipping - no image URL found")
                continue

            try:
                print(f"  Downloading image from {image_url}")
                image_bytes = self.get_image_bytes(image_url)

                print("  Generating alt text...")
                json_result = self.generate_alttext(metadata, image_bytes)

                # Parse the JSON response
                try:
                    parsed_result = json.loads(json_result)
                    results.append(parsed_result)
                    print(
                        f"  ✓ Generated alt text: "
                        f"{parsed_result.get('alt_text', '')[:50]}..."
                    )
                except json.JSONDecodeError:
                    print(f"  ✗ Failed to parse JSON response: {json_result}")
                    continue

            except Exception as e:
                print(f"  ✗ Error processing object: {e}")
                continue

        # Save results
        print(f"Saving {len(results)} enhanced objects to {output_file}")
        with open(output_file, "w", encoding="utf8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        return results


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
