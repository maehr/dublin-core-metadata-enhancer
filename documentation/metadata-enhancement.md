# Metadata Enhancement Pipeline

The Dublin Core Metadata Enhancer includes an automated pipeline for generating WCAG 2.2-compliant alternative text for images in Dublin Core metadata records.

## Overview

This pipeline uses OpenAI's GPT-4o multimodal capabilities to analyze images within their metadata context and generate appropriate alternative text descriptions in German.

## Components

### Core Module (`src/metadata_enhancer.py`)

The main `MetadataEnhancer` class provides:

- **Metadata Loading**: Fetch Dublin Core metadata from JSON URLs
- **Image Processing**: Download and prepare images for AI analysis
- **Prompt Generation**: Create contextual prompts using metadata
- **AI Integration**: Generate alt text using OpenAI GPT-4o API
- **Output Generation**: Save enhanced metadata as JSON

### CLI Interface (`enhance_metadata.py`)

Command-line tool for running the enhancement pipeline:

```bash
python enhance_metadata.py [options]
```

Options:

- `--metadata-url`: Source URL for metadata JSON
- `--output`: Output file for enhanced metadata
- `--api-key`: OpenAI API key (or use environment variable)

### Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or copy `example.env` to `.env` and configure:

```bash
cp example.env .env
# Edit .env with your API key
```

## AI Prompt Design

The pipeline uses a carefully designed German prompt that:

1. **Identifies image types**:
   - Informative images (1-2 sentences, max 120 characters)
   - Complex content like diagrams/maps (max 200 characters, optional long description)
   - Text images (OCR-based alt text)

2. **Incorporates metadata context**:
   - Title, description, subject terms
   - Historical era, creator, dates
   - Collection and relationship information

3. **Follows WCAG 2.2 guidelines**:
   - Concise and descriptive
   - No redundant "Image of..." prefixes
   - German language output
   - Structured JSON response

## Output Format

Enhanced metadata objects include:

```json
{
	"objectid": "unique-identifier",
	"alt_text": "Descriptive alternative text in German",
	"longdesc": "Optional detailed description for complex content"
}
```

## Error Handling

The pipeline includes robust error handling for:

- Network connectivity issues
- Invalid image formats
- API rate limits and errors
- Malformed metadata
- Missing required fields

Failed objects are logged and skipped, allowing the pipeline to continue processing other objects.

## Testing

Unit tests cover all major components:

```bash
python test/test_metadata_enhancer.py
```

Tests use mocking to avoid API calls during development and validate:

- Metadata extraction and prompt building
- Image processing logic
- Error handling scenarios
- CLI argument parsing

## Performance Considerations

- **Batch Processing**: Process multiple objects in sequence
- **Rate Limiting**: Respect OpenAI API limits
- **Image Optimization**: Resize images to 800x800 maximum
- **Caching**: Consider implementing caching for repeated images

## Security

- API keys are handled securely through environment variables
- No sensitive data is logged or stored in outputs
- Image data is processed in memory only
