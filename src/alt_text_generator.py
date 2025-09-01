#!/usr/bin/env python3
"""
Alt Text Generator Module

This module provides functionality to generate WCAG 2.2-compliant alternative
text for images using OpenAI's GPT-5 model.
"""

import base64
import json
import logging
from typing import Any

import requests


class AltTextGenerator:
    """Generates WCAG-compliant alternative text for images."""

    def __init__(self, openai_client=None, logger=None):
        """
        Initialize the alt text generator.

        Args:
            openai_client: OpenAI client for GPT-5 access
            logger: Optional logger instance
        """
        self.openai_client = openai_client
        self.logger = logger or logging.getLogger(__name__)

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

    def generate_alt_text(
        self, metadata: dict[str, Any], image_bytes: bytes
    ) -> dict[str, Any]:
        """
        Generate alt text using OpenAI API.

        Args:
            metadata: Object metadata
            image_bytes: Image data as bytes

        Returns:
            Dictionary with alt text and optional long description
        """
        if not self.openai_client:
            raise ValueError("OpenAI client is required for alt text generation")

        prompt = self.build_prompt(metadata)

        # Convert bytes to base64 for API
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5",  # Use GPT-5 consistently
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
                max_completion_tokens=2000,  # Increased token limit
            )
        except Exception as e:
            raise ValueError(f"OpenAI API call failed: {e}") from e

        content = response.choices[0].message.content

        # Log the complete API response for debugging
        self.logger.debug("=" * 80)
        self.logger.debug(f"Object ID: {metadata.get('objectid', 'unknown')}")
        self.logger.debug(f"Response ID: {response.id}")
        self.logger.debug(f"Model: {response.model}")
        self.logger.debug(f"Usage: {response.usage}")
        self.logger.debug(f"Choices count: {len(response.choices)}")
        if response.choices:
            choice = response.choices[0]
            self.logger.debug(f"Finish reason: {choice.finish_reason}")
            self.logger.debug(f"Message role: {choice.message.role}")
            self.logger.debug(f"Message content type: {type(choice.message.content)}")
            content_length = (
                len(choice.message.content) if choice.message.content else 0
            )
            self.logger.debug(f"Message content length: {content_length}")
            self.logger.debug(f"Message content: '{choice.message.content}'")
        self.logger.debug("=" * 80)

        if content is None or not content.strip():
            # Debug information
            choices_len = len(response.choices)
            self.logger.error(f"Empty response - choices length: {choices_len}")
            if response.choices:
                finish_reason = response.choices[0].finish_reason
                self.logger.error(f"Message content: '{content}'")
                self.logger.error(f"Finish reason: {finish_reason}")

                if finish_reason == "length":
                    raise ValueError(
                        "OpenAI API response was cut off due to "
                        "max_completion_tokens limit. The model reached the "
                        "token limit before completing the response."
                    )
                elif finish_reason == "content_filter":
                    raise ValueError(
                        "OpenAI API response was filtered due to content "
                        "policy. The image or prompt may violate OpenAI's "
                        "usage policies."
                    )
            raise ValueError("OpenAI API returned empty or null response")

        # Parse the JSON response
        try:
            parsed_result = json.loads(content.strip())

            # Validate that we have the required fields
            if not isinstance(parsed_result, dict):
                raise ValueError("Response is not a JSON object")

            if "alt_text" not in parsed_result:
                raise ValueError("Response missing 'alt_text' field")

            return parsed_result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {content.strip()}") from e

    def generate_for_object(self, obj: dict[str, Any]) -> dict[str, Any]:
        """
        Generate alt text for a complete object.

        Args:
            obj: Object metadata dictionary

        Returns:
            Dictionary with alt text data
        """
        metadata = self.get_metadata_for_prompt(obj)
        image_url = metadata.get("object_thumb")

        if not image_url:
            raise ValueError("No image URL found in object_thumb field")

        self.logger.info(f"Downloading image from {image_url}")
        image_bytes = self.get_image_bytes(image_url)

        self.logger.info("Generating alt text...")
        result = self.generate_alt_text(metadata, image_bytes)

        return result
