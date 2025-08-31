#!/usr/bin/env python3
"""
Iconclass Subject Classification Module

This module provides functionality to classify Dublin Core metadata objects
using Iconclass subject terms with URIs as recommended by DCMI.
"""

import json
import os
import re
import time
from typing import Any

import requests


class IconclassClassifier:
    """Classifies objects using Iconclass subject terms."""

    def __init__(self, openai_client=None):
        """
        Initialize the Iconclass classifier.

        Args:
            openai_client: Optional OpenAI client for LLM-based classification
        """
        self.openai_client = openai_client

        # Configuration from environment variables
        self.top_k = int(os.getenv("ICONCLASS_TOP_K", "5"))
        self.lang = os.getenv("ICONCLASS_LANG", "de")
        self.validate = os.getenv("ICONCLASS_VALIDATE", "true").lower() == "true"
        self.search_url = os.getenv("ICONCLASS_SEARCH_URL")  # optional
        self.json_base = "https://iconclass.org"

    def validate_notation(self, notation: str) -> dict[str, Any]:
        """
        Validate an Iconclass notation and retrieve labels.

        Args:
            notation: Iconclass notation to validate

        Returns:
            Dictionary with notation details if valid, empty dict otherwise
        """
        if not notation:
            return {}

        url = f"{self.json_base}/{requests.utils.quote(notation, safe='')}.json"

        try:
            response = requests.get(url, timeout=20)
            if response.status_code != 200:
                return {}

            data = response.json()

            # Extract labels from various possible formats
            label_de = None
            label_en = None

            # Try different label field names that might exist
            for key in ("prefLabel", "label", "labels"):
                if isinstance(data.get(key), dict):
                    label_de = data[key].get("de") or label_de
                    label_en = data[key].get("en") or label_en
                elif isinstance(data.get(key), list):
                    # Handle lists of language-tagged labels
                    for item in data[key]:
                        if isinstance(item, dict):
                            if item.get("lang") == "de":
                                label_de = item.get("value", label_de)
                            if item.get("lang") == "en":
                                label_en = item.get("value", label_en)

            return {
                "notation": notation,
                "label_de": label_de,
                "label_en": label_en,
                "uri": f"https://iconclass.org/{notation}"
            }

        except Exception:
            return {}

    def search_iconclass_terms(self, terms: list[str]) -> list[dict[str, Any]]:
        """
        Search Iconclass terms using the search API if configured.

        Args:
            terms: List of search terms

        Returns:
            List of candidate notations with labels and scores
        """
        if not self.search_url:
            return []

        candidates = []

        for term in terms:
            try:
                response = requests.get(
                    self.search_url,
                    params={"q": term, "lang": self.lang},
                    timeout=20
                )

                if response.status_code == 200:
                    data = response.json()
                    # Expect list of {notation, label, score} - adapt if API differs
                    for item in data[:10]:  # Limit to top 10 per term
                        candidates.append({
                            "notation": item.get("notation"),
                            "label": item.get("label"),
                            "score": item.get("score", 0.5)
                        })

            except Exception:
                continue

            time.sleep(0.1)  # Rate limiting

        return candidates

    def build_iconclass_prompt(self, obj: dict[str, Any]) -> str:
        """
        Build prompt for LLM-based Iconclass classification.

        Args:
            obj: Object metadata

        Returns:
            Formatted prompt string
        """
        # Handle various field types safely
        subject_list = obj.get("subject", [])
        if isinstance(subject_list, list):
            subject_str = ", ".join(subject_list)
        else:
            subject_str = str(subject_list) if subject_list else ""

        creator_list = obj.get("creator", [])
        if isinstance(creator_list, list):
            creator_str = ", ".join(creator_list)
        else:
            creator_str = str(creator_list) if creator_list else ""

        relation_list = obj.get("relation", [])
        if isinstance(relation_list, list):
            relation_str = ", ".join(relation_list)
        else:
            relation_str = str(relation_list) if relation_list else ""

        return f"""You assign up to 10 **Iconclass** notations for this record.
Respond as JSON array of objects:
[{{"notation":"…","label_de":"…","label_en":"…","why":"…"}}]
Use valid Iconclass codes (e.g., 25F, 31A, 52D1). Prefer German labels when possible.

title: {obj.get('title', '')}
description: {obj.get('description', '')}
subject: {subject_str}
creator: {creator_str}
relation: {relation_str}
era/date: {obj.get('coverage', '')} {obj.get('date', '')}
language: {obj.get('language', '')}"""

    def get_llm_candidates(self, prompt: str) -> list[dict[str, Any]]:
        """
        Get Iconclass candidate notations from LLM.

        Args:
            prompt: Classification prompt

        Returns:
            List of candidate notations with labels
        """
        if not self.openai_client:
            return []

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o instead of gpt-5 for more reliability
                messages=[
                    {
                        "role": "system",
                        "content": "Return only JSON. Use valid Iconclass notations."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )

            content = response.choices[0].message.content
            if not content:
                return []

            # Find JSON array in the response
            start = content.find("[")
            end = content.rfind("]") + 1

            if start == -1 or end == 0:
                return []

            return json.loads(content[start:end])

        except Exception:
            return []

    def extract_keywords(self, obj: dict[str, Any]) -> list[str]:
        """
        Extract keywords from object metadata for search.

        Args:
            obj: Object metadata

        Returns:
            List of keywords
        """
        # Combine relevant text fields
        text_parts = []

        title = obj.get("title", "")
        if title:
            text_parts.append(str(title))

        description = obj.get("description", "")
        if description:
            text_parts.append(str(description))

        subject = obj.get("subject", [])
        if isinstance(subject, list):
            text_parts.extend(subject)
        elif subject:
            text_parts.append(str(subject))

        text = " ".join(text_parts)

        # Simple German keyword extraction (split on non-letters)
        terms = re.findall(r"[A-Za-zÄÖÜäöüß\-]+", text)
        terms = [t.lower() for t in terms if len(t) > 2]

        # Remove duplicates and limit
        return sorted(set(terms))[:20]

    def classify_object(self, obj: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Classify an object using Iconclass subject terms.

        Args:
            obj: Object metadata dictionary

        Returns:
            List of up to 5 Iconclass subject classifications
        """
        # 1) Extract search terms
        terms = self.extract_keywords(obj)

        # 2) Get candidates from API search (if configured)
        api_candidates = self.search_iconclass_terms(terms)

        # 3) Get candidates from LLM
        prompt = self.build_iconclass_prompt(obj)
        llm_candidates = self.get_llm_candidates(prompt)

        # 4) Unify and deduplicate candidates
        candidate_pool = {}

        for candidate in api_candidates + llm_candidates:
            notation = candidate.get("notation")
            if not notation:
                continue

            if notation not in candidate_pool:
                candidate_pool[notation] = {
                    "notation": notation,
                    "score": 0.0,
                    "label_de": candidate.get("label_de") or candidate.get("label"),
                    "label_en": candidate.get("label_en")
                }

            # Update with highest score
            score = float(candidate.get("score", 0.7))
            candidate_pool[notation]["score"] = max(
                candidate_pool[notation]["score"], score
            )

        # 5) Validate notations if enabled
        validated_candidates = []

        for notation, candidate in candidate_pool.items():
            if self.validate:
                validation_result = self.validate_notation(notation)
                if not validation_result:
                    continue  # Skip invalid notations

                candidate["uri"] = validation_result["uri"]
                candidate["label_de"] = (
                    candidate["label_de"] or validation_result["label_de"]
                )
                candidate["label_en"] = (
                    candidate["label_en"] or validation_result["label_en"]
                )
            else:
                candidate["uri"] = f"https://iconclass.org/{notation}"

            validated_candidates.append(candidate)

        # 6) Apply diversity heuristic by main division (first digit)
        by_division = {}
        for candidate in sorted(
            validated_candidates, key=lambda x: x["score"], reverse=True
        ):
            division = candidate["notation"][0] if candidate["notation"] else "0"
            if division not in by_division:
                by_division[division] = []
            if len(by_division[division]) < 1:  # Max 1 per division initially
                by_division[division].append(candidate)

        # 7) Select top-k candidates
        selected = []

        # First pass: best candidate from each division
        for division_candidates in by_division.values():
            for candidate in division_candidates:
                if len(selected) < self.top_k:
                    selected.append(candidate)

        # Second pass: fill remaining slots by score
        if len(selected) < self.top_k:
            remaining = [
                c for c in validated_candidates
                if c not in selected
            ]
            remaining.sort(key=lambda x: x["score"], reverse=True)
            selected.extend(remaining[:self.top_k - len(selected)])

        # 8) Format final output
        subjects = []
        for candidate in selected[:self.top_k]:
            subjects.append({
                "valueURI": candidate["uri"],
                "notation": candidate["notation"],
                "prefLabel": {
                    "de": candidate.get("label_de"),
                    "en": candidate.get("label_en")
                },
                "confidence": round(float(candidate.get("score", 0.7)), 2),
                "scheme": "Iconclass"
            })

        return subjects
