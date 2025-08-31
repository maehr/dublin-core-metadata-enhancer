# Iconclass Configuration

The Dublin Core Metadata Enhancer now includes optional Iconclass subject classification. This feature generates up to 5 Dublin Core `subject` values per object using Iconclass notations and URIs.

## Environment Variables

Configure Iconclass classification using these environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `ICONCLASS_ENABLE` | `true` | Enable/disable Iconclass classification |
| `ICONCLASS_TOP_K` | `5` | Maximum number of subjects to generate (1-10) |
| `ICONCLASS_LANG` | `de` | Preferred language for labels (`de` or `en`) |
| `ICONCLASS_VALIDATE` | `true` | Validate notations via Iconclass API |
| `ICONCLASS_SEARCH_URL` | unset | Optional Iconclass Search API URL |

## Usage

```bash
# Enable Iconclass classification (default)
export ICONCLASS_ENABLE=true
export ICONCLASS_TOP_K=5
export ICONCLASS_LANG=de
export ICONCLASS_VALIDATE=true

# Run enhancement with Iconclass subjects
uv run python enhance_metadata.py --metadata-url "data/metadata.json"

# Disable Iconclass classification
export ICONCLASS_ENABLE=false
uv run python enhance_metadata.py --metadata-url "data/metadata.json"

# Configure for English labels with validation disabled (faster)
export ICONCLASS_LANG=en
export ICONCLASS_VALIDATE=false
export ICONCLASS_TOP_K=3
uv run python enhance_metadata.py --metadata-url "data/metadata.json"
```

## Output Format

When Iconclass classification is enabled, each enhanced object includes a `subjects` array:

```json
{
  "objectid": "example001",
  "alt_text": "Karte von Basel als befestigte Grenzstadt, umgeben von Breisgau und Sundgau.",
  "longdesc": "",
  "subjects": [
    {
      "valueURI": "https://iconclass.org/25F",
      "notation": "25F",
      "prefLabel": {
        "de": "Stadtansicht",
        "en": "city view"
      },
      "confidence": 0.86,
      "scheme": "Iconclass"
    },
    {
      "valueURI": "https://iconclass.org/62",
      "notation": "62", 
      "prefLabel": {
        "de": "Karte",
        "en": "map"
      },
      "confidence": 0.83,
      "scheme": "Iconclass"
    }
  ]
}
```

## DCMI Compliance

This implementation follows DCMI guidelines:
- Uses controlled vocabulary URIs (https://iconclass.org/{notation})
- Provides structured subject metadata with confidence scores
- Includes multilingual labels (German and English)
- Each subject resolves to machine-readable JSON via `{notation}.json`

## How It Works

1. **Keyword Extraction**: Extracts relevant terms from title, description, and subject fields
2. **Candidate Generation**: Uses LLM to propose Iconclass notations based on metadata context
3. **Validation**: Optionally validates each notation via Iconclass JSON API
4. **Diversity**: Applies heuristics to ensure diverse coverage across Iconclass main divisions
5. **Selection**: Ranks and selects top-K subjects based on confidence scores

## Performance Considerations

- **Validation**: Set `ICONCLASS_VALIDATE=false` for faster processing (skips API validation)
- **Top-K**: Lower `ICONCLASS_TOP_K` values reduce processing time
- **Search API**: Configure `ICONCLASS_SEARCH_URL` when available for improved accuracy

## Error Handling

Iconclass classification is designed to fail gracefully:
- If classification fails, objects still include alt text
- Invalid notations are filtered out during validation
- Missing OpenAI packages disable Iconclass automatically
- Network errors during validation are logged but don't stop processing