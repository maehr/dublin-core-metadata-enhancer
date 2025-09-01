# Iconclass Configuration

The Dublin Core Metadata Enhancer includes optional Iconclass subject classification using ChatGPT-5. This feature generates up to 5 Dublin Core `subject` values per object using Iconclass notations and URIs, following DCMI best practices.

## Architecture

The Iconclass classification is implemented as a separate module (`src/iconclass_classifier.py`) with its own API, similar to the alt text generator (`src/alt_text_generator.py`). Both modules are orchestrated by the main metadata enhancer (`src/metadata_enhancer.py`) and output results in timestamped JSON-LD format using the common utilities (`src/common.py`).

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

# Run enhancement with Iconclass subjects (outputs JSON-LD)
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

When Iconclass classification is enabled, the JSON-LD output includes standardized Dublin Core subject metadata:

```json
{
  "@context": {
    "dc": "http://purl.org/dc/terms/",
    "dcmitype": "http://purl.org/dc/dcmitype/",
    "edm": "http://www.europeana.eu/schemas/edm/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "edm:providedCHO": [
    {
      "@type": "edm:ProvidedCHO",
      "dc:identifier": "example001",
      "dc:description": {
        "@type": "edm:AltText",
        "@value": "Karte von Basel als befestigte Grenzstadt, umgeben von Breisgau und Sundgau.",
        "@language": "de"
      },
      "dc:subject": [
        {
          "@id": "https://iconclass.org/25F",
          "skos:notation": "25F",
          "skos:prefLabel": [
            {
              "@value": "Stadtansicht",
              "@language": "de"
            },
            {
              "@value": "city view", 
              "@language": "en"
            }
          ],
          "edm:confidence": 0.86,
          "skos:inScheme": {
            "@id": "https://iconclass.org/",
            "skos:prefLabel": "Iconclass"
          }
        },
        {
          "@id": "https://iconclass.org/62",
          "skos:notation": "62",
          "skos:prefLabel": [
            {
              "@value": "Karte",
              "@language": "de"
            },
            {
              "@value": "map",
              "@language": "en"
            }
          ],
          "edm:confidence": 0.83,
          "skos:inScheme": {
            "@id": "https://iconclass.org/",
            "skos:prefLabel": "Iconclass"
          }
        }
      ]
    }
  ]
}
```

## DCMI Compliance

This implementation follows DCMI guidelines and JSON-LD best practices:
- Uses controlled vocabulary URIs (https://iconclass.org/{notation})
- Provides structured subject metadata with confidence scores
- Includes multilingual labels (German and English) using `skos:prefLabel`
- Each subject resolves to machine-readable JSON via `{notation}.json`
- Follows Europeana Data Model (EDM) for cultural heritage objects
- Uses SKOS vocabulary for concept schemes and notations

## How It Works

The Iconclass classifier (`src/iconclass_classifier.py`) implements the following workflow:

1. **Keyword Extraction**: Extracts relevant terms from title, description, and subject fields
2. **Candidate Generation**: Uses ChatGPT-5 to propose Iconclass notations based on metadata context
3. **Validation**: Optionally validates each notation via Iconclass JSON API
4. **Diversity**: Applies heuristics to ensure diverse coverage across Iconclass main divisions
5. **Selection**: Ranks and selects top-K subjects based on confidence scores
6. **JSON-LD Formatting**: Outputs results using Dublin Core terms and JSON-LD context

## API Usage

The Iconclass classifier can also be used independently:

```python
from src.iconclass_classifier import IconclassClassifier
from openai import OpenAI

# Initialize with OpenAI client
client = OpenAI(api_key="your-api-key")
classifier = IconclassClassifier(client)

# Classify an object
obj = {
    "objectid": "test001",
    "title": "Basel Stadtansicht",
    "description": "Eine historische Karte von Basel"
}

subjects = classifier.classify_object(obj)
print(subjects)
```

## Performance Considerations

- **Validation**: Set `ICONCLASS_VALIDATE=false` for faster processing (skips API validation)
- **Top-K**: Lower `ICONCLASS_TOP_K` values reduce processing time
- **Search API**: Configure `ICONCLASS_SEARCH_URL` when available for improved accuracy
- **Model**: Uses ChatGPT-5 consistently for both alt text and Iconclass classification

## Error Handling

Iconclass classification is designed to fail gracefully:
- If classification fails, objects still include alt text
- Invalid notations are filtered out during validation
- Missing OpenAI packages disable Iconclass automatically
- Network errors during validation are logged but don't stop processing
- The modular architecture ensures alt text generation continues even if Iconclass fails

## Testing

The Iconclass classifier includes comprehensive tests:

```bash
# Run Iconclass-specific tests
python -m pytest test/test_iconclass_classifier.py -v

# Run all tests including integration
python -m pytest test/ -v
```